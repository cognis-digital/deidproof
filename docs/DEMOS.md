# Demos

Five runnable, narrated scenarios in [`../demos/`](../demos/), each aimed at a
different audience. Every scenario reads only the CSV/TSV fixtures bundled under
`demos/NN-*/`, calls the **real** `deidproof` API, runs fully **offline**, and
exits `0`.

```bash
PYTHONUTF8=1 python demos/run_all.py                  # all five, end to end
PYTHONUTF8=1 python demos/03_data_steward_safe_harbor.py   # or just one
```

| # | Scenario | Audience | What it shows |
|---|----------|----------|---------------|
| 1 | [`01_privacy_officer_gate.py`](../demos/01_privacy_officer_gate.py) | Privacy / GRC officers | Gate a release on a k/l/Safe-Harbor policy and get a provable PASS/FAIL with the CI exit code. |
| 2 | [`02_data_scientist_generalize.py`](../demos/02_data_scientist_generalize.py) | Data scientists | Measure k on a raw extract, generalize to ZIP3/age-bands, and re-measure until the metric clears the bar. |
| 3 | [`03_data_steward_safe_harbor.py`](../demos/03_data_steward_safe_harbor.py) | Healthcare / research data stewards | Itemize every HIPAA Safe Harbor identifier (all 18 categories) leaking from an ED export, by header and by cell content. |
| 4 | [`04_auditor_sarif_evidence.py`](../demos/04_auditor_sarif_evidence.py) | Auditors | Produce machine-checkable SARIF 2.1.0 evidence — rule ids (S1–S18, DEID-K/L) and locations — for code scanning and the audit trail. |
| 5 | [`05_l_diversity_homogeneity.py`](../demos/05_l_diversity_homogeneity.py) | Research stewards & analysts | Why k alone is not safety: a cohort that passes k≥2 but fails l≥2 leaks the sensitive value (the homogeneity attack). |

Each demo prints clear, narrated output and exits `0`, so they double as smoke
tests — `tests/test_demo_scenarios.py` imports and runs every `main()` under
`pytest`, and `tests/test_demos.py` covers the underlying CLI exit codes on the
bundled fixtures.

> The bundled fixtures are synthetic. There is no real patient data anywhere in
> this repository.
