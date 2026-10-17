# AI Document Comparison Assistant

A Streamlit web app that compares two PDF documents with an LLM (Google Gemini). It extracts text with
`pypdf`, summarises each document, finds similarities and differences, compares key details (dates,
amounts, names, requirements), and exports a DOCX report.

> **Scope:** informational comparison only. The app never claims a document is legally safe, compliant or equivalent.

## Features (mapped to the brief)
| Requirement | Where |
|---|---|
| FR-01 Upload two PDFs, show names | `app.py` |
| FR-02 Validate (type, empty, corrupt, encrypted, no text) | `document_reader.read_pdf` |
| FR-03 Separate text per document, with page numbers (`[Page N]` markers) | `document_reader.py` |
| FR-04 Preview + page/character counts | "Extracted content preview" expander |
| FR-05–FR-08 Summaries, similarities, differences, key details | `comparison.py` (3 LLM calls) |
| FR-09 Tabs: Summary A/B, Similarities, Differences, Key Details, Conclusion, Limitations | `app.py` |
| FR-10 DOCX download | `report_generator.py` (python-docx) |
| FR-11 Error handling (API errors, timeouts, rate limits, long docs, missing files) | `comparison.py`, `app.py` |
| FR-12 Reset / compare again | **Reset** button |

## Setup
```bash
git clone <your-repo-url> && cd ai-document-comparison-assistant
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # then put your key in .env (get one at https://aistudio.google.com/apikey)
python make_sample_documents.py  # optional: regenerates sample_documents/*.pdf
streamlit run app.py
```
Try it with `sample_documents/document_a.pdf` and `document_b.pdf` (fee $400→$450, 8→10 weeks,
quiz weighting, attendance, new coordinator, new section 6).

## Project structure
```
app.py                  Streamlit UI and session state
document_reader.py      PDF validation + text extraction (pypdf)
comparison.py           Prompts, Gemini client, JSON validation, orchestration
report_generator.py     DOCX report (python-docx)
make_sample_documents.py  Creates the sample PDFs
tests/test_app_logic.py   16 tests (no API key needed)
```

## How it works
1. **Validate & extract** – extension, `%PDF` signature, empty/encrypted/corrupt check; text is extracted
   page by page. Pages with no text are recorded and listed under *Limitations*. If *no* page has text
   (scanned PDF) the app stops with a clear message instead of producing a misleading comparison.
2. **Input limits** – `MAX_CHARS_PER_DOC` / `MAX_TOTAL_CHARS` (configurable in `.env`). Over the limit → clear message.
3. **LLM calls** – Document A summary, Document B summary, then a comparison call. All use low temperature
   (0.1) and JSON output mode.
4. **Prompt rules** – use only supplied text; keep A and B separate; no invented details; short verbatim
   excerpts with page references; the exact phrase `Not found in the provided text` for missing details;
   neutral tone and no legal claims.
5. **Validation** – JSON is parsed (code fences tolerated), schema/enums are normalised, malformed output
   is retried once with a corrective hint, then a safe error is shown. Every quoted excerpt is checked
   against the extracted text; items whose quotes can't be matched are flagged **"excerpt not verified"**
   and counted in *Limitations* – a guard against hallucinated differences.
6. **Display & export** – seven tabs on screen; the DOCX contains the same sections.

## Testing
```bash
python -m unittest discover -s tests -v      # or: pip install pytest && pytest
```
Automated: valid PDFs, wrong type, empty file, fake/corrupted PDF, scanned (no text) PDF, API failure,
malformed JSON retry, identical documents (no invented differences), fabricated evidence flagged,
long-document limit, unreadable pages, report contains all sections.

Manual checklist (needs your API key): two valid PDFs · one file missing · wrong type · scanned PDF ·
changed dates/numbers · near-identical docs · long document · wrong API key (error + retry) ·
download report · Reset.

## Limitations & future work
- No OCR: scanned PDFs are rejected (could add `pytesseract`).
- Very long documents are rejected rather than chunked (could add map-reduce chunking).
- Tables and multi-column layouts may extract in imperfect reading order.
- AI output can still be wrong – verify important findings against the originals.

## Viva cheat-sheet
- **PDF processing:** `PdfReader` → per-page `extract_text()` → cleaned text with `[Page N]` markers.
- **Prompt:** system prompt with strict evidence rules + JSON schema in the user prompt.
- **Workflow:** upload → validate → extract → limit check → summarise A → summarise B → compare → validate JSON → display → export/reset.
- **Error handling:** custom `DocumentError` / `ComparisonError`; friendly messages; retry button; backoff on 429/5xx.
- **Limitations:** see above.
