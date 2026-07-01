"""Scenario 6 - Payer / claims analytics.

A payer wants to share a claims extract with an actuarial partner. Beyond the
obvious PHI, claims files carry *member ids* and *account numbers* -- Safe Harbor
categories S9 and S10 -- that are easy to overlook because they look like
harmless internal keys. This demo shows deidproof flagging them by header, and
the small (zip, age, sex) cells that also fail k.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("PAYER / CLAIMS  -  member id + account number are Safe Harbor ids")

    csv = dataset("08-claims-export", "payer_claims.csv")
    print("\nGating a claims extract before it leaves for an actuarial partner:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["icd10"],
        k=2,
        l=2,
    )
    print(f"Rows analyzed : {rep.row_count}")
    print(f"k-anonymity   : k = {rep.min_k}   " + verdict("k>=2", rep.k_passed))
    print(f"l-diversity   : l = {rep.min_l}   " + verdict("l>=2", rep.l_passed))

    cats = {f.rule_id for f in rep.safe_harbor_findings}
    print(f"\nSafe Harbor findings: {len(rep.safe_harbor_findings)}")
    for f in rep.safe_harbor_findings:
        print(f"   {f.rule_id:>4}  {f.category}: column '{f.column}'")
    assert "S9" in cats, "member_id should be flagged S9 (health-plan beneficiary)"
    assert "S10" in cats, "account should be flagged S10 (account number)"

    overall(rep)
    print("\nScrub list: drop member_id (S9) and account (S10), coarsen zip/age,")
    print("then re-run. Internal keys are still direct identifiers under S9/S10.")


if __name__ == "__main__":
    main()
