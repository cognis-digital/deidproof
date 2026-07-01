"""CLI behavior: exit codes, argument validation, delimiter resolution, formats."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.cli import _resolve_delimiter, _split_cols, main  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _demo(*parts):
    return os.path.join(ROOT, "demos", *parts)


CLEAN = _demo("02-clean", "clean_export.csv")
LEAK = _demo("04-safe-harbor-leak", "ed_export.csv")


# ---- exit codes ------------------------------------------------------------

def test_exit_0_on_clean(capsys):
    rc = main(["check", CLEAN, "--qi", "region,age_band,sex",
               "--sensitive", "diagnosis_group", "-k", "2", "-l", "2"])
    capsys.readouterr()
    assert rc == 0


def test_exit_2_on_fail(capsys):
    rc = main(["check", LEAK, "--qi", "zip,age,sex",
               "--sensitive", "chief_complaint", "-k", "2", "-l", "2"])
    capsys.readouterr()
    assert rc == 2


def test_exit_1_missing_file(capsys):
    rc = main(["check", "nope.csv", "--qi", "a"])
    assert rc == 1
    assert "error:" in capsys.readouterr().err


def test_exit_1_unknown_column(capsys):
    rc = main(["check", CLEAN, "--qi", "not_a_col"])
    assert rc == 1
    assert "error:" in capsys.readouterr().err


def test_exit_1_multichar_delimiter(capsys):
    rc = main(["check", CLEAN, "--qi", "region", "--delimiter", "::"])
    assert rc == 1
    assert "single character" in capsys.readouterr().err


def test_exit_1_negative_k(capsys):
    rc = main(["check", CLEAN, "--qi", "region", "-k", "-1"])
    assert rc == 1
    assert "positive" in capsys.readouterr().err


def test_exit_1_negative_l(capsys):
    rc = main(["check", CLEAN, "--qi", "region", "--sensitive", "diagnosis_group",
               "-l", "-2"])
    assert rc == 1
    assert "positive" in capsys.readouterr().err


def test_exit_1_l_without_sensitive(capsys):
    rc = main(["check", CLEAN, "--qi", "region", "-l", "2"])
    assert rc == 1
    assert "sensitive" in capsys.readouterr().err


def test_exit_1_k_without_qi_does_not_pass_silently(capsys):
    # gating on -k with no QIs must be an error, never a silent PASS
    rc = main(["check", CLEAN, "-k", "5"])
    assert rc == 1
    assert "quasi-identifier" in capsys.readouterr().err


def test_no_command_prints_help(capsys):
    rc = main([])
    assert rc == 1
    out = capsys.readouterr().out
    assert "deidproof" in out


# ---- output formats --------------------------------------------------------

def test_json_format_is_valid_json(capsys):
    main(["check", CLEAN, "--qi", "region,age_band,sex",
          "--sensitive", "diagnosis_group", "-k", "2", "-l", "2",
          "--format", "json"])
    doc = json.loads(capsys.readouterr().out)
    assert doc["tool"] == "deidproof"
    assert doc["passed"] is True


def test_sarif_format_is_valid_json(capsys):
    main(["check", LEAK, "--qi", "zip,age,sex",
          "--sensitive", "chief_complaint", "-k", "2", "-l", "2",
          "--format", "sarif"])
    doc = json.loads(capsys.readouterr().out)
    assert doc["version"] == "2.1.0"


def test_table_format_has_overall(capsys):
    main(["check", CLEAN, "--qi", "region,age_band,sex",
          "--sensitive", "diagnosis_group", "-k", "2", "-l", "2"])
    out = capsys.readouterr().out
    assert "OVERALL: PASS" in out
    assert "k-anonymity" in out


def test_table_shows_fail_and_findings(capsys):
    main(["check", LEAK, "--qi", "zip,age,sex",
          "--sensitive", "chief_complaint", "-k", "2", "-l", "2"])
    out = capsys.readouterr().out
    assert "OVERALL: FAIL" in out
    assert "Safe Harbor" in out


def test_no_safe_harbor_flag_l_fails(capsys):
    # hiv_cohort is k>=2 but has a homogeneous class -> fails l>=2 even with
    # the Safe Harbor scan disabled.
    rc = main(["check", _demo("06-l-diversity-gap", "hiv_cohort.csv"),
               "--qi", "zip3,age_band,sex", "--sensitive", "hiv_status",
               "-k", "2", "-l", "2", "--no-safe-harbor"])
    capsys.readouterr()
    assert rc == 2


def test_no_safe_harbor_flag_passes_on_k_only(capsys):
    # with only -k (k>=2 holds) and Safe Harbor disabled, it PASSES.
    rc = main(["check", _demo("06-l-diversity-gap", "hiv_cohort.csv"),
               "--qi", "zip3,age_band,sex", "-k", "2", "--no-safe-harbor"])
    capsys.readouterr()
    assert rc == 0


def test_version_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


# ---- helpers ---------------------------------------------------------------

def test_split_cols():
    assert _split_cols("a, b ,c") == ["a", "b", "c"]
    assert _split_cols("") == []
    assert _split_cols(None) == []
    assert _split_cols(",,") == []


def test_resolve_delimiter_tab_token():
    assert _resolve_delimiter(r"\t") == "\t"
    assert _resolve_delimiter("tab") == "\t"
    assert _resolve_delimiter(",") == ","
    assert _resolve_delimiter(";") == ";"


def test_qi_alias(capsys):
    # --quasi-identifiers and --qi are the same option
    rc = main(["check", CLEAN, "--quasi-identifiers", "region", "-k", "1"])
    capsys.readouterr()
    assert rc == 0
