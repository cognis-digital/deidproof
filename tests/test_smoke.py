"""Smoke tests for DEIDPROOF - import core, run on the demo, assert real behavior."""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof import (  # noqa: E402
    TOOL_NAME,
    TOOL_VERSION,
    analyze_csv,
    analyze_rows,
    k_anonymity,
    l_diversity,
    safe_harbor_scan,
)
from deidproof.cli import main  # noqa: E402

DEMO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "demos",
    "01-basic",
    "patients.csv",
)


def test_metadata():
    assert TOOL_NAME == "deidproof"
    assert TOOL_VERSION.count(".") == 2


def test_k_anonymity_singletons():
    # The demo's (zip,age,sex) makes every patient unique -> k = 1.
    rep = analyze_csv(DEMO, quasi_identifiers=["zip", "age", "sex"], k=2)
    assert rep.row_count == 8
    assert rep.min_k == 1
    assert rep.k_passed is False


def test_k_anonymity_grouped():
    # Drop sex: (zip,age) pairs each appear twice -> k = 2.
    rep = analyze_csv(DEMO, quasi_identifiers=["zip", "age"], k=2)
    # zip 60601 has ages 92 and 41 -> those are singletons -> k stays 1.
    assert rep.min_k == 1
    # zip,age alone: 90210/34 appears twice, 10001/58 twice, 30303/27 twice.
    min_k, classes = k_anonymity(
        [
            {"zip": "90210", "age": "34"},
            {"zip": "90210", "age": "34"},
            {"zip": "10001", "age": "58"},
            {"zip": "10001", "age": "58"},
        ],
        ["zip", "age"],
    )
    assert min_k == 2
    assert len(classes) == 2


def test_l_diversity():
    min_l, per_class = l_diversity(
        [
            {"zip": "1", "dx": "A"},
            {"zip": "1", "dx": "B"},
            {"zip": "2", "dx": "C"},
            {"zip": "2", "dx": "C"},
        ],
        ["zip"],
        ["dx"],
    )
    # class zip=1 has {A,B} -> 2 distinct; zip=2 has {C} -> 1 distinct.
    assert min_l == 1
    assert sorted(per_class.values()) == [1, 2]


def test_safe_harbor_detects_identifiers():
    rep = analyze_csv(DEMO, quasi_identifiers=["zip", "age", "sex"])
    cats = {f.rule_id for f in rep.safe_harbor_findings}
    assert "S1" in cats  # name (by header)
    assert "S6" in cats  # email (by header + value)
    assert "S7" in cats  # ssn (by header + value)
    assert rep.safe_harbor_passed is False


def test_safe_harbor_age_over_89():
    # age 92 must be flagged as S3 (dates / age > 89) by value content.
    findings = safe_harbor_scan(
        [{"years": "92"}, {"years": "40"}], ["years"]
    )
    s3 = [f for f in findings if f.rule_id == "S3"]
    assert s3, "age > 89 should produce an S3 finding"
    assert s3[0].match_count == 1


def test_clean_dataset_passes():
    rows = [
        {"region": "West", "age_band": "30-39", "dx": "A"},
        {"region": "West", "age_band": "30-39", "dx": "B"},
        {"region": "West", "age_band": "30-39", "dx": "A"},
        {"region": "East", "age_band": "40-49", "dx": "C"},
        {"region": "East", "age_band": "40-49", "dx": "B"},
        {"region": "East", "age_band": "40-49", "dx": "C"},
    ]
    rep = analyze_rows(
        rows,
        columns=["region", "age_band", "dx"],
        quasi_identifiers=["region", "age_band"],
        sensitive=["dx"],
        k=3,
        l=2,
    )
    assert rep.min_k == 3
    assert rep.k_passed is True
    assert rep.min_l == 2
    assert rep.l_passed is True
    assert rep.safe_harbor_passed is True
    assert rep.passed is True


def test_missing_column_raises():
    with pytest.raises(ValueError):
        analyze_csv(DEMO, quasi_identifiers=["nonexistent_col"])


def test_cli_exit_code_fail():
    rc = main(
        [
            "check",
            DEMO,
            "--qi",
            "zip,age,sex",
            "--sensitive",
            "diagnosis",
            "-k",
            "2",
            "-l",
            "2",
            "--format",
            "json",
        ]
    )
    assert rc == 2  # de-identification fails -> non-zero for CI gate


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert TOOL_VERSION in out


# ---------------------------------------------------------------------------
# Hardening tests — bad input / edge cases
# ---------------------------------------------------------------------------


def test_cli_missing_file_exits_1(capsys):
    """Requesting a non-existent CSV must exit 1 with a clear stderr message."""
    rc = main(["check", "/no/such/file.csv"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "error:" in err


def test_cli_multichar_delimiter_exits_1(capsys):
    """A multi-character delimiter is not a valid CSV separator; must exit 1."""
    rc = main(["check", DEMO, "--delimiter", "TAB"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "delimiter" in err.lower()


def test_cli_negative_k_exits_1(capsys):
    """Negative k is semantically invalid; must exit 1 with a clear message."""
    rc = main(["check", DEMO, "-k", "-3"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "error:" in err


def test_cli_zero_l_exits_1(capsys):
    """l=0 is semantically invalid; must exit 1 with a clear message."""
    rc = main(["check", DEMO, "--sensitive", "diagnosis", "-l", "0"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "error:" in err


def test_analyze_csv_multichar_delimiter_raises():
    """analyze_csv must raise ValueError for a multi-character delimiter."""
    with pytest.raises(ValueError, match="delimiter"):
        analyze_csv(DEMO, delimiter="||")


def test_analyze_csv_non_utf8_raises():
    """analyze_csv must propagate UnicodeDecodeError for non-UTF-8 files."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".csv", delete=False) as fh:
        fh.write(b"name,age\nJos\xe9,30\n")  # Latin-1 byte in UTF-8 context
        fpath = fh.name
    try:
        with pytest.raises(UnicodeDecodeError):
            analyze_csv(fpath)
    finally:
        os.unlink(fpath)


def test_mcp_server_importable():
    """mcp_server must import without error (broken imports must not survive)."""
    import importlib
    mod = importlib.import_module("deidproof.mcp_server")
    assert callable(mod.serve)
