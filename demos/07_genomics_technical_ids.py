"""Scenario 7 - Genomics / biobank engineers.

A biobank release looks "de-identified" -- barcodes instead of names -- yet it
leaks four technical identifiers people forget are PHI: a participant portal
*URL* (S14), a *sequencer serial* (S13), an *upload IP* (S15), and a
*collection date* (S3). deidproof catches all four, by header and by cell shape.
"""
from _common import dataset, rule, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("GENOMICS / BIOBANK  -  technical ids are PHI too (URL/IP/serial/date)")

    csv = dataset("09-genomics-biobank", "biobank_samples.csv")
    print("\nClearing a biobank sample manifest for a collaborator:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip3", "age", "ancestry"],
        sensitive=["ancestry"],
        k=2,
    )
    print(f"Rows analyzed : {rep.row_count}")
    print(f"k-anonymity   : k = {rep.min_k}")

    by_cat = {}
    for f in rep.safe_harbor_findings:
        by_cat.setdefault(f.rule_id, []).append(f.column)
    print(f"\nSafe Harbor findings: {len(rep.safe_harbor_findings)}")
    for rid in sorted(by_cat):
        print(f"   {rid:>4}  columns: {', '.join(sorted(set(by_cat[rid])))}")

    for expected in ("S13", "S14", "S15"):
        assert expected in by_cat, f"{expected} should be detected"

    overall(rep)
    print("\nLesson: URLs (S14), IPs (S15), device serials (S13) and full dates")
    print("(S3) are Safe Harbor identifiers even when no name is present.")


if __name__ == "__main__":
    main()
