-- ============================================================================
-- database_schema.sql — Book-Crossing DuckDB schema (DDL only)
--
-- Course : MSIS-2402, Santa Clara University
-- Source : Book-Crossing dataset (Cai-Nicolas Ziegler, 2004)
-- Target : books.duckdb
--
-- This file defines STRUCTURE ONLY. No data is loaded here.
-- The ETL — parsing, deduplication, cleaning, orphan quarantine — lives in
-- build_database.py, which executes this file first and then populates it.
--
-- Run standalone with:
--     duckdb books.duckdb < database_schema.sql
--
-- Design rationale for every decision below is documented in
-- database_schema_design.md. Read that first if anything here looks arbitrary.
-- ============================================================================

-- Dropped in reverse dependency order so the FOREIGN KEY on ratings does not
-- block the drop of books/users.
DROP TABLE IF EXISTS ratings_orphaned;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS users;


-- ----------------------------------------------------------------------------
-- books — one row per ISBN
--
-- ISBN is the natural primary key. It is genuinely unique in the source data
-- (271,379 distinct values in 271,379 rows), so no surrogate key is needed.
--
-- publication_year is nullable ON PURPOSE. Roughly 4% of source rows carry a
-- year that is not a year: author names shifted into the column by a bad CSV
-- export ('Ashley Olsen', 'Faye Kellerman'), literal 0, or future dates such as
-- 2050. Those become NULL rather than being discarded, because the *book*
-- record is still valid — only its year is unusable.
-- ----------------------------------------------------------------------------
CREATE TABLE books (
    isbn                VARCHAR     NOT NULL,
    title               VARCHAR     NOT NULL,
    author              VARCHAR,
    publication_year    SMALLINT,
    publisher           VARCHAR,
    image_url           VARCHAR,

    CONSTRAINT pk_books PRIMARY KEY (isbn),

    -- 1376 is the earliest year present in the data; 2004 is when the dataset
    -- was compiled. Anything outside that window was set to NULL during load,
    -- so this constraint documents the cleaning rule and guards future inserts.
    CONSTRAINT ck_books_year CHECK (
        publication_year IS NULL
        OR publication_year BETWEEN 1376 AND 2004
    )
);


-- ----------------------------------------------------------------------------
-- users — one row per User-ID
--
-- The source ships a single free-text `Location` column shaped roughly as
-- 'city, state, country'. We keep the raw string AND the three parsed parts:
-- the raw column preserves fidelity, the parsed columns make the data usable
-- as dimensions for GROUP BY.
--
-- age is nullable and cleaned: about 40% of users never supplied one, and the
-- values that survive include impossible entries (ages of 0 and 244). Values
-- outside 5-100 are stored as NULL.
-- ----------------------------------------------------------------------------
CREATE TABLE users (
    user_id             INTEGER     NOT NULL,
    location_raw        VARCHAR,
    city                VARCHAR,
    state               VARCHAR,
    country             VARCHAR,
    age                 SMALLINT,

    CONSTRAINT pk_users PRIMARY KEY (user_id),

    CONSTRAINT ck_users_age CHECK (
        age IS NULL OR age BETWEEN 5 AND 100
    )
);


-- ----------------------------------------------------------------------------
-- ratings — the fact table; one row per (user, book) pair
--
-- Composite primary key. Verified against the source: zero natural duplicates
-- on (user_id, isbn), and zero cases where the same pair carries conflicting
-- ratings. Any duplicate you find here was injected by inject_duplicates.py.
--
-- is_explicit is a derived convenience column, not new information. In the
-- source, a rating of 0 does NOT mean "rated zero out of ten" — it means the
-- user interacted with the book without scoring it (an implicit rating).
-- 62% of all rows are implicit. Averaging without excluding them produces a
-- number that is wrong but entirely plausible-looking, which is the single
-- most dangerous trap in this dataset. The flag makes the distinction
-- impossible to miss:
--
--     WHERE is_explicit     -- readable, self-documenting
--     WHERE rating > 0      -- identical result, easier to forget
--
-- Both foreign keys are enforced. That is only possible because orphaned rows
-- were diverted to ratings_orphaned during load — see below.
-- ----------------------------------------------------------------------------
CREATE TABLE ratings (
    user_id             INTEGER     NOT NULL,
    isbn                VARCHAR     NOT NULL,
    rating              TINYINT     NOT NULL,
    is_explicit         BOOLEAN     NOT NULL,

    CONSTRAINT pk_ratings PRIMARY KEY (user_id, isbn),
    CONSTRAINT fk_ratings_user FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT fk_ratings_book FOREIGN KEY (isbn)    REFERENCES books (isbn),

    CONSTRAINT ck_ratings_scale CHECK (rating BETWEEN 0 AND 10),

    -- Keeps the derived flag honest: it must always agree with rating.
    CONSTRAINT ck_ratings_explicit CHECK (is_explicit = (rating > 0))
);


-- ----------------------------------------------------------------------------
-- ratings_orphaned — quarantine
--
-- 118,589 source ratings (10.3%) reference an ISBN that does not appear in
-- books.csv. They are not corrupt: the user really did rate something. The
-- book record is simply missing from the catalogue extract.
--
-- Deleting them would destroy evidence. Leaving them in `ratings` would make
-- the FOREIGN KEY above impossible to declare. Quarantining resolves the
-- conflict: `ratings` stays referentially perfect, and the excluded rows remain
-- fully queryable and countable.
--
-- Deliberately NO foreign key on isbn — that is the entire point of the table.
-- The user_id FK is kept, because every orphan's user does exist.
-- ----------------------------------------------------------------------------
CREATE TABLE ratings_orphaned (
    user_id             INTEGER     NOT NULL,
    isbn                VARCHAR     NOT NULL,
    rating              TINYINT     NOT NULL,
    is_explicit         BOOLEAN     NOT NULL,

    CONSTRAINT pk_ratings_orphaned PRIMARY KEY (user_id, isbn),
    CONSTRAINT fk_orphaned_user FOREIGN KEY (user_id) REFERENCES users (user_id),

    CONSTRAINT ck_orphaned_scale CHECK (rating BETWEEN 0 AND 10)
);


-- ----------------------------------------------------------------------------
-- Table and column comments
-- Visible in DuckDB via:  SELECT * FROM duckdb_tables();  /  duckdb_columns();
-- ----------------------------------------------------------------------------
COMMENT ON TABLE books            IS 'Book catalogue, one row per ISBN. Deduplicated on load.';
COMMENT ON TABLE users            IS 'Registered users, one row per User-ID. Location parsed into city/state/country.';
COMMENT ON TABLE ratings          IS 'Fact table. One row per (user, book). Referentially complete.';
COMMENT ON TABLE ratings_orphaned IS 'Quarantined ratings whose ISBN is absent from books. Excluded from ratings to permit the FK.';

COMMENT ON COLUMN books.publication_year   IS 'NULL where the source value was non-numeric, zero, or outside 1376-2004.';
COMMENT ON COLUMN books.image_url          IS 'Large cover image. Small/medium variants differ only by the size code in the filename.';
COMMENT ON COLUMN users.location_raw       IS 'Unparsed source Location string, retained for auditing the city/state/country split.';
COMMENT ON COLUMN users.age                IS 'NULL where absent in source or outside the plausible range 5-100.';
COMMENT ON COLUMN ratings.rating           IS '1-10 explicit score, or 0 meaning implicit (interacted, not scored).';
COMMENT ON COLUMN ratings.is_explicit      IS 'Derived: rating > 0. Filter on this to exclude implicit interactions.';
