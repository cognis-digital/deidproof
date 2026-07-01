"""k-anonymity math: equivalence-class sizing, edge cases, and error paths."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import _equivalence_classes, k_anonymity  # noqa: E402


def test_single_class_all_identical():
    rows = [{"a": "x", "b": "y"}] * 5
    min_k, classes = k_anonymity(rows, ["a", "b"])
    assert min_k == 5
    assert len(classes) == 1


def test_all_singletons():
    rows = [{"a": str(i)} for i in range(6)]
    min_k, classes = k_anonymity(rows, ["a"])
    assert min_k == 1
    assert len(classes) == 6


def test_min_is_smallest_class():
    # one class of 3, one of 1 -> k = 1
    rows = [{"g": "A"}, {"g": "A"}, {"g": "A"}, {"g": "B"}]
    min_k, classes = k_anonymity(rows, ["g"])
    assert min_k == 1
    assert sorted(len(v) for v in classes.values()) == [1, 3]


def test_multi_column_key():
    rows = [
        {"z": "1", "s": "M"}, {"z": "1", "s": "M"},
        {"z": "1", "s": "F"}, {"z": "2", "s": "M"},
    ]
    min_k, classes = k_anonymity(rows, ["z", "s"])
    assert len(classes) == 3  # (1,M),(1,F),(2,M)
    assert min_k == 1


def test_whitespace_normalization_groups_together():
    # leading/trailing whitespace is stripped so "34" and " 34 " share a class
    rows = [{"age": "34"}, {"age": " 34 "}, {"age": "34"}]
    min_k, classes = k_anonymity(rows, ["age"])
    assert min_k == 3
    assert len(classes) == 1


def test_missing_key_treated_as_empty_string():
    # a row lacking the QI column is grouped under the empty-string value
    rows = [{"a": "1"}, {}, {"a": ""}]
    min_k, classes = k_anonymity(rows, ["a"])
    # {} and {"a": ""} both key to ("",) -> class of 2; {"a":"1"} -> class of 1
    assert min_k == 1
    assert sorted(len(v) for v in classes.values()) == [1, 2]


def test_case_sensitive_values():
    rows = [{"c": "Yes"}, {"c": "yes"}]
    min_k, classes = k_anonymity(rows, ["c"])
    assert min_k == 1  # values are not case-folded
    assert len(classes) == 2


def test_empty_rows_returns_zero():
    min_k, classes = k_anonymity([], ["a"])
    assert min_k == 0
    assert classes == {}


def test_empty_quasi_identifiers_raises():
    with pytest.raises(ValueError, match="non-empty"):
        k_anonymity([{"a": "1"}], [])


def test_equivalence_class_indices_preserved():
    rows = [{"g": "A"}, {"g": "B"}, {"g": "A"}]
    classes = _equivalence_classes(rows, ["g"])
    assert classes[("A",)] == [0, 2]
    assert classes[("B",)] == [1]


def test_class_index_order_is_input_order():
    rows = [{"g": "A"} for _ in range(4)]
    classes = _equivalence_classes(rows, ["g"])
    assert classes[("A",)] == [0, 1, 2, 3]


@pytest.mark.parametrize("n", [1, 2, 10, 50])
def test_k_equals_group_size_for_uniform_data(n):
    rows = [{"g": "A"} for _ in range(n)]
    min_k, _ = k_anonymity(rows, ["g"])
    assert min_k == n
