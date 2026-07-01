"""Scenario 15 - Operator errors, handled cleanly.

A good gate fails *loudly and clearly* when it is misused, and never silently
passes. This demo drives the real CLI through the common operator mistakes --
missing file, wrong column name, a bad delimiter, and gating on -k with no
quasi-identifiers -- and shows each returns exit code 1 with a readable message,
distinct from a genuine policy failure (exit 2).
"""
import io
from contextlib import redirect_stderr

from _common import dataset, rule
from deidproof.cli import main as cli_main


def _run(argv):
    err = io.StringIO()
    with redirect_stderr(err):
        code = cli_main(argv)
    return code, err.getvalue().strip()


def main() -> None:
    rule("OPERATOR ERRORS  -  fail clearly (exit 1), never pass silently")

    real = dataset("02-clean", "clean_export.csv")

    cases = [
        ("missing file",
         ["check", "no-such-file.csv", "--qi", "region"]),
        ("unknown quasi-identifier column",
         ["check", real, "--qi", "not_a_column"]),
        ("bad multi-char delimiter",
         ["check", real, "--qi", "region", "--delimiter", "::"]),
        ("-k with no quasi-identifiers (would pass silently)",
         ["check", real, "-k", "5"]),
        ("negative -k",
         ["check", real, "--qi", "region", "-k", "-3"]),
    ]

    all_ok = True
    for label, argv in cases:
        code, msg = _run(argv)
        ok = code == 1 and msg.startswith("error:")
        all_ok = all_ok and ok
        print(f"\n[{ 'ok' if ok else 'BAD' }] {label}")
        print(f"      exit={code}  {msg.splitlines()[0] if msg else '(no message)'}")

    assert all_ok, "every misuse must exit 1 with a clear error"
    print("\nOVERALL: PASS   (all misuse paths return exit 1 with a clear message)")


if __name__ == "__main__":
    main()
