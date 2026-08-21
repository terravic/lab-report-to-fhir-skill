"""Unit tests for FHIR R4 validator."""
import pytest
from src.fhir_validator import validate_fhir_bundle, FHIRValidator


def test_valid_bundle_validation():
    valid_bundle = {
        "resourceType": "Bundle",
        "id": "bundle-1",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:patient-1",
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "name": [{"text": "John Doe"}],
                    "gender": "male",
                    "birthDate": "1980-01-01"
                }
            },
            {
                "fullUrl": "urn:uuid:obs-1",
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-1",
                    "status": "final",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "2857-1", "display": "Total PSA"}]
                    },
                    "subject": {"reference": "urn:uuid:patient-1"},
                    "valueQuantity": {"value": 5.4, "unit": "ng/mL"}
                }
            },
            {
                "fullUrl": "urn:uuid:report-1",
                "resource": {
                    "resourceType": "DiagnosticReport",
                    "id": "report-1",
                    "status": "final",
                    "code": {
                        "coding": [{"system": "http://loinc.org", "code": "72305-6", "display": "Prostate Panel"}]
                    },
                    "subject": {"reference": "urn:uuid:patient-1"},
                    "result": [{"reference": "urn:uuid:obs-1"}]
                }
            }
        ]
    }

    res = validate_fhir_bundle(valid_bundle)
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0
    assert res["resource_counts"]["Patient"] == 1
    assert res["resource_counts"]["Observation"] == 1
    assert res["resource_counts"]["DiagnosticReport"] == 1


def test_invalid_bundle_missing_patient():
    invalid_bundle = {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": [
            {
                "fullUrl": "urn:uuid:report-1",
                "resource": {
                    "resourceType": "DiagnosticReport",
                    "id": "report-1",
                    "status": "final",
                    "code": {"coding": [{"system": "http://loinc.org", "code": "11502-2"}]},
                    "subject": {"reference": "urn:uuid:nonexistent-patient"},
                    "result": []
                }
            }
        ]
    }

    res = validate_fhir_bundle(invalid_bundle)
    assert res["is_valid"] is False
    assert any("Patient" in e for e in res["errors"])
    assert any("could not be resolved" in e for e in res["errors"])


def test_invalid_resource_type():
    res = validate_fhir_bundle({"resourceType": "Observation"})
    assert res["is_valid"] is False
    assert any("Expected resourceType 'Bundle'" in e for e in res["errors"])
