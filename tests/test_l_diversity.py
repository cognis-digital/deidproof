"""l-diversity math: distinct sensitive values per class, tuples, error paths."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import l_diversity  # noqa: E402


def test_homogeneous_class_has_l_one():
    rows = [{"z": "1", "d": "A"}, {"z": "1", "d": "A"}]
    min_l, per = l_diversity(rows, ["z"], ["d"])
    assert min_l == 1
    assert per[("1",)] == 1


def test_diverse_class():
    rows = [{"z": "1", "d": "A"}, {"z": "1", "d": "B"}, {"z": "1", "d": "C"}]
    min_l, per = l_diversity(rows, ["z"], ["d"])
    assert min_l == 3
    assert per[("1",)] == 3


def test_min_across_classes():
    rows = [
        {"z": "1", "d": "A"}, {"z": "1", "d": "B"},   # class 1 -> l=2
        {"z": "2", "d": "C"}, {"z": "2", "d": "C"},   # class 2 -> l=1
    ]
    min_l, per = l_diversity(rows, ["z"], ["d"])
    assert min_l == 1
    assert sorted(per.values()) == [1, 2]


def test_combined_sensitive_tuple():
    # distinctness over a (dx, drug) tuple, not either column alone
    rows = [
        {"z": "1", "dx": "A", "drug": "x"},
        {"z": "1", "dx": "A", "drug": "y"},
    ]
    min_l, per = l_diversity(rows, ["z"], ["dx", "drug"])
    # dx alone is homogeneous (A,A) but (dx,drug) tuples differ -> l=2
    assert min_l == 2
    assert per[("1",)] == 2


def test_tuple_never_lower_than_single_attr():
    rows = [
        {"z": "1", "dx": "A", "drug": "x"},
        {"z": "1", "dx": "B", "drug": "x"},
        {"z": "1", "dx": "A", "drug": "x"},
    ]
    l_single, _ = l_diversity(rows, ["z"], ["dx"])
    l_tuple, _ = l_diversity(rows, ["z"], ["dx", "drug"])
    assert l_tuple >= l_single


def test_whitespace_stripped_in_sensitive():
    rows = [{"z": "1", "d": "A"}, {"z": "1", "d": " A "}]
    min_l, per = l_diversity(rows, ["z"], ["d"])
    assert min_l == 1  # "A" and " A " collapse to one distinct value


def test_missing_sensitive_value_is_empty_string():
    rows = [{"z": "1", "d": "A"}, {"z": "1"}]  # second row missing d
    min_l, per = l_diversity(rows, ["z"], ["d"])
    assert min_l == 2  # {"A", ""} -> 2 distinct


def test_no_quasi_identifiers_single_global_class():
    rows = [{"d": "A"}, {"d": "B"}, {"d": "B"}]
    min_l, per = l_diversity(rows, [], ["d"])
    assert list(per.keys()) == [()]
    assert min_l == 2  # {A, B}


def test_empty_sensitive_raises():
    with pytest.raises(ValueError, match="non-empty"):
        l_diversity([{"z": "1"}], ["z"], [])


def test_empty_rows_returns_zero():
    min_l, per = l_diversity([], ["z"], ["d"])
    assert min_l == 0
    assert per == {}


@pytest.mark.parametrize("distinct", [1, 2, 3, 5])
def test_l_equals_distinct_count(distinct):
    rows = [{"z": "1", "d": chr(65 + i)} for i in range(distinct)]
    min_l, _ = l_diversity(rows, ["z"], ["d"])
    assert min_l == distinct
