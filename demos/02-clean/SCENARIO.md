# Demo 02 — Clean baseline (zero findings, PASS)

A minimal, properly de-identified export (`clean_export.csv`, 8 rows): broad
`region`, 10-year `age_band`, no direct identifiers, every equivalence class has
2 members with 2 distinct diagnoses.

## Run

```bash
python -m deidproof check demos/02-clean/clean_export.csv \
    --quasi-identifiers region,age_band,sex \
    --sensitive diagnosis_group \
    -k 2 -l 2
```

## Expected

Exit **0 (PASS)** — `k = 2`, `l = 2`, no Safe Harbor findings. Use this as the
smallest possible "known-good" fixture in your tests.
