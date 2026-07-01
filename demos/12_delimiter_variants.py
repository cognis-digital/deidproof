"""Scenario 12 - Non-comma delimiters (TSV, semicolon).

Real exports are not always comma-separated: European tools emit semicolon files,
and research pipelines emit TSV. deidproof reads any single-character delimiter,
and the CLI accepts the literal token '\\t' for a tab. This demo runs the same
generalized dataset through comma, tab, and semicolon delimiters.
"""
from _common import dataset, rule, overall
from deidproof.cli import _resolve_delimiter
from deidproof.core import analyze_csv


def main() -> None:
    rule("DELIMITERS  -  TSV and semicolon exports, not just CSV")

    # tab-delimited
    tsv = dataset("10-tsv-research-extract", "behavioral_extract.tsv")
    print(f"\nTab-delimited research extract: {tsv}")
    print(r"   (CLI users pass --delimiter '\t'; it resolves to a real tab)")
    assert _resolve_delimiter(r"\t") == "\t"
    rep_tsv = analyze_csv(
        tsv, quasi_identifiers=["state", "age_band", "sex"],
        sensitive=["diagnosis"], k=2, l=2, delimiter="\t",
    )
    print(f"   k = {rep_tsv.min_k}  l = {rep_tsv.min_l}  "
          f"-> {'PASS' if rep_tsv.passed else 'FAIL'}")
    assert rep_tsv.passed

    # semicolon-delimited (common in EU locales)
    eu = dataset("13-semicolon-europe", "eu_export.csv")
    print(f"\nSemicolon-delimited EU export: {eu}")
    rep_eu = analyze_csv(
        eu, quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["diagnosis_group"], k=2, l=2, delimiter=";",
    )
    print(f"   k = {rep_eu.min_k}  l = {rep_eu.min_l}  "
          f"-> {'PASS' if rep_eu.passed else 'FAIL'}")
    assert rep_eu.passed

    print("\nOVERALL: PASS   (both non-comma delimiters parsed and analyzed)")
    print("\nLesson: point --delimiter at whatever your export uses; the privacy")
    print("math is identical regardless of the field separator.")


if __name__ == "__main__":
    main()
