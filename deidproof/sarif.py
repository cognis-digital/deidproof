"""SARIF 2.1.0 export for DEIDPROOF reports.

Serializes a :class:`deidproof.core.Report` into the OASIS SARIF 2.1.0 schema
(Static Analysis Results Interchange Format) so re-identification findings can be
uploaded to GitHub code scanning, Azure DevOps, or any SARIF-aware viewer.

Mapping
-------
* Each HIPAA Safe Harbor finding -> one SARIF ``result`` (level ``error``).
* A failed k-anonymity threshold  -> one ``result`` (rule ``DEID-K``).
* A failed l-diversity threshold  -> one ``result`` (rule ``DEID-L``).
The dataset path is recorded as the result's ``physicalLocation.artifactLocation``.

Standard library only.
"""

from __future__ import annotations

from typing import Dict, List

from .core import SAFE_HARBOR_IDENTIFIERS, TOOL_NAME, TOOL_VERSION, Report

SARIF_VERSION = "2.1.0"
SARIF_SCHEMA = (
    "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/"
    "Schemata/sarif-schema-2.1.0.json"
)
INFO_URI = "https://github.com/cognis-digital/deidproof"


def _rules() -> List[Dict]:
    """One SARIF reporting descriptor per Safe Harbor category, plus k and l."""
    rules: List[Dict] = []
    for ident in SAFE_HARBOR_IDENTIFIERS:
        rules.append(
            {
                "id": ident["id"],
                "name": "SafeHarbor" + ident["id"],
                "shortDescription": {
                    "text": "HIPAA Safe Harbor identifier: " + ident["category"]
                },
                "helpUri": INFO_URI,
                "defaultConfiguration": {"level": "error"},
                "properties": {"category": "hipaa-safe-harbor"},
            }
        )
    rules.append(
        {
            "id": "DEID-K",
            "name": "KAnonymityThreshold",
            "shortDescription": {
                "text": "k-anonymity below the required minimum"
            },
            "helpUri": INFO_URI,
            "defaultConfiguration": {"level": "error"},
            "properties": {"category": "k-anonymity"},
        }
    )
    rules.append(
        {
            "id": "DEID-L",
            "name": "LDiversityThreshold",
            "shortDescription": {
                "text": "l-diversity below the required minimum"
            },
            "helpUri": INFO_URI,
            "defaultConfiguration": {"level": "error"},
            "properties": {"category": "l-diversity"},
        }
    )
    return rules


def _result(rule_id: str, message: str, dataset: str, column: str = "") -> Dict:
    location = {
        "physicalLocation": {
            "artifactLocation": {"uri": dataset.replace("\\", "/")}
        }
    }
    if column:
        location["logicalLocations"] = [
            {"name": column, "kind": "member"}
        ]
    return {
        "ruleId": rule_id,
        "level": "error",
        "message": {"text": message},
        "locations": [location],
    }


def report_to_sarif(rep: Report, dataset: str = "dataset.csv") -> Dict:
    """Build a SARIF 2.1.0 log document (as a dict) from a Report."""
    results: List[Dict] = []

    for f in rep.safe_harbor_findings:
        msg = (
            f"{f.category}: column '{f.column}' - {f.reason}; "
            f"{f.match_count} hit(s)"
        )
        results.append(_result(f.rule_id, msg, dataset, column=f.column))

    if rep.k_passed is False:
        results.append(
            _result(
                "DEID-K",
                (
                    f"k-anonymity k={rep.min_k} is below the required "
                    f"minimum of {rep.k_threshold} over quasi-identifiers "
                    f"{', '.join(rep.quasi_identifiers)}"
                ),
                dataset,
            )
        )

    if rep.l_passed is False:
        results.append(
            _result(
                "DEID-L",
                (
                    f"l-diversity l={rep.min_l} is below the required "
                    f"minimum of {rep.l_threshold} for sensitive attribute(s) "
                    f"{', '.join(rep.sensitive)}"
                ),
                dataset,
            )
        )

    return {
        "version": SARIF_VERSION,
        "$schema": SARIF_SCHEMA,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": TOOL_NAME,
                        "version": TOOL_VERSION,
                        "informationUri": INFO_URI,
                        "rules": _rules(),
                    }
                },
                "results": results,
            }
        ],
    }
