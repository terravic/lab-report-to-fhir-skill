"""Unit tests for FHIR R4 Bundle and Resource Construction."""
import pytest
from src.parser import parse_lab_report_file
from src.fhir_builder import FHIRBundleBuilder, convert_parsed_data_to_fhir


@pytest.fixture
def sample_parsed_data():
    return {
        "report_title": "Synthetic Cancer Screening Report",
        "patient": {
            "name": "Jane Q. Sample",
            "dob": "1972-05-12",
            "gender": "female",
            "patient_id": "MRN-123456"
        },
        "provider": {
            "name": "Dr. Avery Sterling",
            "npi": "1234567890"
        },
        "facility": {
            "name": "Nexus Precision Diagnostics",
            "clia_id": "00D1234567",
            "address": "888 Synthetic Way, Fictional Heights, CA"
        },
        "specimen": {
            "specimen_id": "SYN-992834-X",
            "collection_date": "2026-08-07",
            "received_date": "2026-08-08",
            "report_date": "2026-08-14",
            "specimen_type": "Blood / Plasma"
        },
        "summary_result": {
            "status": "final",
            "result_text": "Cancer Signal Detected",
            "conclusion": "A cancer signal was detected in this blood sample."
        },
        "observations": [
            {
                "code": "94076-7",
                "display": "Cancer signal methylation analysis in cell-free DNA",
                "test_name": "Cancer Signal Status",
                "value": "Cancer Signal Detected",
                "value_type": "string",
                "interpretation": "A",
                "interpretation_display": "Abnormal",
                "reference_range": "Cancer Signal Not Detected"
            }
        ],
        "clinical_interpretation": "Clinical follow-up recommended.",
        "methodology": "NGS bisulfite sequencing.",
        "limitations": "Screening test only."
    }


def test_build_bundle_structure(sample_parsed_data):
    builder = FHIRBundleBuilder(sample_parsed_data, bundle_type="transaction")
    bundle = builder.build_bundle()

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "transaction"
    assert len(bundle["entry"]) >= 5

    res_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    assert "Patient" in res_types
    assert "Practitioner" in res_types
    assert "Organization" in res_types
    assert "Specimen" in res_types
    assert "Observation" in res_types
    assert "DiagnosticReport" in res_types


def test_patient_resource_attributes(sample_parsed_data):
    builder = FHIRBundleBuilder(sample_parsed_data)
    patient = builder.build_patient()

    assert patient["resourceType"] == "Patient"
    assert patient["name"][0]["family"] == "Sample"
    assert patient["name"][0]["given"] == ["Jane", "Q."]
    assert patient["gender"] == "female"
    assert patient["birthDate"] == "1972-05-12"
    assert patient["identifier"][0]["value"] == "MRN-123456"


def test_diagnostic_report_references(sample_parsed_data):
    builder = FHIRBundleBuilder(sample_parsed_data)
    bundle = builder.build_bundle()

    diag_entry = next(e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "DiagnosticReport")
    obs_entries = [e["resource"] for e in bundle["entry"] if e["resource"]["resourceType"] == "Observation"]

    assert diag_entry["status"] == "final"
    assert len(diag_entry["result"]) == len(obs_entries)

    for r_ref in diag_entry["result"]:
        ref_uuid = r_ref["reference"]
        assert any(e["fullUrl"] == ref_uuid for e in bundle["entry"])
