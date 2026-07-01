"""Scenario 11 - Cell suppression and missing values.

A common de-identification move is *cell suppression*: blanking a quasi-identifier
value to merge small classes. deidproof treats an empty QI cell as its own value
(the empty string), so suppressing 'sex' merges the two singletons into one
class of size 2. This demo shows suppression turning a k=1 group into k>=2.
"""
from _common import dataset, rule, verdict, overall
from deidproof.core import analyze_csv, k_anonymity


def _rows(path):
    import csv
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def main() -> None:
    rule("SUPPRESSION  -  blanking a cell merges small equivalence classes")

    csv_path = dataset("12-suppressed-cells", "registry_suppressed.csv")
    rows = _rows(csv_path)
    print(f"\nDataset with two suppressed 'sex' cells: {csv_path}\n")

    # With sex present, the two blank-sex West/30-39 rows still group together.
    k_all, classes = k_anonymity(rows, ["region", "age_band", "sex"])
    print(f"k over (region, age_band, sex) = {k_all}")
    print(f"   {len(classes)} equivalence classes")
    for key, idxs in sorted(classes.items(), key=lambda kv: len(kv[1])):
        shown = tuple(v if v else "(suppressed)" for v in key)
        print(f"   {shown} -> size {len(idxs)}")

    rep = analyze_csv(
        csv_path,
        quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["diagnosis_group"],
        k=2,
        l=2,
    )
    print(f"\nk = {rep.min_k}   " + verdict("k>=2", rep.k_passed))
    print(f"l = {rep.min_l}   " + verdict("l>=2", rep.l_passed))

    assert rep.min_k >= 2, "suppression should have merged the singletons to k>=2"
    overall(rep)
    print("\nLesson: an empty QI cell is a value in its own right; suppression is")
    print("a legitimate generalization step, and deidproof measures its effect.")


if __name__ == "__main__":
    main()
