"""Malformed / edge-case datasets and analyze_csv error paths."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import analyze_csv, analyze_rows  # noqa: E402


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_missing_file_raises_filenotfound():
    with pytest.raises(FileNotFoundError):
        analyze_csv("this-path-does-not-exist.csv", quasi_identifiers=["a"])


def test_directory_path_raises(tmp_path):
    with pytest.raises((IsADirectoryError, PermissionError, OSError)):
        analyze_csv(str(tmp_path), quasi_identifiers=["a"])


def test_empty_file_raises_value_error(tmp_path):
    p = _write(tmp_path, "empty.csv", "")
    with pytest.raises(ValueError, match="no header"):
        analyze_csv(p, quasi_identifiers=["a"])


def test_header_only_no_rows(tmp_path):
    p = _write(tmp_path, "hdr.csv", "region,age,dx\n")
    rep = analyze_csv(p, quasi_identifiers=["region"], sensitive=["dx"], k=2, l=2)
    assert rep.row_count == 0
    assert rep.min_k == 0
    assert rep.k_passed is False  # 0 < 2


def test_unknown_quasi_identifier_column(tmp_path):
    p = _write(tmp_path, "d.csv", "a,b\n1,2\n")
    with pytest.raises(ValueError, match="quasi-identifier"):
        analyze_csv(p, quasi_identifiers=["nope"])


def test_unknown_sensitive_column(tmp_path):
    p = _write(tmp_path, "d.csv", "a,b\n1,2\n")
    with pytest.raises(ValueError, match="sensitive"):
        analyze_csv(p, quasi_identifiers=["a"], sensitive=["missing"])


def test_error_message_lists_available_columns(tmp_path):
    p = _write(tmp_path, "d.csv", "alpha,beta\n1,2\n")
    with pytest.raises(ValueError) as exc:
        analyze_csv(p, quasi_identifiers=["gamma"])
    assert "alpha" in str(exc.value) and "beta" in str(exc.value)


def test_multi_char_delimiter_rejected(tmp_path):
    p = _write(tmp_path, "d.csv", "a,b\n1,2\n")
    with pytest.raises(ValueError, match="single character"):
        analyze_csv(p, quasi_identifiers=["a"], delimiter="::")


def test_empty_delimiter_rejected(tmp_path):
    p = _write(tmp_path, "d.csv", "a,b\n1,2\n")
    with pytest.raises(ValueError, match="single character"):
        analyze_csv(p, quasi_identifiers=["a"], delimiter="")


def test_semicolon_delimiter_ok(tmp_path):
    p = _write(tmp_path, "d.csv", "region;dx\nWest;A\nWest;A\n")
    rep = analyze_csv(p, quasi_identifiers=["region"], sensitive=["dx"],
                      k=2, delimiter=";")
    assert rep.row_count == 2
    assert rep.min_k == 2


def test_tab_delimiter_ok(tmp_path):
    p = _write(tmp_path, "d.tsv", "region\tdx\nWest\tA\nWest\tB\n")
    rep = analyze_csv(p, quasi_identifiers=["region"], sensitive=["dx"],
                      k=2, l=2, delimiter="\t")
    assert rep.min_k == 2 and rep.min_l == 2


def test_bom_stripped_from_header(tmp_path):
    # utf-8-sig BOM must not become part of the first column name
    p = tmp_path / "bom.csv"
    p.write_bytes(b"\xef\xbb\xbfregion,dx\nWest,A\nWest,B\n")
    rep = analyze_csv(str(p), quasi_identifiers=["region"], sensitive=["dx"], k=2)
    assert rep.min_k == 2  # "region" resolved despite the BOM


def test_ragged_rows_do_not_crash(tmp_path):
    # a short row (missing trailing field) -> DictReader fills None; must not crash
    p = _write(tmp_path, "ragged.csv", "a,b,c\n1,2,3\n4,5\n")
    rep = analyze_csv(p, quasi_identifiers=["a"])
    assert rep.row_count == 2


def test_extra_fields_row_does_not_crash(tmp_path):
    # a long row -> DictReader puts extras under a None key; must not crash
    p = _write(tmp_path, "long.csv", "a,b\n1,2\n3,4,5,6\n")
    rep = analyze_csv(p, quasi_identifiers=["a"])
    assert rep.row_count == 2


def test_duplicate_header_names(tmp_path):
    # duplicate columns: csv keeps the last; analysis must still run
    p = _write(tmp_path, "dup.csv", "a,a\n1,2\n3,4\n")
    rep = analyze_csv(p, quasi_identifiers=["a"])
    assert rep.row_count == 2


def test_unicode_values(tmp_path):
    p = _write(tmp_path, "u.csv", "region,dx\nÎle,Café\nÎle,Thé\n")
    rep = analyze_csv(p, quasi_identifiers=["region"], sensitive=["dx"], k=2, l=2)
    assert rep.min_k == 2 and rep.min_l == 2


def test_analyze_rows_no_checks_passes():
    rep = analyze_rows([{"a": "1"}], ["a"])
    assert rep.passed is True
    assert rep.min_k is None  # no QIs requested


def test_analyze_rows_safe_harbor_only():
    rep = analyze_rows(
        [{"email": "a@b.co"}], ["email"], safe_harbor=True
    )
    assert rep.safe_harbor_passed is False
    assert rep.passed is False
