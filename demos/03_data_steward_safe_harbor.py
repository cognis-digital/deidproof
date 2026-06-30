"""Scenario 3 - Healthcare / research data stewards.

A data steward releasing an emergency-department extract has to satisfy HIPAA
Safe Harbor: none of the 18 identifier categories of 45 CFR 164.514(b)(2) may
remain. deidproof scans both column *names* and cell *contents*, so it catches
an MRN column by its header and a phone number hiding in a free-text field by
its shape.

This demo runs the Safe Harbor scan over a realistic ED export and itemizes
every leaking category the steward must scrub before release.
"""
from _common import dataset, rule, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("DATA STEWARD  -  HIPAA Safe Harbor, all 18 categories")

    csv = dataset("04-safe-harbor-leak", "ed_export.csv")
    print("\nClearing an ED export for a quality-improvement study:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["chief_complaint"],
        k=2,
        l=2,
    )

    print(f"Rows analyzed : {rep.row_count}")
    print(f"k-anonymity   : k = {rep.min_k}   "
          f"({'pass' if rep.k_passed else 'fail'} at k>=2)")
    print(f"l-diversity   : l = {rep.min_l}   "
          f"({'pass' if rep.l_passed else 'fail'} at l>=2)")

    print(f"\nSafe Harbor findings: {len(rep.safe_harbor_findings)} "
          "identifier categories present")
    print("   (S# = the 18 categories of 45 CFR 164.514(b)(2))\n")
    for f in rep.safe_harbor_findings:
        rows = f" e.g. rows {f.sample_rows}" if f.sample_rows else ""
        print(f"   {f.rule_id:>4}  {f.category}")
        print(f"         column '{f.column}' - {f.match_count} hit(s){rows}")

    overall(rep)
    print("\nScrub list for the steward: drop/replace each flagged column, then")
    print("re-run. Note S3 also fires on a literal age of 91 (Safe Harbor caps")
    print("reported age at 90+), not only on calendar dates.")


if __name__ == "__main__":
    main()
