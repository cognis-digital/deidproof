# Demo 10 — Tab-separated research extract (custom delimiter, PASS)

## Where this data came from

A behavioral-health research team exports tab-separated files from their stats
package rather than CSV. This extract (`behavioral_extract.tsv`, 8 rows) has
already been generalized: state-level geography, 10-year age bands, no direct
identifiers. It demonstrates running DEIDPROOF on a **TSV** with `--delimiter`.

Diagnosis terms are common behavioral-health categories.

## Run it

```bash
python -m deidproof check demos/10-tsv-research-extract/behavioral_extract.tsv \
    --delimiter $'\t' \
    --quasi-identifiers state,age_band,sex \
    --sensitive diagnosis \
    -k 2 -l 2
```

(On Windows `cmd`, pass the tab differently; in PowerShell use
`` --delimiter "`t" ``.)

## What to expect

Exit code **0 (PASS)**:

- **k-anonymity = 2**, **l-diversity = 2**, **Safe Harbor: no findings**.

## How to act

Confirms the `--delimiter` flag handles non-comma files. Wire the same command
into the pipeline so tab-delimited exports get the same gate as CSV ones.
