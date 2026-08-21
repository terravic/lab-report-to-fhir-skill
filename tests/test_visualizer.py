"""Unit tests for Canvas UI HTML Dashboard Generator."""

import os
import json
import tempfile
import pytest

from src.visualizer import generate_html_dashboard, load_all_preset_bundles
from src.parser import parse_lab_report_file
from src.fhir_builder import convert_parsed_data_to_fhir


def test_load_all_preset_bundles():
    presets = load_all_preset_bundles("output")
    assert len(presets) > 0
    assert "synthetic_cancer_lab_report" in presets
    assert presets["synthetic_cancer_lab_report"]["resourceType"] == "Bundle"


def test_generate_html_dashboard_default():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "test_viewer.html")
        res_path = generate_html_dashboard(output_html_path=out_html)

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "<!DOCTYPE html>" in content
        assert "HL7 FHIR Clinical Diagnostic Dashboard & Inspector" in content
        assert 'id="clinical-dashboard"' in content
        assert 'id="fhir-inspector"' in content
        assert 'id="preset-selector"' in content
        assert 'id="biomarkers-list"' in content
        assert "synthetic-banner" in content
        assert "Jane Q. Sample" in content


def test_generate_html_dashboard_with_custom_bundle():
    parsed = parse_lab_report_file("reports/synthetic_colorectal_ctdna.pdf")
    bundle = convert_parsed_data_to_fhir(parsed)

    with tempfile.TemporaryDirectory() as tmpdir:
        out_html = os.path.join(tmpdir, "colorectal_view.html")
        res_path = generate_html_dashboard(bundle=bundle, output_html_path=out_html)

        assert os.path.exists(res_path)
        with open(res_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Harold K. Sample" in content
        assert "SEPT9" in content
        assert "active_custom_report" in content
