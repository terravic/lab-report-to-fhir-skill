# Product Requirements Document (PRD): Laboratory Report to HL7 FHIR R4 Conversion Toolkit and Agent Skill

## 1. Overview and Purpose

This document defines the product requirements, system architecture, data models, and verification specifications for the Laboratory Report to HL7 FHIR R4 Conversion Toolkit and Agent Skill. The system extracts clinical entities, quantitative biomarkers, genomic variants, specimen custody metadata, and diagnostic interpretations from unstructured or semi-structured laboratory report PDFs and plain text, converting them into validated HL7 FHIR Release 4 (R4) JSON resources and generating a report-specific interactive Web UI dashboard.

---

## 2. Problem Statement

Clinical diagnostic laboratories frequently transmit specialized test results--such as Multi-Cancer Early Detection (MCED) cell-free DNA methylation profiles, liquid biopsy circulating tumor DNA (ctDNA) somatic panels, hereditary oncology Next-Generation Sequencing (NGS) panels, and immunoassay biomarker panels--as formatted PDF documents rather than discrete electronic messages.

Manual transcription of PDF findings into Electronic Health Record (EHR) systems and clinical data repositories introduces transcription delays and prevents automated clinical decision support. Converting these documents into structured HL7 FHIR R4 resources with standardized LOINC and SNOMED CT terminology enables direct ingestion into clinical systems and structured visual review.

---

## 3. Target Users

1. **Clinical Coordinators and Medical Records Staff**: Non-technical healthcare personnel who upload laboratory report PDFs or paste portal text into an AI agent chat interface to obtain structured summaries and downloadable FHIR JSON files.
2. **Health Informatics Analysts**: Technical staff who inspect LOINC/SNOMED CT terminology mappings, verify US Core profile alignment, and review biomarker reference intervals using the interactive Web UI dashboard.
3. **Healthcare Software Engineers**: Developers integrating the Python library (`src/`) or Command Line Interface (`src/cli.py`, `scripts/`) into automated document ingestion pipelines.

---

## 4. System Architecture

```text
+-----------------------+     +--------------------------+     +--------------------------+
|  Input Sources        | --> |  Extraction & Parsing    | --> |  HL7 FHIR R4 Builder     |
|  - PDF Lab Reports    |     |  - Layout & Table Parser |     |  - Patient / Practitioner|
|  - Plain Text / CSV   |     |  - Entity Normalization  |     |  - Organization / Spec.  |
+-----------------------+     +--------------------------+     |  - Observation / Report  |
                                           |                   +--------------------------+
                                           v                                |
                              +--------------------------+                  v
                              |  Schema & Reference      |     +--------------------------+
                              |  Validator               | --> |  Outputs                 |
                              |  - Required FHIR Elements|     |  - FHIR R4 JSON Bundles  |
                              |  - UUID Integrity Check  |     |  - Report Web UI HTML    |
                              +--------------------------+     +--------------------------+
```

### Core Modules
- `src/extractor.py`: Extracts text and tabular structures from PDF files using `pdfplumber` with fallback to `pypdf`, normalizing private-use font glyphs, ligatures, and whitespace.
- `src/parser.py`: Parses patient demographics, ordering clinician identifiers, performing laboratory credentials (CLIA ID, CAP number, medical director), specimen chain-of-custody timestamps, quantitative/qualitative observations, variant components, and clinical recommendations.
- `src/fhir_builder.py`: Maps extracted entities to LOINC and SNOMED CT codes and constructs interconnected HL7 FHIR R4 resources packaged in a `transaction` or `collection` `Bundle`.
- `src/fhir_validator.py`: Validates resource schemas, required attributes, value sets, and internal `urn:uuid:` cross-resource references.
- `src/visualizer.py`: Generates a standalone, report-specific HTML dashboard (`ui/fhir_viewer.html`) pairing a clinical diagnostic view with a synchronized FHIR JSON inspector.
- `src/synthetic_generator.py`: Programmatically generates five synthetic oncology PDF reports in `reports/` containing zero Protected Health Information (PHI).
- `src/cli.py`: Provides single-file and batch directory processing with optional validation and browser launch.

---

## 5. Functional Requirements

### FR-1: PDF and Text Extraction (`src/extractor.py`)
- Extract multi-column layouts and structured tables from PDF documents.
- Decode Private Use Area (PUA) Unicode characters (`\ue000` to `\uf8ff`) and CID font artifacts into standard ASCII punctuation.
- Normalize line breaks and intra-line whitespace while preserving section headers and table boundaries.

### FR-2: Clinical Entity and Biomarker Parsing (`src/parser.py`)
- **Patient Demographics**: Parse full name, date of birth (normalized to ISO-8601 `YYYY-MM-DD`), calculated age, administrative gender (`male`, `female`, `other`, `unknown`), and medical record number (MRN).
- **Ordering Provider**: Parse clinician name, 10-digit National Provider Identifier (NPI), ordering facility, and location.
- **Performing Laboratory**: Parse laboratory name, CLIA identifier, CAP accreditation number, street address, and authorizing laboratory director.
- **Specimen Chain of Custody**: Parse specimen accession ID, specimen type, collection tube specification, specimen volume (`mL`), collection date, received date, and report issue date.
- **Observations and Variants**: Extract analyte name, LOINC code, numeric value, UCUM unit, reference range bounds (`low`, `high`), interpretation flag (`N`, `A`, `H`, `L`, `POS`, `NEG`), and structured genomic sub-components (HGVS cDNA, HGVS protein change, Variant Allele Frequency, zygosity, and predicted cancer signal origin probabilities).
- **Narrative Sections**: Extract summary result, clinical interpretation, bulleted clinical recommendations, assay methodology, and test limitations.

### FR-3: Clinical Terminology Mapping (`src/fhir_builder.py`)
- Assign LOINC panel codes to `DiagnosticReport.code`:
  - `94076-7`: Multi-Cancer Early Detection cell-free DNA methylation panel
  - `94078-3`: Circulating tumor DNA methylation and somatic mutation panel
  - `79207-7`: Hereditary cancer predisposition panel by Next-Generation Sequencing
  - `72305-6`: Prostate Health Index (phi) and PSA sub-fractions panel
  - `11502-2`: General laboratory report fallback
- Assign LOINC observation codes to discrete analytes (`94076-7`, `94077-5`, `77983-5`, `48018-6`, `81695-9`, `69548-6`, `2857-1`, `10886-0`, `19195-7`, `72304-9`, `72305-6`).
- Assign SNOMED CT specimen codes to `Specimen.type`:
  - `119361006`: Plasma specimen
  - `119364003`: Serum specimen
  - `119297000`: Blood specimen
  - `119376003`: Tissue specimen
  - `123038009`: Generic biological specimen

### FR-4: HL7 FHIR R4 Bundle Construction (`src/fhir_builder.py`)
- Generate `Patient`, `Practitioner`, `Organization`, `Specimen`, `Observation`, and `DiagnosticReport` resources with UUIDv4 identifiers.
- Link `Observation.subject`, `Specimen.subject`, and `DiagnosticReport.subject` to the `Patient` UUID (`urn:uuid:<id>`).
- Link `DiagnosticReport.result` to every generated `Observation` UUID.
- Link `DiagnosticReport.performer` to the `Practitioner` and `Organization` UUIDs, and `DiagnosticReport.specimen` to the `Specimen` UUID.
- Support `transaction` (with `POST` request blocks per entry) and `collection` bundle types.

### FR-5: Schema and Referential Validation (`src/fhir_validator.py`)
- Verify top-level `Bundle` structure, allowed `Bundle.type`, and non-empty `entry` array.
- Verify presence of required `Patient` and `DiagnosticReport` resources.
- Validate administrative gender codes, `Observation.status`, and `DiagnosticReport.status` against HL7 FHIR R4 value sets.
- Verify that all internal references (`subject`, `result`, `specimen`, `performer`) resolve to resources present within the bundle.

### FR-6: Report-Specific Interactive Web UI Dashboard (`src/visualizer.py`)
- Generate a self-contained HTML application (`ui/fhir_viewer.html`) scoped to the active laboratory report without cross-report data mixing or sample preset dropdowns.
- Provide a dual-perspective interface:
  - **Clinical Diagnostic View (Left)**: Severity-coded result banner, 4-card demographic and governance grid, 4-step specimen chain-of-custody timeline, biomarker search and category filter pills (`All Observations`, `Flagged / Abnormal`, `Quantitative Gauges`, `Genomic Variants`), horizontal quantitative reference range gauges, genomic variant chips, cancer signal origin probability bars, clinical recommendations list, and methodology/limitations cards.
  - **FHIR Resource Inspector (Right)**: Syntax-highlighted JSON viewer with resource navigation tabs (`Bundle (Full)`, `Patient`, `Practitioner`, `Organization`, `Specimen`, individual `Observation` tabs, `DiagnosticReport`), one-click JSON clipboard copy, and bundle JSON file download.
- Support bidirectional click-to-inspect synchronization between clinical cards/rows and the FHIR JSON inspector.
- Support Light and Dark mode themes and client-side drag-and-drop upload for JSON, text, CSV, and PDF files.

### FR-7: Synthetic Test Data Suite (`src/synthetic_generator.py`)
- Maintain five synthetic oncology PDF reports in `reports/` with corresponding FHIR R4 JSON bundles in `output/` and standalone HTML dashboards in `ui/`:
  1. `reports/synthetic_cancer_lab_report.pdf`: Multi-Cancer Early Detection positive screening report (Lung 85%, Pancreas 12%).
  2. `reports/synthetic_mced_negative.pdf`: Multi-Cancer Early Detection negative baseline report.
  3. `reports/synthetic_colorectal_ctdna.pdf`: Colorectal ctDNA liquid biopsy report (SEPT9 positive, KRAS p.G12D, TP53 p.R273H).
  4. `reports/synthetic_hereditary_ngs_panel.pdf`: 15-gene hereditary cancer NGS panel (BRCA1 c.5266dupC pathogenic frameshift variant).
  5. `reports/synthetic_prostate_phi_panel.pdf`: Prostate Health Index immunoassay panel (Total PSA 5.6 ng/mL, phi 47.8).

---

## 6. Non-Functional Requirements

1. **Zero-PHI Synthetic Fixtures**: All sample PDF reports, JSON outputs, and test fixtures must contain exclusively computer-generated, fictional data with zero real patient Protected Health Information (PHI) or Personally Identifiable Information (PII).
2. **Relative Path Standardization**: All scripts, configuration files, and module functions must operate using relative paths originating from the project root directory without hardcoded local machine paths.
3. **Offline Self-Contained Execution**: Both the Python conversion pipeline and the generated HTML dashboard must execute offline without external network requests or third-party scripts.
4. **Automated Test Verification**: All extraction, parsing, FHIR resource building, validation, CLI execution, and UI generation workflows must be verified by automated `pytest` tests in `tests/`.
