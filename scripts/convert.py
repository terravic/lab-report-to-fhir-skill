#!/usr/bin/env python3
"""Runner script for lab report to FHIR conversion."""
import os
import sys

# Ensure repository root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cli import main

if __name__ == "__main__":
    main()
