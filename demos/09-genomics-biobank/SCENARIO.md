# Demo 09 — Genomics biobank manifest (URLs, IPs, device serials)

## Where this data came from

A biobank exported a sample manifest (`biobank_samples.csv`, 6 rows) alongside
sequencing data. The team scrubbed participant names but left operational
metadata that are themselves Safe Harbor identifiers: a per-participant portal
**URL** (S14), the **upload IP** address (S15), and the **sequencer serial**
number (S13). `ancestry` is treated as the sensitive attribute.

All values are synthetic: `example.org` portal links, RFC-1918 private IPs
(`10.4.18.x`), and made-up `SEQ-NB55xxxx` serials.

## Run it

```bash
python -m deidproof check demos/09-genomics-biobank/biobank_samples.csv \
    --quasi-identifiers zip3,age,ancestry \
    --sensitive ancestry \
    -k 2
```

## What to expect

Exit code **2 (FAIL)**:

- **Safe Harbor:** `participant_url` (S14), `upload_ip` (S15),
  `sequencer_serial` (S13), `collection_date` (S3), `zip3` (S2), and `age = 91`
  (S3 age > 89).
- **k-anonymity = 1** — two participants are unique on `(zip3, age, ancestry)`.

> Note: the numeric `zip3` values are also flagged S3, because any standalone
> 3-digit number > 89 trips the "age over 89" value heuristic. This is expected
> conservative behavior — review such hits in context.

## How to act

Operational/device metadata is a frequent blind spot. Drop `participant_url`,
`upload_ip`, and `sequencer_serial` from any shared manifest, generalize
`collection_date` to year, cap age at `90+`, and increase cell sizes before
release.
