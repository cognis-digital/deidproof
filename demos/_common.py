"""Shared helpers for the deidproof demo scenarios.

Every scenario runs fully offline against the CSV/TSV fixtures bundled under
``demos/NN-*/`` and calls the *real* deidproof API (``analyze_csv``,
``analyze_rows``, ``k_anonymity``, ``l_diversity``, ``safe_harbor_scan``) — no
network, no fabricated functions, no fabricated output.
"""
from __future__ import annotations

import os
import sys

# allow `python demos/NN_name.py` from anywhere
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import Report  # noqa: E402,F401  (re-exported for demos)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS_DIR = os.path.join(REPO_ROOT, "demos")


def dataset(*parts: str) -> str:
    """Absolute path to a bundled demo fixture, e.g. dataset('01-basic', 'patients.csv')."""
    return os.path.join(DEMOS_DIR, *parts)


def rule(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def verdict(label: str, passed) -> str:
    """Render a tri-state check result (None = not evaluated)."""
    if passed is None:
        return f"{label}: (not evaluated)"
    return f"{label}: {'PASS' if passed else 'FAIL'}"


def overall(rep: "Report") -> None:
    print(f"\nOVERALL: {'PASS' if rep.passed else 'FAIL'}"
          f"   (CLI exit code would be {0 if rep.passed else 2})")
