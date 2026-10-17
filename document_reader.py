import pypdf
from typing import Dict, Any

def extract_and_validate_pdf(file) -> Dict[str, Any]:
    """
    Validates the uploaded file, extracts text page-by-page,
    and returns metrics or error states.
    """
    result = {
        "success": False,
        "text": "",
        "page_count": 0,
        "char_count": 0,
        "error_message": ""
    }
    
    # Validate extension
    if not file.name.lower().endswith('.pdf'):
        result["error_message"] = "Invalid file type. Please upload a PDF document."
        return result

    try:
        reader = pypdf.PdfReader(file)
        page_count = len(reader.pages)
        result["page_count"] = page_count
        
        if page_count == 0:
            result["error_message"] = f"The file '{file.name}' is empty."
            return result
        
        extracted_chunks = []
        # Extract text while retaining page trace indicators
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                extracted_chunks.append(f"[Page {page_num}]\n{page_text.strip()}")
        
        full_text = "\n\n".join(extracted_chunks)
        result["char_count"] = len(full_text)
        
        # Check for image-only/scanned PDFs
        if result["char_count"] == 0:
            result["error_message"] = (
                f"Could not extract any readable text from '{file.name}'. "
                "The document might be scanned or image-only (requires OCR)."
            )
            return result
        
        # Rule of thumb check for extremely oversized data
        if result["char_count"] > 400000:
            result["error_message"] = f"'{file.name}' exceeds the optimal context limits for this comparison tier."
            return result

        result["text"] = full_text
        result["success"] = True
        
    except Exception as e:
        result["error_message"] = f"Failed to process PDF file: {str(e)}"
    
    return result
