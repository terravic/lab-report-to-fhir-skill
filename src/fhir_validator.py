"""
FHIR R4 Validator Module.
Validates structural integrity, required fields, coding systems, and referential integrity of FHIR R4 Bundles.
"""

from typing import Dict, Any, List, Set, Tuple, Optional


class FHIRValidator:
    """
    Validates HL7 FHIR R4 Bundles and clinical diagnostic resources.
    """

    ALLOWED_GENDERS = {"male", "female", "other", "unknown"}
    ALLOWED_DIAG_STATUS = {"registered", "partial", "preliminary", "final", "amended", "corrected", "appended", "cancelled", "entered-in-error", "unknown"}
    ALLOWED_OBS_STATUS = {"registered", "preliminary", "final", "amended", "corrected", "cancelled", "entered-in-error", "unknown"}
    ALLOWED_BUNDLE_TYPES = {"document", "message", "transaction", "transaction-response", "batch", "batch-response", "history", "searchset", "collection"}

    def __init__(self, bundle: Dict[str, Any]):
        self.bundle = bundle
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.resource_counts: Dict[str, int] = {}
        self.resource_ids: Set[str] = set()
        self.full_urls: Set[str] = set()

    def validate(self) -> Dict[str, Any]:
        """
        Executes all validation checks on the bundle.
        
        Returns:
            Dict containing is_valid, errors, warnings, and resource_counts.
        """
        self.errors.clear()
        self.warnings.clear()
        self.resource_counts.clear()
        self.resource_ids.clear()
        self.full_urls.clear()

        # 1. Top level bundle validation
        if not isinstance(self.bundle, dict):
            self.errors.append("Bundle root must be a JSON object.")
            return self._build_result()

        if self.bundle.get("resourceType") != "Bundle":
            self.errors.append(f"Expected resourceType 'Bundle', got '{self.bundle.get('resourceType')}'.")

        b_type = self.bundle.get("type")
        if not b_type or b_type not in self.ALLOWED_BUNDLE_TYPES:
            self.errors.append(f"Invalid or missing Bundle type: '{b_type}'. Allowed types: {sorted(self.ALLOWED_BUNDLE_TYPES)}.")

        entries = self.bundle.get("entry")
        if not isinstance(entries, list) or len(entries) == 0:
            self.errors.append("Bundle must contain a non-empty 'entry' list.")
            return self._build_result()

        # 2. Collect resources and check entries
        resources: List[Dict[str, Any]] = []
        for idx, entry in enumerate(entries):
            if not isinstance(entry, dict):
                self.errors.append(f"Entry [{idx}] is not a valid JSON object.")
                continue

            full_url = entry.get("fullUrl")
            if full_url:
                self.full_urls.add(full_url)

            res = entry.get("resource")
            if not isinstance(res, dict):
                self.errors.append(f"Entry [{idx}] is missing a valid 'resource' object.")
                continue

            r_type = res.get("resourceType")
            r_id = res.get("id")

            if not r_type:
                self.errors.append(f"Entry [{idx}] resource is missing 'resourceType'.")
                continue

            if not r_id:
                self.errors.append(f"Entry [{idx}] ({r_type}) resource is missing 'id'.")
            else:
                self.resource_ids.add(r_id)
                self.resource_ids.add(f"{r_type}/{r_id}")
                if full_url:
                    self.resource_ids.add(full_url)

            self.resource_counts[r_type] = self.resource_counts.get(r_type, 0) + 1
            resources.append(res)

        # 3. Validate specific resources
        has_patient = False
        has_diagnostic_report = False

        for res in resources:
            r_type = res.get("resourceType")
            if r_type == "Patient":
                has_patient = True
                self._validate_patient(res)
            elif r_type == "DiagnosticReport":
                has_diagnostic_report = True
                self._validate_diagnostic_report(res)
            elif r_type == "Observation":
                self._validate_observation(res)
            elif r_type == "Specimen":
                self._validate_specimen(res)
            elif r_type == "Organization":
                self._validate_organization(res)
            elif r_type == "Practitioner":
                self._validate_practitioner(res)

        if not has_patient:
            self.errors.append("Bundle is missing required 'Patient' resource.")
        if not has_diagnostic_report:
            self.errors.append("Bundle is missing required 'DiagnosticReport' resource.")

        return self._build_result()

    def _resolve_reference(self, ref_str: Optional[str]) -> bool:
        """Checks if a reference string resolves to an existing resource in the bundle."""
        if not ref_str:
            return False
        if ref_str in self.resource_ids or ref_str in self.full_urls:
            return True
        # Strip urn:uuid: prefix
        if ref_str.startswith("urn:uuid:") and ref_str[9:] in self.resource_ids:
            return True
        # Strip resourceType/ prefix
        if "/" in ref_str:
            parts = ref_str.split("/", 1)
            if parts[1] in self.resource_ids:
                return True
        return False

    def _validate_patient(self, res: Dict[str, Any]):
        p_id = res.get("id", "unknown")
        gender = res.get("gender")
        if gender and gender not in self.ALLOWED_GENDERS:
            self.errors.append(f"Patient ({p_id}) has invalid gender '{gender}'.")
        
        name = res.get("name")
        if not name or not isinstance(name, list) or len(name) == 0:
            self.warnings.append(f"Patient ({p_id}) is missing 'name' element.")

    def _validate_diagnostic_report(self, res: Dict[str, Any]):
        r_id = res.get("id", "unknown")
        status = res.get("status")
        if not status or status not in self.ALLOWED_DIAG_STATUS:
            self.errors.append(f"DiagnosticReport ({r_id}) has invalid status '{status}'.")

        code = res.get("code")
        if not code or not isinstance(code, dict) or not code.get("coding"):
            self.errors.append(f"DiagnosticReport ({r_id}) is missing required 'code.coding'.")

        subject = res.get("subject", {})
        sub_ref = subject.get("reference")
        if not sub_ref:
            self.errors.append(f"DiagnosticReport ({r_id}) is missing required 'subject.reference'.")
        elif not self._resolve_reference(sub_ref):
            self.errors.append(f"DiagnosticReport ({r_id}) subject reference '{sub_ref}' could not be resolved.")

        results = res.get("result", [])
        if not results or len(results) == 0:
            self.warnings.append(f"DiagnosticReport ({r_id}) contains no 'result' observation references.")
        for idx, res_ref_obj in enumerate(results):
            res_ref = res_ref_obj.get("reference")
            if not res_ref:
                self.errors.append(f"DiagnosticReport ({r_id}) result [{idx}] is missing 'reference'.")
            elif not self._resolve_reference(res_ref):
                self.errors.append(f"DiagnosticReport ({r_id}) result reference '{res_ref}' could not be resolved.")

    def _validate_observation(self, res: Dict[str, Any]):
        o_id = res.get("id", "unknown")
        status = res.get("status")
        if not status or status not in self.ALLOWED_OBS_STATUS:
            self.errors.append(f"Observation ({o_id}) has invalid status '{status}'.")

        code = res.get("code")
        if not code or not isinstance(code, dict) or not code.get("coding"):
            self.errors.append(f"Observation ({o_id}) is missing required 'code.coding'.")

        subject = res.get("subject", {})
        sub_ref = subject.get("reference")
        if not sub_ref:
            self.errors.append(f"Observation ({o_id}) is missing required 'subject.reference'.")
        elif not self._resolve_reference(sub_ref):
            self.errors.append(f"Observation ({o_id}) subject reference '{sub_ref}' could not be resolved.")

        has_val = any([
            "valueQuantity" in res,
            "valueString" in res,
            "valueCodeableConcept" in res,
            "valueBoolean" in res,
            "valueInteger" in res,
            "component" in res,
            "dataAbsentReason" in res
        ])
        if not has_val:
            self.warnings.append(f"Observation ({o_id}) has no value[x] or component defined.")

    def _validate_specimen(self, res: Dict[str, Any]):
        s_id = res.get("id", "unknown")
        subject = res.get("subject", {})
        sub_ref = subject.get("reference")
        if sub_ref and not self._resolve_reference(sub_ref):
            self.errors.append(f"Specimen ({s_id}) subject reference '{sub_ref}' could not be resolved.")

    def _validate_organization(self, res: Dict[str, Any]):
        o_id = res.get("id", "unknown")
        if not res.get("name"):
            self.warnings.append(f"Organization ({o_id}) is missing 'name'.")

    def _validate_practitioner(self, res: Dict[str, Any]):
        p_id = res.get("id", "unknown")
        if not res.get("name"):
            self.warnings.append(f"Practitioner ({p_id}) is missing 'name'.")

    def _build_result(self) -> Dict[str, Any]:
        return {
            "is_valid": len(self.errors) == 0,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "resource_counts": dict(self.resource_counts)
        }


def validate_fhir_bundle(bundle: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to validate an HL7 FHIR R4 Bundle.
    """
    validator = FHIRValidator(bundle)
    return validator.validate()
