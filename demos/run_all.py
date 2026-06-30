"""Run every deidproof demo scenario end to end.

    python demos/run_all.py

Each scenario is independent and reads only the bundled CSV/TSV fixtures via the
real deidproof API, fully offline. They can be run in any order or on their own.
"""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCENARIOS = [
    "01_privacy_officer_gate",
    "02_data_scientist_generalize",
    "03_data_steward_safe_harbor",
    "04_auditor_sarif_evidence",
    "05_l_diversity_homogeneity",
]


def main() -> None:
    for name in SCENARIOS:
        mod = importlib.import_module(name)
        mod.main()
    print("\n" + "=" * 70)
    print("  All demo scenarios completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()
