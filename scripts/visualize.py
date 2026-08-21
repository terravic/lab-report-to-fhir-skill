#!/usr/bin/env python3
"""
CLI script to launch or generate the interactive Canvas UI Dashboard for FHIR Lab Reports.
Usage:
    python3 scripts/visualize.py output/synthetic_cancer_lab_report_fhir.json
    python3 scripts/visualize.py reports/synthetic_colorectal_ctdna.pdf
    python3 scripts/visualize.py --no-open
"""

import os
import sys
import json
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visualizer import generate_html_dashboard, open_in_browser
from src.parser import parse_lab_report_file
from src.fhir_builder import convert_parsed_data_to_fhir


def main():
    parser = argparse.ArgumentParser(description="Generate and open interactive Canvas UI Dashboard for FHIR Lab Reports.")
    parser.add_argument("input_file", nargs="?", default=None, help="Path to input FHIR JSON or PDF file to visualize.")
    parser.add_argument("-o", "--output", default="ui/fhir_viewer.html", help="Path to output HTML dashboard (default: ui/fhir_viewer.html).")
    parser.add_argument("--no-open", action="store_true", help="Generate HTML without launching web browser.")

    args = parser.parse_args()

    bundle = None
    if args.input_file:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' does not exist.", file=sys.stderr)
            sys.exit(1)

        ext = os.path.splitext(args.input_file)[1].lower()
        if ext == ".json":
            with open(args.input_file, "r", encoding="utf-8") as f:
                bundle = json.load(f)
            print(f"Loaded FHIR JSON bundle from: {args.input_file}")
        elif ext == ".pdf":
            print(f"Converting PDF report to FHIR: {args.input_file}")
            parsed_data = parse_lab_report_file(args.input_file)
            bundle = convert_parsed_data_to_fhir(parsed_data)
            print(f"Converted {args.input_file} ({len(bundle.get('entry', []))} FHIR resources).")
        else:
            print(f"Error: Unsupported file format '{ext}'. Expected .json or .pdf.", file=sys.stderr)
            sys.exit(1)

    html_path = generate_html_dashboard(bundle=bundle, output_html_path=args.output)
    print(f"Generated interactive Canvas UI dashboard at: {html_path}")

    # Also sync to skills directory if default
    if args.output == "ui/fhir_viewer.html":
        skills_ui_path = "skills/lab-report-to-fhir/ui/fhir_viewer.html"
        generate_html_dashboard(bundle=bundle, output_html_path=skills_ui_path)

    if not args.no_open:
        print("Opening in default web browser...")
        open_in_browser(html_path)


if __name__ == "__main__":
    main()
