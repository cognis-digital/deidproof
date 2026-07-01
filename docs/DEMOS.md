# Demos

Twenty runnable, narrated scenarios in [`../demos/`](../demos/), each aimed at a
different audience or edge case. Every scenario reads only the CSV/TSV fixtures
bundled under `demos/NN-*/`, calls the **real** `deidproof` API, runs fully
**offline**, and exits `0`.

```bash
PYTHONUTF8=1 python demos/run_all.py                       # all twenty, end to end
PYTHONUTF8=1 python demos/03_data_steward_safe_harbor.py   # or just one
```

| # | Scenario | Audience | What it shows |
|---|----------|----------|---------------|
| 1 | [`01_privacy_officer_gate.py`](../demos/01_privacy_officer_gate.py) | Privacy / GRC officers | Gate a release on a k/l/Safe-Harbor policy and get a provable PASS/FAIL with the CI exit code. |
| 2 | [`02_data_scientist_generalize.py`](../demos/02_data_scientist_generalize.py) | Data scientists | Measure k on a raw extract, generalize to ZIP3/age-bands, and re-measure until the metric clears the bar. |
| 3 | [`03_data_steward_safe_harbor.py`](../demos/03_data_steward_safe_harbor.py) | Healthcare / research data stewards | Itemize every HIPAA Safe Harbor identifier (all 18 categories) leaking from an ED export, by header and by cell content. |
| 4 | [`04_auditor_sarif_evidence.py`](../demos/04_auditor_sarif_evidence.py) | Auditors | Produce machine-checkable SARIF 2.1.0 evidence — rule ids (S1–S18, DEID-K/L) and locations — for code scanning and the audit trail. |
| 5 | [`05_l_diversity_homogeneity.py`](../demos/05_l_diversity_homogeneity.py) | Research stewards & analysts | Why k alone is not safety: a cohort that passes k≥2 but fails l≥2 leaks the sensitive value (the homogeneity attack). |
| 6 | [`06_claims_export_gate.py`](../demos/06_claims_export_gate.py) | Payer / claims analytics | Member id (S9) and account number (S10) are Safe Harbor identifiers, not harmless internal keys. |
| 7 | [`07_genomics_technical_ids.py`](../demos/07_genomics_technical_ids.py) | Genomics / biobank engineers | Technical identifiers are PHI too: portal URL (S14), sequencer serial (S13), upload IP (S15), collection date (S3). |
| 8 | [`08_ci_gate_exit_codes.py`](../demos/08_ci_gate_exit_codes.py) | CI / release engineers | The three documented exit codes driven through the real CLI: 0 (ship), 2 (block), 1 (misuse). |
| 9 | [`09_json_pipeline_emit.py`](../demos/09_json_pipeline_emit.py) | Platform / data engineering | Parse the stable JSON verdict and route failing records to a remediation queue. |
| 10 | [`10_free_text_leak.py`](../demos/10_free_text_leak.py) | Clinical NLP / free-text review | Content scanning finds phone (S4), email (S6), SSN (S7), URL (S14) and IP (S15) buried inside a `note` column. |
| 11 | [`11_suppression_missing_cells.py`](../demos/11_suppression_missing_cells.py) | Data stewards | Cell suppression: a blank QI cell is a value in its own right, and merges small equivalence classes up to k≥2. |
| 12 | [`12_delimiter_variants.py`](../demos/12_delimiter_variants.py) | Data engineering | Non-comma exports: tab-delimited (TSV) and semicolon (EU locale) files analyzed with `--delimiter`. |
| 13 | [`13_device_telemetry.py`](../demos/13_device_telemetry.py) | Connected-device / telemetry | Device serial (S13), IMEI (S13) and upload IP (S15) re-identify hardware, and thus a patient. |
| 14 | [`14_k_vs_l_tradeoff.py`](../demos/14_k_vs_l_tradeoff.py) | Data stewards | Quantify the k↔l trade-off across QI sets: k is monotone non-decreasing as you coarsen; l is not. |
| 15 | [`15_error_handling.py`](../demos/15_error_handling.py) | Operators | Every misuse (missing file, bad column, multi-char delimiter, `-k` with no QIs, negative `-k`) exits 1 with a clear message. |
| 16 | [`16_safe_harbor_catalog.py`](../demos/16_safe_harbor_catalog.py) | Reviewers | A reference card: the 18 categories plus one engineered row that trips the value-level detectors (S3/S4/S6/S7/S14/S15). |
| 17 | [`17_before_after_release.py`](../demos/17_before_after_release.py) | Data scientists ↔ privacy officers | Before/after remediation: the same tool and thresholds turn a documented FAIL into a PASS. |
| 18 | [`18_sarif_clean_vs_dirty.py`](../demos/18_sarif_clean_vs_dirty.py) | Auditors | SARIF for both a clean release (empty `results`, proof it was checked) and a dirty one (error-level results). |
| 19 | [`19_biobank_singletons.py`](../demos/19_biobank_singletons.py) | Small-cohort stewards | Surface the singleton equivalence classes that fail k — the exact rows to generalize or suppress. |
| 20 | [`20_multi_attribute_qi.py`](../demos/20_multi_attribute_qi.py) | Advanced analysts | Multi-column quasi-identifiers and l-diversity evaluated over a tuple of sensitive attributes. |

Each demo prints clear, narrated output and exits `0`, so they double as smoke
tests — `tests/test_demo_scenarios.py` imports and runs every `main()` under
`pytest`, and `tests/test_demos.py` covers the underlying CLI exit codes on the
bundled fixtures.

> The bundled fixtures are synthetic. There is no real patient data anywhere in
> this repository.
