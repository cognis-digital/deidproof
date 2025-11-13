# Demo 01 - basic de-identification audit

This demo runs DEIDPROOF against `patients.csv`, a small "de-identified"
healthcare export that still leaks personal data. It demonstrates all three
checks failing on a realistic bad export.

## The dataset

`patients.csv` has 8 rows with columns:

- `patient_name` - a direct identifier (HIPAA Safe Harbor S1)
- `email` - a direct identifier (S6)
- `ssn` - a direct identifier (S7)
- `zip` - 5-digit ZIP, a geographic quasi-identifier (S2)
- `age` - quasi-identifier (one value is `92`, which is age > 89 -> S3)
- `sex` - quasi-identifier
- `diagnosis` - the sensitive attribute

## Run it

```bash
python -m deidproof check demos/01-basic/patients.csv \
    --quasi-identifiers zip,age,sex \
    --sensitive diagnosis \
    -k 2 -l 2
```

For CI / piping:

```bash
python -m deidproof check demos/01-basic/patients.csv \
    --qi zip,age,sex --sensitive diagnosis -k 2 -l 2 --format json
```

## Expected result

The tool exits with code **2** (FAIL) because:

- **k-anonymity**: the smallest equivalence class over `(zip, age, sex)` has
  size **1** (several patients are uniquely identifiable), so `k = 1 < 2`.
- **l-diversity**: those singleton classes contain only one distinct
  `diagnosis`, so `l = 1 < 2`.
- **Safe Harbor**: `patient_name`, `email`, and `ssn` columns are flagged by
  name and by value pattern; `age = 92` is flagged as age > 89 (S3).

A properly de-identified export (no direct identifiers, generalized ZIP/age,
larger equivalence classes) would exit **0** with `OVERALL: PASS`.
