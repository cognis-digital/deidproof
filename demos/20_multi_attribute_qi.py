"""Scenario 20 - Multi-attribute quasi-identifiers and joint sensitivity.

Re-identification risk is a property of the *combination* of quasi-identifiers,
not any single column, and l-diversity can be evaluated over a *tuple* of
sensitive attributes. This demo runs k over three QIs and l over two combined
sensitive columns on the clinical-trial listing, using the real API directly.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv, l_diversity


def _rows(path):
    import csv
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def main() -> None:
    rule("MULTI-ATTRIBUTE  -  joint QIs and combined sensitive attributes")

    csv = dataset("07-clinical-trial", "trial_subjects.csv")
    rows = _rows(csv)
    print(f"\nClinical-trial listing: {csv}  ({len(rows)} rows)\n")

    # k over a 3-column QI combination.
    rep = analyze_csv(
        csv,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["arm", "adverse_event"],  # combined sensitive tuple
        k=2,
        l=2,
        safe_harbor=False,
    )
    print(f"k over (zip, age, sex)                 = {rep.min_k}   "
          + verdict("k>=2", rep.k_passed))
    print(f"l over (arm, adverse_event) combined   = {rep.min_l}   "
          + verdict("l>=2", rep.l_passed))

    # Show that l over the *tuple* differs from l over a single attribute.
    l_single, _ = l_diversity(rows, ["zip", "age", "sex"], ["adverse_event"])
    l_tuple, _ = l_diversity(rows, ["zip", "age", "sex"], ["arm", "adverse_event"])
    print(f"\nl over adverse_event alone   = {l_single}")
    print(f"l over (arm, adverse_event)  = {l_tuple}")
    assert l_tuple >= l_single, "adding a sensitive dimension cannot lower distinctness"

    overall(rep)
    print("\nLesson: define the QI set as everything an adversary could join on,")
    print("and evaluate l over the sensitive columns that matter together.")


if __name__ == "__main__":
    main()
