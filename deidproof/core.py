"""Core engine for DEIDPROOF.

Real implementations of:
  * k-anonymity      -- size of the smallest equivalence class over quasi-identifiers
  * l-diversity      -- distinct sensitive values within each equivalence class
  * HIPAA Safe Harbor -- detection of the 18 identifier categories (45 CFR 164.514(b)(2))

Standard library only.
"""

from __future__ import annotations

import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

TOOL_NAME = "deidproof"
TOOL_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# HIPAA Safe Harbor: the 18 identifier categories of 45 CFR 164.514(b)(2)
# ---------------------------------------------------------------------------
# Each rule has: id, category label, a value-level regex (applied to cell text),
# and header-name keywords (applied to column names, case-insensitive).

SAFE_HARBOR_IDENTIFIERS: List[Dict[str, str]] = [
    {"id": "S1", "category": "Name"},
    {"id": "S2", "category": "Geographic subdivision smaller than state"},
    {"id": "S3", "category": "Dates (other than year) / age > 89"},
    {"id": "S4", "category": "Telephone number"},
    {"id": "S5", "category": "Fax number"},
    {"id": "S6", "category": "Email address"},
    {"id": "S7", "category": "Social Security number"},
    {"id": "S8", "category": "Medical record number"},
    {"id": "S9", "category": "Health plan beneficiary number"},
    {"id": "S10", "category": "Account number"},
    {"id": "S11", "category": "Certificate / license number"},
    {"id": "S12", "category": "Vehicle identifier / license plate"},
    {"id": "S13", "category": "Device identifier / serial number"},
    {"id": "S14", "category": "Web URL"},
    {"id": "S15", "category": "IP address"},
    {"id": "S16", "category": "Biometric identifier"},
    {"id": "S17", "category": "Full-face photo / image reference"},
    {"id": "S18", "category": "Any other unique identifying number/code"},
]

# Value-level regexes (applied to individual cell strings).
_SSN_RE = re.compile(r"^\s*\d{3}-\d{2}-\d{4}\s*$")
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)"
)
_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(r"https?://|www\.[A-Za-z0-9-]+\.")
_IPV4_RE = re.compile(
    r"(?<!\d)(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?!\d)"
)
_ZIP_RE = re.compile(r"^\s*\d{5}(?:-\d{4})?\s*$")
# A date that includes month/day (not just a bare year).
_DATE_TOKEN_RE = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2})\b",
    re.IGNORECASE,
)

# Header-name keyword -> Safe Harbor rule id.
_HEADER_KEYWORDS: List[Tuple[Tuple[str, ...], str]] = [
    (("name", "firstname", "lastname", "fullname", "patientname", "surname"), "S1"),
    (("address", "street", "city", "county", "precinct", "zip", "zipcode", "postal"), "S2"),
    (("dob", "birth", "birthdate", "admit", "admission", "discharge", "deathdate", "date"), "S3"),
    (("phone", "telephone", "mobile", "cell"), "S4"),
    (("fax",), "S5"),
    (("email", "e-mail"), "S6"),
    (("ssn", "socialsecurity"), "S7"),
    (("mrn", "medicalrecord", "recordnumber"), "S8"),
    (("beneficiary", "memberid", "planid", "healthplan"), "S9"),
    (("account", "acct"), "S10"),
    (("license", "certificate", "licensenumber"), "S11"),
    (("vin", "plate", "licenseplate", "vehicle"), "S12"),
    (("serial", "deviceid", "device", "imei"), "S13"),
    (("url", "website", "webpage"), "S14"),
    (("ip", "ipaddress", "ipaddr"), "S15"),
    (("fingerprint", "biometric", "retina", "voiceprint", "iris"), "S16"),
    (("photo", "image", "picture", "facephoto"), "S17"),
]

_CATEGORY_BY_ID = {r["id"]: r["category"] for r in SAFE_HARBOR_IDENTIFIERS}


def _norm_header(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (name or "").lower())


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SafeHarborFinding:
    rule_id: str
    category: str
    column: str
    reason: str
    sample_rows: List[int] = field(default_factory=list)
    match_count: int = 0


@dataclass
class Report:
    tool: str = TOOL_NAME
    version: str = TOOL_VERSION
    row_count: int = 0
    quasi_identifiers: List[str] = field(default_factory=list)
    sensitive: List[str] = field(default_factory=list)
    k_threshold: Optional[int] = None
    l_threshold: Optional[int] = None
    min_k: Optional[int] = None
    min_l: Optional[int] = None
    k_passed: Optional[bool] = None
    l_passed: Optional[bool] = None
    smallest_classes: List[Dict] = field(default_factory=list)
    safe_harbor_findings: List[SafeHarborFinding] = field(default_factory=list)
    safe_harbor_passed: bool = True
    passed: bool = True

    def to_dict(self) -> Dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# k-anonymity
# ---------------------------------------------------------------------------

def _equivalence_classes(
    rows: Sequence[Dict[str, str]], quasi_identifiers: Sequence[str]
) -> Dict[Tuple[str, ...], List[int]]:
    classes: Dict[Tuple[str, ...], List[int]] = defaultdict(list)
    for i, row in enumerate(rows):
        key = tuple((row.get(q) or "").strip() for q in quasi_identifiers)
        classes[key].append(i)
    return classes


def k_anonymity(
    rows: Sequence[Dict[str, str]], quasi_identifiers: Sequence[str]
) -> Tuple[int, Dict[Tuple[str, ...], List[int]]]:
    """Return (min_class_size, equivalence_classes).

    k-anonymity = size of the smallest equivalence class over the quasi-identifiers.
    A dataset satisfies k-anonymity for a given k if min_class_size >= k.
    """
    if not quasi_identifiers:
        raise ValueError("quasi_identifiers must be non-empty for k-anonymity")
    classes = _equivalence_classes(rows, quasi_identifiers)
    if not classes:
        return 0, classes
    min_k = min(len(idxs) for idxs in classes.values())
    return min_k, classes


# ---------------------------------------------------------------------------
# l-diversity
# ---------------------------------------------------------------------------

def l_diversity(
    rows: Sequence[Dict[str, str]],
    quasi_identifiers: Sequence[str],
    sensitive: Sequence[str],
) -> Tuple[int, Dict[Tuple[str, ...], int]]:
    """Return (min_distinct_sensitive, per_class_diversity).

    Distinct l-diversity: each equivalence class must contain at least l
    *distinct* values for the (combined) sensitive attribute(s). We report the
    minimum across classes.
    """
    if not sensitive:
        raise ValueError("sensitive attributes must be non-empty for l-diversity")
    classes = _equivalence_classes(rows, quasi_identifiers)
    per_class: Dict[Tuple[str, ...], int] = {}
    for key, idxs in classes.items():
        distinct = {
            tuple((rows[i].get(s) or "").strip() for s in sensitive) for i in idxs
        }
        per_class[key] = len(distinct)
    if not per_class:
        return 0, per_class
    min_l = min(per_class.values())
    return min_l, per_class


# ---------------------------------------------------------------------------
# HIPAA Safe Harbor
# ---------------------------------------------------------------------------

def _value_matches(value: str) -> List[str]:
    """Return list of rule ids whose value-level pattern matches this cell."""
    hits: List[str] = []
    v = value.strip()
    if not v:
        return hits
    if _SSN_RE.match(v):
        hits.append("S7")
    if _EMAIL_RE.search(v):
        hits.append("S6")
    if _URL_RE.search(v):
        hits.append("S14")
    if _IPV4_RE.search(v):
        hits.append("S15")
    # Phone: avoid double-counting SSN (already a different shape) and IPs.
    if "S15" not in hits and "S7" not in hits and _PHONE_RE.search(v):
        # Require it not be a pure 9-digit run already flagged; phone regex is
        # specific enough. Guard against zip codes (5 digits only).
        if not _ZIP_RE.match(v):
            hits.append("S4")
    if _DATE_TOKEN_RE.search(v):
        hits.append("S3")
    # Age over 89 (Safe Harbor requires aggregating ages >89 into 90+).
    if re.fullmatch(r"\d{1,3}", v):
        try:
            if int(v) > 89:
                hits.append("S3")
        except ValueError:
            pass
    return hits


def safe_harbor_scan(
    rows: Sequence[Dict[str, str]],
    columns: Sequence[str],
    max_samples: int = 3,
) -> List[SafeHarborFinding]:
    """Detect HIPAA Safe Harbor identifiers by column name and cell content."""
    findings: Dict[Tuple[str, str], SafeHarborFinding] = {}

    def _record(rule_id: str, column: str, reason: str, row_idx: Optional[int]):
        key = (rule_id, column)
        f = findings.get(key)
        if f is None:
            f = SafeHarborFinding(
                rule_id=rule_id,
                category=_CATEGORY_BY_ID.get(rule_id, "Unknown"),
                column=column,
                reason=reason,
            )
            findings[key] = f
        f.match_count += 1
        if row_idx is not None and len(f.sample_rows) < max_samples:
            f.sample_rows.append(row_idx)

    # 1) Header-name based detection.
    header_rule: Dict[str, str] = {}
    for col in columns:
        norm = _norm_header(col)
        for keywords, rule_id in _HEADER_KEYWORDS:
            if any(kw in norm for kw in keywords):
                header_rule[col] = rule_id
                _record(
                    rule_id,
                    col,
                    f"column name '{col}' matches identifier category",
                    None,
                )
                break

    # 2) Value-content based detection.
    for i, row in enumerate(rows):
        for col in columns:
            val = row.get(col)
            if not val:
                continue
            for rule_id in _value_matches(str(val)):
                _record(
                    rule_id,
                    col,
                    f"cell value matches {_CATEGORY_BY_ID.get(rule_id)} pattern",
                    i,
                )

    # Stable ordering by rule id then column.
    return sorted(findings.values(), key=lambda f: (f.rule_id, f.column))


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def analyze_rows(
    rows: Sequence[Dict[str, str]],
    columns: Sequence[str],
    quasi_identifiers: Optional[Sequence[str]] = None,
    sensitive: Optional[Sequence[str]] = None,
    k: Optional[int] = None,
    l: Optional[int] = None,
    safe_harbor: bool = True,
    max_samples: int = 3,
) -> Report:
    """Run the full DEIDPROOF analysis over already-parsed rows."""
    quasi_identifiers = list(quasi_identifiers or [])
    sensitive = list(sensitive or [])

    rep = Report(
        row_count=len(rows),
        quasi_identifiers=quasi_identifiers,
        sensitive=sensitive,
        k_threshold=k,
        l_threshold=l,
    )

    classes: Dict[Tuple[str, ...], List[int]] = {}
    if quasi_identifiers:
        rep.min_k, classes = k_anonymity(rows, quasi_identifiers)
        if k is not None:
            rep.k_passed = rep.min_k >= k
        # Report the smallest equivalence classes for actionable output.
        ordered = sorted(classes.items(), key=lambda kv: len(kv[1]))
        for key, idxs in ordered[:5]:
            rep.smallest_classes.append(
                {
                    "values": dict(zip(quasi_identifiers, key)),
                    "size": len(idxs),
                    "row_indices": idxs[:max_samples],
                }
            )

    if quasi_identifiers and sensitive:
        rep.min_l, _ = l_diversity(rows, quasi_identifiers, sensitive)
        if l is not None:
            rep.l_passed = rep.min_l >= l

    if safe_harbor:
        rep.safe_harbor_findings = safe_harbor_scan(rows, columns, max_samples)
        rep.safe_harbor_passed = len(rep.safe_harbor_findings) == 0

    rep.passed = (
        (rep.k_passed in (None, True))
        and (rep.l_passed in (None, True))
        and rep.safe_harbor_passed
    )
    return rep


def analyze_csv(
    path: str,
    quasi_identifiers: Optional[Sequence[str]] = None,
    sensitive: Optional[Sequence[str]] = None,
    k: Optional[int] = None,
    l: Optional[int] = None,
    safe_harbor: bool = True,
    delimiter: str = ",",
    max_samples: int = 3,
) -> Report:
    """Parse a CSV file and run the full analysis."""
    with open(path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh, delimiter=delimiter)
        columns = list(reader.fieldnames or [])
        rows = [dict(r) for r in reader]

    _validate_columns(columns, quasi_identifiers, "quasi-identifier")
    _validate_columns(columns, sensitive, "sensitive")

    return analyze_rows(
        rows,
        columns,
        quasi_identifiers=quasi_identifiers,
        sensitive=sensitive,
        k=k,
        l=l,
        safe_harbor=safe_harbor,
        max_samples=max_samples,
    )


def _validate_columns(
    columns: Sequence[str], requested: Optional[Sequence[str]], label: str
) -> None:
    if not requested:
        return
    missing = [c for c in requested if c not in columns]
    if missing:
        raise ValueError(
            f"{label} column(s) not found in dataset: {', '.join(missing)}. "
            f"Available columns: {', '.join(columns)}"
        )
