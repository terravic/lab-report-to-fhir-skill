# EHR Integration Guide: Epic, Cerner, and Cloud FHIR Repositories

This guide describes integration patterns for transmitting and storing generated HL7 FHIR R4 bundles in enterprise Electronic Health Record (EHR) systems and healthcare data lakes.

---

## 1. EHR Ingestion Workflow

```text
+-----------------------+     +--------------------------+     +--------------------------+
|  Laboratory PDF /     | --> |  Lab Report to FHIR      | --> |  Standard FHIR R4        |
|  Unstructured Report  |     |  Converter (Skill Engine)|     |  Transaction Bundle      |
+-----------------------+     +--------------------------+     +--------------------------+
                                                                            |
                                                                            v
                                                               +--------------------------+
                                                               |  EHR / FHIR Server       |
                                                               |  - Epic FHIR / Interconnect
                                                               |  - Oracle Cerner Ignite  |
                                                               |  - Google Cloud Health   |
                                                               +--------------------------+
```

---

## 2. Ingestion via FHIR Transaction Endpoint

Generated bundles are packaged with `type: "transaction"` and relative POST requests for each entry.

### HTTP Request
```http
POST /fhir/R4 HTTP/1.1
Host: ehr-fhir.hospital-system.org
Authorization: Bearer <OAuth2_Token>
Content-Type: application/fhir+json
Accept: application/fhir+json

{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [ ... ]
}
```

### Epic US Core Alignment
Epic requires specific profiles for diagnostic lab results:
- **Patient**: US Core Patient Profile (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient`)
- **DiagnosticReport**: US Core DiagnosticReport Profile for Laboratory Results (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-diagnosticreport-lab`)
- **Observation**: US Core Laboratory Result Observation Profile (`http://hl7.org/fhir/us/core/StructureDefinition/us-core-observation-lab`)

---

## 3. Cerner Millennium Ignite Integration
- Cerner endpoints accept `DiagnosticReport` and `Observation` resources linked via `subject.reference`.
- Codes must map to valid LOINC terms recognized by the hospital's Millennium Charge Services and PathNet lab master tables.

---

## 4. Google Cloud Healthcare API (FHIR Store)
Execute bundle ingestion using `curl` or Google Cloud SDK:

```bash
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth application-default print-access-token)" \
  -H "Content-Type: application/fhir+json; charset=utf-8" \
  --data-binary @output/synthetic_colorectal_ctdna_fhir.json \
  "https://healthcare.googleapis.com/v1/projects/MY_PROJECT/locations/MY_LOCATION/datasets/MY_DATASET/fhirStores/MY_FHIR_STORE/fhir"
```
