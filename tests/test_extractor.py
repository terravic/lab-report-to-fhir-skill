"""Unit tests for PDF extraction and text normalization."""
import os
import pytest
from src.extractor import clean_extracted_text, extract_text_from_pdf, extract_structured_pages


def test_clean_extracted_text():
    raw = "Patient\xa0Name\ue092 Jane Doe\nSYN\ue0881234\ue088X\n\n\n\nResult:\t\tPositive"
    cleaned = clean_extracted_text(raw)
    assert "Jane Doe" in cleaned
    assert ":" in cleaned
    assert "SYN-1234-X" in cleaned
    assert "\xa0" not in cleaned
    assert "\n\n\n\n" not in cleaned


def test_extract_text_from_pdf():
    pdf_path = "reports/synthetic_cancer_lab_report.pdf"
    assert os.path.exists(pdf_path), "Sample report must exist"
    text = extract_text_from_pdf(pdf_path)
    assert len(text) > 0
    assert "Multi-Cancer Early Detection" in text or "CLINICAL REFERENCE" in text
    assert "Jane Q. Sample" in text
    assert "Cancer Signal Detected" in text


def test_extract_structured_pages():
    pdf_path = "reports/synthetic_prostate_phi_panel.pdf"
    assert os.path.exists(pdf_path)
    pages = extract_structured_pages(pdf_path)
    assert len(pages) >= 1
    assert "page_number" in pages[0]
    assert "cleaned_text" in pages[0]
    assert "tables" in pages[0]
    assert len(pages[0]["tables"]) > 0


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("reports/non_existent_file.pdf")
