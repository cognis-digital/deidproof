"""Command-line interface for DEIDPROOF.

Examples
--------
  # k-anonymity + l-diversity + Safe Harbor on a CSV export
  deidproof check export.csv \\
      --quasi-identifiers zip,age,sex \\
      --sensitive diagnosis \\
      -k 5 -l 2

  # JSON for CI pipelines (exits non-zero if de-identification fails)
  deidproof check export.csv --qi zip,age --sensitive dx -k 5 --format json

  # Safe Harbor scan only
  deidproof check export.csv --no-k --format table

Exit codes:
  0  dataset passes all requested checks
  2  dataset FAILS a privacy check (k/l threshold or Safe Harbor finding)
  1  usage / runtime error
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .core import TOOL_NAME, TOOL_VERSION, Report, analyze_csv


def _split_cols(value: Optional[str]) -> List[str]:
    if not value:
        return []
    return [c.strip() for c in value.split(",") if c.strip()]


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog=TOOL_NAME,
        description=(
            "DEIDPROOF - prove a de-identified healthcare export actually is. "
            "Computes k-anonymity, l-diversity, and HIPAA Safe Harbor checks."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}"
    )
    sub = p.add_subparsers(dest="command", metavar="COMMAND")

    c = sub.add_parser(
        "check",
        help="Analyze a CSV dataset for re-identification risk.",
        description="Analyze a CSV dataset for re-identification risk.",
    )
    c.add_argument("dataset", help="Path to the CSV file to analyze.")
    c.add_argument(
        "--quasi-identifiers",
        "--qi",
        dest="quasi_identifiers",
        default="",
        help="Comma-separated quasi-identifier columns (e.g. zip,age,sex).",
    )
    c.add_argument(
        "--sensitive",
        dest="sensitive",
        default="",
        help="Comma-separated sensitive columns (e.g. diagnosis).",
    )
    c.add_argument(
        "-k",
        dest="k",
        type=int,
        default=None,
        help="Required minimum k for k-anonymity (smallest equivalence class).",
    )
    c.add_argument(
        "-l",
        dest="l",
        type=int,
        default=None,
        help="Required minimum l for l-diversity (distinct sensitive values).",
    )
    c.add_argument(
        "--no-safe-harbor",
        dest="safe_harbor",
        action="store_false",
        help="Skip the HIPAA Safe Harbor identifier scan.",
    )
    c.add_argument(
        "--delimiter", default=",", help="CSV delimiter (default: ',')."
    )
    c.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table).",
    )
    return p


def _render_table(rep: Report) -> str:
    lines: List[str] = []
    lines.append(f"DEIDPROOF {rep.version} - de-identification report")
    lines.append("=" * 56)
    lines.append(f"Rows analyzed        : {rep.row_count}")
    if rep.quasi_identifiers:
        lines.append(f"Quasi-identifiers    : {', '.join(rep.quasi_identifiers)}")
    if rep.sensitive:
        lines.append(f"Sensitive attributes : {', '.join(rep.sensitive)}")
    lines.append("")

    # k-anonymity
    if rep.min_k is not None:
        status = ""
        if rep.k_passed is not None:
            status = "  [PASS]" if rep.k_passed else f"  [FAIL < {rep.k_threshold}]"
        lines.append(f"k-anonymity  : k = {rep.min_k}{status}")
        if rep.smallest_classes:
            lines.append("  Smallest equivalence classes:")
            for cls in rep.smallest_classes:
                vals = ", ".join(f"{k}={v}" for k, v in cls["values"].items())
                lines.append(f"    size {cls['size']:>4}  ({vals})")

    # l-diversity
    if rep.min_l is not None:
        status = ""
        if rep.l_passed is not None:
            status = "  [PASS]" if rep.l_passed else f"  [FAIL < {rep.l_threshold}]"
        lines.append(f"l-diversity  : l = {rep.min_l}{status}")

    # Safe Harbor
    lines.append("")
    if not rep.safe_harbor_findings:
        lines.append("Safe Harbor  : no identifier categories detected  [PASS]")
    else:
        lines.append(
            f"Safe Harbor  : {len(rep.safe_harbor_findings)} finding(s)  [FAIL]"
        )
        for f in rep.safe_harbor_findings:
            samples = (
                f" (e.g. rows {f.sample_rows})" if f.sample_rows else ""
            )
            lines.append(
                f"    {f.rule_id} {f.category}: column '{f.column}' "
                f"- {f.reason}; {f.match_count} hit(s){samples}"
            )

    lines.append("")
    lines.append("OVERALL: " + ("PASS" if rep.passed else "FAIL"))
    return "\n".join(lines)


def _report_to_json(rep: Report) -> str:
    d = rep.to_dict()
    # SafeHarborFinding objects are already dict-ified by asdict in to_dict.
    return json.dumps(d, indent=2)


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command != "check":
        parser.print_help()
        return 1

    qi = _split_cols(args.quasi_identifiers)
    sensitive = _split_cols(args.sensitive)

    try:
        rep = analyze_csv(
            args.dataset,
            quasi_identifiers=qi,
            sensitive=sensitive,
            k=args.k,
            l=args.l,
            safe_harbor=args.safe_harbor,
            delimiter=args.delimiter,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(_report_to_json(rep))
    else:
        print(_render_table(rep))

    # Exit non-zero when de-identification fails (CI gate).
    return 0 if rep.passed else 2


if __name__ == "__main__":
    sys.exit(main())
