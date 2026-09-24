"""Runner script for lab report to FHIR conversion."""
import sys

# Ensure repository root is in python path
if "." not in sys.path:
    sys.path.insert(0, ".")

from src.cli import main

if __name__ == "__main__":
    main()
