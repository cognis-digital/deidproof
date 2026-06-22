# Demo 04 — Emergency-department export with leaked direct identifiers

## Where this data came from

A data analyst was asked to hand an ED (emergency department) encounter extract
to a quality-improvement vendor. They dropped the `name` column they *thought*
was the only identifier and exported `ed_export.csv` (6 synthetic rows). Several
HIPAA Safe Harbor identifiers were left in place.

The values are synthetic but realistically shaped: `(XXX) 555-01XX` phone
numbers (the 555-01xx block is reserved for fiction), `example.org` emails, and
MRNs in a plausible `A00xxxxxx` format.

## Run it

```bash
python -m deidproof check demos/04-safe-harbor-leak/ed_export.csv \
    --quasi-identifiers zip,age,sex \
    --sensitive chief_complaint \
    -k 2 -l 2
```

## What to expect

Exit code **2 (FAIL)**. The report flags:

- **Safe Harbor (7 findings):** `mrn` (S8), `patient_name` (S1), `phone` (S4),
  `email` (S6), `admit_date` (S3 dates), `zip` (S2), and `age = 91` as an
  age > 89 (S3).
- **k-anonymity = 1:** every `(zip, age, sex)` combination is unique, so each
  patient is singled out.
- **l-diversity = 1:** the singleton classes carry only one chief complaint
  each.

## How to act

This export must **not** ship. Remove `patient_name`, `mrn`, `phone`, `email`,
and `admit_date`; truncate `zip` to its first 3 digits; band `age` into ranges
and recode any age > 89 as `90+`. Re-run until `OVERALL: PASS`.
