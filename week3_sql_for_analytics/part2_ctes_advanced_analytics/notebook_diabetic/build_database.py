#!/usr/bin/env python3
"""
build_database.py

Builds a persistent (on-disk) DuckDB database for the Diabetes 130-US
Hospitals (1999-2008) dataset — Week 3 (SQL for Data Analytics), MSIS-2402.

What it does, in order:
    1. Deletes any existing diabetic_hospitals.duckdb so this script is
       always safe to re-run from scratch.
    2. Creates the on-disk database and applies database_schema.sql
       (the single source of truth for the schema — see database_schema.md
       for the full explanation of every table and design decision).
    3. Parses data/IDS_mapping.csv (three lookup tables concatenated in one
       file, separated by a lone-comma line) and loads the three lookup
       tables: admission_type, discharge_disposition, admission_source.
    4. Loads the 21-row medications dimension table.
    5. Reads data/diabetic_data.csv into a temporary staging table (all
       columns as VARCHAR, so '?' can be cleaned uniformly before casting),
       then loads it into two tables:
         - encounters             (one row per hospital encounter)
         - encounter_medications  (long/normalized form of the 23 wide
                                    medication columns, via UNPIVOT)
    6. Runs a handful of sanity checks (row counts, orphan-key checks) and
       prints a summary.

Requires only the `duckdb` Python package — no pandas needed, since DuckDB's
own SQL (read_csv + UNPIVOT) does all the cleaning and reshaping.

Usage:
    python3 build_database.py
"""

import csv
import sys
from pathlib import Path

import duckdb

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SCHEMA_SQL = HERE / "database_schema.sql"
DB_PATH = HERE / "diabetic_hospitals.duckdb"

ENCOUNTERS_CSV = DATA_DIR / "diabetic_data.csv"
IDS_MAPPING_CSV = DATA_DIR / "IDS_mapping.csv"

# The 21 medication columns that actually vary in the data (see
# database_schema.md / database_schema.sql for why `examide` and
# `citoglipton` are excluded: they are 'No' for all 101,766 rows).
MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "insulin", "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone",
]


def parse_ids_mapping(path: Path) -> list[list[tuple[int, str]]]:
    """IDS_mapping.csv holds three lookup tables (admission_type,
    discharge_disposition, admission_source) back to back, each separated by
    a line that's just a bare comma (an empty two-column row), not a truly
    blank line. Returns a list of three [(id, description), ...] blocks, in
    file order."""
    with path.open(encoding="utf-8-sig", newline="") as f:
        raw_lines = [line.rstrip("\r\n") for line in f]

    blocks: list[list[str]] = []
    current: list[str] = []
    for line in raw_lines:
        if line.strip(",").strip() == "":
            if current:
                blocks.append(current)
            current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    if len(blocks) != 3:
        sys.exit(
            f"Expected 3 lookup blocks in {path.name}, found {len(blocks)}. "
            "The file format may have changed — check parse_ids_mapping()."
        )

    parsed = []
    for block in blocks:
        reader = csv.reader(block)
        next(reader)  # header row, e.g. "admission_type_id,description"
        rows = [(int(row[0]), row[1]) for row in reader if row and row[0] != ""]
        parsed.append(rows)
    return parsed


def main() -> None:
    if not ENCOUNTERS_CSV.exists() or not IDS_MAPPING_CSV.exists():
        sys.exit(f"Expected source CSVs under {DATA_DIR} — run this script from its own folder.")

    if DB_PATH.exists():
        print(f"Removing existing database: {DB_PATH.name}")
        DB_PATH.unlink()

    print(f"Creating on-disk DuckDB database: {DB_PATH.name}")
    con = duckdb.connect(str(DB_PATH))  # persistent — a real file, not ':memory:'

    # --- 1. Schema -----------------------------------------------------------
    print("Applying schema from database_schema.sql ...")
    con.execute(SCHEMA_SQL.read_text())

    # --- 2. Lookup tables from IDS_mapping.csv --------------------------------
    print("Loading lookup tables from IDS_mapping.csv ...")
    admission_type_rows, discharge_disposition_rows, admission_source_rows = parse_ids_mapping(IDS_MAPPING_CSV)

    con.executemany("INSERT INTO admission_type VALUES (?, ?)", admission_type_rows)
    con.executemany("INSERT INTO discharge_disposition VALUES (?, ?)", discharge_disposition_rows)
    con.executemany("INSERT INTO admission_source VALUES (?, ?)", admission_source_rows)
    print(
        f"  admission_type: {len(admission_type_rows)} rows | "
        f"discharge_disposition: {len(discharge_disposition_rows)} rows | "
        f"admission_source: {len(admission_source_rows)} rows"
    )

    # --- 3. medications dimension table ---------------------------------------
    print("Loading medications dimension table ...")
    con.executemany(
        "INSERT INTO medications VALUES (?, ?)",
        [(name, "-" in name) for name in MEDICATION_COLUMNS],
    )

    # --- 4. Staging table from diabetic_data.csv ------------------------------
    print("Reading data/diabetic_data.csv into a staging table ...")
    con.execute(
        f"""
        CREATE TEMP TABLE stg_encounters AS
        SELECT *
        FROM read_csv('{ENCOUNTERS_CSV.as_posix()}', header = true, all_varchar = true)
        """
    )
    staged = con.execute("SELECT COUNT(*) FROM stg_encounters").fetchall()[0][0]
    print(f"  staged {staged:,} rows")

    # --- 5. encounters (clean '?' -> NULL, cast types, rename 3 columns) -----
    print("Loading encounters ...")
    con.execute(
        """
        INSERT INTO encounters
        SELECT
            CAST(encounter_id AS BIGINT),
            CAST(patient_nbr AS BIGINT),
            NULLIF(race, '?'),
            gender,
            age,
            NULLIF(weight, '?'),
            CAST(admission_type_id AS INTEGER),
            CAST(discharge_disposition_id AS INTEGER),
            CAST(admission_source_id AS INTEGER),
            CAST(time_in_hospital AS INTEGER),
            NULLIF(payer_code, '?'),
            NULLIF(medical_specialty, '?'),
            CAST(num_lab_procedures AS INTEGER),
            CAST(num_procedures AS INTEGER),
            CAST(num_medications AS INTEGER),
            CAST(number_outpatient AS INTEGER),
            CAST(number_emergency AS INTEGER),
            CAST(number_inpatient AS INTEGER),
            NULLIF(diag_1, '?'),
            NULLIF(diag_2, '?'),
            NULLIF(diag_3, '?'),
            CAST(number_diagnoses AS INTEGER),
            max_glu_serum,          -- 'None' here is a real category, not missing — no NULLIF
            "A1Cresult",
            "change",
            "diabetesMed",
            readmitted
        FROM stg_encounters
        """
    )

    # --- 6. encounter_medications (wide -> long via UNPIVOT) -------------------
    print("Loading encounter_medications (UNPIVOT of 21 medication columns) ...")
    med_col_list = ", ".join(f'"{c}"' if "-" in c else c for c in MEDICATION_COLUMNS)
    con.execute(
        f"""
        INSERT INTO encounter_medications (encounter_id, medication_name, status)
        SELECT CAST(encounter_id AS BIGINT), medication_name, status
        FROM stg_encounters
        UNPIVOT (status FOR medication_name IN ({med_col_list}))
        WHERE status <> 'No'
        """
    )

    con.execute("DROP TABLE stg_encounters")

    # --- 7. Sanity checks --------------------------------------------------
    print("\nRunning sanity checks ...")
    counts = {
        tbl: con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchall()[0][0]
        for tbl in [
            "admission_type", "discharge_disposition", "admission_source",
            "medications", "encounters", "encounter_medications",
        ]
    }
    for tbl, n in counts.items():
        print(f"  {tbl:<24} {n:>10,} rows")

    assert counts["encounters"] == 101766, "expected 101,766 encounters"
    assert counts["admission_type"] == 8
    assert counts["discharge_disposition"] == 30
    assert counts["admission_source"] == 25
    assert counts["medications"] == 21

    orphan_meds = con.execute(
        """
        SELECT COUNT(*) FROM encounter_medications em
        LEFT JOIN encounters e USING (encounter_id)
        WHERE e.encounter_id IS NULL
        """
    ).fetchall()[0][0]
    assert orphan_meds == 0, "found encounter_medications rows with no matching encounter"

    print("\nAll checks passed.")
    print(f"Database ready: {DB_PATH}")

    con.close()


if __name__ == "__main__":
    main()
