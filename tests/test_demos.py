"""Integrity tests: every shipped demo must actually run and produce its
documented exit code (0 = PASS, 2 = FAIL)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.cli import main  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _demo(*parts):
    return os.path.join(ROOT, "demos", *parts)


# (argv, expected_exit_code)
CASES = [
    (
        [
            "check", _demo("02-clean", "clean_export.csv"),
            "--qi", "region,age_band,sex", "--sensitive", "diagnosis_group",
            "-k", "2", "-l", "2",
        ],
        0,
    ),
    (
        [
            "check", _demo("04-safe-harbor-leak", "ed_export.csv"),
            "--qi", "zip,age,sex", "--sensitive", "chief_complaint",
            "-k", "2", "-l", "2",
        ],
        2,
    ),
    (
        [
            "check", _demo("05-generalized-pass", "registry_release.csv"),
            "--qi", "region,age_band,sex", "--sensitive", "diagnosis_group",
            "-k", "2", "-l", "2",
        ],
        0,
    ),
    (
        [
            "check", _demo("06-l-diversity-gap", "hiv_cohort.csv"),
            "--qi", "zip3,age_band,sex", "--sensitive", "hiv_status",
            "-k", "2", "-l", "2", "--no-safe-harbor",
        ],
        2,
    ),
    (
        [
            "check", _demo("07-clinical-trial", "trial_subjects.csv"),
            "--qi", "zip,age,sex", "--sensitive", "adverse_event",
            "-k", "2", "-l", "2",
        ],
        2,
    ),
    (
        [
            "check", _demo("08-claims-export", "payer_claims.csv"),
            "--qi", "zip,age,sex", "--sensitive", "icd10",
            "-k", "2", "-l", "2",
        ],
        2,
    ),
    (
        [
            "check", _demo("09-genomics-biobank", "biobank_samples.csv"),
            "--qi", "zip3,age,ancestry", "--sensitive", "ancestry",
            "-k", "2",
        ],
        2,
    ),
    (
        [
            "check", _demo("10-tsv-research-extract", "behavioral_extract.tsv"),
            "--delimiter", "\t",
            "--qi", "state,age_band,sex", "--sensitive", "diagnosis",
            "-k", "2", "-l", "2",
        ],
        0,
    ),
]


@pytest.mark.parametrize("argv,expected", CASES, ids=[c[0][1].split(os.sep)[-2] for c in CASES])
def test_demo_runs(argv, expected, capsys):
    rc = main(argv)
    capsys.readouterr()
    assert rc == expected
