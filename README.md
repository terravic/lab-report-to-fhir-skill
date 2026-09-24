# Laboratory Report to HL7 FHIR Conversion Toolkit and Agent Skill

A clinical data conversion toolkit and Agent Skill that transforms unstructured and semi-structured laboratory report PDFs and clinical text into standard HL7 FHIR Release 4 (R4) JSON resources (`Patient`, `Observation`, `DiagnosticReport`, `Specimen`, `Organization`, `Practitioner`, and transaction `Bundle`).

This toolkit supports healthcare interoperability workflows by automating the ingestion of specialized diagnostic results--including Multi-Cancer Early Detection (MCED) cell-free DNA methylation assays, liquid biopsy circulating tumor DNA (ctDNA) panels, hereditary oncology Next-Generation Sequencing (NGS) panels, and biomarker immunoassays--into Electronic Health Record (EHR) systems, Laboratory Information Systems (LIS), and clinical FHIR repositories.

---

## Table of Contents

1. [Architecture and Clinical Scope](#architecture-and-clinical-scope)
2. [Project Directory Layout](#project-directory-layout)
3. [Non-Technical User Guide: How to Use This Skill](#non-technical-user-guide-how-to-use-this-skill)
   - [Overview for Non-Technical Users](#overview-for-non-technical-users)
   - [Real-World Use Case Examples](#real-world-use-case-examples)
   - [What Files You Can Upload](#what-files-you-can-upload)
   - [Sample Files Available for Testing](#sample-files-available-for-testing)
   - [Step-by-Step Walkthrough in an Agent Chat](#step-by-step-walkthrough-in-an-agent-chat)
   - [Example Prompts to Use](#example-prompts-to-use)
   - [Understanding the Results](#understanding-the-results)
4. [Interactive Web UI Dashboard](#interactive-web-ui-dashboard)
   - [Dashboard Capabilities](#dashboard-capabilities)
   - [How to Launch and Use the Visualizer](#how-to-launch-and-use-the-visualizer)
5. [Developer and Technical Guide](#developer-and-technical-guide)
   - [Installation and Dependencies](#installation-and-dependencies)
   - [Command Line Interface (CLI)](#command-line-interface-cli)
   - [Python API Usage](#python-api-usage)
   - [Generating Synthetic Test Data](#generating-synthetic-test-data)
   - [Validating FHIR Bundles](#validating-fhir-bundles)
   - [Automated Testing](#automated-testing)
6. [HL7 FHIR R4 Mapping Specification](#hl7-fhir-r4-mapping-specification)
7. [Clinical Ontology Standards (LOINC and SNOMED CT)](#clinical-ontology-standards-loinc-and-snomed-ct)
8. [Synthetic Data and Privacy Compliance Statement](#synthetic-data-and-privacy-compliance-statement)
9. [License](#license)

---

## Synthetic Data Notice

The sample laboratory PDF reports provided in the `reports/` directory and test fixtures contain exclusively synthetic data with zero real patient Protected Health Information (PHI) or Personally Identifiable Information (PII). All names, dates of birth, medical record numbers (MRNs), provider identities, laboratory credentials, and diagnostic measurements in the sample files are simulated values created for development and testing.

The conversion modules, FHIR JSON output structures, and Web UI visualizer do not insert synthetic disclaimers into generated records, ensuring standard formatting when processing clinical laboratory reports.

---

## Architecture and Clinical Scope

Diagnostic laboratory results are frequently delivered to clinical teams as PDF documents. Integrating these records into health information systems requires converting document-level text and tabular findings into discrete, coded resources.

This project provides:
- **Layout and PDF Extraction Module (`src/extractor.py`)**: Extracts text, page geometries, and tabular structures using `pdfplumber` and `pypdf`, normalizing private font encodings and ligatures.
- **Clinical Entity and Biomarker Parser (`src/parser.py`)**: Parses patient demographics, ordering providers, CLIA-certified testing laboratories, specimen chain of custody, quantitative measurements, qualitative variant classifications, and clinical narratives.
- **HL7 FHIR R4 Constructor (`src/fhir_builder.py`)**: Assembles standard FHIR resources and transaction bundles with cross-resource referential integrity (`urn:uuid:` references).
- **Referential and Schema Validator (`src/fhir_validator.py`)**: Verifies resource constraints, required elements, and internal reference targets.
- **Interactive Web UI Visualizer (`src/visualizer.py`)**: Generates a standalone, report-specific HTML dashboard and FHIR JSON inspector (`ui/fhir_viewer.html`).
- **Agent Skill (`SKILL.md` and `skills/lab-report-to-fhir/SKILL.md`)**: Enables conversational AI assistants to parse, validate, convert, and visualize laboratory reports.

```text
+-----------------------+     +--------------------------+     +--------------------------+
|  Laboratory PDF /     | --> |  Extraction & Parsing    | --> |  HL7 FHIR R4 Bundle      |
|  Unstructured Text    |     |  - Key-Value Extraction  |     |  - Patient               |
+-----------------------+     |  - LOINC / SNOMED CT     |     |  - DiagnosticReport      |
                              +--------------------------+     |  - Observations          |
                                           |                   |  - Specimen              |
                                           v                   |  - Practitioner / Org    |
                              +--------------------------+     +--------------------------+
                              |  Web UI Dashboard        |                  |
                              |  - Clinical View & Gauges|                  v
                              +--------------------------+     +--------------------------+
                                                               |  EHR / FHIR Server       |
                                                               |  (Hospital & Cloud APIs) |
                                                               +--------------------------+
```

---

## Project Directory Layout

All file paths in this project are referenced relative to the repository root directory:

```text
.
|-- .gitignore                                   # Git ignore rules
|-- LICENSE                                      # Apache 2.0 license
|-- README.md                                    # Project documentation and user guide
|-- SKILL.md                                     # Root Agent Skill definition
|-- prd.md                                       # Product Requirements Document
|-- requirements.txt                             # Python package dependencies
|-- output/                                      # Generated HL7 FHIR R4 JSON bundles
|   |-- all_sample_bundles.json                  # Aggregate collection of sample FHIR bundles
|   |-- synthetic_cancer_lab_report_fhir.json    # FHIR R4 bundle for MCED positive report
|   |-- synthetic_colorectal_ctdna_fhir.json     # FHIR R4 bundle for Colorectal ctDNA report
|   |-- synthetic_hereditary_ngs_panel_fhir.json # FHIR R4 bundle for Hereditary NGS report
|   |-- synthetic_mced_negative_fhir.json        # FHIR R4 bundle for MCED negative report
|   `-- synthetic_prostate_phi_panel_fhir.json   # FHIR R4 bundle for Prostate phi report
|-- reports/                                     # Synthetic oncology PDF test reports
|   |-- synthetic_cancer_lab_report.pdf          # Multi-Cancer Early Detection (Positive)
|   |-- synthetic_colorectal_ctdna.pdf           # Colorectal ctDNA Liquid Biopsy Panel
|   |-- synthetic_hereditary_ngs_panel.pdf       # 15-Gene Hereditary Oncology NGS Panel
|   |-- synthetic_mced_negative.pdf              # Multi-Cancer Early Detection (Negative)
|   `-- synthetic_prostate_phi_panel.pdf         # Prostate Health Index (phi) Biomarker Panel
|-- scripts/                                     # Command-line execution scripts
|   |-- convert.py                               # PDF to FHIR conversion runner
|   |-- generate_reports.py                      # Synthetic PDF report generator runner
|   |-- validate.py                              # FHIR bundle validation runner
|   `-- visualize.py                             # Web UI dashboard generator runner
|-- skills/
|   `-- lab-report-to-fhir/
|       |-- SKILL.md                             # Packaged Agent Skill instructions
|       |-- references/
|       |   |-- ehr_integration_guide.md         # Clinical system and FHIR store integration guide
|       |   |-- fhir_r4_schemas.md               # HL7 FHIR R4 JSON schema definitions
|       |   `-- loinc_snomed_mapping.md          # LOINC and SNOMED CT ontology reference tables
|       |-- scripts/
|       |   |-- convert.py                       # Skill conversion runner
|       |   `-- visualize.py                     # Skill visualizer runner
|       `-- ui/
|           `-- fhir_viewer.html                 # Packaged standalone Web UI dashboard
|-- src/                                         # Core Python package
|   |-- __init__.py
|   |-- cli.py                                   # Command Line Interface implementation
|   |-- extractor.py                             # PDF layout, table, and text extractor
|   |-- fhir_builder.py                          # HL7 FHIR R4 resource and bundle builder
|   |-- fhir_validator.py                        # Schema and referential integrity validator
|   |-- parser.py                                # Clinical entity and biomarker parser
|   |-- synthetic_generator.py                   # Synthetic laboratory PDF generator
|   `-- visualizer.py                            # Web UI HTML generator
|-- tests/                                       # Automated pytest suite
|   |-- __init__.py
|   |-- test_cli.py                              # End-to-end CLI tests
|   |-- test_extractor.py                        # PDF extraction and cleaning tests
|   |-- test_fhir_builder.py                     # FHIR resource construction tests
|   |-- test_fhir_validator.py                   # Bundle validation tests
|   |-- test_parser.py                           # Clinical entity and table parsing tests
|   `-- test_visualizer.py                       # Web UI HTML generation tests
`-- ui/                                          # Generated standalone HTML dashboards
    |-- fhir_viewer.html                         # Active report Web UI dashboard
    |-- synthetic_cancer_lab_report.html         # Dashboard for MCED positive report
    |-- synthetic_colorectal_ctdna.html          # Dashboard for Colorectal ctDNA report
    |-- synthetic_hereditary_ngs_panel.html      # Dashboard for Hereditary NGS panel
    |-- synthetic_mced_negative.html             # Dashboard for MCED negative report
    `-- synthetic_prostate_phi_panel.html        # Dashboard for Prostate phi panel
```

---

## Non-Technical User Guide: How to Use This Skill

This guide provides instructions for clinical coordinators, medical records specialists, health informatics analysts, and other non-technical staff who use this skill through an AI assistant interface.

### Overview for Non-Technical Users

When outside reference laboratories send test results as PDF attachments or faxes, hospital electronic medical record systems cannot automatically read the individual test numbers or genetic findings locked inside the document. Medical record systems require laboratory data to be formatted in a standardized healthcare data structure called **HL7 FHIR**.

With this skill enabled in an AI assistant, you do not need to write code or manually type lab numbers into a database. You can attach a laboratory report PDF or paste the text from a lab message into the chat window, and the assistant will:
1. Read the document layout, tables, and clinical notes.
2. Identify the patient name, date of birth, medical record number, ordering doctor, specimen details, and test results.
3. Match each laboratory test and specimen type to standard medical codes (LOINC codes for tests and SNOMED CT codes for specimens).
4. Provide a clear summary table, an interactive visual dashboard, and a validated HL7 FHIR JSON file ready for upload into a clinical system.

---

### Real-World Use Case Examples

#### Example 1: Oncology Clinic Coordinator Processing an Outside Screening Report
A patient arrives at an oncology clinic for a consultation and brings a PDF copy of a Multi-Cancer Early Detection blood test performed at an outside reference laboratory (`reports/synthetic_cancer_lab_report.pdf`). Instead of manually typing the predicted cancer signal origins and cell-free DNA concentrations into the clinic's charting system, the coordinator uploads the PDF into the AI chat and asks the assistant to convert it into FHIR and open the visual dashboard. Within seconds, the coordinator can review the highlighted abnormal findings on the screen and export the `synthetic_cancer_lab_report_fhir.json` file for the patient's electronic chart.

#### Example 2: Genetic Counseling Assistant Reviewing a Hereditary Cancer Panel
A genetic counseling office receives a 15-gene hereditary cancer panel PDF (`reports/synthetic_hereditary_ngs_panel.pdf`). The assistant uploads the file and asks for a summary of all tested genes and any pathogenic mutations. The skill extracts the positive `BRCA1` frameshift variant (`c.5266dupC`), separates it from the negative genes (`BRCA2`, `PALB2`, `TP53`, `CHEK2`), lists the recommended breast MRI and family cascade testing steps, and packages the complete genetic report into a standard FHIR bundle.

#### Example 3: Medical Records Specialist Converting Text from a Patient Portal Message
A primary care nurse receives a plain-text message copied from an outside laboratory portal containing a patient's Prostate Health Index (`phi`) and PSA numbers, without a PDF attachment. The specialist pastes the text directly into the chat window. The skill extracts each numeric measurement (`Total PSA: 5.6 ng/mL`, `% Free PSA: 10.4%`, `phi: 47.8`), flags the values outside the normal reference range, and generates the corresponding FHIR observation records.

---

### What Files You Can Upload

- **PDF Laboratory Reports**: Single-page or multi-page PDF documents containing blood work panels, liquid biopsy screenings, pathology summaries, or genetic sequencing results.
- **Plain Text or Copied Portal Results**: Text copied and pasted from laboratory portals, clinical messages, or electronic fax transcripts.

#### Supported Diagnostic Panels Include:
- Multi-Cancer Early Detection (MCED) cell-free DNA methylation reports.
- Circulating Tumor DNA (ctDNA) liquid biopsy panels (e.g. `SEPT9`, `KRAS`, `BRAF`, `TP53`).
- Hereditary oncology gene sequencing panels (e.g. `BRCA1`, `BRCA2`, `PALB2`, `TP53`, `ATM`, `MLH1`).
- Prostate biomarker immunoassay panels (`Total PSA`, `Free PSA`, `% Free PSA`, `[-2]proPSA`, `Prostate Health Index`).
- Standard clinical chemistry and hematology panels.

---

### Sample Files Available for Testing

This repository includes five synthetic laboratory PDF reports in the `reports/` directory for testing:

1. `reports/synthetic_cancer_lab_report.pdf`: Multi-Cancer Early Detection report showing a detected cancer signal with predicted origin in lung (85%) and pancreas (12%).
2. `reports/synthetic_mced_negative.pdf`: Multi-Cancer Early Detection report showing a negative result with no cancer signal detected.
3. `reports/synthetic_colorectal_ctdna.pdf`: Colorectal liquid biopsy report showing positive `SEPT9` methylation and somatic mutations in `KRAS` and `TP53`.
4. `reports/synthetic_hereditary_ngs_panel.pdf`: 15-gene hereditary cancer panel identifying a heterozygous pathogenic `BRCA1` frameshift mutation.
5. `reports/synthetic_prostate_phi_panel.pdf`: Prostate biomarker panel showing elevated Total PSA (`5.6 ng/mL`) and elevated Prostate Health Index (`47.8`).

---

### Step-by-Step Walkthrough in an Agent Chat

1. **Open the Chat Interface**: Open the AI assistant interface where the `lab-report-to-fhir` skill is loaded.
2. **Attach the Lab Report**: Select the file attachment control and upload your laboratory report PDF (for example, `reports/synthetic_cancer_lab_report.pdf`), or paste the report text directly into the message box.
3. **Enter Your Request**: Type a plain-language request describing what you want extracted or converted (see examples below).
4. **Review and Export**: Review the human-readable summary table, open the generated `ui/fhir_viewer.html` visual dashboard if requested, and download or copy the generated FHIR JSON bundle.

---

### Example Prompts to Use

#### Prompt 1: Convert an Uploaded PDF Report to FHIR
> "Please convert the attached lab report PDF ('reports/synthetic_cancer_lab_report.pdf') into a standard HL7 FHIR R4 transaction bundle. Extract patient demographics, ordering provider, specimen information, test observations with LOINC codes, and the clinical interpretation."

#### Prompt 2: Summarize Abnormal Findings for Clinical Review
> "Please analyze the attached lab report ('reports/synthetic_colorectal_ctdna.pdf'). Create a summary table showing every tested biomarker, the patient's result, the normal reference range, and whether the result is normal or abnormal. Also generate the FHIR JSON file."

#### Prompt 3: Batch Convert All Reports in a Folder
> "Please process all laboratory report PDFs in the 'reports/' folder, save the converted FHIR JSON bundles into the 'output/' folder, and provide a summary table showing the patient name, panel type, and validation result for each report."

#### Prompt 4: Convert Copied Plain Text Without a PDF File
> "Convert the following laboratory text into HL7 FHIR R4 Patient, Observation, and DiagnosticReport JSON resources:
>
> Patient: Brenda S. Sample, DOB: 09/30/1985, Female, Patient ID: SYN-MRN-9912048
> Provider: Dr. Ethan Ross, NPI: 9847392015
> Specimen: Whole Blood, ID: SYN-SPEC-NGS-2098, Collected: 2026-07-15
> Test: Hereditary Cancer Risk 15-Gene NGS Panel
> Result: Pathogenic Variant Identified
> - BRCA1 Genetic Analysis: Pathogenic - c.5266dupC (p.Gln1756Profs*74), Heterozygous, Abnormal
> - BRCA2 Genetic Analysis: Negative / No Pathogenic Variant, Normal
> - TP53 Genetic Analysis: Negative / No Pathogenic Variant, Normal
> Conclusion: Heterozygous pathogenic founder mutation in BRCA1 confirming HBOC syndrome."

#### Prompt 5: Generate and Open the Interactive Visual Dashboard
> "Please convert 'reports/synthetic_prostate_phi_panel.pdf' into FHIR and generate the interactive Web UI dashboard so I can view the biomarker range gauges and click on individual observations to inspect their FHIR JSON."

---

### Understanding the Results

When processing completes, you receive:
1. **Structured Clinical Summary**:
   - **Patient and Specimen Details**: Name, Date of Birth, Gender, Medical Record Number, Specimen Type, Collection Date, and Performing Laboratory.
   - **Biomarker Table**: Test names, numeric values, units (`ng/mL`, `%`, `pg/mL`), LOINC codes, reference intervals, and interpretation flags (`Normal`, `High`, `Low`, `Abnormal`, `Pathogenic`).
   - **Clinical Recommendations**: Follow-up diagnostic steps extracted from the report narrative.
2. **HL7 FHIR R4 JSON Bundle**:
   - A validated JSON file containing linked `Patient`, `Practitioner`, `Organization`, `Specimen`, `Observation`, and `DiagnosticReport` resources formatted for clinical database ingestion.

---

## Interactive Web UI Dashboard

When converting a report, the toolkit generates a standalone HTML application (`ui/fhir_viewer.html`) scoped specifically to the processed laboratory report.

```text
+---------------------------------------------------------------------------------------------------------+
| HL7 FHIR Clinical Diagnostic Report  [Patient: Jane Q. Sample | MRN: P-44556677]      [Theme] [Upload] |
+----------------------------------------------------+----------------------------------------------------+
|  CLINICAL DIAGNOSTIC DASHBOARD                     |  INTERACTIVE FHIR RESOURCE INSPECTOR               |
|                                                    |                                                    |
|  +----------------------------------------------+  |  [Bundle (Full)] [Patient] [DiagnosticReport] ...  |
|  | Cancer Signal Detected (Abnormal Finding)    |  |  +----------------------------------------------+  |
|  +----------------------------------------------+  |  | {                                            |  |
|                                                    |  | |   "resourceType": "Observation",           |  |
|  PATIENT: Jane Q. Sample (DOB: 1972-05-12, Female) |  | |   "id": "obs-94076-7",                     |  |
|  SPECIMEN: Blood / Plasma (ID: SYN-992834-X)       |  | |   "code": {                                |  |
|  FACILITY: Clinical Reference Diagnostics Lab      |  | |     "coding": [{                           |  |
|                                                    |  | |       "system": "http://loinc.org",        |  |
|  FILTER: [ Search biomarkers or LOINC codes... ]   |  | |       "code": "94076-7",                   |  |
|                                                    |  | |       "display": "Cancer Signal Status"    |  |
|  OBSERVATIONS & GAUGES:                            |  | |     }]                                     |  |
|  - Cancer Signal Status: Detected [Abnormal]       |  | |   },                                       |  |
|  - Origin 1: Lung (85% prob)                       |  | |   "interpretation": [{ "code": "A" }]     |  |
|  - Total PSA: 5.6 ng/mL [HIGH]                     |  | | }                                            |  |
|    [=== Normal ===|=== High * ===]                 |  |  +----------------------------------------------+  |
|                                                    |  |  [ Copy JSON ] [ Download JSON ]                |  |
|  CLINICAL RECOMMENDATIONS:                         |  |                                                    |
|  - High-resolution imaging: Chest CT and MRI/EUS   |  |                                                    |
+----------------------------------------------------+----------------------------------------------------+
```

### Dashboard Capabilities

1. **Dual-Perspective Layout**:
   - **Clinical Dashboard (Left)**: Displays severity banners, demographic and laboratory governance cards, a 4-stage specimen custody timeline, biomarker findings, quantitative reference range gauges, and clinical recommendations.
   - **FHIR Resource Inspector (Right)**: Displays syntax-highlighted JSON with navigation tabs for `Bundle`, `Patient`, `Practitioner`, `Organization`, `Specimen`, `Observation`, and `DiagnosticReport`.
2. **Synchronized Click-to-Inspect Navigation**:
   - Selecting any demographic card, specimen card, or biomarker row highlights that element and loads its corresponding FHIR resource in the JSON inspector.
3. **Biomarker Search and Category Filtering**:
   - Filter observations by keyword, LOINC code, or category (`All Observations`, `Flagged / Abnormal`, `Quantitative Gauges`, `Genomic Variants`).
4. **Quantitative Range Gauges and Variant Chips**:
   - Displays horizontal meters marking reference intervals (`Low`, `Normal`, `High`) for numeric results and structured chips for genomic variants (HGVS DNA, HGVS protein, VAF, zygosity).
5. **Light / Dark Theme Toggle and File Upload**:
   - Supports switching between Light and Dark themes and drag-and-drop loading of JSON, text, CSV, or PDF files.

### How to Launch and Use the Visualizer

#### Method 1: Generate Dashboard from a PDF or FHIR JSON File
```bash
# Extract data from a PDF report and generate ui/fhir_viewer.html:
python3 scripts/visualize.py reports/synthetic_cancer_lab_report.pdf

# Generate ui/fhir_viewer.html from an existing FHIR JSON bundle:
python3 scripts/visualize.py output/synthetic_colorectal_ctdna_fhir.json
```

#### Method 2: Convert and Launch in One Command
```bash
python3 -m src.cli -i "reports/synthetic_prostate_phi_panel.pdf" -o "output/prostate_fhir.json" --view
```

#### Method 3: Open Standalone HTML File
Open `ui/fhir_viewer.html` in any standard web browser. The file is self-contained and requires no local web server or external network connection.

---

## Developer and Technical Guide

### Installation and Dependencies

Requires Python 3.9 or newer. Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

#### Required Packages:
- `pypdf`: PDF reading and fallback text extraction.
- `pdfplumber`: Layout analysis and table extraction.
- `reportlab`: Programmatic generation of synthetic PDF test reports.
- `pytest`: Automated testing framework.

---

### Command Line Interface (CLI)

Execute single-file or batch directory conversions from the project root directory:

```bash
# Convert a single PDF report:
python3 -m src.cli -i "reports/synthetic_cancer_lab_report.pdf" -o "output/synthetic_cancer_lab_report_fhir.json"

# Batch convert all PDF reports in a directory:
python3 -m src.cli -i "reports/" -o "output/"

# Run via helper script:
python3 scripts/convert.py -i "reports/synthetic_prostate_phi_panel.pdf" -o "output/prostate_fhir.json"

# Output minified single-line JSON:
python3 scripts/convert.py -i "reports/synthetic_mced_negative.pdf" -o "output/mced_neg.json" --compact
```

#### CLI Arguments:
- `-i, --input`: Relative path to an input PDF file or directory.
- `-o, --output`: Relative path to an output JSON file or directory.
- `-t, --type`: FHIR Bundle type (`transaction` [default] or `collection`).
- `--no-validate`: Skip FHIR schema and referential validation.
- `--compact`: Output minified JSON.
- `--view, --ui`: Open the generated HTML dashboard in the system browser.

---

### Python API Usage

Import the conversion and validation functions directly in Python scripts:

```python
import json
from src.parser import parse_lab_report_file
from src.fhir_builder import convert_parsed_data_to_fhir
from src.fhir_validator import validate_fhir_bundle

# 1. Extract and parse entities from a PDF report
parsed_data = parse_lab_report_file("reports/synthetic_colorectal_ctdna.pdf")
print("Patient:", parsed_data["patient"]["name"])
print("Summary Result:", parsed_data["summary_result"]["result_text"])

# 2. Construct an HL7 FHIR R4 Bundle
fhir_bundle = convert_parsed_data_to_fhir(parsed_data, bundle_type="transaction")

# 3. Validate structural and referential integrity
validation = validate_fhir_bundle(fhir_bundle)
print("Is Valid:", validation["is_valid"])
print("Resource Counts:", validation["resource_counts"])

# 4. Write output JSON
with open("output/custom_colorectal_fhir.json", "w", encoding="utf-8") as f:
    json.dump(fhir_bundle, f, indent=2)
```

---

### Generating Synthetic Test Data

Regenerate all five synthetic PDF test reports in `reports/`:

```bash
python3 scripts/generate_reports.py reports
```

---

### Validating FHIR Bundles

Validate all FHIR JSON bundles in `output/` against schema and referential rules:

```bash
python3 scripts/validate.py -i output/
```

Validation checks:
- `Bundle.resourceType` and `Bundle.type` conformance.
- Presence of mandatory fields (`id`, `status`, `code`, `subject`).
- Internal reference resolution (`DiagnosticReport.subject`, `Observation.subject`, `Specimen.subject`, and `DiagnosticReport.result` match resource UUIDs within the bundle).
- LOINC and SNOMED CT coding object structures.

---

### Automated Testing

Run the test suite using `pytest`:

```bash
pytest -v tests/
```

---

## HL7 FHIR R4 Mapping Specification

| Clinical Entity | FHIR Resource | Mapped Attributes |
| :--- | :--- | :--- |
| Patient Demographics | `Patient` | `identifier` (MRN), `name` (family, given), `gender`, `birthDate` |
| Ordering Clinician | `Practitioner` | `identifier` (NPI), `name` |
| Performing Laboratory | `Organization` | `identifier` (CLIA ID, CAP Number), `name`, `address` |
| Biological Specimen | `Specimen` | `identifier`, `type` (SNOMED CT), `collection.collectedDateTime`, `collection.quantity`, `receivedTime`, `container` |
| Discrete Biomarkers | `Observation` | `code` (LOINC), `valueQuantity` / `valueString`, `component`, `referenceRange`, `interpretation`, `specimen` |
| Diagnostic Report | `DiagnosticReport` | `status` (`final`), `code` (LOINC panel), `subject`, `effectiveDateTime`, `issued`, `performer`, `specimen`, `result`, `conclusion` |
| Transaction Package | `Bundle` | `type: "transaction"`, `timestamp`, `entry` list with `POST` request definitions |

---

## Clinical Ontology Standards (LOINC and SNOMED CT)

| Domain | Concept | Coding System | Code |
| :--- | :--- | :--- | :--- |
| Panel | Multi-Cancer Early Detection cfDNA Panel | LOINC | `94076-7` |
| Panel | ctDNA Liquid Biopsy Somatic Panel | LOINC | `94078-3` |
| Panel | Hereditary Cancer NGS Predisposition Panel | LOINC | `79207-7` |
| Panel | Prostate Health Index (phi) Panel | LOINC | `72305-6` |
| Observation | Cancer Signal Methylation Status | LOINC | `94076-7` |
| Observation | Predicted Cancer Signal Origin 1 / 2 | LOINC | `94077-5` |
| Observation | Septin 9 (SEPT9) DNA Methylation | LOINC | `77983-5` |
| Observation | Somatic Gene Mutation (KRAS, TP53, BRAF) | LOINC | `48018-6` |
| Observation | Microsatellite Instability (MSI) | LOINC | `81695-9` |
| Observation | Hereditary Gene NGS Analysis (BRCA1/2, PALB2, TP53) | LOINC | `69548-6` |
| Observation | Total PSA | LOINC | `2857-1` |
| Observation | Free PSA | LOINC | `10886-0` |
| Observation | Percent Free PSA | LOINC | `19195-7` |
| Observation | [-2]proPSA | LOINC | `72304-9` |
| Specimen | Plasma Specimen (cfDNA) | SNOMED CT | `119361006` |
| Specimen | Serum Specimen | SNOMED CT | `119364003` |
| Specimen | Whole Blood Specimen | SNOMED CT | `119297000` |

---

## Synthetic Data and Privacy Compliance Statement

1. **Synthetic Data Only**: All files in `reports/`, unit test fixtures in `tests/`, and sample JSON files in `output/` contain computer-generated clinical data with zero Protected Health Information (PHI).
2. **Fictional Patient and Provider Identities**: All patient names (Jane Q. Sample, Robert T. Sample, Harold K. Sample, Brenda S. Sample, Arthur B. Sample), dates of birth, medical record numbers, clinician names, NPIs, laboratory names, and CLIA/CAP identifiers are fictitious placeholders.
3. **Standard Output Formatting**: Generated FHIR JSON resources and HTML dashboards contain only the clinical fields extracted from the input document.

---

## License

This project is licensed under the **Apache License, Version 2.0**. See the [LICENSE](LICENSE) file in the root directory for full license terms.
