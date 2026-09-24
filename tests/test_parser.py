"""Unit tests for lab report parsing and entity extraction."""
import os
import pytest
from src.parser import normalize_date, normalize_gender, LabReportParser, parse_lab_report_file


def test_normalize_date():
    assert normalize_date("05/12/1972") == "1972-05-12"
    assert normalize_date("1972-05-12") == "1972-05-12"
    assert normalize_date("Aug 7, 2026") == "2026-08-07"
    assert normalize_date("August 7, 2026") == "2026-08-07"
    assert normalize_date("08-07-2026") == "2026-08-07"
    assert normalize_date("") is None
    assert normalize_date(None) is None


def test_normalize_gender():
    assert normalize_gender("Female") == "female"
    assert normalize_gender("F") == "female"
    assert normalize_gender("Male") == "male"
    assert normalize_gender("M") == "male"
    assert normalize_gender("Non-binary") == "other"
    assert normalize_gender("Other") == "other"
    assert normalize_gender("Unknown") == "unknown"
    assert normalize_gender("") == "unknown"


def test_parse_sample_mced_report():
    data = parse_lab_report_file("reports/synthetic_cancer_lab_report.pdf")
    assert data["patient"]["name"] == "Jane Q. Sample"
    assert data["patient"]["dob"] == "1972-05-12"
    assert data["patient"]["gender"] == "female"
    assert data["patient"]["patient_id"] == "P-44556677"
    assert "Dr. Avery Sterling" in data["provider"]["name"]
    assert data["provider"]["npi"] == "1234567890"
    assert data["specimen"]["specimen_id"] == "SYN-992834-X"
    assert data["specimen"]["collection_date"] == "2026-08-07"
    assert data["specimen"]["received_date"] == "2026-08-08"
    assert data["specimen"]["report_date"] == "2026-08-14"
    assert "Cancer Signal Detected" in data["summary_result"]["result_text"]
    assert len(data["observations"]) >= 3
    
    # Check CSO components
    origins = [o for o in data["observations"] if "Origin" in o["test_name"]]
    assert len(origins) == 2
    assert any("Lung" in o["value"] for o in origins)
    assert any("Pancreas" in o["value"] for o in origins)


def test_parse_colorectal_ctdna_report():
    data = parse_lab_report_file("reports/synthetic_colorectal_ctdna.pdf")
    assert data["patient"]["name"] == "Harold K. Sample"
    assert data["patient"]["dob"] == "1964-04-18"
    assert data["patient"]["gender"] == "male"
    assert "Positive" in data["summary_result"]["result_text"]
    assert len(data["observations"]) >= 4

    obs_names = [o["test_name"] for o in data["observations"]]
    assert "SEPT9 Methylation" in obs_names
    assert "KRAS Mutation Analysis" in obs_names
    assert "TP53 Mutation Analysis" in obs_names


def test_parse_hereditary_ngs_report():
    data = parse_lab_report_file("reports/synthetic_hereditary_ngs_panel.pdf")
    assert data["patient"]["name"] == "Brenda S. Sample"
    assert data["patient"]["gender"] == "female"
    assert "Pathogenic" in data["summary_result"]["result_text"]

    brca1_obs = next(o for o in data["observations"] if "BRCA1" in o["test_name"])
    assert "c.5266dupC" in brca1_obs["value"]
    assert brca1_obs["interpretation"] == "A"


def test_parse_prostate_phi_report():
    data = parse_lab_report_file("reports/synthetic_prostate_phi_panel.pdf")
    assert data["patient"]["name"] == "Arthur B. Sample"
    assert data["patient"]["gender"] == "male"
    assert len(data["observations"]) == 5

    psa_obs = next(o for o in data["observations"] if o["test_name"] == "Total PSA")
    assert psa_obs["value"] == 5.6
    assert psa_obs["unit"] == "ng/mL"
    assert psa_obs["interpretation"] == "H"

    phi_obs = next(o for o in data["observations"] if "phi" in o["test_name"].lower())
    assert phi_obs["value"] == 47.8
    assert phi_obs["interpretation"] == "H"


def test_parse_full_governance_and_specimen_details():
    data = parse_lab_report_file("reports/synthetic_cancer_lab_report.pdf")
    
    # Patient age
    assert data["patient"]["age"] == 54
    assert data["patient"]["dob"] == "1972-05-12"
    
    # Facility governance
    assert "CLINICAL REFERENCE" in data["facility"]["name"]
    assert data["facility"]["clia_id"] == "00D1234567"
    assert data["facility"]["cap_number"] == "8923412"
    assert "Dr. Eleanor Hayes" in data["facility"]["lab_director"]
    assert "FCAP" in data["facility"]["lab_director"]
    assert data["facility"]["address"] is not None
    
    # Specimen custody
    assert data["specimen"]["specimen_id"] == "SYN-992834-X"
    assert "Cell-Free DNA BCT" in data["specimen"]["collection_tube"]
    assert "10.0 mL" in data["specimen"]["volume"]
    assert data["specimen"]["collection_date"] == "2026-08-07"
    assert data["specimen"]["received_date"] == "2026-08-08"
    assert data["specimen"]["report_date"] == "2026-08-14"
    
    # Recommendations
    assert len(data["clinical_recommendations"]) >= 2
    assert any("imaging" in r.lower() for r in data["clinical_recommendations"])


def test_genomic_variant_components_parsing():
    data = parse_lab_report_file("reports/synthetic_hereditary_ngs_panel.pdf")
    brca1 = next(o for o in data["observations"] if "BRCA1" in o["test_name"])
    assert brca1.get("component") is not None
    assert brca1["component"].get("zygosity") == "Heterozygous"
    assert brca1["component"].get("hgvs_dna") == "c.5266dupC"
    assert brca1["component"].get("hgvs_protein") == "p.Gln1756Profs*74"

    crc = parse_lab_report_file("reports/synthetic_colorectal_ctdna.pdf")
    kras = next(o for o in crc["observations"] if "KRAS" in o["test_name"])
    assert kras.get("component") is not None
    assert kras["component"].get("vaf") == "1.8%"
    assert kras["component"].get("hgvs_protein") == "p.G12D"
