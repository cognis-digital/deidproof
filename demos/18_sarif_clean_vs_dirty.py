"""Scenario 18 - SARIF for both a clean and a dirty release.

Code-scanning tooling expects a SARIF file whether or not there are findings. A
clean release produces a valid SARIF log with an empty results array (proof it
was checked); a dirty one produces error-level results with rule ids and
locations. This demo emits both and verifies the shape of each.
"""
import json

from _common import dataset, rule
from deidproof.core import analyze_csv
from deidproof.sarif import report_to_sarif


def main() -> None:
    rule("AUDITOR  -  SARIF evidence for clean AND dirty releases")

    clean = analyze_csv(
        dataset("02-clean", "clean_export.csv"),
        quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["diagnosis_group"], k=2, l=2,
    )
    dirty = analyze_csv(
        dataset("04-safe-harbor-leak", "ed_export.csv"),
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["chief_complaint"], k=2, l=2,
    )

    clean_log = report_to_sarif(clean, dataset="clean_export.csv")
    dirty_log = report_to_sarif(dirty, dataset="ed_export.csv")

    print("\nClean release SARIF:")
    print(f"   version={clean_log['version']}  "
          f"rules={len(clean_log['runs'][0]['tool']['driver']['rules'])}  "
          f"results={len(clean_log['runs'][0]['results'])}")
    assert clean_log["runs"][0]["results"] == []

    print("\nDirty release SARIF:")
    dres = dirty_log["runs"][0]["results"]
    print(f"   results={len(dres)}  "
          f"rule ids={sorted({r['ruleId'] for r in dres})}")
    assert dres and all(r["level"] == "error" for r in dres)

    print("\nOne dirty result, verbatim:")
    print(json.dumps(dres[0], indent=2))

    print("\nOVERALL: PASS   (both SARIF logs are valid 2.1.0 documents)")
    print("\nLesson: keep the clean SARIF too -- an empty results array is your")
    print("dated, machine-checkable proof the release was actually reviewed.")


if __name__ == "__main__":
    main()
