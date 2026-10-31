-- =============================================================================
-- database_schema.sql
--
-- Diabetes 130-US Hospitals (1999-2008) — DuckDB schema
-- Week 5 (Advanced SQL) — MSIS-2402
--
-- This file is the single source of truth for the schema. build_database.py
-- reads and executes this exact file — see database_schema.md for the full
-- explanation of every table and design decision made here.
--
-- Six tables:
--   4 small lookup/dimension tables : admission_type, discharge_disposition,
--                                      admission_source, medications
--   2 fact tables                   : encounters (one row per hospital
--                                      encounter), encounter_medications
--                                      (one row per medication actually
--                                      prescribed/adjusted during an encounter)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Lookup table: admission_type
-- Source: IDS_mapping.csv, block 1 (8 rows)
-- -----------------------------------------------------------------------------
CREATE TABLE admission_type (
    admission_type_id  INTEGER PRIMARY KEY,
    description         VARCHAR NOT NULL
);

-- -----------------------------------------------------------------------------
-- Lookup table: discharge_disposition
-- Source: IDS_mapping.csv, block 2 (30 rows)
-- -----------------------------------------------------------------------------
CREATE TABLE discharge_disposition (
    discharge_disposition_id  INTEGER PRIMARY KEY,
    description                 VARCHAR NOT NULL
);

-- -----------------------------------------------------------------------------
-- Lookup table: admission_source
-- Source: IDS_mapping.csv, block 3 (25 rows)
-- -----------------------------------------------------------------------------
CREATE TABLE admission_source (
    admission_source_id  INTEGER PRIMARY KEY,
    description            VARCHAR NOT NULL
);

-- -----------------------------------------------------------------------------
-- Lookup table: medications
-- The 23 wide medication columns in the raw CSV are normalized into the long
-- (EAV-style) encounter_medications fact table below. This dimension table
-- lists the 21 medications that ever vary in the data (excludes `examide` and
-- `citoglipton`, which are literally 'No' for all 101,766 rows and so never
-- produce a row in encounter_medications — see database_schema.md).
-- -----------------------------------------------------------------------------
CREATE TABLE medications (
    medication_name  VARCHAR PRIMARY KEY,
    is_combination    BOOLEAN NOT NULL   -- TRUE for two-drug combination medications
                                          -- (name contains a hyphen, e.g. 'glyburide-metformin')
);

-- -----------------------------------------------------------------------------
-- Fact table: encounters
-- One row per hospital encounter (101,766 rows). Grain: encounter_id.
-- A single patient (patient_nbr) may appear in many encounters (up to 40 in
-- this data) — that repetition is what makes window-function and self-join
-- queries over this table interesting.
--
-- Renamed from the source CSV for consistent snake_case naming:
--   A1Cresult    -> a1c_result
--   change       -> change_made
--   diabetesMed  -> diabetes_med
--
-- '?' (the source file's missing-value marker) is converted to real SQL NULL
-- for race, weight, payer_code, medical_specialty, diag_1, diag_2, diag_3
-- during load. max_glu_serum and a1c_result are NOT NULL-cleaned: their
-- literal value 'None' is a meaningful clinical category ("test was not
-- performed"), not a missing value, so it is kept as-is.
-- -----------------------------------------------------------------------------
CREATE TABLE encounters (
    encounter_id               BIGINT PRIMARY KEY,
    patient_nbr                 BIGINT NOT NULL,
    race                         VARCHAR,             -- NULL = missing (2.2% of rows)
    gender                       VARCHAR NOT NULL,    -- 'Male' | 'Female' | 'Unknown/Invalid' (3 rows)
    age                          VARCHAR NOT NULL,    -- 10-year bracket, e.g. '[70-80)'
    weight                       VARCHAR,             -- NULL = missing (96.9% of rows — see notes)
    admission_type_id            INTEGER NOT NULL REFERENCES admission_type(admission_type_id),
    discharge_disposition_id     INTEGER NOT NULL REFERENCES discharge_disposition(discharge_disposition_id),
    admission_source_id          INTEGER NOT NULL REFERENCES admission_source(admission_source_id),
    time_in_hospital             INTEGER NOT NULL,    -- days
    payer_code                   VARCHAR,             -- NULL = missing (39.6% of rows)
    medical_specialty            VARCHAR,             -- NULL = missing (49.1% of rows)
    num_lab_procedures           INTEGER NOT NULL,
    num_procedures                INTEGER NOT NULL,
    num_medications                INTEGER NOT NULL,
    number_outpatient              INTEGER NOT NULL,  -- outpatient visits in prior year
    number_emergency               INTEGER NOT NULL,  -- ER visits in prior year
    number_inpatient               INTEGER NOT NULL,  -- inpatient visits in prior year
    diag_1                          VARCHAR,           -- primary diagnosis, ICD-9 code
    diag_2                          VARCHAR,           -- secondary diagnosis, ICD-9 code
    diag_3                          VARCHAR,           -- additional secondary diagnosis, ICD-9 code
    number_diagnoses                 INTEGER NOT NULL,
    max_glu_serum                     VARCHAR NOT NULL,  -- 'None' | 'Norm' | '>200' | '>300'
    a1c_result                         VARCHAR NOT NULL, -- 'None' | 'Norm' | '>7' | '>8'
    change_made                         VARCHAR NOT NULL, -- 'Ch' (meds changed) | 'No'
    diabetes_med                         VARCHAR NOT NULL, -- 'Yes' | 'No' (any diabetes med prescribed)
    readmitted                            VARCHAR NOT NULL -- 'NO' | '<30' | '>30' (days to readmission)
);

-- -----------------------------------------------------------------------------
-- Fact table: encounter_medications
-- Long/normalized form of the 23 wide medication columns in the source CSV.
-- One row per (encounter, medication) pair where that medication's status was
-- something other than 'No' — i.e. it records medications that were actually
-- prescribed during the encounter and whether the dose was held steady or
-- adjusted. Encounters with no diabetes medication at all simply have zero
-- rows here (join from encounters, don't expect a row per encounter).
-- -----------------------------------------------------------------------------
CREATE TABLE encounter_medications (
    encounter_id      BIGINT  NOT NULL REFERENCES encounters(encounter_id),
    medication_name    VARCHAR NOT NULL REFERENCES medications(medication_name),
    status               VARCHAR NOT NULL,   -- 'Steady' | 'Up' | 'Down'
    PRIMARY KEY (encounter_id, medication_name)
);
