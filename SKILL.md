---
name: lab-report-to-fhir
description: >-
  Extracts clinical entities and key-value pairs from laboratory report PDFs or unstructured lab text,
  converts them into standard HL7 FHIR Release 4 (R4) JSON resources (Patient, Observation,
  DiagnosticReport, Specimen, Practitioner, Organization, transaction Bundle) for EHR interoperability,
  and renders interactive Canvas UI clinical dashboards with live FHIR JSON inspection.
---

# Lab Report to HL7 FHIR Conversion Skill

This skill teaches the agent how to process unstructured or semi-structured laboratory diagnostic reports (PDF files, OCR scans, or text excerpts), convert them into standard HL7 FHIR Release 4 (R4) JSON resources, and render interactive Canvas UI dashboards for clinical review and JSON inspection.

---

## When to Use This Skill

Activate this skill when:
- The user provides or asks to process a laboratory report PDF file.
- The user asks to convert unstructured lab results into HL7 FHIR JSON objects.
- The user wants to map oncology screening panels (e.g. Multi-Cancer Early Detection, Liquid Biopsy ctDNA, Hereditary NGS genetics, Prostate Biomarkers) or clinical chemistry panels into standard `DiagnosticReport` and `Observation` resources for Electronic Health Record (EHR) integration (such as Epic, Cerner, or cloud FHIR stores).
- The user requests an interactive visual dashboard, Canvas UI, or click-to-inspect FHIR visualization.

---

## Execution Modes

The agent can perform the conversion and visualization in three ways:

### Mode 1: Automated Script Execution & Conversion
When a PDF file or directory is available on the filesystem, execute the conversion script directly:

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

### Mode 2: Interactive Canvas UI Dashboard (Recommended for User Interfaces)
To provide the user with a visual, interactive clinical dashboard featuring dual-pane FHIR JSON inspection:

```bash
# Launch interactive visual dashboard for a specific converted FHIR bundle:
python3 scripts/visualize.py output/synthetic_cancer_lab_report_fhir.json

# Or directly convert a PDF and launch the visual dashboard:
python3 scripts/visualize.py reports/synthetic_colorectal_ctdna.pdf
```

In agent harnesses supporting iframe or Canvas HTML rendering (such as Gemini Enterprise App, Spark, and Antigravity):
- Point the user to the self-contained Canvas UI file at `ui/fhir_viewer.html`.
- The dashboard allows users to click on any patient card, biomarker gauge, or observation row to instantly view its underlying HL7 FHIR R4 JSON definition.

### Mode 3: Direct Agent Extraction and Mapping (For Text Inputs)
When the user pastes raw lab text or asks for on-the-fly mapping without disk access:
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
   - Output clean, valid JSON to the user.

---

## Detailed Reference Documentation

- [LOINC and SNOMED CT Ontology Mapping](skills/lab-report-to-fhir/references/loinc_snomed_mapping.md)
- [HL7 FHIR R4 Resource Schemas](skills/lab-report-to-fhir/references/fhir_r4_schemas.md)
- [EHR Integration Guide (Epic, Cerner, Cloud FHIR Stores)](skills/lab-report-to-fhir/references/ehr_integration_guide.md)
- [Interactive Canvas UI Application](ui/fhir_viewer.html)
