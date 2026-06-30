"""Scenario 5 - Research data stewards & analysts: the homogeneity attack.

k-anonymity alone is not safety. If every record in an equivalence class shares
the same sensitive value, an attacker who locates the class learns the sensitive
attribute *without* singling anyone out - k passed, but privacy failed. That is
the homogeneity attack l-diversity defends against.

This demo runs an HIV-status cohort that satisfies k>=2 yet fails l>=2, and
contrasts it with a TSV research extract (loaded via --delimiter) that clears
both bars - using only the real deidproof API.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv, l_diversity


def main() -> None:
    rule("RESEARCH STEWARD  -  why k alone is not enough (l-diversity)")

    csv = dataset("06-l-diversity-gap", "hiv_cohort.csv")
    print("\nA cohort grouped to k>=2 on (zip3, age_band, sex):")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip3", "age_band", "sex"],
        sensitive=["hiv_status"],
        k=2,
        l=2,
        safe_harbor=False,  # generalized columns; focus on k vs l here
    )
    print(f"k-anonymity  : k = {rep.min_k}   " + verdict("k>=2", rep.k_passed))
    print(f"l-diversity  : l = {rep.min_l}   " + verdict("l>=2", rep.l_passed))

    # Show the per-class diversity that drives the verdict.
    _, per_class = l_diversity(
        _rows(csv), ["zip3", "age_band", "sex"], ["hiv_status"]
    )
    print("\nDistinct sensitive values per equivalence class:")
    for key, n in sorted(per_class.items()):
        flag = "  <-- homogeneous: leaks hiv_status" if n < 2 else ""
        print(f"   {key} -> {n} distinct{flag}")

    overall(rep)

    print("\nContrast: a generalized TSV research extract (tab-delimited):")
    tsv = dataset("10-tsv-research-extract", "behavioral_extract.tsv")
    rep2 = analyze_csv(
        tsv,
        quasi_identifiers=["state", "age_band", "sex"],
        sensitive=["diagnosis"],
        k=2,
        l=2,
        delimiter="\t",
    )
    print(f"   k = {rep2.min_k}  l = {rep2.min_l}  -> "
          + ("PASS" if rep2.passed else "FAIL"))
    print("\nLesson: gate on k AND l. A class can be k-anonymous and still hand")
    print("the attacker the sensitive value for free.")


def _rows(path: str):
    import csv
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


if __name__ == "__main__":
    main()
