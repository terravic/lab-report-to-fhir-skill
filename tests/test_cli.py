"""Integration tests for CLI execution."""
import json
import os
import tempfile
import pytest
from src.cli import process_single_file, process_directory


def test_cli_process_single_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_json = os.path.join(tmpdir, "output_bundle.json")
        bundle = process_single_file("reports/synthetic_cancer_lab_report.pdf", out_json, validate=True)

        assert os.path.exists(out_json)
        assert bundle["resourceType"] == "Bundle"

        with open(out_json, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["resourceType"] == "Bundle"
        assert len(data["entry"]) > 0


def test_cli_process_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        process_directory("reports", tmpdir, validate=True)
        json_files = os.listdir(tmpdir)
        assert len(json_files) == 5
        for jf in json_files:
            assert jf.endswith(".json")
