import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Notebook 1: Build the Book-Crossing DuckDB Database

    This notebook turns three messy CSV files into a clean, constraint-enforced
    DuckDB database called **`books.duckdb`**.

    | Source file | Rows | Contents |
    |---|---|---|
    | `data/books.csv` | 271,419 | Book catalogue — ISBN, title, author, year, publisher |
    | `data/users.csv` | 278,883 | Users — ID, free-text location, age |
    | `data/ratings.csv` | 1,149,830 | Ratings — who rated what, 0–10 |

    Those counts include two sets of records added on purpose before the build:

    * **Duplicates** from `inject_duplicates.py` — 20 users, 30 books, 50 ratings.
      Removing them is one of the jobs of this notebook.
    * **Unrated records** from `inject_unrated.py` — 5 users and 10 books that no
      one rates, so the anti-join queries in the analysis notebook have a small,
      checkable answer. These are kept, not removed.

    ## What this notebook does

    | Step | Task |
    |---|---|
    | 1 | Show why a naive CSV read **silently loses 70% of the ratings** |
    | 2 | Repair the mojibake in 8,669 damaged lines |
    | 3 | Parse all three files correctly into raw staging tables |
    | 4 | Detect the duplicate rows |
    | 5 | Deduplicate — and explain *why* we use `QUALIFY ROW_NUMBER()` |
    | 6 | Create the schema from `database_schema.sql`, then clean and load |
    | 7 | Quarantine ratings that reference a missing book |
    | 8 | Verify every claim we just made |
    | 9 | Report the finished database |

    Design decisions are explained in **`database_schema_design.md`**.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    """)
    return


@app.cell
def _():
    import os
    from pathlib import Path

    import duckdb

    import repair_encoding

    HERE = Path(__file__).parent if "__file__" in dir() else Path.cwd()
    DATA_DIR = HERE / "data"
    DB_FILE = HERE / "books.duckdb"
    SCHEMA_FILE = HERE / "database_schema.sql"

    # Always rebuild from scratch so the notebook is idempotent.
    if DB_FILE.exists():
        os.remove(DB_FILE)
        print(f"Removed existing {DB_FILE.name}")

    con = duckdb.connect(str(DB_FILE))
    print(f"Connected to {DB_FILE.name} (DuckDB {duckdb.__version__})")
    return DATA_DIR, SCHEMA_FILE, con, repair_encoding


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 1 — The trap: a naive CSV read loses 70% of the data

    These files are **not** ordinary CSVs:

    * the delimiter is a **semicolon**, not a comma
    * every field is wrapped in double quotes, but **some fields contain a stray
      unmatched quote**, which breaks the standard CSV quoting rules
    * `books.csv` and `users.csv` carry **double-encoded** text that is not
      valid UTF-8 (Step 2 repairs this)
    * line endings are Windows **CRLF**

    Watch what happens when we let DuckDB's parser apply the CSV standard
    strictly. It does not crash. It does not warn. It just returns fewer rows.
    """)
    return


@app.cell
def _(DATA_DIR, con):
    _naive = con.execute(f"""
        SELECT COUNT(*) FROM read_csv(
            '{DATA_DIR}/ratings.csv',
            delim = ';', quote = '"', header = true,
            ignore_errors = true          -- skip rows that break the standard
        )
    """).fetchall()[0][0]

    _actual_lines = 1_149_830   # verified with `wc -l`, minus the header

    print(f"Rows a naive read returns : {_naive:>10,}")
    print(f"Rows actually in the file : {_actual_lines:>10,}")
    print(f"Silently discarded        : {_actual_lines - _naive:>10,} "
          f"({100 * (_actual_lines - _naive) / _actual_lines:.1f}%)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **That is the most dangerous kind of data-quality bug**: the load *succeeded*.
    Nothing turned red. Every downstream number would have been computed from
    less than a third of the data, and looked entirely reasonable.

    ### A second, better-hidden problem

    Disabling the quote character rescues the missing rows, but a subtler bug
    survives. Look at what a naive split on `;` does to this line:

    ```
    "0393045218";"The Mummies of Urumchi";"E. J. W. Barber";"1999";"W. W. Norton &amp; Company";...
    ```

    The publisher contains `&amp;` — the HTML escape for `&`. **That escape ends
    in a semicolon**, which is our delimiter. The parser splits inside it, and
    every field after that point shifts one position to the left.

    **20,464 books (7.5% of the file) contain `&amp;`.** In each one the author
    lands in the title column, the year lands in the author column, and a name
    lands in the year column. This is the true source of the "author names in the
    publication year" corruption — values like `'Ashley Olsen'` and
    `'Faye Kellerman'` sitting in a column that should hold integers.

    ### The fix for both problems

    1. Read each line **whole**, using a delimiter byte (`\x01`) that appears
       nowhere in the file.
    2. Decode the HTML entities — `&amp;` → `&`, `&lt;` → `<` — so no escape
       contains a delimiter any more.
    3. *Then* split on `;` and strip the quotes ourselves.

    Doing the replacement before the split is the whole trick. Afterwards would
    be too late; the damage is done at split time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 2 — Repair the character encoding

    One more injury has to be dealt with before any parsing. 3.2% of the lines in
    `books.csv` look like this:

    | Stored in the file | Should read |
    |---|---|
    | `Der illustrierte Mann. ErzÃÂ¤hlungen.` | `Erzählungen` |
    | `El guardiÃ¡n entre el centeno` | `guardián` |
    | `LÃ?Â¼bbe` | `Lübbe` |

    This is **mojibake**. UTF-8 bytes were decoded as Latin-1 and re-encoded as
    UTF-8 — twice — so every accented character expanded into two or four bytes
    of garbage. A later lossy conversion also replaced the control byte `0x83`
    with a literal `?`, which is where the `Ã?` sequences come from.

    `repair_encoding.py` reverses this: restore the clobbered byte, then apply
    `encode('latin-1').decode('utf-8')` repeatedly until the text stops changing.
    **8,004 of 8,669 damaged lines (92.3%) are fully recovered.** The other 665
    lost bytes permanently and are left untouched rather than guessed at.

    Repaired copies are written as `data/*.utf8.csv`. The originals stay in place
    so the "before" remains inspectable.
    """)
    return


@app.cell
def _(repair_encoding):
    # Regenerate whenever the source CSV is newer than its repaired copy. Testing
    # only for existence would mean that appending rows to a source file has no
    # effect on the database, silently and without error.
    for _name in repair_encoding.TARGETS:
        _src = repair_encoding.DATA_DIR / _name
        _out = _src.with_suffix(".utf8.csv")
        if repair_encoding.is_stale(_src, _out):
            _r = repair_encoding.process(_src)
            print(f"{_out.name:<20} {_r['damaged_lines']:>6,} damaged  "
                  f"{_r['fully_repaired']:>6,} repaired  "
                  f"{_r['still_damaged']:>4,} residual")
        else:
            print(f"{_out.name:<20} up to date")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 3 — Parse all three files into raw staging tables

    Staging tables hold the data **exactly as it appears in the file**, with only
    parsing and quote-stripping applied. No cleaning yet. This separation
    matters: if a later cleaning rule turns out to be wrong, we can re-derive
    from staging without re-reading 120 MB of CSV.

    ### Reading fields from the end, not the start

    After decoding, 99.6% of book lines split into exactly 8 fields. The other
    988 contain a **genuine** semicolon inside the title, so counting fields
    from the left would misalign them.

    The last three fields are always image URLs, so we count from the **right**
    instead, where the layout is stable:

    | Field | Position from the end |
    |---|---|
    | `image_url` (large) | `f[len]` |
    | `publisher` | `f[len-3]` |
    | `year` | `f[len-4]` |
    | `author` | `f[len-5]` |
    | `title` | everything between `f[2]` and `f[len-6]`, rejoined with `;` |

    This one expression handles the clean rows and the messy ones identically.
    `users.csv` gets the same treatment for its ~137 multi-semicolon locations.
    """)
    return


@app.cell
def _(DATA_DIR, con):
    # Read whole lines (\x01 appears nowhere in these files), decode the HTML
    # entities whose trailing ';' would otherwise be read as a delimiter, then
    # split. Entity decoding MUST happen before the split.
    con.execute(f"""
        CREATE OR REPLACE TEMP TABLE books_lines AS
        SELECT str_split(
                   replace(replace(line, '&amp;', '&'), '&lt;', '<'),
                   ';'
               ) AS f
        FROM read_csv(
            '{DATA_DIR}/books.utf8.csv',
            delim = '\x01', quote = '', header = false, skip = 1,
            columns = {{'line': 'VARCHAR'}}, encoding = 'utf-8',
            strict_mode = false, ignore_errors = true
        );

        CREATE OR REPLACE TEMP TABLE books_raw AS
        SELECT
            trim(both '"' from f[1])                                        AS isbn,
            trim(both '"' from array_to_string(list_slice(f, 2, len(f) - 6), ';')) AS title,
            trim(both '"' from f[len(f) - 5])                               AS author,
            trim(both '"' from f[len(f) - 4])                               AS year_raw,
            trim(both '"' from f[len(f) - 3])                               AS publisher,
            trim(both '"' from f[len(f)])                                   AS image_url
        FROM books_lines
        WHERE len(f) >= 8;

        CREATE OR REPLACE TEMP TABLE users_raw AS
        SELECT
            trim(both '"' from f[1])                                        AS user_id_raw,
            trim(both '"' from array_to_string(list_slice(f, 2, len(f) - 1), ';')) AS location_raw,
            trim(both '"' from f[len(f)])                                   AS age_raw
        FROM (
            SELECT str_split(line, ';') AS f
            FROM read_csv(
                '{DATA_DIR}/users.utf8.csv',
                delim = '\x01', quote = '', header = false, skip = 1,
                columns = {{'line': 'VARCHAR'}}, encoding = 'utf-8',
                strict_mode = false, ignore_errors = true
            )
        )
        WHERE len(f) >= 3;

        CREATE OR REPLACE TEMP TABLE ratings_raw AS
        SELECT
            trim(both '"' from f[1]) AS user_id_raw,
            trim(both '"' from f[2]) AS isbn,
            trim(both '"' from f[3]) AS rating_raw
        FROM (
            SELECT str_split(line, ';') AS f
            FROM read_csv(
                '{DATA_DIR}/ratings.csv',
                delim = '\x01', quote = '', header = false, skip = 1,
                columns = {{'line': 'VARCHAR'}},
                strict_mode = false, ignore_errors = true
            )
        )
        WHERE len(f) >= 3;
    """)

    con.execute("""
        SELECT 'books_raw'   AS staging_table, COUNT(*) AS rows_loaded FROM books_raw
        UNION ALL SELECT 'users_raw',   COUNT(*) FROM users_raw
        UNION ALL SELECT 'ratings_raw', COUNT(*) FROM ratings_raw
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Proof the entity fix worked

    Before decoding, `'Angels &amp; Demons'` split into a title of
    `'Angels &amp'` and an author of `' Demons'`. After decoding, the title,
    author and year all land in the right columns.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT isbn, title, author, year_raw, publisher
        FROM books_raw
        WHERE title IN ('Angels & Demons', 'The Mummies of Urumchi')
           OR title LIKE 'Mary-Kate & Ashley Switching%'
        ORDER BY title
        LIMIT 5
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 4 — Find the duplicates

    A duplicate is a row whose **key** already appeared earlier in the file. The
    key differs per table:

    | Table | Key | Why |
    |---|---|---|
    | `books_raw` | `isbn` | One catalogue entry per ISBN |
    | `users_raw` | `user_id` | One profile per user |
    | `ratings_raw` | `(user_id, isbn)` | A user rates a given book at most once |

    `COUNT(*) - COUNT(DISTINCT key)` gives the number of surplus rows directly.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT 'books'   AS table_name, 'isbn'            AS key_columns,
               COUNT(*) AS total_rows, COUNT(DISTINCT isbn) AS distinct_keys,
               COUNT(*) - COUNT(DISTINCT isbn) AS duplicate_rows
        FROM books_raw
        UNION ALL
        SELECT 'users', 'user_id',
               COUNT(*), COUNT(DISTINCT user_id_raw),
               COUNT(*) - COUNT(DISTINCT user_id_raw)
        FROM users_raw
        UNION ALL
        SELECT 'ratings', 'user_id + isbn',
               COUNT(*), COUNT(DISTINCT (user_id_raw, isbn)),
               COUNT(*) - COUNT(DISTINCT (user_id_raw, isbn))
        FROM ratings_raw
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **30 books, 20 users, 50 ratings** — exactly what `inject_duplicates.py`
    added. Let us look at a few before deleting them, so we can confirm they
    really are identical copies and not legitimately different records that
    happen to share a key.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT isbn, title, author, publication_year_raw, n_copies
        FROM (
            SELECT isbn, ANY_VALUE(title) AS title, ANY_VALUE(author) AS author,
                   ANY_VALUE(year_raw)    AS publication_year_raw,
                   COUNT(*)               AS n_copies,
                   COUNT(DISTINCT (title, author, year_raw, publisher)) AS n_variants
            FROM books_raw
            GROUP BY isbn
            HAVING COUNT(*) > 1
        )
        WHERE n_variants = 1     -- every copy is byte-identical
        ORDER BY title
        LIMIT 8
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 5 — Deduplicate

    There are two standard ways to remove duplicate rows in SQL. They are **not**
    interchangeable, and choosing the wrong one is a common mistake.

    ### Option A — `SELECT DISTINCT`

    ```sql
    SELECT DISTINCT * FROM books_raw;
    ```

    Collapses rows that are identical across **every column**. Simple, but it has
    a hard limitation: if two rows share an ISBN and differ in even one other
    column — a trailing space in the publisher, a different edition year —
    `DISTINCT` keeps **both**, and the primary key still fails.

    ### Option B — `QUALIFY ROW_NUMBER()`  ← what we use

    ```sql
    SELECT * FROM books_raw
    QUALIFY ROW_NUMBER() OVER (PARTITION BY isbn ORDER BY title) = 1;
    ```

    Read it as three parts:

    | Clause | Meaning |
    |---|---|
    | `PARTITION BY isbn` | Group the rows into one bucket per ISBN |
    | `ORDER BY title` | Decide the ranking **within** each bucket |
    | `= 1` | Keep only the top-ranked row from each bucket |

    `ROW_NUMBER()` numbers the rows in each bucket 1, 2, 3, …; `QUALIFY` then
    filters on that number. `QUALIFY` is to window functions what `HAVING` is to
    aggregates — a `WHERE` clause that runs *after* the window is computed.
    (`WHERE ROW_NUMBER() ... = 1` is a syntax error; the window function does not
    exist yet at `WHERE` time.)

    **Why B is the right default:** it guarantees exactly one row per key *no
    matter how much the duplicates disagree*, and the `ORDER BY` lets you state
    which survivor you want — newest record, most complete record, highest
    rating. `DISTINCT` gives you no such control.

    Here the injected duplicates are byte-identical, so both options happen to
    return the same answer. We use B because it is the technique that keeps
    working when the data gets worse.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 6 — Clean while loading

    Deduplication and cleaning happen in the same `INSERT ... SELECT`. Three
    cleaning rules apply:

    ### `publication_year` — still imperfect after the entity fix

    Decoding `&amp;` in Step 2 repaired the vast majority of this column: rows
    whose "year" was a non-numeric string fell from **6,056 to 30**. What remains
    is genuine source corruption rather than a parsing artifact — a literal `0`
    (4,589 rows, meaning "unknown"), and future dates up to `2050`.

    `try_cast` returns `NULL` rather than raising on the non-numeric survivors,
    and `BETWEEN 1376 AND 2004` discards the impossible ones — 1376 is the
    earliest year present, 2004 is when the dataset was compiled. The **book** is
    always kept; only its year becomes `NULL`.

    ### `age` — 40% missing, plus impossible values

    Ages of 0 and 244 appear in the source. Anything outside 5–100 becomes `NULL`.

    ### `location` — one free-text field, three useful dimensions

    `'nyc, new york, usa'` splits into city / state / country. We take the
    **first** element as city and the **last** as country (`[-1]`), rather than
    positions 1/2/3, because 1,667 rows do not have exactly two commas. The
    original string is retained in `location_raw` so the split can be audited.
    """)
    return


@app.cell
def _(SCHEMA_FILE, con):
    # Create the real tables, constraints and comments from the DDL file.
    con.execute(SCHEMA_FILE.read_text())

    con.execute("""
        INSERT INTO books
        SELECT
            isbn,
            title,
            nullif(author, '')    AS author,
            CASE WHEN try_cast(year_raw AS INTEGER) BETWEEN 1376 AND 2004
                 THEN try_cast(year_raw AS INTEGER)
            END                   AS publication_year,
            nullif(publisher, '') AS publisher,
            nullif(image_url, '') AS image_url
        FROM books_raw
        WHERE isbn <> '' AND title <> ''
        QUALIFY ROW_NUMBER() OVER (PARTITION BY isbn ORDER BY title) = 1;
    """)

    # Placeholder strings that mean "no answer". Left as-is they masquerade as
    # real countries: only 3 users say 'n/a', but between them they contribute
    # nearly 7,000 ratings, which is enough to reach a top-10 country list.
    con.execute("""
        CREATE OR REPLACE MACRO clean_place(s) AS
            CASE WHEN lower(trim(s)) IN (
                     '', 'n/a', 'na', 'none', 'null', 'unknown', 'universe',
                     'space', 'earth', 'everywhere', 'somewhere', 'quit',
                     '...', '-', '--', '---', '.'
                 )
                 THEN NULL
                 ELSE trim(s)
            END;
    """)

    con.execute("""
        INSERT INTO users
        SELECT
            user_id, location_raw, city, state, country, age
        FROM (
            SELECT
                try_cast(user_id_raw AS INTEGER)                       AS user_id,
                nullif(location_raw, '')                               AS location_raw,
                clean_place(str_split(location_raw, ',')[1])           AS city,
                CASE WHEN len(str_split(location_raw, ',')) >= 3
                     THEN clean_place(str_split(location_raw, ',')[2])
                END                                                    AS state,
                clean_place(str_split(location_raw, ',')[-1])          AS country,
                CASE WHEN try_cast(age_raw AS INTEGER) BETWEEN 5 AND 100
                     THEN try_cast(age_raw AS INTEGER)
                END                                                    AS age
            FROM users_raw
        )
        WHERE user_id IS NOT NULL
        QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY user_id) = 1;
    """)

    con.execute("""
        SELECT 'books' AS table_name, COUNT(*) AS rows_loaded FROM books
        UNION ALL SELECT 'users', COUNT(*) FROM users
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 7 — Quarantine the orphaned ratings

    **118,589 ratings (10.3%) reference an ISBN that does not exist in
    `books.csv`.** The user really did rate a book; the catalogue extract is
    simply missing that title.

    This creates a conflict. We want a `FOREIGN KEY` on `ratings.isbn` — it is
    what makes the database a *database* rather than three loose tables. But a
    foreign key cannot be declared while 118,589 rows violate it.

    Three ways out:

    | Option | Consequence |
    |---|---|
    | Delete the orphans | FK works, but 118,589 real observations destroyed |
    | Skip the FK | All data kept, but nothing prevents future corruption, and every `JOIN` silently drops 10% of rows |
    | **Quarantine** ← chosen | FK works **and** the rows stay queryable |

    Quarantining routes the orphans to a second table, `ratings_orphaned`, that
    deliberately has **no** foreign key on `isbn`. `ratings` becomes
    referentially perfect; the excluded rows remain available for anyone who
    asks what was left out.

    We also verify the *other* foreign key — that every rating belongs to a real
    user — and report any row that fails both.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        CREATE OR REPLACE TEMP TABLE ratings_dedup AS
        SELECT user_id, isbn, rating, rating > 0 AS is_explicit
        FROM (
            SELECT
                try_cast(user_id_raw AS INTEGER) AS user_id,
                isbn,
                try_cast(rating_raw AS TINYINT)  AS rating
            FROM ratings_raw
        )
        WHERE user_id IS NOT NULL
          AND isbn <> ''
          AND rating BETWEEN 0 AND 10
        QUALIFY ROW_NUMBER() OVER (PARTITION BY user_id, isbn ORDER BY rating) = 1;
    """)

    con.execute("""
        INSERT INTO ratings
        SELECT d.user_id, d.isbn, d.rating, d.is_explicit
        FROM ratings_dedup d
        WHERE EXISTS (SELECT 1 FROM books b WHERE b.isbn    = d.isbn)
          AND EXISTS (SELECT 1 FROM users u WHERE u.user_id = d.user_id);
    """)

    con.execute("""
        INSERT INTO ratings_orphaned
        SELECT d.user_id, d.isbn, d.rating, d.is_explicit
        FROM ratings_dedup d
        WHERE NOT EXISTS (SELECT 1 FROM books b WHERE b.isbn    = d.isbn)
          AND     EXISTS (SELECT 1 FROM users u WHERE u.user_id = d.user_id);
    """)

    con.execute("""
        SELECT
            (SELECT COUNT(*) FROM ratings_dedup)     AS after_dedup,
            (SELECT COUNT(*) FROM ratings)           AS loaded_clean,
            (SELECT COUNT(*) FROM ratings_orphaned)  AS quarantined_missing_book,
            (SELECT COUNT(*) FROM ratings_dedup d
             WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = d.user_id))
                                                     AS dropped_missing_user
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 8 — Verify every claim

    A build script that reports success without checking is worth nothing. Each
    query below tests one specific promise made earlier in this notebook.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 8a. Deduplication actually removed exactly the injected rows
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT 'books' AS table_name,
               (SELECT COUNT(*) FROM books_raw)                       AS staged,
               (SELECT COUNT(*) FROM books)                           AS final,
               (SELECT COUNT(*) FROM books_raw) -
               (SELECT COUNT(*) FROM books)                           AS removed,
               30                                                     AS expected
        UNION ALL
        SELECT 'users',
               (SELECT COUNT(*) FROM users_raw),
               (SELECT COUNT(*) FROM users),
               (SELECT COUNT(*) FROM users_raw) - (SELECT COUNT(*) FROM users),
               20
        UNION ALL
        SELECT 'ratings',
               (SELECT COUNT(*) FROM ratings_raw),
               (SELECT COUNT(*) FROM ratings) + (SELECT COUNT(*) FROM ratings_orphaned),
               (SELECT COUNT(*) FROM ratings_raw)
                 - (SELECT COUNT(*) FROM ratings)
                 - (SELECT COUNT(*) FROM ratings_orphaned),
               50
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Exactly 30, 20 and 50 — matching the injection manifest precisely.**

    For `ratings`, `final` is the sum of `ratings` and `ratings_orphaned`, because
    the quarantine split in Step 7 sends rows to two tables. Adding them back
    together is what makes the comparison honest: the only rows that disappeared
    between staging and loading are the duplicates.

    Note also what is *not* here. An earlier version of this notebook lost extra
    rows to unparseable IDs and embedded newlines; the whole-line parser in Step 3
    recovers them. The next cell confirms there is nothing left being quietly
    discarded.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT
            (SELECT COUNT(*) FROM ratings_raw)                          AS staged_rows,
            (SELECT COUNT(*) FROM ratings_raw
             WHERE try_cast(user_id_raw AS INTEGER) IS NULL)            AS bad_user_id,
            (SELECT COUNT(*) FROM ratings_raw
             WHERE try_cast(rating_raw AS TINYINT) IS NULL
                OR try_cast(rating_raw AS TINYINT) NOT BETWEEN 0 AND 10) AS bad_rating,
            (SELECT COUNT(*) FROM ratings_raw WHERE isbn = '')          AS empty_isbn
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 8b. Primary keys hold
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT 'books.isbn' AS primary_key,
               COUNT(*) AS rows, COUNT(DISTINCT isbn) AS distinct_keys,
               COUNT(*) = COUNT(DISTINCT isbn) AS is_unique
        FROM books
        UNION ALL
        SELECT 'users.user_id', COUNT(*), COUNT(DISTINCT user_id),
               COUNT(*) = COUNT(DISTINCT user_id)
        FROM users
        UNION ALL
        SELECT 'ratings.(user_id, isbn)', COUNT(*), COUNT(DISTINCT (user_id, isbn)),
               COUNT(*) = COUNT(DISTINCT (user_id, isbn))
        FROM ratings
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 8c. Foreign keys hold

    Both counts must be zero. If they are, every `JOIN` in the analysis notebook
    is guaranteed to be lossless — nothing disappears silently.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT
            (SELECT COUNT(*) FROM ratings r
             WHERE NOT EXISTS (SELECT 1 FROM books b WHERE b.isbn = r.isbn))
                AS ratings_with_missing_book,
            (SELECT COUNT(*) FROM ratings r
             WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = r.user_id))
                AS ratings_with_missing_user
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 8d. Cleaning rules were applied
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT 'books.publication_year' AS column_name,
               COUNT(*) AS total,
               COUNT(*) FILTER (WHERE publication_year IS NULL) AS nulled_out,
               MIN(publication_year) AS min_kept, MAX(publication_year) AS max_kept
        FROM books
        UNION ALL
        SELECT 'users.age', COUNT(*),
               COUNT(*) FILTER (WHERE age IS NULL), MIN(age), MAX(age)
        FROM users
        UNION ALL
        SELECT 'users.country', COUNT(*),
               COUNT(*) FILTER (WHERE country IS NULL), NULL, NULL
        FROM users
        ORDER BY 1
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 8e. The implicit-rating flag agrees with the rating
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT
            is_explicit,
            COUNT(*)                                    AS n_ratings,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct,
            MIN(rating) AS min_rating, MAX(rating) AS max_rating
        FROM ratings
        GROUP BY is_explicit
        ORDER BY is_explicit
    """).df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Step 9 — Final database

    The build is complete. `books.duckdb` now contains four tables with enforced
    primary keys, foreign keys and check constraints.
    """)
    return


@app.cell
def _(con):
    con.execute("""
        SELECT
            t.table_name,
            t.estimated_size AS approx_rows,
            t.comment        AS description
        FROM duckdb_tables() t
        ORDER BY t.table_name
    """).df()
    return


@app.cell
def _(con):
    _summary = con.execute("""
        SELECT
            (SELECT COUNT(*) FROM books)            AS books,
            (SELECT COUNT(*) FROM users)            AS users,
            (SELECT COUNT(*) FROM ratings)          AS ratings,
            (SELECT COUNT(*) FROM ratings_orphaned) AS orphaned
    """).fetchall()[0]

    print("books.duckdb built successfully")
    print(f"  books            {_summary[0]:>10,}")
    print(f"  users            {_summary[1]:>10,}")
    print(f"  ratings          {_summary[2]:>10,}")
    print(f"  ratings_orphaned {_summary[3]:>10,}")
    print("\nNext: open analyze_data.py for the 18 analysis queries.")

    con.close()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## What to take away

    1. **A successful load is not a correct load.** The naive read returned
       340,619 of 1,149,830 rows and raised no error. Always reconcile row
       counts against the source.
    2. **Stage first, clean second.** Raw staging tables make every cleaning
       rule reversible.
    3. **`QUALIFY ROW_NUMBER()` beats `DISTINCT`** for deduplication, because it
       works on a key rather than the whole row, and lets you choose the survivor.
    4. **Constraints are documentation that executes.** The `CHECK` on
       `publication_year` states the cleaning rule *and* enforces it forever.
    5. **Quarantine beats deleting.** `ratings_orphaned` keeps 118,589
       observations that a `DELETE` would have destroyed, without weakening the
       foreign key on `ratings`.
    """)
    return


if __name__ == "__main__":
    app.run()
