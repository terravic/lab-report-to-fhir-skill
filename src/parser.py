"""
Lab Report Parser Module.
Extracts structured patient demographics, provider/lab details, specimen info,
test observations, reference ranges, and clinical interpretations from extracted PDF tables and text.
"""

from typing import Dict, Any, List, Optional, Union
import re
from datetime import datetime
from src.extractor import clean_extracted_text, extract_structured_pages, extract_text_from_pdf


def normalize_date(date_str: str) -> Optional[str]:
    """
    Parses various date string formats and converts to ISO-8601 (YYYY-MM-DD).
    """
    if not date_str:
        return None
        
    date_str = date_str.strip().rstrip('.,;')
    
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%d/%m/%Y",
        "%b %d, %Y",
        "%B %d, %Y",
        "%b %d %Y",
        "%B %d %Y",
        "%d-%b-%Y",
        "%d %b %Y"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
            
    m2 = re.search(r'([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})', date_str)
    if m2:
        try:
            dt = datetime.strptime(f"{m2.group(1)} {m2.group(2)} {m2.group(3)}", "%b %d %Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            try:
                dt = datetime.strptime(f"{m2.group(1)} {m2.group(2)} {m2.group(3)}", "%B %d %Y")
                return dt.strftime("%Y-%m-%d")
            except Exception:
                pass
                
    m1 = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})', date_str)
    if m1:
        try:
            m, d, y = int(m1.group(1)), int(m1.group(2)), int(m1.group(3))
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            pass
            
    return None


def normalize_gender(gender_str: str) -> str:
    """
    Normalizes gender string to FHIR standard: male, female, other, unknown.
    """
    if not gender_str:
        return "unknown"
    g = gender_str.lower().strip()
    if g.startswith("f") or "female" in g:
        return "female"
    if g.startswith("m") or "male" in g:
        return "male"
    if "other" in g or "non-binary" in g:
        return "other"
    return "unknown"


class LabReportParser:
    """
    Parser for clinical diagnostic laboratory reports and oncology panels.
    Accepts raw text or structured pages containing extracted tables.
    """
    
    def __init__(self, input_data: Union[str, List[Dict[str, Any]]]):
        if isinstance(input_data, str):
            self.raw_text = clean_extracted_text(input_data)
            self.pages_data = []
        else:
            self.pages_data = input_data
            self.raw_text = "\n\n--- PAGE BREAK ---\n\n".join(
                [clean_extracted_text(p.get("cleaned_text", p.get("raw_text", ""))) for p in input_data]
            )
            
        self.lines = [line.strip() for line in self.raw_text.split("\n") if line.strip()]
        self.extracted_tables = []
        for p in self.pages_data:
            for table in p.get("tables", []):
                cleaned_table = [[clean_extracted_text(cell or '') for cell in row] for row in table]
                self.extracted_tables.append(cleaned_table)
                
    def parse(self) -> Dict[str, Any]:
        """
        Parses all sections of the lab report into a unified dictionary.
        """
        report_data: Dict[str, Any] = {
            "report_title": self._extract_report_title(),
            "patient": self._extract_patient_info(),
            "provider": self._extract_provider_info(),
            "facility": self._extract_facility_info(),
            "specimen": self._extract_specimen_info(),
            "summary_result": self._extract_summary_result(),
            "observations": self._extract_observations(),
            "clinical_interpretation": self._extract_interpretation(),
            "methodology": self._extract_methodology(),
            "limitations": self._extract_limitations(),
            "raw_text": self.raw_text
        }
        return report_data
        
    def _extract_report_title(self) -> str:
        """Extracts the lab report title or panel name."""
        for line in self.lines[:10]:
            line_clean = line.strip()
            if any(term in line_clean.lower() for term in [
                "synthetic lab report", "cancer detection", "galleri", "diagnostic report",
                "liquid biopsy", "genetic test", "hereditary cancer", "pathology report",
                "laboratory report", "prostate health index", "ctdna panel", "early detection",
                "screening report"
            ]):
                return line_clean
        return "Laboratory Diagnostic Report"

    def _extract_from_tables(self, pattern: str) -> Optional[str]:
        """Helper to find matching text across all extracted table cells."""
        for table in self.extracted_tables:
            for row in table:
                for cell in row:
                    m = re.search(pattern, cell, re.IGNORECASE)
                    if m:
                        return m.group(1).strip()
        return None

    def _extract_patient_info(self) -> Dict[str, Any]:
        """Extracts patient demographics."""
        patient: Dict[str, Any] = {
            "name": None,
            "dob": None,
            "gender": "unknown",
            "patient_id": None
        }
        
        table_name = self._extract_from_tables(r'Name:\s*([A-Za-z\s\.\,\-]+?)(?:\n|$)')
        table_dob = self._extract_from_tables(r'DOB:\s*([A-Za-z0-9\/\,\s\-]+?)(?:\n|$)')
        table_sex = self._extract_from_tables(r'Sex:\s*([A-Za-z]+)')
        table_pid = self._extract_from_tables(r'Patient ID:\s*([A-Za-z0-9\-]+)')
        
        if table_name:
            patient["name"] = table_name
        if table_dob:
            patient["dob"] = normalize_date(table_dob) or table_dob
        if table_sex:
            patient["gender"] = normalize_gender(table_sex)
        if table_pid:
            patient["patient_id"] = table_pid
            
        if not patient["name"]:
            name_match = re.search(r'Name:\s*([A-Za-z\s\.\,\-]+?)(?=\s+(?:Provider|DOB|Sex|Gender|Patient ID|MRN|Specimen|Facility)|$|\n)', self.raw_text, re.IGNORECASE)
            if name_match:
                cand = name_match.group(1).strip()
                if cand and not cand.lower().startswith("information"):
                    patient["name"] = cand
                    
        if not patient["dob"]:
            dob_match = re.search(r'DOB:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Facility|Sex|Gender|Provider|Location|Collection)|$|\n)', self.raw_text, re.IGNORECASE)
            if dob_match:
                patient["dob"] = normalize_date(dob_match.group(1)) or dob_match.group(1).strip()

        if patient["gender"] == "unknown":
            sex_match = re.search(r'Sex:\s*([A-Za-z]+)', self.raw_text, re.IGNORECASE)
            if sex_match:
                patient["gender"] = normalize_gender(sex_match.group(1))
                
        if not patient["patient_id"]:
            id_match = re.search(r'(?:Patient ID|MRN|Subject ID):\s*([A-Za-z0-9\-]+)', self.raw_text, re.IGNORECASE)
            if id_match:
                patient["patient_id"] = id_match.group(1).strip()
                
        return patient

    def _extract_provider_info(self) -> Dict[str, Any]:
        """Extracts ordering provider / physician information."""
        provider: Dict[str, Any] = {
            "name": None,
            "npi": None
        }
        
        table_prov = self._extract_from_tables(r'Provider:\s*([A-Za-z\s\.\,\-]+?)(?:\n|$)')
        table_npi = self._extract_from_tables(r'NPI:\s*([0-9]{10})')
        
        if table_prov:
            provider["name"] = table_prov
        if table_npi:
            provider["npi"] = table_npi
            
        if not provider["name"]:
            prov_match = re.search(r'Provider:\s*([A-Za-z\s\.\,\-]+?)(?=\s+(?:Specimen ID|Facility|NPI|Location|DOB|Collection)|$|\n)', self.raw_text, re.IGNORECASE)
            if prov_match:
                cand = prov_match.group(1).strip()
                if cand and not cand.lower().startswith("information"):
                    provider["name"] = cand
                    
        if not provider["npi"]:
            npi_match = re.search(r'NPI:\s*([0-9]{10})', self.raw_text, re.IGNORECASE)
            if npi_match:
                provider["npi"] = npi_match.group(1).strip()
                
        return provider

    def _extract_facility_info(self) -> Dict[str, Any]:
        """Extracts testing facility, address, and CLIA certification."""
        facility: Dict[str, Any] = {
            "name": None,
            "clia_id": None,
            "address": None,
            "lab_director": None
        }
        
        table_fac = self._extract_from_tables(r'Facility:\s*([\s\S]+?)(?=$|\n\n)')
        if table_fac:
            facility["name"] = " ".join([l.strip() for l in table_fac.split('\n') if l.strip()])
            
        if not facility["name"]:
            fac_match = re.search(r'Facility:\s*([A-Za-z0-9\s\.\,\-]+?)(?=\s+(?:Collection|Location|NPI|Specimen|Report Date)|$|\n)', self.raw_text, re.IGNORECASE)
            if fac_match:
                facility["name"] = fac_match.group(1).strip()
            
        clia_match = re.search(r'CLIA(?:\s*ID)?:\s*([A-Za-z0-9]+)', self.raw_text, re.IGNORECASE)
        if clia_match:
            facility["clia_id"] = clia_match.group(1).strip()
            
        lab_addr_match = re.search(r'Laboratory Address:\s*([\s\S]+?)(?=CLIA|Laboratory Director|$)', self.raw_text, re.IGNORECASE)
        if lab_addr_match:
            facility["address"] = " ".join([line.strip() for line in lab_addr_match.group(1).split("\n") if line.strip()])
            
        dir_match = re.search(r'Director:\s*([A-Za-z\s\.\,\-]+?)(?=\s*(?:Electronic Signature|Date|CLIA)|$|\n)', self.raw_text, re.IGNORECASE)
        if dir_match:
            facility["lab_director"] = dir_match.group(1).strip()
            
        return facility

    def _extract_specimen_info(self) -> Dict[str, Any]:
        """Extracts specimen ID, collection date, received date, report date, and type."""
        specimen: Dict[str, Any] = {
            "specimen_id": None,
            "collection_date": None,
            "received_date": None,
            "report_date": None,
            "specimen_type": "Blood / Plasma"
        }
        
        table_sid = self._extract_from_tables(r'Specimen ID:\s*([A-Za-z0-9\-]+)')
        table_coll = self._extract_from_tables(r'Collection Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?:\n|$)')
        table_rec = self._extract_from_tables(r'Received Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?:\n|$)')
        table_rep = self._extract_from_tables(r'Report Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?:\n|$)')
        
        if table_sid:
            specimen["specimen_id"] = table_sid
        if table_coll:
            specimen["collection_date"] = normalize_date(table_coll) or table_coll
        if table_rec:
            specimen["received_date"] = normalize_date(table_rec) or table_rec
        if table_rep:
            specimen["report_date"] = normalize_date(table_rep) or table_rep
            
        if not specimen["specimen_id"]:
            spec_id_match = re.search(r'Specimen ID:\s*([A-Za-z0-9\-]+)', self.raw_text, re.IGNORECASE)
            if spec_id_match:
                specimen["specimen_id"] = spec_id_match.group(1).strip()
                
        if not specimen["collection_date"]:
            coll_match = re.search(r'Collection Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Sex|Received|Report|Specimen)|$|\n)', self.raw_text, re.IGNORECASE)
            if coll_match:
                specimen["collection_date"] = normalize_date(coll_match.group(1)) or coll_match.group(1).strip()
                
        if not specimen["received_date"]:
            rec_match = re.search(r'Received Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Patient ID|Report|Report Date|Specimen|NPI)|$|\n)', self.raw_text, re.IGNORECASE)
            if rec_match:
                specimen["received_date"] = normalize_date(rec_match.group(1)) or rec_match.group(1).strip()

        if not specimen["report_date"]:
            rep_match = re.search(r'Report Date:\s*([A-Za-z0-9\/\,\s\-]+?)(?=\s+(?:Test|Result|Summary|Methodology)|$|\n)', self.raw_text, re.IGNORECASE)
            if rep_match:
                specimen["report_date"] = normalize_date(rep_match.group(1)) or rep_match.group(1).strip()

        spec_type_match = re.search(r'(?:Specimen Type|Sample Type):\s*([A-Za-z0-9\s\/\-]+?)(?=\s+(?:Collection|Received|Volume)|$|\n)', self.raw_text, re.IGNORECASE)
        if spec_type_match:
            specimen["specimen_type"] = spec_type_match.group(1).strip()
            
        return specimen

    def _extract_summary_result(self) -> Dict[str, Any]:
        """Extracts primary test result summary."""
        summary = {
            "status": "final",
            "result_text": None,
            "conclusion": None
        }
        
        res_match = re.search(r'Result:\s*(Cancer Signal (?:Detected|Not Detected)|Positive(?:\s*\([^\)]+\))?|Negative(?:\s*\([^\)]+\))?|Normal|Abnormal|Elevated Risk(?:\s*\([^\)]+\))?|Pathogenic Variant Identified)', self.raw_text, re.IGNORECASE)
        if res_match:
            summary["result_text"] = res_match.group(1).strip()
            
        narr_match = re.search(r'Test Result Summary[\s\S]+?(?:Result:\s*[^\n]+\n)?([\s\S]+?)(?=Cancer Signal Origin|Clinical Interpretation|Observations|Quantitative and Qualitative|Detailed Genetic Variant|Biomarker Findings|Test Results|Origin 1|Priority|$)', self.raw_text, re.IGNORECASE)
        if narr_match:
            summary["conclusion"] = " ".join([l.strip() for l in narr_match.group(1).split("\n") if l.strip()])
            
        return summary

    def _extract_observations(self) -> List[Dict[str, Any]]:
        """Extracts discrete observation items from tables and text."""
        observations: List[Dict[str, Any]] = []
        seen_keys = set()

        def get_interp(text: str) -> tuple[str, str]:
            t = text.lower() if text else ""
            if "pathogenic" in t or "abnormal" in t or "positive" in t:
                return "A", "Abnormal"
            if "high" in t or "h)" in t:
                return "H", "High"
            if "low" in t or "l)" in t:
                return "L", "Low"
            return "N", "Normal"

        # 1. Extract from Structured Tables
        for table in self.extracted_tables:
            if not table or len(table) < 2:
                continue
            
            header = [clean_extracted_text(c).lower() for c in table[0]]
            
            # Check for Galleri CSO Priority table
            if len(header) >= 3 and "priority" in header[0] and "origin" in header[1]:
                for row in table[1:]:
                    if len(row) >= 3:
                        orig_num_m = re.search(r'\d+', row[0])
                        num_str = orig_num_m.group(0) if orig_num_m else "1"
                        tissue = clean_extracted_text(row[1]).replace('\n', ' ')
                        freq = clean_extracted_text(row[2]).replace('\n', ' ')
                        obs_key = f"CSO_{num_str}_{tissue}"
                        if obs_key not in seen_keys:
                            observations.append({
                                "code": "94077-5",
                                "display": f"Predicted cancer signal origin {num_str}",
                                "test_name": f"Predicted Cancer Signal Origin {num_str}",
                                "value": f"{tissue} ({freq})",
                                "value_type": "string",
                                "component": {
                                    "tissue": tissue,
                                    "accuracy_frequency": freq
                                },
                                "interpretation": "A",
                                "interpretation_display": "Abnormal"
                            })
                            seen_keys.add(obs_key)
                continue

            # Check for Generic Laboratory / Oncology Observation Tables
            is_obs_table = any(k in header[0] for k in ['target', 'gene', 'biomarker', 'test', 'analyte'])
            if is_obs_table:
                loinc_col_idx = -1
                res_col_idx = 2
                unit_col_idx = -1
                ref_col_idx = -1
                interp_col_idx = -1

                for idx, col_name in enumerate(header):
                    if "loinc" in col_name:
                        loinc_col_idx = idx
                    elif "result" in col_name or "classification" in col_name:
                        res_col_idx = idx
                    elif "unit" in col_name:
                        unit_col_idx = idx
                    elif "reference" in col_name:
                        ref_col_idx = idx
                    elif "interpretation" in col_name or "flag" in col_name:
                        interp_col_idx = idx

                for row in table[1:]:
                    if len(row) < 2:
                        continue
                    test_name = clean_extracted_text(row[0]).replace('\n', ' ')
                    loinc_code = clean_extracted_text(row[loinc_col_idx]) if loinc_col_idx >= 0 and loinc_col_idx < len(row) else "11502-2"
                    if loinc_code.lower() == "local":
                        loinc_code = "11502-2"
                    
                    raw_val = clean_extracted_text(row[res_col_idx]).replace('\n', ' ') if res_col_idx < len(row) else ""
                    raw_units = clean_extracted_text(row[unit_col_idx]) if unit_col_idx >= 0 and unit_col_idx < len(row) else ""
                    raw_ref = clean_extracted_text(row[ref_col_idx]).replace('\n', ' ') if ref_col_idx >= 0 and ref_col_idx < len(row) else ""
                    raw_interp = clean_extracted_text(row[interp_col_idx]) if interp_col_idx >= 0 and interp_col_idx < len(row) else ""

                    icode, idisp = get_interp(raw_interp or raw_val)

                    # Check numeric quantity
                    try:
                        numeric_val = float(raw_val)
                        val_type = "quantity"
                        obs_val = numeric_val
                    except ValueError:
                        val_type = "string"
                        obs_val = raw_val

                    obs_item = {
                        "code": loinc_code,
                        "display": test_name,
                        "test_name": test_name,
                        "value": obs_val,
                        "value_type": val_type,
                        "interpretation": icode,
                        "interpretation_display": idisp
                    }
                    if raw_units:
                        obs_item["unit"] = raw_units
                    if raw_ref:
                        obs_item["reference_range"] = raw_ref

                    obs_key = f"{loinc_code}_{test_name}"
                    if obs_key not in seen_keys:
                        observations.append(obs_item)
                        seen_keys.add(obs_key)

        # 2. Add Primary Result from Summary if not in table observations
        summary_result = self._extract_summary_result()
        res_text = summary_result.get("result_text") or ""
        
        if "Cancer Signal Detected" in res_text and "94076-7_Cancer Signal Status" not in seen_keys:
            obs = {
                "code": "94076-7",
                "display": "Cancer signal methylation analysis in cell-free DNA",
                "test_name": "Cancer Signal Status",
                "value": "Cancer Signal Detected",
                "value_type": "string",
                "interpretation": "A",
                "interpretation_display": "Abnormal",
                "reference_range": "Cancer Signal Not Detected"
            }
            observations.insert(0, obs)
            seen_keys.add("94076-7_Cancer Signal Status")
        elif "Cancer Signal Not Detected" in res_text and "94076-7_Cancer Signal Status" not in seen_keys:
            obs = {
                "code": "94076-7",
                "display": "Cancer signal methylation analysis in cell-free DNA",
                "test_name": "Cancer Signal Status",
                "value": "Cancer Signal Not Detected",
                "value_type": "string",
                "interpretation": "N",
                "interpretation_display": "Normal",
                "reference_range": "Cancer Signal Not Detected"
            }
            observations.insert(0, obs)
            seen_keys.add("94076-7_Cancer Signal Status")

        # 3. Fallback: If no table observations were extracted, use text pattern matching
        if len(observations) == 0 or (len(observations) == 1 and "Cancer Signal Status" in observations[0].get("test_name", "")):
            origin_matches = re.finditer(r'Origin\s*(\d+)\s+([A-Za-z\s]+?)\s+(\d+(?:\.\d+)?\s*%)', self.raw_text)
            for m in origin_matches:
                orig_num = m.group(1)
                tissue = m.group(2).strip()
                freq = m.group(3).strip()
                obs_key = f"CSO_{orig_num}_{tissue}"
                if obs_key not in seen_keys:
                    observations.append({
                        "code": "94077-5",
                        "display": f"Predicted cancer signal origin {orig_num}",
                        "test_name": f"Predicted Cancer Signal Origin {orig_num}",
                        "value": f"{tissue} ({freq})",
                        "value_type": "string",
                        "component": {
                            "tissue": tissue,
                            "accuracy_frequency": freq
                        },
                        "interpretation": "A",
                        "interpretation_display": "Abnormal"
                    })
                    seen_keys.add(obs_key)

        return observations

    def _extract_interpretation(self) -> Optional[str]:
        """Extracts the clinical interpretation and recommendations block."""
        match = re.search(r'Clinical Interpretation[\s:：]+([\s\S]+?)(?=Methodology|Limitations|Laboratory Authorization|References|$)', self.raw_text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            return " ".join([l.strip() for l in text.split("\n") if l.strip()])
        return None

    def _extract_methodology(self) -> Optional[str]:
        """Extracts test methodology and assay description."""
        match = re.search(r'Methodology:\s*([\s\S]+?)(?=Limitations|Clinical Interpretation|Laboratory Authorization|$)', self.raw_text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            return " ".join([l.strip() for l in text.split("\n") if l.strip()])
        return None

    def _extract_limitations(self) -> Optional[str]:
        """Extracts test limitations and intended use."""
        match = re.search(r'Limitations:\s*([\s\S]+?)(?=Laboratory Authorization|Methodology|References|$)', self.raw_text, re.IGNORECASE)
        if match:
            text = match.group(1).strip()
            return " ".join([l.strip() for l in text.split("\n") if l.strip()])
        return None


def parse_lab_report_file(pdf_path: str) -> Dict[str, Any]:
    """
    Convenience function to extract and parse a lab report PDF.
    """
    pages = extract_structured_pages(pdf_path)
    parser = LabReportParser(pages)
    return parser.parse()
