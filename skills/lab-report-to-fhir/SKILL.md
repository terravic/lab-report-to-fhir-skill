---
name: lab-report-to-fhir
description: >-
  Extracts clinical entities and key-value pairs from laboratory report PDFs or unstructured lab text,
  converts them into standard HL7 FHIR Release 4 (R4) JSON resources (Patient, Observation,
  DiagnosticReport, Specimen, Practitioner, Organization, transaction Bundle) for EHR interoperability,
  and renders interactive Web UI clinical dashboards with live FHIR JSON inspection.
---

# Lab Report to HL7 FHIR Conversion Skill

This skill processes unstructured or semi-structured laboratory diagnostic reports (PDF files, OCR scans, or text excerpts), converts them into standard HL7 FHIR Release 4 (R4) JSON resources, and generates interactive Web UI dashboards for clinical review and JSON inspection.

---

## When to Use This Skill

Activate this skill when:
- The user provides or asks to process a laboratory report PDF file.
- The user asks to convert unstructured lab results into HL7 FHIR JSON objects.
- The user wants to map oncology screening panels (e.g. Multi-Cancer Early Detection, Liquid Biopsy ctDNA, Hereditary NGS genetics, Prostate Biomarkers) or clinical chemistry panels into standard `DiagnosticReport` and `Observation` resources for Electronic Health Record (EHR) systems and clinical FHIR repositories.
- The user requests an interactive visual dashboard, Web UI, or click-to-inspect FHIR visualization.

---

## Execution Modes

The conversion and visualization workflow supports three execution modes:

### Mode 1: Automated Script Execution and Conversion
When a PDF file or directory is available on the filesystem, execute the conversion script directly from the project root directory:

```bash
# Convert a single PDF file to FHIR JSON:
python3 scripts/convert.py -i "reports/synthetic_cancer_lab_report.pdf" -o "output/synthetic_cancer_lab_report_fhir.json"

# Batch convert a directory of PDF reports:
python3 scripts/convert.py -i "reports/" -o "output/"
```

To validate generated bundles against FHIR R4 schema and referential integrity rules:
```bash
python3 scripts/validate.py -i "output/"
```

### Mode 2: Interactive Report-Specific Web UI Dashboard
When a user asks to view or visualize a laboratory report in an interactive dashboard:
1. **Extract and Convert**: Extract clinical entities and observations from the specified report and convert them into an HL7 FHIR R4 Bundle.
2. **Generate Report-Specific Web UI**: Generate a dedicated Web UI HTML file (`ui/fhir_viewer.html`) displaying the extracted data for that single report.

```bash
# Extract data from a PDF report and build the dedicated Web UI dashboard:
python3 scripts/visualize.py reports/synthetic_cancer_lab_report.pdf

# Or build the dedicated Web UI dashboard from a converted FHIR JSON bundle:
python3 scripts/visualize.py output/synthetic_colorectal_ctdna_fhir.json
```

In web interfaces supporting HTML dashboard rendering:
- Direct the user to the self-contained Web UI file at `ui/fhir_viewer.html`.
- The dashboard allows users to select any patient card, biomarker gauge, or observation row from that report to view its underlying HL7 FHIR R4 JSON definition.

### Mode 3: Direct Extraction and Mapping (For Text Inputs)
When the user provides raw lab text without disk access:
1. **Extract Core Entities**:
   - **Patient**: Name, Date of Birth (ISO format `YYYY-MM-DD`), Gender (`male`, `female`, `other`, `unknown`), Patient ID / MRN.
   - **Provider**: Ordering Physician Name, NPI (10-digit).
   - **Laboratory**: Facility Name, CLIA Number, Address, Laboratory Director.
   - **Specimen**: Specimen ID, Collection Date/Time, Received Date/Time, Specimen Type (Blood, Plasma, Serum, Tissue).
   - **Test Results**: Analyte names, quantitative values + units of measure, qualitative classifications, reference ranges, abnormal flags (`N`, `A`, `H`, `L`, `POS`, `NEG`).
   - **Clinical Narrative**: Overall summary result, clinical interpretation, test methodology, and limitations.

2. **Map Clinical Ontologies**:
   - Consult the [LOINC and SNOMED Mapping Reference](skills/lab-report-to-fhir/references/loinc_snomed_mapping.md) to assign standard LOINC codes (e.g. `94076-7` for MCED cfDNA methylation, `77983-5` for SEPT9 methylation, `2857-1` for Total PSA, `69548-6` for BRCA1/2 NGS).
   - Map specimen types to SNOMED CT (e.g. `119361006` for Plasma, `119364003` for Serum, `119297000` for Blood).

3. **Construct Valid FHIR R4 Bundle**:
   - Review [FHIR R4 Schema Reference](skills/lab-report-to-fhir/references/fhir_r4_schemas.md).
   - Build a `Bundle` with `type: "transaction"`.
   - Ensure `DiagnosticReport.subject` references the `Patient` resource using matching UUIDs.
   - Ensure every `DiagnosticReport.result` entry points to an `Observation` present in the bundle.

4. **Verify Output Integrity**:
   - Confirm no required fields are missing (`resourceType`, `id`, `status`, `code`).
   - Output valid JSON to the user.

---

## Detailed Reference Documentation

- [LOINC and SNOMED CT Ontology Mapping](skills/lab-report-to-fhir/references/loinc_snomed_mapping.md)
- [HL7 FHIR R4 Resource Schemas](skills/lab-report-to-fhir/references/fhir_r4_schemas.md)
- [EHR Integration Guide](skills/lab-report-to-fhir/references/ehr_integration_guide.md)
- [Interactive Web UI Application](ui/fhir_viewer.html)
