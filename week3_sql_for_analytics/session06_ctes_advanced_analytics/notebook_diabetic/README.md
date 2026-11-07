# Diabetes 130-US Hospitals — Advanced SQL with DuckDB

[← Week 3](../../README.md) · [Course home](../../../README.md) · **Week 3 · Session 6 · Example notebook**

A real, de-identified public healthcare dataset — **101,766 hospital
encounters** for **71,518 patients** at 130 US hospitals, 1999–2008 — built
into an on-disk DuckDB database and analyzed with advanced SQL.

| | |
|---|---|
| **Source** | [UCI Machine Learning Repository — Diabetes 130-US Hospitals](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008) |
| **Database** | 6 tables, built by `build_database.py` into `diabetic_hospitals.duckdb` |
| **Notebook** | 13 SQL queries (3 simple · 5 intermediate · 5 intermediate+) and 4 charts |
| **SQL features** | Joins, CTEs, window functions, `QUALIFY`, `PIVOT` |

---

## Quick Start

Run both steps from **inside this folder**.

**1. Build the database** (first time only — the `.duckdb` file is not
included in the repository):

```bash
python3 build_database.py
```

This reads the two CSV files in `data/`, creates the schema, cleans the data,
and writes `diabetic_hospitals.duckdb`. It finishes with row-count and
foreign-key checks, and it is safe to re-run at any time.

**2. Open the notebook:**

```bash
marimo edit notebook_diabetic_marimo.py
```

The notebook connects to the database **read-only**, so it never changes the
data. If you modify the CSV files, re-run step 1.

---

## Files

| File | What it is |
|---|---|
| [`database_schema.md`](database_schema.md) | **Read this first.** The data, the schema, every design decision, and an ER diagram |
| [`database_schema.sql`](database_schema.sql) | The schema itself, run as-is by `build_database.py` |
| [`build_database.py`](build_database.py) | Builds `diabetic_hospitals.duckdb` from the CSV files |
| [`notebook_diabetic_marimo.py`](notebook_diabetic_marimo.py) | The Marimo notebook — queries and charts |
| [`plot_helpers.py`](plot_helpers.py) | Chart functions used by the notebook (`plot_bar`, `plot_hbar`, `plot_pie`, `plot_line`), so the notebook itself stays focused on SQL |
| [`data/`](data/) | Raw source files: `diabetic_data.csv` and `IDS_mapping.csv` |

## Schema at a Glance

| Table | Role |
|---|---|
| `encounters` | Fact table — one row per hospital encounter |
| `encounter_medications` | One row per medication prescribed in an encounter |
| `admission_type` | Lookup |
| `discharge_disposition` | Lookup |
| `admission_source` | Lookup |
| `medications` | Lookup |

**Worth noticing in the build:** the raw file stores 23 medications as 23
separate columns. `build_database.py` reshapes them into the long
`encounter_medications` table with `UNPIVOT` — a normalization step you can
compare with the [normalization tutorial](../../../tutorials/normalization/normalization_tutorial.md).
It also converts the source file's `'?'` placeholders to real `NULL`s and
splits `IDS_mapping.csv`, which packs three lookup tables into one file. Full
details are in [`database_schema.md`](database_schema.md).

---

[← Week 3](../../README.md) · [Course home](../../../README.md)
