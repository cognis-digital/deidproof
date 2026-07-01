"""Scenario 10 - Clinical NLP / free-text review.

The hardest leaks hide in free-text notes: a phone number, an email, a URL, an
IP, or an SSN buried in a sentence. deidproof scans cell *contents*, not just
column names, so it finds identifiers even when the column is called "note".
This demo runs the content scanner over a notes table and itemizes every hit.
"""
from _common import dataset, rule, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("CLINICAL NLP  -  identifiers hiding inside free-text notes")

    csv = dataset("11-free-text-notes", "clinical_notes.csv")
    print("\nScanning free-text clinical notes for embedded identifiers:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["age_band", "sex"],
        sensitive=["visit_reason"],
        k=2,
    )
    print(f"Rows analyzed : {rep.row_count}")
    print(f"Safe Harbor findings in free text: {len(rep.safe_harbor_findings)}\n")
    for f in rep.safe_harbor_findings:
        rows = f" (rows {f.sample_rows})" if f.sample_rows else ""
        print(f"   {f.rule_id:>4}  {f.category}: '{f.column}' x{f.match_count}{rows}")

    cats = {f.rule_id for f in rep.safe_harbor_findings}
    for expected in ("S4", "S6", "S7", "S14", "S15"):
        assert expected in cats, f"{expected} should be found in the note text"

    overall(rep)
    print("\nLesson: header-only scrubbing is not enough. A phone number (S4),")
    print("email (S6), SSN (S7), URL (S14) or IP (S15) in a note is still PHI.")


if __name__ == "__main__":
    main()
