"""Tests for the SARIF 2.1.0 exporter."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import analyze_csv  # noqa: E402
from deidproof.sarif import SARIF_VERSION, report_to_sarif  # noqa: E402
from deidproof.cli import main  # noqa: E402

DEMO = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "demos",
    "01-basic",
    "patients.csv",
)


def _build():
    rep = analyze_csv(
        DEMO,
        quasi_identifiers=["zip", "age", "sex"],
        sensitive=["diagnosis"],
        k=2,
        l=2,
    )
    return report_to_sarif(rep, dataset="patients.csv")


def test_sarif_top_level_shape():
    log = _build()
    assert log["version"] == SARIF_VERSION == "2.1.0"
    assert log["$schema"].endswith("sarif-schema-2.1.0.json")
    assert isinstance(log["runs"], list) and len(log["runs"]) == 1


def test_sarif_driver_and_rules():
    run = _build()["runs"][0]
    driver = run["tool"]["driver"]
    assert driver["name"] == "deidproof"
    rule_ids = {r["id"] for r in driver["rules"]}
    # 18 Safe Harbor categories + the two threshold rules.
    assert "S1" in rule_ids and "S18" in rule_ids
    assert "DEID-K" in rule_ids and "DEID-L" in rule_ids
    assert len(driver["rules"]) == 20


def test_sarif_results_include_k_and_l_failures():
    run = _build()["runs"][0]
    ids = {res["ruleId"] for res in run["results"]}
    # The demo fails k and l and leaks identifiers.
    assert "DEID-K" in ids
    assert "DEID-L" in ids
    assert "S1" in ids  # name
    assert "S7" in ids  # ssn
    for res in run["results"]:
        assert res["level"] == "error"
        uri = res["locations"][0]["physicalLocation"]["artifactLocation"]["uri"]
        assert uri == "patients.csv"


def test_sarif_clean_dataset_has_no_results(tmp_path):
    p = tmp_path / "clean.csv"
    p.write_text(
        "region,age_band,sex,dx\n"
        "West,30-39,F,A\nWest,30-39,F,B\n"
        "West,30-39,M,A\nWest,30-39,M,B\n",
        encoding="utf-8",
    )
    rep = analyze_csv(
        str(p),
        quasi_identifiers=["region", "age_band", "sex"],
        sensitive=["dx"],
        k=2,
        l=2,
    )
    log = report_to_sarif(rep, dataset=str(p))
    assert log["runs"][0]["results"] == []


def test_cli_sarif_output(capsys):
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
            "sarif",
        ]
    )
    assert rc == 2  # still fails the privacy gate
    out = capsys.readouterr().out
    doc = json.loads(out)  # must be valid JSON
    assert doc["version"] == "2.1.0"
    assert doc["runs"][0]["tool"]["driver"]["name"] == "deidproof"
