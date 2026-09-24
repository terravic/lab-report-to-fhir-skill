# EHR Integration Guide: Clinical Systems and FHIR Repositories

This guide describes integration patterns for transmitting and storing generated HL7 FHIR R4 bundles in Electronic Health Record (EHR) systems, Laboratory Information Systems (LIS), and clinical data repositories.

---

## 1. EHR Ingestion Workflow

```text
+-----------------------+     +--------------------------+     +--------------------------+
|  Laboratory PDF /     | --> |  Lab Report to FHIR      | --> |  Standard FHIR R4        |
|  Unstructured Report  |     |  Converter               |     |  Transaction Bundle      |
+-----------------------+     +--------------------------+     +--------------------------+
                                                                            |
                                                                            v
                                                               +--------------------------+
                                                               |  EHR / FHIR Server       |
                                                               |  - US Core FHIR Profiles |
                                                               |  - Hospital LIS Tables   |
                                                               |  - Cloud FHIR Store      |
                                                               +--------------------------+
```

---

## 2. Ingestion via FHIR Transaction Endpoint

Generated bundles are packaged with `type: "transaction"` and relative POST requests for each resource entry.

### HTTP Request
```http
POST /fhir/R4 HTTP/1.1
Host: ehr-fhir.hospital-system.org
Authorization: Bearer <OAuth2_Access_Token>
Content-Type: application/fhir+json
Accept: application/fhir+json

{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [ ... ]
}
```

### HL7 US Core Profile Alignment
Clinical systems implementing HL7 US Core validate diagnostic laboratory results against three primary profiles:
- **Patient**: US Core Patient Profile (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient`)
- **DiagnosticReport**: US Core DiagnosticReport Profile for Laboratory Results (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab`)
- **Observation**: US Core Laboratory Result Observation Profile (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab`)

---

## 3. Laboratory Information System (LIS) Integration
- Clinical endpoints accept `DiagnosticReport` and `Observation` resources linked via `subject.reference` (`urn:uuid:` within transaction bundles).
- Observation codes must map to standard LOINC identifiers recognized by the receiving institution's laboratory master compendium.
- Specimen records should include SNOMED CT specimen type codes (`119361006` for Plasma, `119364003` for Serum, `119297000` for Whole Blood) and collection timestamps (`Specimen.collection.collectedDateTime`).

---

## 4. Cloud FHIR Server Ingestion via Command Line
Execute transaction bundle ingestion against an OAuth2-protected FHIR R4 server endpoint using `curl`:

```bash
curl -X POST \
  -H "Authorization: Bearer ${FHIR_ACCESS_TOKEN}" \
  -H "Content-Type: application/fhir+json; charset=utf-8" \
  --data-binary @output/synthetic_colorectal_ctdna_fhir.json \
  "https://fhir.hospital-system.org/r4"
```
