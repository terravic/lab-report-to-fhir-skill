#!/usr/bin/env python3
"""Runner script to generate synthetic test PDF reports."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.synthetic_generator import generate_all_synthetic_reports

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    created = generate_all_synthetic_reports(out_dir)
    print(f"Generated {len(created)} synthetic PDF reports in '{out_dir}':")
    for p in created:
        print(f"  - {p}")
