# Demo 06 — k passes but l fails (the homogeneity attack)

## Where this data came from

A research group released an HIV-status cohort (`hiv_cohort.csv`, 12 rows)
believing k-anonymity alone made it safe. They generalized geography to `zip3`
and ages to bands, and every equivalence class has **3** members — so k = 3,
which sounds protective.

The catch: in one class, *all three* members share the same sensitive value.

## Run it

```bash
python -m deidproof check demos/06-l-diversity-gap/hiv_cohort.csv \
    --quasi-identifiers zip3,age_band,sex \
    --sensitive hiv_status \
    -k 2 -l 2 --no-safe-harbor
```

(`--no-safe-harbor` is used here to focus on the k/l interaction; `zip3`/age
generalization is already confirmed, so we are auditing distribution risk only.)

## What to expect

Exit code **2 (FAIL)**:

- **k-anonymity = 3 [PASS]** — the class sizes look safe.
- **l-diversity = 1 [FAIL < 2]** — the class `zip3=100, age_band=30-39, sex=M`
  is entirely `Positive`. An attacker who knows the quasi-identifiers learns the
  HIV status with certainty even though the group has 3 people.

## How to act

This is the textbook reason l-diversity exists. k-anonymity is necessary but not
sufficient. Either suppress/merge the homogeneous class, add records, or apply
t-closeness-style controls so each class carries at least 2 distinct sensitive
values. **Never gate a sensitive-attribute release on k alone — always require
`-l` too.**
