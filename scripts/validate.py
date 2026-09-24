"""Runner script to validate generated FHIR JSON bundles."""
import argparse
import glob
import json
import os
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

from src.fhir_validator import validate_fhir_bundle


def main():
    parser = argparse.ArgumentParser(description="Validate FHIR R4 JSON bundles against schema and referential rules.")
    parser.add_argument("-i", "--input", required=True, help="Path to FHIR JSON file or directory containing JSON bundles.")
    args = parser.parse_args()

    files = []
    if os.path.isdir(args.input):
        files = sorted(glob.glob(os.path.join(args.input, "*.json")))
    else:
        files = [args.input]

    if not files:
        print(f"No JSON files found in {args.input}", file=sys.stderr)
        sys.exit(1)

    all_valid = True
    print(f"Validating {len(files)} FHIR bundle file(s)...\n")

    for f_path in files:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            res = validate_fhir_bundle(data)
            status_str = "VALID" if res["is_valid"] else "INVALID"
            print(f"[{status_str}] {os.path.basename(f_path)}")
            print(f"  Resources: {res['resource_counts']}")
            if res["errors"]:
                print(f"  Errors: {res['errors']}")
                all_valid = False
            if res["warnings"]:
                print(f"  Warnings: {res['warnings']}")
        except Exception as e:
            print(f"[ERROR] {os.path.basename(f_path)}: {str(e)}")
            all_valid = False
        print()

    if not all_valid:
        sys.exit(1)
    else:
        print("All FHIR bundles passed validation successfully.")


if __name__ == "__main__":
    main()
