"""Scenario 13 - Connected medical devices / telemetry.

Device exports carry identifiers unique to hardware: a *device serial* (S13), an
*IMEI* (S13), and the *IP* the reading was uploaded from (S15). None of these is
a name, yet each can re-identify a device -- and thus a patient. This demo shows
deidproof catching all three from a small telemetry export.
"""
from _common import dataset, rule, overall
from deidproof.core import analyze_csv


def main() -> None:
    rule("DEVICE TELEMETRY  -  serial / IMEI / upload IP are identifiers")

    csv = dataset("14-device-telemetry", "device_export.csv")
    print("\nReviewing a connected-device telemetry export:")
    print(f"   {csv}\n")

    rep = analyze_csv(
        csv,
        quasi_identifiers=["age_band", "sex"],
        sensitive=["reading"],
        k=2,
    )
    print(f"Rows analyzed : {rep.row_count}")
    print(f"Safe Harbor findings: {len(rep.safe_harbor_findings)}\n")
    for f in rep.safe_harbor_findings:
        print(f"   {f.rule_id:>4}  {f.category}: column '{f.column}'")

    by_col = {f.column: f.rule_id for f in rep.safe_harbor_findings}
    assert by_col.get("device_serial") == "S13"
    assert by_col.get("imei") == "S13"
    assert "upload_ip" in by_col  # IP by header and/or value

    overall(rep)
    print("\nLesson: hardware identifiers (S13) and network identifiers (S15) must")
    print("be stripped before a device dataset can be called de-identified.")


if __name__ == "__main__":
    main()
