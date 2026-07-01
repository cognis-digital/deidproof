"""Scenario 16 - The full Safe Harbor catalog, one row at a time.

45 CFR 164.514(b)(2) enumerates 18 identifier categories. This demo builds a
tiny synthetic row that trips as many value-level detectors as possible (SSN,
email, URL, IP, phone, full date, age>89) plus header-level detectors, and prints
the catalog of rule ids deidproof recognizes -- a reference card for reviewers.
"""
from _common import rule, overall
from deidproof.core import (
    SAFE_HARBOR_IDENTIFIERS,
    analyze_rows,
    safe_harbor_scan,
)


def main() -> None:
    rule("REFERENCE  -  the 18 HIPAA Safe Harbor categories (S1-S18)")

    print("\nCatalog of identifier categories deidproof knows about:\n")
    for ident in SAFE_HARBOR_IDENTIFIERS:
        print(f"   {ident['id']:>4}  {ident['category']}")

    # One row engineered to trip many value-level detectors at once.
    row = {
        "patient_name": "Jane Roe",
        "ssn": "111-22-3333",
        "email": "jane@example.org",
        "site_url": "https://portal.example.org/x",
        "ip": "198.51.100.7",
        "phone": "(202) 555-0111",
        "admit_date": "03/14/2025",
        "age": "97",
        "dx": "Asthma",
    }
    columns = list(row.keys())
    findings = safe_harbor_scan([row], columns)
    hit_ids = sorted({f.rule_id for f in findings})
    print(f"\nCategories tripped by one engineered row: {hit_ids}")

    # Value-level detectors we expect regardless of header names.
    for expected in ("S3", "S4", "S6", "S7", "S14", "S15"):
        assert expected in hit_ids, f"{expected} value detector should fire"

    rep = analyze_rows([row], columns)
    print(f"\nSafe Harbor passed: {rep.safe_harbor_passed} "
          f"(expected False -- this row is a worst case)")
    assert rep.safe_harbor_passed is False

    overall(rep)
    print("\nUse this as a reference: every S# maps to a category in the rule,")
    print("and detection fires on column names AND cell content.")


if __name__ == "__main__":
    main()
