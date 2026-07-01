"""Scenario 17 - Before / after: turning a FAIL into a PASS.

The whole point of measuring re-identification risk is to fix it. This demo puts
the leaky 01-basic export next to the generalized 05 release and shows the exact
metric movement: k 1 -> higher, direct identifiers gone, OVERALL FAIL -> PASS.
It is the story a data scientist tells their privacy officer.
"""
from _common import dataset, rule
from deidproof.core import analyze_csv


def _summ(rep):
    return (f"k={rep.min_k} l={rep.min_l} "
            f"safe_harbor_findings={len(rep.safe_harbor_findings)} "
            f"OVERALL={'PASS' if rep.passed else 'FAIL'}")


def main() -> None:
    rule("BEFORE / AFTER  -  remediation turns FAIL into PASS")

    before = analyze_csv(
        dataset("01-basic", "patients.csv"),
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["diagnosis"], k=2, l=2,
    )
    after = analyze_csv(
        dataset("05-generalized-pass", "registry_release.csv"),
        quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["diagnosis_group"], k=2, l=2,
    )

    print("\nBEFORE (raw patients.csv, fine-grained QIs, direct identifiers):")
    print(f"   {_summ(before)}")
    print("\nAFTER  (generalized registry_release.csv):")
    print(f"   {_summ(after)}")

    assert before.passed is False
    assert after.passed is True
    print("\nDelta:")
    print(f"   k: {before.min_k} -> {after.min_k}")
    print(f"   direct identifiers: {len(before.safe_harbor_findings)} -> "
          f"{len(after.safe_harbor_findings)}")

    print("\nOVERALL: PASS")
    print("\nThis is the evidence pair to attach to a release ticket: the same")
    print("tool, the same thresholds, a documented FAIL and its remediated PASS.")


if __name__ == "__main__":
    main()
