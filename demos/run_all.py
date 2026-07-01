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
    "06_claims_export_gate",
    "07_genomics_technical_ids",
    "08_ci_gate_exit_codes",
    "09_json_pipeline_emit",
    "10_free_text_leak",
    "11_suppression_missing_cells",
    "12_delimiter_variants",
    "13_device_telemetry",
    "14_k_vs_l_tradeoff",
    "15_error_handling",
    "16_safe_harbor_catalog",
    "17_before_after_release",
    "18_sarif_clean_vs_dirty",
    "19_biobank_singletons",
    "20_multi_attribute_qi",
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
