# Demo 03 — SARIF 2.1.0 export for code scanning

Re-uses the leaky dataset from `demos/01-basic/patients.csv` but emits **SARIF
2.1.0** instead of a table, so findings show up in GitHub code-scanning, Azure
DevOps, or any SARIF viewer.

## Run

```bash
python -m deidproof check demos/01-basic/patients.csv \
    --quasi-identifiers zip,age,sex \
    --sensitive diagnosis \
    -k 2 -l 2 \
    --format sarif > deidproof.sarif
```

Upload `deidproof.sarif` in CI, e.g. with GitHub's `upload-sarif` action.

## Expected

A SARIF log with `version: "2.1.0"`, a `deidproof` tool driver carrying 20
reporting descriptors (the 18 HIPAA Safe Harbor categories plus `DEID-K` and
`DEID-L`), and one `error`-level `result` per Safe Harbor finding plus one each
for the failed k-anonymity and l-diversity thresholds. Exit code is still **2**
so the CI gate trips.
