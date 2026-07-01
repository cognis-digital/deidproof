"""analyze_rows orchestration: pass/fail composition, smallest_classes, thresholds."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import Report, analyze_rows  # noqa: E402


def _clean_rows(n_per_class=3):
    rows = []
    for region in ("West", "East"):
        for _ in range(n_per_class):
            rows.append({"region": region, "dx": "A"})
        rows.append({"region": region, "dx": "B"})
    return rows


def test_overall_pass_requires_all_checks():
    rows = _clean_rows()
    rep = analyze_rows(rows, ["region", "dx"],
                       quasi_identifiers=["region"], sensitive=["dx"],
                       k=2, l=2)
    assert rep.k_passed and rep.l_passed and rep.safe_harbor_passed
    assert rep.passed is True


def test_overall_fail_if_k_fails():
    rows = [{"region": "West", "dx": "A"}, {"region": "East", "dx": "B"}]
    rep = analyze_rows(rows, ["region", "dx"],
                       quasi_identifiers=["region"], k=2)
    assert rep.k_passed is False
    assert rep.passed is False


def test_overall_fail_if_l_fails():
    rows = [{"region": "West", "dx": "A"}, {"region": "West", "dx": "A"}]
    rep = analyze_rows(rows, ["region", "dx"],
                       quasi_identifiers=["region"], sensitive=["dx"],
                       k=2, l=2)
    assert rep.k_passed is True
    assert rep.l_passed is False
    assert rep.passed is False


def test_overall_fail_if_safe_harbor_fails():
    rows = [{"region": "West", "email": "a@b.co"},
            {"region": "West", "email": "c@d.co"}]
    rep = analyze_rows(rows, ["region", "email"],
                       quasi_identifiers=["region"], k=2)
    assert rep.k_passed is True
    assert rep.safe_harbor_passed is False
    assert rep.passed is False


def test_thresholds_none_do_not_fail():
    # min_k computed but no threshold requested -> k_passed stays None, passes
    rows = [{"region": "West"}, {"region": "East"}]
    rep = analyze_rows(rows, ["region"], quasi_identifiers=["region"])
    assert rep.min_k == 1
    assert rep.k_passed is None
    assert rep.passed is True


def test_smallest_classes_sorted_ascending():
    rows = (
        [{"g": "A"}] * 1 + [{"g": "B"}] * 2 + [{"g": "C"}] * 3 + [{"g": "D"}] * 4
    )
    rep = analyze_rows(rows, ["g"], quasi_identifiers=["g"], k=2)
    sizes = [c["size"] for c in rep.smallest_classes]
    assert sizes == sorted(sizes)
    assert sizes[0] == 1


def test_smallest_classes_capped_at_five():
    rows = [{"g": str(i)} for i in range(20)]
    rep = analyze_rows(rows, ["g"], quasi_identifiers=["g"], k=2)
    assert len(rep.smallest_classes) <= 5


def test_smallest_class_values_map_to_qi():
    rows = [{"z": "1", "s": "M"}, {"z": "1", "s": "M"}]
    rep = analyze_rows(rows, ["z", "s"], quasi_identifiers=["z", "s"], k=2)
    cls = rep.smallest_classes[0]
    assert cls["values"] == {"z": "1", "s": "M"}
    assert cls["size"] == 2


def test_report_to_dict_is_serializable():
    import json
    rep = analyze_rows([{"email": "a@b.co"}], ["email"])
    d = rep.to_dict()
    # SafeHarborFinding must be dict-ified so json.dumps works
    json.dumps(d)
    assert d["tool"] == "deidproof"
    assert isinstance(d["safe_harbor_findings"], list)


def test_report_defaults():
    r = Report()
    assert r.passed is True
    assert r.safe_harbor_passed is True
    assert r.row_count == 0


def test_no_qi_no_k_computed():
    rep = analyze_rows([{"a": "1"}], ["a"], sensitive=["a"], l=2)
    # without QIs, l-diversity is not evaluated in analyze_rows
    assert rep.min_k is None
    assert rep.min_l is None
