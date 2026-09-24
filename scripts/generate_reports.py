"""Runner script to generate synthetic test PDF reports."""
import sys

if "." not in sys.path:
    sys.path.insert(0, ".")

from src.synthetic_generator import generate_all_synthetic_reports

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    created = generate_all_synthetic_reports(out_dir)
    print(f"Generated {len(created)} synthetic PDF reports in '{out_dir}':")
    for p in created:
        print(f"  - {p}")
