# Demo 05 — A properly generalized release that PASSES

## Where this data came from

This is what `demos/04` *should* have looked like after remediation. An analyst
generalized a disease-registry extract before public release
(`registry_release.csv`, 16 rows): geography collapsed to broad census
`region`, ages bucketed into 10-year `age_band`s, all direct identifiers
dropped. Each `(region, age_band, sex)` group holds two records with two
distinct diagnosis groups.

## Run it

```bash
python -m deidproof check demos/05-generalized-pass/registry_release.csv \
    --quasi-identifiers region,age_band,sex \
    --sensitive diagnosis_group \
    -k 2 -l 2
```

## What to expect

Exit code **0 (PASS)**:

- **k-anonymity = 2** — every equivalence class has at least 2 members.
- **l-diversity = 2** — every class has at least 2 distinct diagnosis groups.
- **Safe Harbor: no findings** — no column name or cell value matches any of
  the 18 identifier categories.

## How to act

This is the green baseline. Use it as the contract in CI:

```bash
python -m deidproof check release.csv --qi region,age_band,sex \
    --sensitive diagnosis_group -k 2 -l 2 || exit 1
```

Any future release that regresses below `k=2`/`l=2` or reintroduces an
identifier column will break the build.
