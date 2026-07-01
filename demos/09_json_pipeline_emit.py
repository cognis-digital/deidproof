"""Scenario 9 - Platform / data-engineering pipelines.

deidproof's JSON output is stable and machine-readable, so a pipeline can parse
the verdict, count findings, and route the record downstream. This demo renders
the report as JSON (the same document the CLI's --format json prints), then
consumes it programmatically the way a webhook or ETL step would.
"""
import io
import json
from contextlib import redirect_stdout

from _common import dataset, rule
from deidproof.cli import main as cli_main


def main() -> None:
    rule("DATA ENGINEERING  -  parse the JSON verdict in a pipeline")

    csv = dataset("07-clinical-trial", "trial_subjects.csv")
    print("\nCapturing the JSON report for a downstream consumer:")
    print(f"   {csv}\n")

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli_main([
            "check", csv,
            "--qi", "zip,age,sex", "--sensitive", "adverse_event",
            "-k", "2", "-l", "2", "--format", "json",
        ])
    doc = json.loads(buf.getvalue())  # must be valid JSON

    print(f"CLI exit code       : {code}")
    print(f"tool / version      : {doc['tool']} {doc['version']}")
    print(f"rows analyzed       : {doc['row_count']}")
    print(f"k (min_k)           : {doc['min_k']}  passed={doc['k_passed']}")
    print(f"l (min_l)           : {doc['min_l']}  passed={doc['l_passed']}")
    print(f"safe harbor findings: {len(doc['safe_harbor_findings'])}")
    print(f"overall passed      : {doc['passed']}")

    # A pipeline decision: only forward records that FAILED, for remediation.
    if not doc["passed"]:
        cats = sorted({f["rule_id"] for f in doc["safe_harbor_findings"]})
        print(f"\n-> routing to remediation queue; leaking categories: {cats}")

    assert code == 2 and doc["passed"] is False
    print("\nOVERALL: PASS   (JSON parsed and consumed exactly as a pipeline would)")


if __name__ == "__main__":
    main()
