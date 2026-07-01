"""Scenario 14 - The k-vs-l trade-off, quantified.

Generalizing quasi-identifiers raises k but can *lower* l, because merging
classes can pool records that share the same sensitive value. This demo uses the
low-level k_anonymity() and l_diversity() calls to chart both metrics as we
coarsen the quasi-identifier set, so a steward can pick the sweet spot.
"""
from _common import dataset, rule
from deidproof.core import k_anonymity, l_diversity


def _rows(path):
    import csv
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def main() -> None:
    rule("STEWARD  -  quantify the k <-> l trade-off as you generalize")

    rows = _rows(dataset("05-generalized-pass", "registry_release.csv"))
    print(f"\nRegistry release, {len(rows)} rows. Sensitive attribute: diagnosis_group\n")

    qi_sets = [
        ["region", "age_band", "sex"],
        ["region", "age_band"],
        ["region"],
    ]
    print(f"{'quasi-identifiers':<32}{'k':>4}{'l':>4}")
    print("-" * 40)
    for qi in qi_sets:
        k, _ = k_anonymity(rows, qi)
        l, _ = l_diversity(rows, qi, ["diagnosis_group"])
        print(f"{', '.join(qi):<32}{k:>4}{l:>4}")

    # Coarsening from (region,age_band,sex) upward is monotone non-decreasing in k.
    ks = [k_anonymity(rows, qi)[0] for qi in qi_sets]
    assert ks == sorted(ks), "coarsening QIs should never decrease k"
    print("\nOVERALL: PASS")
    print("\nLesson: k is monotone non-decreasing as you drop/coarsen QIs; l is not")
    print("guaranteed to move the same way. Gate on BOTH, and stop at the knee.")


if __name__ == "__main__":
    main()
