"""
FHIR Builder Module.
Constructs valid HL7 FHIR R4 JSON resources and Bundles from structured laboratory data.
"""

from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timezone


def generate_uuid() -> str:
    """Generates a UUIDv4 string."""
    return str(uuid.uuid4())


def get_current_iso_timestamp() -> str:
    """Returns current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def map_panel_loinc(report_title: str) -> Dict[str, str]:
    """Maps a report title to standard LOINC coding."""
    title_lower = report_title.lower() if report_title else ""
    
    if any(k in title_lower for k in ["galleri", "cancer signal", "early detection", "mced"]):
        return {
            "code": "94076-7",
            "display": "Cancer signal methylation analysis in cell-free DNA panel",
            "system": "http://loinc.org"
        }
    if any(k in title_lower for k in ["liquid biopsy", "ctdna", "colorectal", "sept9"]):
        return {
            "code": "94078-3",
            "display": "Circulating tumor DNA methylation and somatic mutation analysis panel",
            "system": "http://loinc.org"
        }
    if any(k in title_lower for k in ["hereditary", "brca", "genetic test", "germline", "ngs"]):
        return {
            "code": "79207-7",
            "display": "Hereditary cancer predisposition panel Next generation sequencing",
            "system": "http://loinc.org"
        }
    if any(k in title_lower for k in ["prostate", "phi", "psa"]):
        return {
            "code": "72305-6",
            "display": "Prostate Health Index and PSA sub-fractions panel",
            "system": "http://loinc.org"
        }
        
    return {
        "code": "11502-2",
        "display": "Laboratory report",
        "system": "http://loinc.org"
    }


def map_specimen_snomed(specimen_type: str) -> Dict[str, str]:
    """Maps specimen type text to standard SNOMED CT coding."""
    type_lower = specimen_type.lower() if specimen_type else ""
    if "plasma" in type_lower or "cfdna" in type_lower:
        return {
            "code": "119361006",
            "display": "Plasma specimen",
            "system": "http://snomed.info/sct"
        }
    if "serum" in type_lower:
        return {
            "code": "119364003",
            "display": "Serum specimen",
            "system": "http://snomed.info/sct"
        }
    if "whole blood" in type_lower or "blood" in type_lower:
        return {
            "code": "119297000",
            "display": "Blood specimen",
            "system": "http://snomed.info/sct"
        }
    if "tissue" in type_lower or "biopsy" in type_lower:
        return {
            "code": "119376003",
            "display": "Tissue specimen",
            "system": "http://snomed.info/sct"
        }
    return {
        "code": "123038009",
        "display": "Specimen",
        "system": "http://snomed.info/sct"
    }


class FHIRBundleBuilder:
    """
    Constructs HL7 FHIR R4 Bundle containing Patient, Practitioner, Organization,
    Specimen, Observation(s), and DiagnosticReport resources.
    """

    def __init__(self, parsed_data: Dict[str, Any], bundle_type: str = "transaction"):
        self.data = parsed_data
        self.bundle_type = bundle_type
        
        # Deterministic / Unique IDs for linking resources within the bundle
        self.patient_uuid = generate_uuid()
        self.practitioner_uuid = generate_uuid()
        self.org_uuid = generate_uuid()
        self.specimen_uuid = generate_uuid()
        self.report_uuid = generate_uuid()
        
    def build_patient(self) -> Dict[str, Any]:
        """Builds FHIR R4 Patient resource."""
        patient_info = self.data.get("patient", {})
        name_str = patient_info.get("name") or "Unknown Patient"
        
        # Split name into given and family names
        name_parts = name_str.split()
        if len(name_parts) > 1:
            family_name = name_parts[-1]
            given_names = name_parts[:-1]
        else:
            family_name = name_str
            given_names = []
            
        patient_resource: Dict[str, Any] = {
            "resourceType": "Patient",
            "id": self.patient_uuid,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Patient:</b> {name_str}</p></div>"
            },
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
                    "value": patient_info.get("patient_id") or f"MRN-{self.patient_uuid[:8]}"
                }
            ],
            "active": True,
            "name": [
                {
                    "use": "official",
                    "text": name_str,
                    "family": family_name,
                    "given": given_names
                }
            ],
            "gender": patient_info.get("gender") or "unknown"
        }
        
        if patient_info.get("dob"):
            patient_resource["birthDate"] = patient_info["dob"]
            
        return patient_resource

    def build_practitioner(self) -> Optional[Dict[str, Any]]:
        """Builds FHIR R4 Practitioner resource."""
        provider_info = self.data.get("provider", {})
        provider_name = provider_info.get("name")
        npi = provider_info.get("npi")
        
        if not provider_name and not npi:
            return None
            
        name_str = provider_name or "Ordering Physician"
        practitioner_resource: Dict[str, Any] = {
            "resourceType": "Practitioner",
            "id": self.practitioner_uuid,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Practitioner:</b> {name_str}</p></div>"
            },
            "active": True,
            "name": [
                {
                    "use": "official",
                    "text": name_str
                }
            ]
        }
        
        if npi:
            practitioner_resource["identifier"] = [
                {
                    "system": "http://hl7.org/fhir/sid/us-npi",
                    "value": npi
                }
            ]
            
        return practitioner_resource

    def build_organization(self) -> Dict[str, Any]:
        """Builds FHIR R4 Organization (Performing Laboratory) resource."""
        facility_info = self.data.get("facility", {})
        facility_name = facility_info.get("name") or "Nexus Precision Diagnostics"
        clia_id = facility_info.get("clia_id") or "00D1234567"
        
        org_resource: Dict[str, Any] = {
            "resourceType": "Organization",
            "id": self.org_uuid,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Laboratory:</b> {facility_name}</p></div>"
            },
            "active": True,
            "name": facility_name,
            "identifier": [
                {
                    "system": "urn:oid:2.16.840.1.113883.4.7",
                    "value": clia_id
                }
            ]
        }
        
        if facility_info.get("address"):
            org_resource["address"] = [
                {
                    "use": "work",
                    "text": facility_info["address"]
                }
            ]
            
        return org_resource

    def build_specimen(self) -> Dict[str, Any]:
        """Builds FHIR R4 Specimen resource."""
        spec_info = self.data.get("specimen", {})
        specimen_id = spec_info.get("specimen_id") or f"SPEC-{self.specimen_uuid[:8]}"
        spec_type = spec_info.get("specimen_type") or "Blood / Plasma"
        snomed_coding = map_specimen_snomed(spec_type)
        
        specimen_resource: Dict[str, Any] = {
            "resourceType": "Specimen",
            "id": self.specimen_uuid,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>Specimen ID:</b> {specimen_id} ({spec_type})</p></div>"
            },
            "identifier": [
                {
                    "system": "urn:ietf:rfc:3986",
                    "value": specimen_id
                }
            ],
            "status": "available",
            "type": {
                "coding": [snomed_coding],
                "text": spec_type
            },
            "subject": {
                "reference": f"urn:uuid:{self.patient_uuid}"
            }
        }
        
        collection_date = spec_info.get("collection_date")
        if collection_date:
            specimen_resource["collection"] = {
                "collectedDateTime": collection_date
            }
            
        received_date = spec_info.get("received_date")
        if received_date:
            specimen_resource["receivedTime"] = received_date
            
        return specimen_resource

    def build_observations(self) -> List[Dict[str, Any]]:
        """Builds a list of FHIR R4 Observation resources."""
        parsed_obs = self.data.get("observations", [])
        obs_resources: List[Dict[str, Any]] = []
        
        spec_info = self.data.get("specimen", {})
        effective_date = spec_info.get("collection_date") or spec_info.get("report_date") or get_current_iso_timestamp()
        
        for item in parsed_obs:
            obs_uuid = generate_uuid()
            code = item.get("code") or "11502-2"
            display = item.get("display") or item.get("test_name") or "Laboratory Observation"
            test_name = item.get("test_name") or display
            val = item.get("value")
            val_type = item.get("value_type", "string")
            
            obs_resource: Dict[str, Any] = {
                "resourceType": "Observation",
                "id": obs_uuid,
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><p><b>{test_name}:</b> {val}</p></div>"
                },
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
                            "code": code,
                            "display": display
                        }
                    ],
                    "text": test_name
                },
                "subject": {
                    "reference": f"urn:uuid:{self.patient_uuid}"
                },
                "effectiveDateTime": effective_date,
                "performer": [
                    {
                        "reference": f"urn:uuid:{self.org_uuid}"
                    }
                ],
                "specimen": {
                    "reference": f"urn:uuid:{self.specimen_uuid}"
                }
            }
            
            # Add Value (Quantity, String, or Component)
            if val_type == "quantity" and isinstance(val, (int, float)):
                unit = item.get("unit") or ""
                obs_resource["valueQuantity"] = {
                    "value": float(val),
                    "unit": unit,
                    "system": "http://unitsofmeasure.org" if unit != "{score}" else "http://unitsofmeasure.org",
                    "code": unit
                }
            else:
                obs_resource["valueString"] = str(val)
                
            # Add Component if available (e.g. CSO accuracy frequency)
            if item.get("component"):
                components = []
                comp_data = item["component"]
                for comp_k, comp_v in comp_data.items():
                    components.append({
                        "code": {
                            "text": comp_k.replace('_', ' ').title()
                        },
                        "valueString": str(comp_v)
                    })
                obs_resource["component"] = components

            # Add Reference Range
            if item.get("reference_range"):
                obs_resource["referenceRange"] = [
                    {
                        "text": item["reference_range"]
                    }
                ]
                
            # Add Interpretation Flag
            interp_code = item.get("interpretation")
            if interp_code:
                interp_display = item.get("interpretation_display") or ("Abnormal" if interp_code == "A" else "Normal")
                obs_resource["interpretation"] = [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                                "code": interp_code,
                                "display": interp_display
                            }
                        ]
                    }
                ]
                
            obs_resources.append(obs_resource)
            
        return obs_resources

    def build_diagnostic_report(self, observation_resources: List[Dict[str, Any]], practitioner_resource: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Builds FHIR R4 DiagnosticReport resource linking all observations and metadata."""
        report_title = self.data.get("report_title") or "Laboratory Diagnostic Report"
        panel_coding = map_panel_loinc(report_title)
        
        spec_info = self.data.get("specimen", {})
        effective_date = spec_info.get("collection_date") or spec_info.get("report_date") or get_current_iso_timestamp()
        issued_date = spec_info.get("report_date") or get_current_iso_timestamp()
        
        summary_result = self.data.get("summary_result", {})
        conclusion_text = summary_result.get("conclusion") or summary_result.get("result_text") or "Diagnostic report complete."
        
        # Clinical interpretation notes
        narrative_notes = []
        if self.data.get("clinical_interpretation"):
            narrative_notes.append(f"Clinical Interpretation: {self.data['clinical_interpretation']}")
        if self.data.get("methodology"):
            narrative_notes.append(f"Methodology: {self.data['methodology']}")
        if self.data.get("limitations"):
            narrative_notes.append(f"Limitations: {self.data['limitations']}")
            
        full_conclusion = conclusion_text
        if narrative_notes:
            full_conclusion += "\n\n" + "\n\n".join(narrative_notes)

        performers = [
            {
                "reference": f"urn:uuid:{self.org_uuid}"
            }
        ]
        if practitioner_resource:
            performers.insert(0, {
                "reference": f"urn:uuid:{practitioner_resource['id']}"
            })

        diag_report: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": self.report_uuid,
            "text": {
                "status": "generated",
                "div": f"<div xmlns=\"http://www.w3.org/1999/xhtml\"><h2>{report_title}</h2><p><b>Conclusion:</b> {conclusion_text}</p></div>"
            },
            "identifier": [
                {
                    "system": "urn:ietf:rfc:3986",
                    "value": spec_info.get("specimen_id") or f"REP-{self.report_uuid[:8]}"
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
                "coding": [panel_coding],
                "text": report_title
            },
            "subject": {
                "reference": f"urn:uuid:{self.patient_uuid}"
            },
            "effectiveDateTime": effective_date,
            "issued": issued_date,
            "performer": performers,
            "specimen": [
                {
                    "reference": f"urn:uuid:{self.specimen_uuid}"
                }
            ],
            "result": [
                {
                    "reference": f"urn:uuid:{obs['id']}"
                }
                for obs in observation_resources
            ],
            "conclusion": full_conclusion
        }
        
        return diag_report

    def build_bundle(self) -> Dict[str, Any]:
        """
        Builds and returns the complete HL7 FHIR R4 Bundle containing all linked resources.
        """
        patient = self.build_patient()
        practitioner = self.build_practitioner()
        org = self.build_organization()
        specimen = self.build_specimen()
        observations = self.build_observations()
        diag_report = self.build_diagnostic_report(observations, practitioner)
        
        all_resources = [patient]
        if practitioner:
            all_resources.append(practitioner)
        all_resources.extend([org, specimen] + observations + [diag_report])
        
        entries = []
        for res in all_resources:
            entry_obj: Dict[str, Any] = {
                "fullUrl": f"urn:uuid:{res['id']}",
                "resource": res
            }
            if self.bundle_type == "transaction":
                entry_obj["request"] = {
                    "method": "POST",
                    "url": res["resourceType"]
                }
            entries.append(entry_obj)
            
        bundle_id = generate_uuid()
        bundle: Dict[str, Any] = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": self.bundle_type,
            "timestamp": get_current_iso_timestamp(),
            "entry": entries
        }
        
        return bundle


def convert_parsed_data_to_fhir(parsed_data: Dict[str, Any], bundle_type: str = "transaction") -> Dict[str, Any]:
    """
    Converts parsed lab data dictionary into an HL7 FHIR R4 Bundle.
    """
    builder = FHIRBundleBuilder(parsed_data, bundle_type=bundle_type)
    return builder.build_bundle()
