"""Scenario 19 - Rare-attribute singletons in a small cohort.

Small cohorts fail k precisely where a rare attribute isolates one person. This
demo takes the biobank manifest, groups on (zip3, age, ancestry), and surfaces
the smallest equivalence classes -- the exact rows a steward must generalize or
suppress. It uses the report's `smallest_classes`, which is the actionable part.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("SMALL COHORT  -  find the singleton rows that fail k")

    csv = dataset("09-genomics-biobank", "biobank_samples.csv")
    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip3", "age", "ancestry"],
        sensitive=["ancestry"],
        k=2,
        safe_harbor=False,  # focus on k here; technical ids covered in demo 7
    )
    print(f"\nBiobank manifest: {rep.row_count} rows")
    print(f"k over (zip3, age, ancestry) = {rep.min_k}   "
          + verdict("k>=2", rep.k_passed))

    print("\nSmallest equivalence classes (each singleton is a re-id risk):")
    singletons = [c for c in rep.smallest_classes if c["size"] == 1]
    for cls in rep.smallest_classes:
        vals = ", ".join(f"{k}={v}" for k, v in cls["values"].items())
        flag = "  <-- SINGLETON" if cls["size"] == 1 else ""
        print(f"   size {cls['size']}  ({vals}){flag}  rows={cls['row_indices']}")

    assert singletons, "this cohort should contain at least one singleton"
    overall(rep)
    print(f"\n{len(singletons)} singleton class(es) must be generalized (widen the")
    print("age band) or suppressed before this manifest can be released.")


if __name__ == "__main__":
    main()
