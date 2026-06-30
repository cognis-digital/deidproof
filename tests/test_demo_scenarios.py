"""Every narrated demo scenario must import and run cleanly (offline, exit 0).

These complement tests/test_demos.py (which checks CLI exit codes on the bundled
fixtures): here we drive the Python `demos/NN_name.py` scenarios directly so the
narrated walkthroughs can never silently rot.
"""
import importlib
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS = os.path.join(ROOT, "demos")
sys.path.insert(0, ROOT)
sys.path.insert(0, DEMOS)

SCENARIOS = [
    "01_privacy_officer_gate",
    "02_data_scientist_generalize",
    "03_data_steward_safe_harbor",
    "04_auditor_sarif_evidence",
    "05_l_diversity_homogeneity",
]


@pytest.mark.parametrize("name", SCENARIOS)
def test_scenario_runs(name, capsys):
    mod = importlib.import_module(name)
    mod.main()  # raises if the real API call or rendering fails
    out = capsys.readouterr().out
    assert "OVERALL:" in out  # each scenario renders a verdict


def test_run_all_executes(capsys):
    mod = importlib.import_module("run_all")
    mod.main()
    out = capsys.readouterr().out
    assert "All demo scenarios completed." in out
