# Clinical Terminology and Ontology Reference: LOINC and SNOMED CT

This reference document defines standard Logical Observation Identifiers Names and Codes (LOINC) and Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT) concepts for laboratory diagnostics and early cancer detection panels.

---

## 1. Laboratory Diagnostic Panels (DiagnosticReport.code)

| Panel / Diagnostic Test | LOINC Code | LOINC Long Name | HL7 FHIR Category |
| :--- | :--- | :--- | :--- |
| Multi-Cancer Early Detection (MCED) | `94076-7` | Cancer signal methylation analysis in cell-free DNA panel | `LAB` / `GE` |
| Circulating Tumor DNA Liquid Biopsy | `94078-3` | Circulating tumor DNA methylation and somatic mutation analysis panel | `LAB` / `GE` |
| Hereditary Cancer Multi-Gene NGS | `79207-7` | Hereditary cancer predisposition panel Next generation sequencing | `GE` |
| Prostate Health Index (phi) Panel | `72305-6` | Prostate Health Index and PSA sub-fractions panel | `LAB` |
| Comprehensive Metabolic Panel (CMP) | `24323-8` | Comprehensive metabolic 2000 panel - Serum or Plasma | `LAB` |
| Complete Blood Count with Diff | `57021-8` | CBC W Auto Differential panel - Blood | `LAB` |
| General Diagnostic Laboratory Report | `11502-2` | Laboratory report | `LAB` |

---

## 2. Quantitative and Qualitative Analytes (Observation.code)

### Multi-Cancer Early Detection & Liquid Biopsy
| Analyte / Finding | LOINC Code | System | Units (UCUM) | Value Type |
| :--- | :--- | :--- | :--- | :--- |
| Cancer Signal Status (Methylation) | `94076-7` | `http://loinc.org` | N/A | `valueString` / `valueCodeableConcept` |
| Predicted Cancer Signal Origin 1 | `94077-5` | `http://loinc.org` | N/A | `valueString` / `component` |
| Predicted Cancer Signal Origin 2 | `94077-5` | `http://loinc.org` | N/A | `valueString` / `component` |
| Septin 9 (SEPT9) DNA Methylation | `77983-5` | `http://loinc.org` | N/A | `valueString` / `valueCodeableConcept` |
| Somatic Variant Analysis (KRAS, TP53, BRAF) | `48018-6` | `http://loinc.org` | N/A | `valueString` |

### Prostate Health & Immunoassays
| Analyte / Finding | LOINC Code | System | Units (UCUM) | Value Type |
| :--- | :--- | :--- | :--- | :--- |
| Total PSA | `2857-1` | `http://loinc.org` | `ng/mL` | `valueQuantity` |
| Free PSA | `10886-0` | `http://loinc.org` | `ng/mL` | `valueQuantity` |
| Percent Free PSA | `19195-7` | `http://loinc.org` | `%` | `valueQuantity` |
| [-2]proPSA | `72304-9` | `http://loinc.org` | `pg/mL` | `valueQuantity` |
| Prostate Health Index (phi) | `72305-6` | `http://loinc.org` | `{score}` | `valueQuantity` |

### Hereditary Oncology NGS
| Gene Tested | LOINC Code | System | Method | Value Type |
| :--- | :--- | :--- | :--- | :--- |
| BRCA1 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |
| BRCA2 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |
| PALB2 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |
| TP53 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |
| CHEK2 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |
| CDH1 Full Sequence & Deletion/Duplication | `69548-6` | `http://loinc.org` | NGS | `valueString` |

---

## 3. Specimen Types (Specimen.type - SNOMED CT)

| Specimen Description | SNOMED CT Code | Display Name |
| :--- | :--- | :--- |
| Plasma Specimen (Cell-Free DNA) | `119361006` | Plasma specimen |
| Serum Specimen | `119364003` | Serum specimen |
| Whole Blood Specimen | `119297000` | Blood specimen |
| Tissue Biopsy Specimen | `119376003` | Tissue specimen |
| Generic Biological Specimen | `123038009` | Specimen |

---

## 4. Observation Interpretations (Observation.interpretation)

| HL7 Interpretation Code | Display | System | Usage Criteria |
| :--- | :--- | :--- | :--- |
| `N` | Normal | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Result falls within reference range |
| `A` | Abnormal | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Qualitative abnormality or pathogenic variant |
| `H` | High | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Quantitative value exceeds upper reference limit |
| `L` | Low | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Quantitative value falls below lower reference limit |
| `POS` | Positive | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Specific presence of target marker or methylation |
| `NEG` | Negative | `http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation` | Absence of target biomarker |
