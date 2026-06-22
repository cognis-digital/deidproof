# Demo 08 — Payer claims extract with ICD-10 sensitive field

## Where this data came from

A health plan's analytics team exported a claims extract (`payer_claims.csv`,
6 rows) for an actuarial partner, treating `member_id` and `account` as "just
internal keys." Both are Safe Harbor identifiers (S9 beneficiary number, S10
account number). The diagnosis is the real sensitive attribute.

ICD-10 codes are genuine, valid codes: `E11.9` (type 2 diabetes), `I10`
(essential hypertension), `J45.909` (unspecified asthma), `E78.5`
(hyperlipidemia), `M54.5` (low back pain).

## Run it

```bash
python -m deidproof check demos/08-claims-export/payer_claims.csv \
    --quasi-identifiers zip,age,sex \
    --sensitive icd10 \
    -k 2 -l 2
```

## What to expect

Exit code **2 (FAIL)**:

- **Safe Harbor:** `member_id` (S9), `account` (S10), `zip` (S2), and
  `service_date` (S3).
- **k-anonymity = 1** and **l-diversity = 1** — exact ZIP+age+sex makes each
  member unique.

## How to act

Strip `member_id`/`account` (or replace with a salted token kept *out* of the
shared file), drop `service_date` down to month or quarter, generalize `zip`/
`age`, and roll ICD-10 codes up to category level (e.g. `E11`) if the partner
does not need the full code. Gate the pipeline on a passing run.
