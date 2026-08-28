"""
PDF Extraction Module.
Extracts raw text, page layouts, and tables from laboratory report PDF documents.
"""

from typing import List, Dict, Any, Optional
import os
import re


def clean_extracted_text(text: str) -> str:
    """
    Cleans raw extracted text by fixing common PDF ligature artifacts,
    Private Use Area (PUA) font encodings, excessive whitespace, and non-printable characters.
    """
    if not text:
        return ""
    
    # Replace known private-use font encoding glyphs and CID bullet glyphs to standard ASCII/Unicode
    pua_mapping = {
        '\ue092': ':',
        '\ue088': '-',
        '\ue082': '(',
        '\ue083': ')',
        '\ue012': '-',
        '\ue013': '-',
        '\ue014': '.',
        '\ue015': ',',
        '\ue016': ';',
        '\ue017': '!'
    }
    for pua_char, replacement in pua_mapping.items():
        text = text.replace(pua_char, replacement)
        
    text = text.replace('(cid:127)', '•')
    text = re.sub(r'\(cid:\d+\)', ' ', text)
    
    # Replace remaining private-use characters
    text = re.sub(r'[\ue000-\uf8ff]', ' ', text)
    
    # Replace non-breaking spaces and irregular whitespace
    text = text.replace('\xa0', ' ')
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Collapse intra-line multi-spaces
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.split('\n')]
    
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts all text content from a PDF file using pdfplumber with fallback to pypdf.
    
    Args:
        pdf_path: Path to the input PDF file.
        
    Returns:
        Cleaned text string of all pages.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    extracted_pages = []
    
    # Attempt extraction via pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text(layout=True) or page.extract_text() or ""
                extracted_pages.append(text)
    except Exception:
        # Fallback to pypdf
        try:
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            for page in reader.pages:
                extracted_pages.append(page.extract_text() or "")
        except Exception as e:
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
            
    full_text = "\n\n--- PAGE BREAK ---\n\n".join(extracted_pages)
    return clean_extracted_text(full_text)


def extract_structured_pages(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts structured page-level text and tabular data from a PDF.
    
    Args:
        pdf_path: Path to the input PDF file.
        
    Returns:
        List of dicts containing page_number, raw_text, cleaned_text, and extracted tables.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found at: {pdf_path}")
        
    pages_data = []
    
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                raw_text = page.extract_text() or ""
                tables = page.extract_tables() or []
                pages_data.append({
                    "page_number": i + 1,
                    "raw_text": raw_text,
                    "cleaned_text": clean_extracted_text(raw_text),
                    "tables": tables
                })
    except Exception:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        for i, page in enumerate(reader.pages):
            raw_text = page.extract_text() or ""
            pages_data.append({
                "page_number": i + 1,
                "raw_text": raw_text,
                "cleaned_text": clean_extracted_text(raw_text),
                "tables": []
            })
            
    return pages_data
