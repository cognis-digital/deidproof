"""Scenario 8 - CI / release engineers.

deidproof is built to be a CI gate: it returns 0 when a dataset passes and 2
when it fails, so a pipeline step can block a bad release with no human in the
loop. This demo drives the *actual* CLI entry point (deidproof.cli.main) and
asserts the exit codes, exactly as a GitHub Action or Makefile target would.
"""
from _common import dataset, rule
from deidproof.cli import main as cli_main


def _run(argv):
    code = cli_main(argv)
    return code


def main() -> None:
    rule("CI / RELEASE ENGINEER  -  exit 0 = ship, exit 2 = block")

    clean = dataset("02-clean", "clean_export.csv")
    leaky = dataset("04-safe-harbor-leak", "ed_export.csv")

    print("\nA passing, generalized export -> the pipeline may proceed:")
    ok = _run([
        "check", clean,
        "--qi", "region,age_band,sex", "--sensitive", "diagnosis_group",
        "-k", "2", "-l", "2", "--format", "json",
    ])
    print(f"   exit code = {ok}   (0 = PASS)")
    assert ok == 0

    print("\nA leaky ED export -> the pipeline is blocked:")
    bad = _run([
        "check", leaky,
        "--qi", "zip,age,sex", "--sensitive", "chief_complaint",
        "-k", "2", "-l", "2", "--format", "json",
    ])
    print(f"   exit code = {bad}   (2 = FAIL, non-zero blocks the job)")
    assert bad == 2

    print("\nA misuse (missing dataset) -> usage error, distinct from a policy fail:")
    err = _run(["check", "does-not-exist.csv", "--qi", "a"])
    print(f"   exit code = {err}   (1 = usage/runtime error)")
    assert err == 1

    print("\nOVERALL: PASS   (all three exit codes are as documented: 0 / 2 / 1)")
    print("\nWire `deidproof check ... -k K -l L` into CI; a non-zero exit fails")
    print("the job. 2 means 'privacy check failed'; 1 means 'you called it wrong'.")


if __name__ == "__main__":
    main()
