# Diabetes 130-US Hospitals (1999–2008) — Database Schema

Week 3 (SQL for Data Analytics) · MSIS-2402

## 1. The data

Source: [UCI Machine Learning Repository — "Diabetes 130-US hospitals for
years 1999-2008"](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008).
Publicly available, de-identified clinical data (no direct patient
identifiers — `encounter_id` and `patient_nbr` are surrogate IDs assigned
by the source study, not real medical record numbers).

Two raw files ship in `data/`:

| File | Rows | What it is |
|---|---|---|
| `diabetic_data.csv` | 101,766 | One row per inpatient hospital encounter, 1999–2008, for patients with diabetes. 50 columns. |
| `IDS_mapping.csv` | 63 (+2 separator lines) | **Three** code lookup tables concatenated into one file, each separated by a line that's just a bare comma. Not one table. |

Each row of `diabetic_data.csv` is one hospital **encounter** (a visit), not
one patient. The same patient can appear many times: the 101,766 encounters
belong to only **71,518 distinct patients**, and 16,773 of those patients
have more than one encounter (one patient has 40). That repetition is the
single most useful thing about this dataset for an advanced-SQL class — it's
what makes window functions, self-joins, and "compare this visit to the
patient's previous visit" queries meaningful, rather than academic.

## 2. Why this dataset earns "advanced" (not just "another table")

- **Repeat patients** → window functions (`ROW_NUMBER`, `LAG`/`LEAD`
  partitioned by `patient_nbr`), self-joins for readmission-gap analysis.
- **23 medication columns**, each `No` / `Steady` / `Up` / `Down` → wide-to-long
  reshaping (`UNPIVOT`), pivoting back out, medication-adjustment analysis.
- **A real, messy missing-value story**: `weight` is 96.9% missing, `payer_code`
  39.6%, `medical_specialty` 49.1%, `race` only 2.2% — very different
  missingness per column, which forces deliberate handling rather than a
  blanket `DROP NA`.
- **A lookup file that is secretly three tables** (`IDS_mapping.csv`) — parsing
  and normalizing it is itself a small ETL exercise.
- **ICD-9 diagnosis codes** (`diag_1/2/3`) → `CASE`-based bucketing into
  clinical categories is a natural "intermediate+" exercise.
- **A real target column** (`readmitted`: `NO` / `>30` / `<30` days) for
  cohort-comparison and rate-style queries.

## 3. Design decisions

- **Star-ish schema, 6 tables**: 1 main fact table (`encounters`), 1
  long/normalized fact table (`encounter_medications`), 4 small lookup/dimension
  tables (`admission_type`, `discharge_disposition`, `admission_source`,
  `medications`). Deliberately *not* a single flat 50-column table — the three
  ID columns and the 23 medication columns are exactly the parts of the raw
  CSV that are actually coded/repeating data, so they're the parts worth
  normalizing. Everything else stays in `encounters` as plain attributes;
  over-normalizing a teaching database (e.g. splitting out `age` or `gender`)
  would add joins without adding any teaching value.
- **`'?'` → `NULL`**: the source CSV uses the literal string `?` for missing
  values in `race`, `weight`, `payer_code`, `medical_specialty`, `diag_1`,
  `diag_2`, `diag_3`. `build_database.py` converts these to real SQL `NULL`
  via `NULLIF(col, '?')` so `IS NULL`, `COALESCE`, etc. behave normally.
- **`'None'` is *not* treated as missing**: `max_glu_serum` and `A1Cresult`
  use the literal string `'None'` to mean *"this test was not performed"* —
  a real clinical category, distinct from "unknown." These are loaded as-is,
  not `NULLIF`'d, so `'None'` stays queryable as its own value.
- **Three renamed columns**, for consistent snake_case naming:
  `A1Cresult` → `a1c_result`, `change` → `change_made` (the bare word `change`
  reads ambiguously as a SQL identifier), `diabetesMed` → `diabetes_med`.
  Every other column keeps its original CSV name.
- **`encounter_medications` only stores non-`'No'` rows.** A medication
  column value of `'No'` means "not prescribed" — storing 101,766 × 23 ≈
  2.3M mostly-`'No'` rows would bloat the table with the least interesting
  value. Instead, a medication simply has **no row** for an encounter if it
  wasn't in use; the table only records medications that *were* prescribed
  and whether the dose was held steady or adjusted. Result: 120,054 rows
  (~1.2 active medications per encounter on average), and the encounter
  count with at least one row (78,363) matches `encounters.diabetes_med =
  'Yes'` exactly — a built-in cross-check that the reshape is correct.
- **`examide` and `citoglipton` are excluded** from `encounter_medications`
  (and from the `medications` lookup table) entirely: both columns are the
  literal value `'No'` for **all 101,766 rows** in this dataset, so they
  would never produce a row anyway. `medications` therefore has 21 rows, not
  23.
- **No manual indexes.** DuckDB is a columnar, vectorized-execution engine —
  full-column scans are already fast, and it's the wrong mental model to
  reach for B-tree-style secondary indexes here the way you might in
  Postgres/MySQL. DuckDB does automatically maintain an index behind every
  `PRIMARY KEY`/`UNIQUE`/`FOREIGN KEY` constraint declared below.
- **All foreign keys are enforced by DuckDB at load time** (see §5) —
  `build_database.py` would fail loudly on any orphaned key, not silently
  produce a database with dangling references.
- **The database file is a real file on disk**, `diabetic_hospitals.duckdb`,
  opened with `duckdb.connect(str(DB_PATH))` — never `duckdb.connect()` /
  `':memory:'`. It persists between runs; re-running `build_database.py`
  deletes and rebuilds it from scratch (safe, idempotent).

## 4. Entity-relationship diagram

```
admission_type          discharge_disposition        admission_source
────────────────        ─────────────────────        ─────────────────
admission_type_id PK    discharge_disposition_id PK   admission_source_id PK
description              description                   description
      │ 1                        │ 1                          │ 1
      └───────────┐              │              ┌─────────────┘
                   │              │              │
                   ▼              ▼              ▼
            ┌───────────────────────────────────────────┐
            │                 encounters                 │   fact table
            │---------------------------------------------│   grain = 1 encounter
            │ encounter_id PK                              │
            │ patient_nbr               (repeats! up to 40) │
            │ race, gender, age, weight                      │
            │ admission_type_id             FK                │
            │ discharge_disposition_id      FK                 │
            │ admission_source_id           FK                  │
            │ time_in_hospital, payer_code, ...                  │
            │ diag_1, diag_2, diag_3                              │
            │ max_glu_serum, a1c_result                            │
            │ change_made, diabetes_med, readmitted                 │
            └───────────────────────┬───────────────────────────────┘
                                     │ 1
                                     │
                                     │ N
                                     ▼
            ┌───────────────────────────────────────────┐
            │            encounter_medications            │   fact table
            │---------------------------------------------│   grain = 1 medication actually
            │ encounter_id      PK, FK                     │   prescribed in 1 encounter
            │ medication_name   PK, FK                      │
            │ status  ('Steady' | 'Up' | 'Down')             │
            └───────────────────────┬─────────────────────┘
                                     │ N
                                     │
                                     │ 1
                                     ▼
                          ┌───────────────────────┐
                          │       medications       │
                          │-------------------------│
                          │ medication_name PK       │
                          │ is_combination            │
                          └───────────────────────┘
```

## 5. Tables in detail

### `admission_type` (8 rows), `discharge_disposition` (30 rows), `admission_source` (25 rows)

Straight lookup tables: an integer code and a human-readable `description`,
parsed out of the three blocks of `IDS_mapping.csv`. A few codes' descriptions
are the literal text `'NULL'` (e.g. `admission_type_id = 6`) or `'Not
Mapped'`/`'Unknown/Invalid'` — that's the *source data's* way of saying "this
code itself denotes an unknown/unavailable value," kept verbatim rather than
converted to SQL `NULL`, since the *code* is still valid and present on real
encounter rows.

### `medications` (21 rows)

One row per medication name that appears in the wide CSV with any non-`'No'`
value. `is_combination = TRUE` for the five two-drug combination medications
(name contains a hyphen, e.g. `'glyburide-metformin'`); `FALSE` for the 16
single-ingredient medications (e.g. `'metformin'`, `'insulin'`).

### `encounters` (101,766 rows) — the main fact table

Grain: one row per hospital encounter. See `database_schema.sql` for the full
column list with types and comments. Every column keeps its original meaning
from the source CSV except the three renames and the `'?'`→`NULL` cleanup
described in §3.

### `encounter_medications` (120,054 rows)

Grain: one row per (encounter, medication) pair where that medication was
actually in use during the encounter. `status` is `'Steady'` (dose unchanged),
`'Up'` (dose increased), or `'Down'` (dose decreased) — the source CSV's
`'No'` value is never stored here (see §3).

## 6. Foreign keys / referential integrity

All foreign keys below are declared as real `REFERENCES` constraints in
`database_schema.sql` and enforced by DuckDB at insert time — `build_database.py`
was run and completed without any constraint violation, and additionally
runs its own orphan-row check on `encounter_medications` → `encounters`
before reporting success.

| Table | Column | References |
|---|---|---|
| `encounters` | `admission_type_id` | `admission_type.admission_type_id` |
| `encounters` | `discharge_disposition_id` | `discharge_disposition.discharge_disposition_id` |
| `encounters` | `admission_source_id` | `admission_source.admission_source_id` |
| `encounter_medications` | `encounter_id` | `encounters.encounter_id` |
| `encounter_medications` | `medication_name` | `medications.medication_name` |

## 7. How the database was built and verified

```bash
python3 build_database.py
```

This is idempotent — it deletes any existing `diabetic_hospitals.duckdb` and
rebuilds it from `data/diabetic_data.csv` + `data/IDS_mapping.csv` every time.
It ends by asserting expected row counts for every table and checking for
orphaned `encounter_medications` rows.

Independently re-verified (outside the build script) against the raw CSV:

- `readmitted` breakdown: `NO` 54,864 / `>30` 35,545 / `<30` 11,357 — matches.
- NULL counts: `race` 2,273 / `weight` 98,569 / `payer_code` 40,256 /
  `medical_specialty` 49,949 — matches the raw `'?'` counts exactly.
- `max_glu_serum` / `a1c_result` still contain `'None'` (not `NULL`) — confirmed.
- Every `admission_type_id` / `discharge_disposition_id` / `admission_source_id`
  value present in `diabetic_data.csv` exists in the corresponding lookup
  table — confirmed before the FK constraints were even added (0 orphans).
- No duplicate `encounter_id` values in the source CSV — confirmed (0 of
  101,766 rows collide), which is why `encounter_id` is a safe `PRIMARY KEY`.
- `COUNT(DISTINCT encounter_id)` in `encounter_medications` = 78,363, which
  equals `COUNT(*) FROM encounters WHERE diabetes_med = 'Yes'` exactly — a
  cross-check that the wide→long medication reshape didn't drop or invent rows.

## 8. Known caveats

- **`weight` is 96.9% `NULL`.** It's kept in the schema (it's part of the
  original clinical record), but any query that groups or filters by it is
  working with a ~3% sample of encounters — call that out explicitly if you
  use it in class, don't treat it like a normal column.
- **This is one study's coding of ICD-9 diagnoses, admission types, etc.** —
  useful for teaching SQL patterns, not a source to cite for real clinical
  conclusions.
- **`gender` includes 3 rows of `'Unknown/Invalid'`** — a real value in the
  source data, not a loading artifact. Decide deliberately whether to filter
  it out per-query rather than silently ignoring it.
