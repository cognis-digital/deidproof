"""SARIF 2.1.0 edge cases: rule catalog, k/l results, locations, clean logs."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import Report, analyze_rows  # noqa: E402
from deidproof.sarif import (  # noqa: E402
    SARIF_SCHEMA,
    SARIF_VERSION,
    report_to_sarif,
)


def test_empty_report_valid_shell():
    log = report_to_sarif(Report())
    assert log["version"] == SARIF_VERSION
    assert log["$schema"] == SARIF_SCHEMA
    assert log["runs"][0]["results"] == []


def test_rule_catalog_is_20():
    log = report_to_sarif(Report())
    rules = log["runs"][0]["tool"]["driver"]["rules"]
    assert len(rules) == 20  # S1..S18 + DEID-K + DEID-L
    ids = {r["id"] for r in rules}
    assert {"S1", "S18", "DEID-K", "DEID-L"} <= ids


def test_all_rules_error_level():
    rules = report_to_sarif(Report())["runs"][0]["tool"]["driver"]["rules"]
    assert all(r["defaultConfiguration"]["level"] == "error" for r in rules)


def test_k_failure_emits_deid_k():
    rep = analyze_rows(
        [{"z": "1"}, {"z": "2"}], ["z"], quasi_identifiers=["z"], k=2
    )
    assert rep.k_passed is False
    log = report_to_sarif(rep, dataset="d.csv")
    ids = {r["ruleId"] for r in log["runs"][0]["results"]}
    assert "DEID-K" in ids


def test_l_failure_emits_deid_l():
    rep = analyze_rows(
        [{"z": "1", "d": "A"}, {"z": "1", "d": "A"}],
        ["z", "d"], quasi_identifiers=["z"], sensitive=["d"], l=2,
    )
    assert rep.l_passed is False
    log = report_to_sarif(rep, dataset="d.csv")
    ids = {r["ruleId"] for r in log["runs"][0]["results"]}
    assert "DEID-L" in ids


def test_k_pass_no_deid_k_result():
    rep = analyze_rows(
        [{"z": "1"}, {"z": "1"}], ["z"], quasi_identifiers=["z"], k=2
    )
    assert rep.k_passed is True
    ids = {r["ruleId"] for r in report_to_sarif(rep)["runs"][0]["results"]}
    assert "DEID-K" not in ids


def test_safe_harbor_finding_has_logical_location():
    rep = analyze_rows([{"email": "a@b.co"}], ["email"])
    res = report_to_sarif(rep, dataset="d.csv")["runs"][0]["results"]
    s6 = [r for r in res if r["ruleId"] == "S6"][0]
    ll = s6["locations"][0]["logicalLocations"][0]
    assert ll["name"] == "email"


def test_windows_path_normalized_to_forward_slashes():
    rep = analyze_rows([{"email": "a@b.co"}], ["email"])
    res = report_to_sarif(rep, dataset=r"C:\data\export.csv")["runs"][0]["results"]
    uri = res[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
    assert "\\" not in uri
    assert uri == "C:/data/export.csv"


def test_message_includes_match_count():
    rep = analyze_rows(
        [{"email": "a@b.co"}, {"email": "c@d.co"}], ["email"]
    )
    res = report_to_sarif(rep)["runs"][0]["results"]
    s6 = [r for r in res if r["ruleId"] == "S6"][0]
    assert "hit(s)" in s6["message"]["text"]


def test_result_count_matches_findings_plus_thresholds():
    rep = analyze_rows(
        [{"email": "a@b.co", "z": "1"}, {"email": "c@d.co", "z": "2"}],
        ["email", "z"], quasi_identifiers=["z"], k=2,
    )
    # one S6 finding + one DEID-K failure = 2 results
    res = report_to_sarif(rep)["runs"][0]["results"]
    assert len(res) == 2
