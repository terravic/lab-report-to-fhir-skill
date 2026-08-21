# HL7 FHIR Release 4 Resource Models for Laboratory Diagnostics

This document details the exact JSON structure for standard HL7 FHIR R4 resources constructed during lab report conversion.

---

## 1. Bundle (Transaction / Collection)

```json
{
  "resourceType": "Bundle",
  "id": "bundle-uuid-example",
  "type": "transaction",
  "timestamp": "2026-08-21T12:00:00Z",
  "entry": [
    {
      "fullUrl": "urn:uuid:patient-uuid",
      "resource": { /* Patient Resource */ },
      "request": {
        "method": "POST",
        "url": "Patient"
      }
    },
    {
      "fullUrl": "urn:uuid:report-uuid",
      "resource": { /* DiagnosticReport Resource */ },
      "request": {
        "method": "POST",
        "url": "DiagnosticReport"
      }
    }
  ]
}
```

---

## 2. Patient Resource

```json
{
  "resourceType": "Patient",
  "id": "c1f7a0b3-1234-4567-89ab-cdef01234567",
  "identifier": [
    {
      "use": "usual",
      "type": {
        "coding": [
          {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
            "code": "MR",
            "display": "Medical Record Number"
          }
        ]
      },
      "system": "urn:ietf:rfc:3986",
      "value": "MRN-8849102"
    }
  ],
  "active": true,
  "name": [
    {
      "use": "official",
      "text": "Robert T. Miller",
      "family": "Miller",
      "given": ["Robert", "T."]
    }
  ],
  "gender": "male",
  "birthDate": "1968-11-23"
}
```

---

## 3. Observation Resource (Quantitative Example)

```json
{
  "resourceType": "Observation",
  "id": "obs-psa-uuid",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "2857-1",
        "display": "Prostate specific Ag [Mass/volume] in Serum or Plasma"
      }
    ],
    "text": "Total PSA"
  },
  "subject": {
    "reference": "urn:uuid:patient-uuid"
  },
  "effectiveDateTime": "2026-08-10",
  "valueQuantity": {
    "value": 5.6,
    "unit": "ng/mL",
    "system": "http://unitsofmeasure.org",
    "code": "ng/mL"
  },
  "referenceRange": [
    {
      "text": "0.0 - 4.0 ng/mL"
    }
  ],
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "H",
          "display": "High"
        }
      ]
    }
  ]
}
```

---

## 4. Observation Resource (Genomic / Qualitative Example)

```json
{
  "resourceType": "Observation",
  "id": "obs-brca-uuid",
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/observation-category",
          "code": "laboratory",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "69548-6",
        "display": "BRCA1 full gene sequence and deletion/duplication analysis"
      }
    ],
    "text": "BRCA1 Genetic Analysis"
  },
  "subject": {
    "reference": "urn:uuid:patient-uuid"
  },
  "effectiveDateTime": "2026-07-15",
  "valueString": "Pathogenic - c.5266dupC (p.Gln1756Profs*74)",
  "referenceRange": [
    {
      "text": "Negative / No Pathogenic Variant"
    }
  ],
  "interpretation": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
          "code": "A",
          "display": "Abnormal"
        }
      ]
    }
  ]
}
```

---

## 5. DiagnosticReport Resource

```json
{
  "resourceType": "DiagnosticReport",
  "id": "report-uuid",
  "identifier": [
    {
      "system": "urn:ietf:rfc:3986",
      "value": "SPEC-CRC-7731"
    }
  ],
  "status": "final",
  "category": [
    {
      "coding": [
        {
          "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
          "code": "LAB",
          "display": "Laboratory"
        }
      ]
    }
  ],
  "code": {
    "coding": [
      {
        "system": "http://loinc.org",
        "code": "94078-3",
        "display": "Circulating tumor DNA methylation and somatic mutation analysis panel"
      }
    ],
    "text": "Liquid Biopsy Colorectal ctDNA Early Screening Report"
  },
  "subject": {
    "reference": "urn:uuid:patient-uuid"
  },
  "effectiveDateTime": "2026-07-28",
  "issued": "2026-08-04",
  "performer": [
    {
      "reference": "urn:uuid:practitioner-uuid"
    },
    {
      "reference": "urn:uuid:org-uuid"
    }
  ],
  "specimen": [
    {
      "reference": "urn:uuid:specimen-uuid"
    }
  ],
  "result": [
    {
      "reference": "urn:uuid:obs-1-uuid"
    },
    {
      "reference": "urn:uuid:obs-2-uuid"
    }
  ],
  "conclusion": "Elevated circulating tumor DNA (ctDNA) markers detected."
}
```
