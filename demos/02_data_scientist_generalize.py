"""Scenario 2 - Data scientists.

A data scientist owns the transform that makes a release safe. The loop is:
measure risk on the raw extract, generalize the quasi-identifiers (ZIP3, age
bands), and re-measure until the metrics clear the bar. deidproof gives you the
exact equivalence class that is still too small, so you know *which* column to
coarsen next.

This demo runs the same risk check on an ungeneralized cohort and on its
generalized successor, side by side, against the real API.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv, k_anonymity


def main() -> None:
    rule("DATA SCIENTIST  -  measure, generalize, re-measure")

    raw = dataset("01-basic", "patients.csv")
    print("\nStep 1 - raw extract, fine-grained quasi-identifiers (zip,age,sex):")
    min_k, classes = k_anonymity(
        # read straight from the bundled CSV via the high-level API
        rows=_rows(raw),
        quasi_identifiers=["zip", "age", "sex"],
    )
    print(f"   {len(classes)} equivalence classes over {sum(len(v) for v in classes.values())} rows")
    print(f"   k = {min_k}  -> every individual is unique; cannot release.")

    print("\nStep 2 - generalized release (region, age_band, sex):")
    gen = dataset("05-generalized-pass", "registry_release.csv")
    rep = analyze_csv(
        gen,
        quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["diagnosis_group"],
        k=2,
        l=2,
    )
    print(f"   Rows: {rep.row_count}   classes are now grouped, not unique.")
    print(f"   k = {rep.min_k}   " + verdict("target k>=2", rep.k_passed))
    print(f"   l = {rep.min_l}   " + verdict("target l>=2", rep.l_passed))

    print("\nLargest residual risk after generalization (smallest classes):")
    for cls in rep.smallest_classes[:3]:
        vals = ", ".join(f"{k}={v}" for k, v in cls["values"].items())
        print(f"   size {cls['size']}  ({vals})")

    overall(rep)
    print("\nThe metric tells you exactly when to stop coarsening: once the")
    print("smallest class clears k, further generalization only costs utility.")


def _rows(path: str):
    """Tiny CSV reader so the demo can show the low-level k_anonymity() call."""
    import csv
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


if __name__ == "__main__":
    main()
