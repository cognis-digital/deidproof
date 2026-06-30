"""Scenario 1 - Privacy / GRC officers.

The question a privacy officer must answer before a data release leaves the
building: "Is this export actually de-identified, and can I prove it?" deidproof
turns that judgment call into a reproducible pass/fail with a CI-grade exit code.

This demo takes one "de-identified" patient export that looks fine at a glance
and shows why it must be blocked: it is unique on (zip, age, sex), carries no
sensitive-value diversity, and still leaks direct identifiers.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("PRIVACY / GRC OFFICER  -  gate a release, prove the verdict")

    csv = dataset("01-basic", "patients.csv")
    print("\nReviewing an export queued for an external research partner:")
    print(f"   {csv}")
    print("Policy: require k >= 5 and l >= 2, and zero Safe Harbor identifiers.\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["diagnosis"],
        k=5,
        l=2,
    )

    print(f"Rows analyzed        : {rep.row_count}")
    print(f"Quasi-identifiers    : {', '.join(rep.quasi_identifiers)}")
    print(f"Sensitive attributes : {', '.join(rep.sensitive)}\n")

    print(f"k-anonymity  : k = {rep.min_k}   "
          + verdict("policy k>=5", rep.k_passed))
    print(f"l-diversity  : l = {rep.min_l}   "
          + verdict("policy l>=2", rep.l_passed))

    print("\nSmallest equivalence classes (each one is a re-id risk):")
    for cls in rep.smallest_classes[:3]:
        vals = ", ".join(f"{k}={v}" for k, v in cls["values"].items())
        print(f"   size {cls['size']}  ({vals})")

    print(f"\nSafe Harbor  : {len(rep.safe_harbor_findings)} direct-identifier "
          f"finding(s)  " + verdict("clean", rep.safe_harbor_passed))
    for f in rep.safe_harbor_findings[:4]:
        print(f"   {f.rule_id} {f.category}: column '{f.column}'")

    overall(rep)
    print("\nDecision: BLOCK. Every patient is unique on (zip,age,sex) and the")
    print("export still carries name/email/SSN. Send it back for generalization.")


if __name__ == "__main__":
    main()
