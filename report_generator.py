import io
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

def build_docx_report(doc_a_name: str, doc_b_name: str, report_body: str) -> io.BytesIO:
    """
    Converts raw text/markdown headers into a structural, downloadable .docx report binary string.
    """
    doc = Document()
    
    # Setup standard margin profiles
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Document Header Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run("AI Document Comparison Analysis Report")
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(20)
    title_run.font.bold = True
    
    # Metadata Segment
    meta = doc.add_paragraph()
    meta.add_run(f"Document A: {doc_a_name}\n").bold = True
    meta.add_run(f"Document B: {doc_b_name}\n").bold = True
    meta.add_run("Scope Notice: This is an informational comparison tool. It is not a legal decision-maker.").italic = True
    doc.add_paragraph("-" * 60)
    
    # Parse the markdown headers cleanly into native file formats
    lines = report_body.split('\n')
    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue
            
        if cleaned.startswith("###"):
            p = doc.add_paragraph()
            run = p.add_run(cleaned.replace("###", "").strip())
            run.font.name = 'Arial'
            run.font.size = Pt(14)
            run.font.bold = True
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
        elif cleaned.startswith("-") or cleaned.startswith("*"):
            p = doc.add_paragraph(style='List Bullet')
            run = p.add_run(cleaned[1:].strip())
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
        else:
            p = doc.add_paragraph()
            run = p.add_run(cleaned)
            run.font.name = 'Calibri'
            run.font.size = Pt(11)
            
    # Save into an in-memory byte buffer
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
