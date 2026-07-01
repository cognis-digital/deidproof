"""HIPAA Safe Harbor detection: value-level patterns, header rules, edge cases."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from deidproof.core import (  # noqa: E402
    SAFE_HARBOR_IDENTIFIERS,
    _value_matches,
    safe_harbor_scan,
)


# ---- value-level detectors -------------------------------------------------

def test_ssn_whole_cell():
    assert "S7" in _value_matches("123-45-6789")


def test_ssn_embedded_in_free_text():
    # regression: SSN inside a note must be caught, not only whole-cell
    assert "S7" in _value_matches("intake form SSN 123-45-6789 to redact")


def test_email_detected():
    assert "S6" in _value_matches("Contact jdoe@example.org please")


def test_url_http_and_www():
    assert "S14" in _value_matches("see https://example.org/x")
    assert "S14" in _value_matches("visit www.example.org today")


def test_ipv4_detected():
    assert "S15" in _value_matches("login from 203.0.113.44")


def test_ipv4_rejects_out_of_range_octets():
    assert "S15" not in _value_matches("999.999.999.999")


def test_phone_various_formats():
    for s in ["(312) 555-0142", "312-555-0188", "312.555.0123", "+1 312 555 0100"]:
        assert "S4" in _value_matches(s), s


def test_zip5_not_flagged_as_phone():
    assert "S4" not in _value_matches("90210")


def test_date_with_month_day_flagged():
    assert "S3" in _value_matches("03/14/2025")
    assert "S3" in _value_matches("2025-03-14")


def test_bare_year_not_flagged_as_date():
    assert "S3" not in _value_matches("1998")


def test_age_over_89_flagged():
    assert "S3" in _value_matches("92")
    assert "S3" in _value_matches("90")


def test_age_89_and_below_not_flagged():
    assert "S3" not in _value_matches("89")
    assert "S3" not in _value_matches("40")


def test_three_digit_code_not_treated_as_age():
    # regression: a bare 3-digit value like 200 is NOT a human age
    assert "S3" not in _value_matches("200")
    assert "S3" not in _value_matches("606")  # e.g. a ZIP3 prefix


def test_implausible_age_ceiling():
    # 126+ is not a plausible age (oldest verified human is 122)
    assert "S3" not in _value_matches("130")
    assert "S3" in _value_matches("110")  # still plausible-ish, flagged


def test_empty_value_no_hits():
    assert _value_matches("") == []
    assert _value_matches("   ") == []


def test_multiple_categories_one_cell():
    hits = _value_matches("jane@example.org 203.0.113.7")
    assert "S6" in hits and "S15" in hits


# ---- header-level detectors ------------------------------------------------

def test_header_name_column():
    findings = safe_harbor_scan([{"patient_name": "Jane"}], ["patient_name"])
    assert any(f.rule_id == "S1" for f in findings)


def test_header_mrn_column():
    findings = safe_harbor_scan([{"mrn": "A123"}], ["mrn"])
    assert any(f.rule_id == "S8" for f in findings)


def test_header_normalization_ignores_case_and_punctuation():
    findings = safe_harbor_scan([{"Patient Name": "Jane"}], ["Patient Name"])
    assert any(f.rule_id == "S1" for f in findings)


def test_header_email_and_value_both_fire_once_per_column():
    rows = [{"email": "a@b.co"}, {"email": "c@d.co"}]
    findings = safe_harbor_scan(rows, ["email"])
    s6 = [f for f in findings if f.rule_id == "S6"]
    assert len(s6) == 1  # coalesced into a single finding per (rule, column)
    assert s6[0].column == "email"


def test_member_id_is_s9():
    findings = safe_harbor_scan([{"member_id": "M1"}], ["member_id"])
    assert any(f.rule_id == "S9" for f in findings)


def test_account_is_s10():
    findings = safe_harbor_scan([{"account": "ACCT-1"}], ["account"])
    assert any(f.rule_id == "S10" for f in findings)


def test_device_serial_and_imei_are_s13():
    findings = safe_harbor_scan(
        [{"device_serial": "D1", "imei": "35209900"}],
        ["device_serial", "imei"],
    )
    ids = {(f.rule_id, f.column) for f in findings}
    assert ("S13", "device_serial") in ids
    assert ("S13", "imei") in ids


# ---- finding structure -----------------------------------------------------

def test_sample_rows_capped_at_max_samples():
    rows = [{"email": f"u{i}@x.co"} for i in range(10)]
    findings = safe_harbor_scan(rows, ["email"], max_samples=3)
    s6 = [f for f in findings if f.rule_id == "S6"][0]
    assert len(s6.sample_rows) <= 3
    # match_count is not capped: 1 header match + 10 value matches = 11
    assert s6.match_count == 11


def test_match_count_value_only_no_header():
    # a column whose header does NOT match but whose values do: pure value count
    rows = [{"note": "call 203.0.113.5"} for _ in range(4)]
    findings = safe_harbor_scan(rows, ["note"], max_samples=2)
    s15 = [f for f in findings if f.rule_id == "S15"][0]
    assert s15.match_count == 4  # no header contribution
    assert len(s15.sample_rows) <= 2


def test_findings_sorted_by_rule_then_column():
    rows = [{"email": "a@b.co", "ssn": "123-45-6789"}]
    findings = safe_harbor_scan(rows, ["email", "ssn"])
    ids = [f.rule_id for f in findings]
    assert ids == sorted(ids)


def test_clean_columns_no_findings():
    rows = [{"region": "West", "band": "30-39"}]
    findings = safe_harbor_scan(rows, ["region", "band"])
    assert findings == []


def test_catalog_has_18_categories():
    ids = [i["id"] for i in SAFE_HARBOR_IDENTIFIERS]
    assert len(ids) == 18
    assert ids[0] == "S1" and ids[-1] == "S18"


def test_no_duplicate_category_ids():
    ids = [i["id"] for i in SAFE_HARBOR_IDENTIFIERS]
    assert len(ids) == len(set(ids))
