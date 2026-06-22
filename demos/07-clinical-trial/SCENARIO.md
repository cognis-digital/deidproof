# Demo 07 — Clinical-trial subject listing

## Where this data came from

A CRO (contract research organization) prepared a subject-level adverse-event
listing (`trial_subjects.csv`, 8 rows) for a data-sharing request. Subject IDs
were pseudonymized to `SUBJ-00N`, but exact `enroll_date`s, 5-digit `zip`s, and
exact `age`s remained — and one subject is age 90.

The `zip` values are real metropolitan ZIPs (Boston 02115, San Francisco 94110,
Houston 77004); adverse-event terms are common MedDRA-style preferred terms.

## Run it

```bash
python -m deidproof check demos/07-clinical-trial/trial_subjects.csv \
    --quasi-identifiers zip,age,sex \
    --sensitive adverse_event \
    -k 2 -l 2
```

## What to expect

Exit code **2 (FAIL)**:

- **k-anonymity = 1** — small trials are notoriously easy to re-identify; the
  `(zip, age, sex)` triple is unique for nearly every subject.
- **l-diversity = 1** — singleton classes expose each adverse event directly.
- **Safe Harbor:** `zip` (S2), exact `enroll_date` (S3), and `age = 90` (S3).

## How to act

Small-N trials need aggressive generalization: drop `enroll_date` (or keep only
the year), truncate `zip` to 3 digits, band `age` with `90+` capping, and
consider suppressing rare adverse events. Re-run before any external transfer.
