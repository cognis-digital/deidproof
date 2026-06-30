"""Scenario 4 - Auditors.

An auditor does not want a screenshot; they want machine-checkable evidence that
fits the tooling they already run. deidproof serializes its findings to OASIS
SARIF 2.1.0 - one reporting descriptor per Safe Harbor category plus DEID-K /
DEID-L - so a failed release surfaces inline on a pull request via GitHub code
scanning and lands in the audit trail with rule ids and locations.

This demo produces the SARIF log for a clinical-trial listing that is unique on
(zip, age, sex) and shows the auditor exactly what the artifact contains.
"""
import json

from _common import dataset, rule, overall
from deidproof.core import analyze_csv
from deidproof.sarif import report_to_sarif


def main() -> None:
    rule("AUDITOR  -  SARIF 2.1.0 evidence, rule ids and locations")

    csv = dataset("07-clinical-trial", "trial_subjects.csv")
    print("\nAuditing a small-N clinical-trial listing before sharing:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["adverse_event"],
        k=2,
        l=2,
    )
    overall(rep)

    sarif = report_to_sarif(rep, dataset=csv)
    run = sarif["runs"][0]
    driver = run["tool"]["driver"]
    results = run["results"]

    print(f"\nSARIF version : {sarif['version']}")
    print(f"Tool driver   : {driver['name']} {driver['version']}")
    print(f"Rule catalog  : {len(driver['rules'])} reporting descriptors "
          "(S1-S18, DEID-K, DEID-L)")
    print(f"Results       : {len(results)} error-level finding(s)\n")

    for res in results[:6]:
        loc = res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        print(f"   [{res['level']}] {res['ruleId']}: {res['message']['text']}")
        print(f"            -> {loc}")

    print("\nFirst result, verbatim SARIF (this is what code-scanning ingests):")
    print(json.dumps(results[0], indent=2))

    print("\nThe auditor keeps the SARIF file as dated, hash-stable evidence that")
    print("the release was checked and exactly which rules it tripped.")


if __name__ == "__main__":
    main()
