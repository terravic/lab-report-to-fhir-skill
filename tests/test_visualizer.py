"""Unit tests for Report-Specific Web UI HTML Dashboard Generator."""

import os
import json
import tempfile
import pytest

from src.visualizer import generate_html_dashboard
from src.parser import parse_lab_report_file
from src.fhir_builder import convert_parsed_data_to_fhir


def test_generate_report_specific_web_ui_cancer_report():
    # 1. Extract from specific lab report
    parsed = parse_lab_report_file("reports/synthetic_cancer_lab_report.pdf")
    bundle = convert_parsed_data_to_fhir(parsed)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "cancer_report_dashboard.html")
        res_path = generate_html_dashboard(bundle=bundle, output_html_path=out_html)

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that it renders the specific patient and report only
        assert "<!DOCTYPE html>" in content
        assert "HL7 FHIR Clinical Diagnostic Report" in content
        assert "Jane Q. Sample" in content
        assert "Cancer Signal Status" in content
        assert 'id="clinical-dashboard"' in content
        assert 'id="fhir-inspector"' in content
        assert 'id="biomarkers-list"' in content
        assert 'id="recommendations-list"' in content
        assert 'id="btn-theme-toggle"' in content
        assert 'id="biomarker-search"' in content
        assert 'id="file-input"' in content
        assert "synthetic-banner" not in content

        # Verify no sample selector dropdown or presets in UI
        assert 'id="sample-select"' not in content
        assert 'id="preset-selector"' not in content
        assert 'SAMPLE_PRESETS' not in content
        assert 'switchSample' not in content


def test_generate_report_specific_web_ui_colorectal_report():
    # 1. Extract from colorectal ctDNA lab report
    parsed = parse_lab_report_file("reports/synthetic_colorectal_ctdna.pdf")
    bundle = convert_parsed_data_to_fhir(parsed)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "colorectal_report_dashboard.html")
        res_path = generate_html_dashboard(bundle=bundle, output_html_path=out_html)

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check that it renders this report's specific patient and findings
        assert "Harold K. Sample" in content
        assert "SEPT9" in content
        assert "KRAS" in content
        # Verify it does not contain other patients or dropdowns
        assert "Jane Q. Sample" not in content
        assert "Brenda S. Sample" not in content
        assert 'id="sample-select"' not in content


def test_generate_report_specific_web_ui_prostate_report():
    # 1. Extract from prostate phi panel
    parsed = parse_lab_report_file("reports/synthetic_prostate_phi_panel.pdf")
    bundle = convert_parsed_data_to_fhir(parsed)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "prostate_report_dashboard.html")
        res_path = generate_html_dashboard(bundle=bundle, output_html_path=out_html)

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Arthur B. Sample" in content
        assert "Total PSA" in content
        assert "Prostate Health Index" in content
        assert 'class="gauge-bar-track"' in content
        assert "Jane Q. Sample" not in content
        assert 'id="sample-select"' not in content
