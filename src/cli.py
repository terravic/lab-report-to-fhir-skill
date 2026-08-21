"""
Command Line Interface for Lab Report to FHIR Conversion.
Converts single or batch PDF lab reports into HL7 FHIR R4 JSON bundles.
"""

import argparse
import glob
import json
import os
import sys
from typing import List

from src.parser import parse_lab_report_file
from src.fhir_builder import convert_parsed_data_to_fhir
from src.fhir_validator import validate_fhir_bundle
from src.visualizer import generate_html_dashboard, open_in_browser


def process_single_file(pdf_path: str, output_path: str = None, bundle_type: str = "transaction", validate: bool = True, compact: bool = False, view: bool = False) -> dict:
    """Processes a single PDF lab report and writes FHIR JSON output."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Input file not found: {pdf_path}")
        
    print(f"Processing: {pdf_path}")
    parsed = parse_lab_report_file(pdf_path)
    bundle = convert_parsed_data_to_fhir(parsed, bundle_type=bundle_type)
    
    if validate:
        val_result = validate_fhir_bundle(bundle)
        if not val_result["is_valid"]:
            print(f"Validation Error for {pdf_path}: {val_result['errors']}", file=sys.stderr)
        else:
            print(f"Validated OK: {val_result['resource_counts']}")
            
    if output_path:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            if compact:
                json.dump(bundle, f, separators=(',', ':'))
            else:
                json.dump(bundle, f, indent=2)
        print(f"Saved FHIR Bundle to: {output_path}")

    if view:
        html_path = generate_html_dashboard(bundle=bundle)
        print(f"Generated Canvas UI dashboard at: {html_path}")
        open_in_browser(html_path)
        
    return bundle


def process_directory(input_dir: str, output_dir: str, bundle_type: str = "transaction", validate: bool = True, compact: bool = False, view: bool = False):
    """Processes all PDF files in a directory."""
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"Input directory not found: {input_dir}")
        
    os.makedirs(output_dir, exist_ok=True)
    pdf_files = sorted(glob.glob(os.path.join(input_dir, "*.pdf")))
    
    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return
        
    print(f"Found {len(pdf_files)} PDF file(s) in {input_dir}")
    summary = []
    
    for pdf in pdf_files:
        base_name = os.path.splitext(os.path.basename(pdf))[0]
        clean_name = base_name.lower().replace(" ", "_") + "_fhir.json"
        out_file = os.path.join(output_dir, clean_name)
        
        try:
            bundle = process_single_file(pdf, out_file, bundle_type=bundle_type, validate=validate, compact=compact, view=False)
            summary.append({"file": pdf, "status": "SUCCESS", "output": out_file, "entries": len(bundle.get("entry", []))})
        except Exception as e:
            print(f"Failed processing {pdf}: {str(e)}", file=sys.stderr)
            summary.append({"file": pdf, "status": "FAILED", "error": str(e)})
            
    print("\n--- Batch Processing Summary ---")
    for item in summary:
        if item["status"] == "SUCCESS":
            print(f"  [SUCCESS] {os.path.basename(item['file'])} -> {os.path.basename(item['output'])} ({item['entries']} resources)")
        else:
            print(f"  [FAILED]  {os.path.basename(item['file'])}: {item['error']}")

    if view:
        html_path = generate_html_dashboard()
        print(f"Generated Canvas UI dashboard with batch results at: {html_path}")
        open_in_browser(html_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convert unstructured laboratory report PDFs into standard HL7 FHIR R4 JSON bundles."
    )
    parser.add_argument("-i", "--input", required=True, help="Path to input PDF file or directory containing PDF reports.")
    parser.add_argument("-o", "--output", help="Path to output JSON file or output directory.")
    parser.add_argument("-t", "--type", choices=["transaction", "collection"], default="transaction", help="FHIR Bundle type (default: transaction).")
    parser.add_argument("--no-validate", action="store_true", help="Disable schema and referential validation.")
    parser.add_argument("--compact", action="store_true", help="Output compact minified JSON instead of indented JSON.")
    parser.add_argument("--view", "--ui", action="store_true", help="Launch interactive Canvas UI dashboard in web browser after conversion.")
    
    args = parser.parse_args()
    
    if os.path.isdir(args.input):
        out_dir = args.output if args.output else "output"
        process_directory(args.input, out_dir, bundle_type=args.type, validate=not args.no_validate, compact=args.compact, view=args.view)
    else:
        out_path = args.output
        if not out_path:
            base_name = os.path.splitext(os.path.basename(args.input))[0]
            out_path = f"output/{base_name.lower().replace(' ', '_')}_fhir.json"
        process_single_file(args.input, out_path, bundle_type=args.type, validate=not args.no_validate, compact=args.compact, view=args.view)


if __name__ == "__main__":
    main()
