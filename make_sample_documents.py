"""Generate two sample PDFs (an old and an updated course policy) in sample_documents/."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "sample_documents"
OUT.mkdir(exist_ok=True)

DOC_A = {
    "title": "Introduction to Data Analytics - Course Policy (Version 1)",
    "sections": [
        ("1. Course Overview",
         "This 8-week course introduces learners to data cleaning, visualisation and basic "
         "statistics using Python. Classes run on Mondays and Wednesdays from 6:00 PM to 8:00 PM."),
        ("2. Eligibility",
         "Applicants must hold a high school diploma and have basic computer skills. "
         "No prior programming experience is required."),
        ("3. Fees and Payment",
         "The total course fee is $400. Payment is due by 1 March 2025. "
         "Refunds are available until the end of week 1."),
        ("4. Assessment",
         "Final grade: 40% weekly quizzes, 60% final project. A minimum attendance of 75% "
         "is required to receive the certificate."),
        ("5. Contact",
         "Questions should be sent to the course coordinator, Ms. Sarah Collins, at "
         "training@example.com."),
    ],
}

DOC_B = {
    "title": "Introduction to Data Analytics - Course Policy (Version 2)",
    "sections": [
        ("1. Course Overview",
         "This 10-week course introduces learners to data cleaning, visualisation and basic "
         "statistics using Python. Classes run on Mondays and Wednesdays from 6:00 PM to 8:00 PM."),
        ("2. Eligibility",
         "Applicants must hold a high school diploma and have basic computer skills. "
         "No prior programming experience is required."),
        ("3. Fees and Payment",
         "The total course fee is $450. Payment is due by 15 March 2025. "
         "Refunds are available until the end of week 1."),
        ("4. Assessment",
         "Final grade: 30% weekly quizzes, 70% final project. A minimum attendance of 80% "
         "is required to receive the certificate."),
        ("5. Contact",
         "Questions should be sent to the course coordinator, Mr. David Reyes, at "
         "training@example.com."),
        ("6. Certificates",
         "Certificates are issued within 14 days after the final project is graded."),
    ],
}


def build(path: Path, spec: dict) -> None:
    styles = getSampleStyleSheet()
    story = [Paragraph(spec["title"], styles["Title"]), Spacer(1, 12)]
    for head, body in spec["sections"]:
        story += [Paragraph(head, styles["Heading2"]), Paragraph(body, styles["BodyText"]), Spacer(1, 8)]
    SimpleDocTemplate(str(path), pagesize=A4).build(story)


if __name__ == "__main__":
    build(OUT / "document_a.pdf", DOC_A)
    build(OUT / "document_b.pdf", DOC_B)
    print("Created sample_documents/document_a.pdf and document_b.pdf")
