"""Run with:  python -m unittest discover -s tests -v   (or: pytest)

Covers the brief's section-12 test cases that don't need a live API key.
"""
import io
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from reportlab.pdfgen import canvas  # noqa: E402

import comparison as cmp  # noqa: E402
from document_reader import DocumentError, read_pdf  # noqa: E402
from report_generator import build_docx  # noqa: E402

SAMPLES = Path(__file__).resolve().parents[1] / "sample_documents"


def make_pdf(text_lines):
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    y = 800
    for line in text_lines:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    return buf.getvalue()


def blank_pdf():
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    c.rect(50, 50, 100, 100)  # a drawing, no text = like a scanned PDF
    c.save()
    return buf.getvalue()


class FakeLLM:
    """Returns canned JSON; can simulate malformed output or API failure."""

    def __init__(self, compare_payload=None, malformed_first=False, fail=False):
        self.calls = 0
        self.compare_payload = compare_payload
        self.malformed_first = malformed_first
        self.fail = fail

    def generate_json(self, system, prompt):
        self.calls += 1
        if self.fail:
            raise cmp.ComparisonError("The AI service is temporarily unavailable.")
        if self.malformed_first and self.calls == 1:
            return "this is {not json"
        if prompt.startswith("Summarise"):
            return json.dumps({"summary": "A summary.", "key_points": ["p1"]})
        return json.dumps(self.compare_payload)


PAYLOAD = {
    "similarities": [{"topic": "Eligibility", "detail": "Both need a diploma",
                      "evidence_a": "Applicants must hold a high school diploma",
                      "evidence_b": "Applicants must hold a high school diploma"}],
    "differences": [{"topic": "Fee", "type": "changed", "document_a": "$400", "document_b": "$450",
                     "evidence_a": "The total course fee is $400", "evidence_b": "The total course fee is $450"}],
    "key_details": [{"category": "amount", "item": "Course fee", "document_a": "$400",
                     "document_b": "$450", "status": "different"}],
    "conclusion": "The fee increased.",
    "limitations": [],
}


class ReaderTests(unittest.TestCase):
    def test_valid_pdf(self):
        d = read_pdf((SAMPLES / "document_a.pdf").read_bytes(), "document_a.pdf")
        self.assertGreater(d.char_count, 100)
        self.assertIn("[Page 1]", d.text)

    def test_wrong_file_type(self):
        with self.assertRaisesRegex(DocumentError, "not a PDF"):
            read_pdf(b"hello", "notes.txt")

    def test_empty_file(self):
        with self.assertRaisesRegex(DocumentError, "empty"):
            read_pdf(b"", "a.pdf")

    def test_fake_pdf(self):
        with self.assertRaisesRegex(DocumentError, "not a real PDF"):
            read_pdf(b"just text", "a.pdf")

    def test_corrupted_pdf(self):
        with self.assertRaises(DocumentError):
            read_pdf(b"%PDF-1.4 garbage garbage", "a.pdf")

    def test_scanned_pdf_no_text(self):
        with self.assertRaisesRegex(DocumentError, "No readable text"):
            read_pdf(blank_pdf(), "scan.pdf")


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.a = read_pdf(make_pdf(["Applicants must hold a high school diploma.",
                                    "The total course fee is $400."]), "a.pdf")
        self.b = read_pdf(make_pdf(["Applicants must hold a high school diploma.",
                                    "The total course fee is $450."]), "b.pdf")

    def test_full_pipeline_and_report(self):
        r = cmp.compare_documents(self.a, self.b, FakeLLM(PAYLOAD))
        self.assertEqual(r.differences[0]["document_b"], "$450")
        self.assertTrue(r.differences[0]["verified"])
        self.assertTrue(build_docx(r).startswith(b"PK"))  # valid docx (zip)

    def test_report_contains_all_sections(self):
        from docx import Document
        r = cmp.compare_documents(self.a, self.b, FakeLLM(PAYLOAD))
        text = "\n".join(p.text for p in Document(io.BytesIO(build_docx(r))).paragraphs)
        for heading in ["Document A", "Document B", "Similarities", "Differences",
                        "Key Details Comparison", "Overall Conclusion", "Limitations"]:
            self.assertIn(heading, text)

    def test_identical_docs_no_invented_differences(self):
        payload = dict(PAYLOAD, differences=[], conclusion="The documents appear identical.")
        r = cmp.compare_documents(self.a, self.a, FakeLLM(payload))
        self.assertEqual(r.differences, [])

    def test_fabricated_evidence_is_flagged(self):
        bad = json.loads(json.dumps(PAYLOAD))
        bad["differences"][0]["evidence_b"] = "The fee is one million dollars"
        r = cmp.compare_documents(self.a, self.b, FakeLLM(bad))
        self.assertFalse(r.differences[0]["verified"])
        self.assertTrue(any("not verified" in x for x in r.limitations))

    def test_malformed_json_retries_once(self):
        llm = FakeLLM(PAYLOAD, malformed_first=True)
        r = cmp.compare_documents(self.a, self.b, llm)
        self.assertEqual(llm.calls, 4)  # 1 bad + 1 retry + 2 more calls
        self.assertTrue(r.conclusion)

    def test_api_failure_surfaces_clean_error(self):
        with self.assertRaises(cmp.ComparisonError) as ctx:
            cmp.compare_documents(self.a, self.b, FakeLLM(fail=True))
        self.assertTrue(ctx.exception.retryable)

    def test_json_fences_are_tolerated(self):
        self.assertEqual(cmp.parse_json('```json\n{"a": 1}\n```'), {"a": 1})

    def test_missing_required_fields_rejected(self):
        with self.assertRaises(ValueError):
            cmp.validate_comparison({"similarities": []}, "x", "y")

    def test_long_document_message(self):
        old = cmp.MAX_CHARS_PER_DOC
        cmp.MAX_CHARS_PER_DOC = 10
        try:
            with self.assertRaisesRegex(cmp.DocumentTooLongError, "above the limit"):
                cmp.check_input_limits(self.a, self.b)
        finally:
            cmp.MAX_CHARS_PER_DOC = old

    def test_unreadable_pages_in_limitations(self):
        self.a.unreadable_pages = [3]
        r = cmp.compare_documents(self.a, self.b, FakeLLM(PAYLOAD))
        self.assertTrue(any("page(s) 3" in x for x in r.limitations))


if __name__ == "__main__":
    unittest.main()
