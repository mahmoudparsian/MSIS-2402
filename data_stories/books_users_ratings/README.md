# Books, Users & Ratings — a DuckDB + Marimo data story

**MSIS-2402 · Santa Clara University**

---

## 1. What this is

> **A complete, self-contained SQL teaching unit.** It takes three messy real-world
> CSV files, turns them into a properly constrained relational database, and then
> asks 18 progressively harder questions of it — with every step explained.

Everything here is built around one idea: **students should learn SQL against data
that fights back.** Tutorial datasets are clean, so they teach syntax and nothing
else. This one is real — it has broken encodings, a delimiter hiding inside its own
data, missing foreign keys, and a rating scale that contains values which are not
ratings. Working through it teaches SQL *and* the judgment that has to go with it.

The unit is two Marimo notebooks that run in order:

```
   data/*.csv  ──▶  build_database.py  ──▶  books.duckdb  ──▶  analyze_data.py
   (three raw          notebook 1:            4 tables,          notebook 2:
    CSV files)         clean & load         constraints          18 queries
```

**Notebook 1 (`build_database.py`)** is the ETL story. In nine documented steps it
shows why a naive CSV read silently loses 70% of the data, repairs the damage,
deduplicates, cleans, quarantines what cannot be made valid, and then re-verifies
every claim it made in SQL.

**Notebook 2 (`analyze_data.py`)** is the analysis story. Eighteen queries tiered
simple → intermediate → intermediate+, each with an explanation before it and an
interpretation of the result after it. Six produce charts.

---

## 2. What a student learns

Three things, in roughly this order:

**SQL, from `SELECT` to window functions.** The queries are deliberately tiered so
the difficulty ramp is visible. Part 1 is orientation; Part 2 is joins and grouping;
Part 3 is CTEs, `ROW_NUMBER`/`QUALIFY`, `NTILE`, self-joins and window frames.

**That loading data is a skill, not a formality.** Notebook 1 exists because the
single most valuable lesson in the unit is that `read_csv` returned 340,619 of
1,149,830 rows and *raised no error*. Every number downstream would have been wrong
and plausible. Students see this happen before they are told about it.

**That a schema encodes decisions.** Foreign keys, `CHECK` constraints and a
quarantine table are not bureaucracy — each one is a choice with alternatives that
were rejected for stated reasons. `database_schema_design.md` records all of them.

---

## 3. Why this dataset

The Book-Crossing dataset (Ziegler, 2004) was chosen over several alternatives
because it is the rare public dataset that is **genuinely relational and genuinely
real**:

| Requirement | Why it matters | Book-Crossing |
|---|---|---|
| More than one table | Otherwise `JOIN` cannot be taught honestly | ✅ 3 tables, a true many-to-many |
| Real primary keys | Constraints must be declarable | ✅ ISBN and User-ID are genuinely unique |
| Imperfect foreign keys | Referential integrity has to be *engineered* | ✅ 10.3% of ratings reference a missing book |
| Real text | For `LIKE`, string parsing, and encoding work | ✅ titles, authors, free-text locations |
| Observational, not synthetic | Findings should be true statements about the world | ✅ 1.1M real ratings from real people |

Its one real gap: **no timestamps**, so nothing time-based can be taught from it.
That is stated plainly rather than worked around — see §10.

---

## 4. At a glance

| | |
|---|---|
| **Database** | DuckDB, 4 tables, enforced PK / FK / CHECK constraints |
| **Rows** | 271,389 books · 278,862 users · 1,031,175 ratings |
| **Notebooks** | Marimo — `build_database.py`, `analyze_data.py` |
| **Queries** | 18 — 3 simple, 9 intermediate, 6 intermediate+ |
| **Charts** | 6 (incl. one pie), all rendered by `plot_helpers.py` outside the notebooks |
| **Build time** | ~8 seconds |
| **Source** | [Book-Crossing on Kaggle](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset) (Ziegler, 2004) |

**Contents of this file:** [1. What this is](#1-what-this-is) ·
[2. What a student learns](#2-what-a-student-learns) ·
[3. Why this dataset](#3-why-this-dataset) ·
[4. At a glance](#4-at-a-glance) ·
[5. Quick start](#5-quick-start) ·
[6. Every file](#6-every-file-in-this-directory) ·
[7. The database](#7-the-database) ·
[8. The build](#8-what-the-build-notebook-teaches) ·
[9. The 18 queries](#9-the-18-queries) ·
[10. Findings & limitations](#10-findings) ·
[11. Conventions](#11-conventions) ·
[12. Requirements](#12-requirements) ·
[13. Citation](#13-citation)

---

## 5. Quick start

```bash
# The course setup already installs everything needed:
#   duckdb, marimo, pandas, matplotlib

# 1 + 2. Copy the source CSVs from the course repo, then build everything
./build_books_db.sh --clean --verify

# 3. Explore
marimo edit analyze_data.py          # interactive
marimo run  analyze_data.py          # read-only, for students
```

Build takes about 8 seconds. `books.duckdb` comes out around 173 MB — the PK/FK
indexes and the cover-image URLs account for most of it.

### The build script

`build_books_db.sh` runs the three pipeline stages in the order they must go, checks
prerequisites first, and stops on the first failure.

| Command | What it does |
|---|---|
| `./build_books_db.sh` | Build. Safe to re-run — the injectors self-guard |
| `./build_books_db.sh --clean` | Restore pristine CSVs from `datasets/`, then build |
| `./build_books_db.sh --verify` | Build, then run 8 integrity checks |
| `./build_books_db.sh --clean --verify` | Both — the full reproducible run |
| `./build_books_db.sh --help` | Usage |

It `cd`s to its own directory, so it works from anywhere. `--verify` confirms all
three primary keys, both foreign keys, the `is_explicit` flag, and that the synthetic
records are present and unrated.

### Running the stages by hand

The script is a convenience, not a requirement — the same pipeline, step by step:

```bash
python inject_duplicates.py     # 20/30/50 duplicate rows to deduplicate
python inject_unrated.py        # 5 users + 10 books that nobody rates
marimo edit build_database.py   # interactive — best for the first run
```

Use `marimo edit build_database.py` when you want to *watch* the build. Each of the
nine steps is a separate cell with its explanation above it, which is the point of
having it as a notebook rather than only a script.

### Why the two "inject" steps

The source data is, in two specific ways, *too clean* to teach with:

- It has **zero duplicate keys**, so there would be nothing for a deduplication
  lesson to remove. `inject_duplicates.py` adds 20 / 30 / 50 exact duplicates.
- Its unrated users and books are real but anonymous. `inject_unrated.py` adds 5
  users and 10 books with recognisable keys so the anti-join queries have a small,
  checkable answer. (The data already contains 186,750 unrated users and 1,209
  unrated books — this is about traceability, not necessity.)

Both are documented, seeded, reversible, and refuse to double-apply.

### Getting the data

The three source CSVs (~120 MB) ship with the course repository in
[`datasets/books_dataset/`](../../datasets/books_dataset/) — **no download needed**.
The build reads them from this story's `data/` folder, so they are copied in
first (the copies in `data/` are gitignored, because the injectors modify them):

```
data/books.csv      data/users.csv      data/ratings.csv
```

`./build_books_db.sh --clean` copies them for you. To copy them by hand, from
this folder:

```bash
# macOS / Linux
cp ../../datasets/books_dataset/{books,ratings,users}.csv data/

# Windows (Command Prompt)
copy ..\..\datasets\books_dataset\books.csv data\
copy ..\..\datasets\books_dataset\ratings.csv data\
copy ..\..\datasets\books_dataset\users.csv data\
```

On Windows, then run the stages by hand (see **Running the stages by hand**
above) — `build_books_db.sh` needs a bash shell.

`data/data.source.URL` records the original source: the
[Book-Crossing dataset on Kaggle](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)
(CC0 public domain).

### Rebuilding from scratch

**Neither injector can double-apply.** Run `inject_duplicates.py` ten times and you
still get 20 / 30 / 50. Two independent guards stop each script:

1. **The manifest** — if `duplicates_injected.json` / `unrated_injected.json` exists,
   it refuses.
2. **The data** — it also scans the CSVs, so it refuses even when the manifest has
   been deleted but the modified CSVs are still in place. Without this second check
   that combination would produce 40 / 60 / 100 duplicates, or a second copy of the
   synthetic users and books, breaking the primary keys.

Either way nothing is written. For a genuinely clean slate, use `--clean`, which
restores the pristine CSVs before building:

```bash
./build_books_db.sh --clean --verify
```

Or by hand:

```bash
rm -f data/*.csv *_injected.json books.duckdb
cp ../../datasets/books_dataset/{books,ratings,users}.csv data/
python inject_duplicates.py && python inject_unrated.py && python build_database.py
```

(`data/*.csv` also removes the generated `*.utf8.csv` copies — they end in `.csv`
too, and `build_database.py` regenerates them. Those copies are rebuilt whenever a
source CSV is newer, so appending rows always reaches the database.)

---

## 6. Every file in this directory

### Notebooks — run these

| File | Lines | What it is |
|---|---|---|
| `build_books_db.sh` | 151 | **The build script.** Runs `inject_duplicates.py` → `inject_unrated.py` → `build_database.py` in the required order, after checking that `python3`, the required packages, and the three source CSVs are all present. `--clean` restores pristine CSVs first; `--verify` runs 8 post-build integrity checks. Exits non-zero on first failure. |
| `build_database.py` | 899 | **Marimo notebook.** Turns the three CSVs into `books.duckdb` in 9 documented steps: exposes the 70%-data-loss parsing trap, repairs the encoding, decodes HTML entities, detects and removes duplicates, cleans years/ages/locations, quarantines orphaned ratings, then re-verifies every claim in SQL. Run first. |
| `analyze_data.py` | 1,457 | **Marimo notebook.** The 18 analysis queries, tiered simple → intermediate → intermediate+, each with a markdown explainer before it and an interpretation after it. Six call into `plot_helpers`. Ends with a findings summary, a technique index, and 8 exercises. |

### Supporting code

| File | Lines | What it is |
|---|---|---|
| `plot_helpers.py` | 358 | The 6 chart functions (`plot_rating_distribution`, `plot_top_books`, `plot_ratings_by_country`, `plot_books_per_decade`, `plot_user_segments`, `plot_reader_activity`). **All plotting code lives here** so the notebook's query cells stay pure SQL. Uses a colour-vision-validated palette; coerces polars → pandas because that is what `mo.sql()` returns. |
| `inject_duplicates.py` | 163 | Appends 20 / 30 / 50 exact duplicate rows to `users.csv` / `books.csv` / `ratings.csv`. The source files have **zero** duplicate keys, so without this there is nothing for the dedup lesson to remove. Seeded (2402) and reproducible. Run **before** the build. `--verify` reports counts without writing. |
| `inject_unrated.py` | 176 | Appends 5 users and 10 books that have **no** ratings, with traceable keys (`user_id` 900001–900005, `isbn` `ISBA2402001`–`010`). The real data already contains 186,750 unrated users and 1,209 unrated books, so this is about giving the anti-join queries a small checkable answer — not about making them non-empty. Run **after** `inject_duplicates.py`. |
| `repair_encoding.py` | 146 | Undoes the double-encoding damage (`ErzÃÂ¤hlungen` → `Erzählungen`) in 8,669 lines. Writes `data/*.utf8.csv`; leaves the originals untouched. Regenerates whenever a source CSV is newer. Called automatically by the build notebook. `--report` shows what would change. |

### Documentation

| File | Lines | What it is |
|---|---|---|
| `README.md` | — | This file. Definition, orientation, setup, file inventory, findings. |
| `database_schema_design.md` | 525 | **The reasoning.** Every design decision with the alternatives that were rejected and what each cost: why orphans are quarantined, why implicit zeros keep a flag, why `QUALIFY ROW_NUMBER()` over `DISTINCT`, every column-cleaning rule, and a frank "Known limitations" section. Read this before changing anything. |
| `database_schema.sql` | 167 | The DDL — 4 tables, 11 constraints, `COMMENT ON` metadata. Structure only, no data. Executed by the build notebook; also runnable standalone with `duckdb books.duckdb < database_schema.sql`. |
| `CLAUDE.md` | 134 | Working notes for Claude Code: conventions, gotchas, validation status. Gitignored. |

### Generated / data

| File | Size | What it is |
|---|---|---|
| `books.duckdb` | 173 MB | **The database.** Produced by `build_database.py`. Gitignored — rebuild it, don't commit it. |
| `duplicates_injected.json` | 3 KB | Manifest recording exactly which keys `inject_duplicates.py` duplicated, so the build can *prove* it removed the right rows rather than asserting it. Tracked in git. |
| `unrated_injected.json` | 3 KB | Manifest of the 5 users and 10 books added by `inject_unrated.py`. Tracked in git. |
| `.gitignore` | — | Excludes the CSVs, the `*.utf8.csv` copies, and `*.duckdb`. |
| `data/books.csv` | 78 MB | Source: ISBN, title, author, year, publisher, 3 cover-image URLs. **Gitignored.** |
| `data/users.csv` | 12 MB | Source: user ID, free-text location, age. **Gitignored.** |
| `data/ratings.csv` | 31 MB | Source: user ID, ISBN, rating 0–10. **Gitignored.** |
| `data/books.utf8.csv` | 78 MB | Encoding-repaired copy, written by `repair_encoding.py`. Regenerable. **Gitignored.** |
| `data/users.utf8.csv` | 12 MB | Same, for users (0 damaged lines — produced for pipeline uniformity). **Gitignored.** |
| `data/data.source.URL` | 1 KB | Provenance note: the Kaggle download URL and dataset description. **Tracked in git.** |

---

## 7. The database

```
users ──1───N── ratings ──N───1── books

  └───1───N── ratings_orphaned      (isbn deliberately NOT a foreign key)
```

| Table | Rows | Purpose |
|---|---|---|
| `books` | 271,389 | One row per ISBN. PK `isbn` |
| `users` | 278,862 | One per user; location parsed into city / state / country |
| `ratings` | 1,031,175 | Junction table. PK `(user_id, isbn)`. **Both FKs enforced** |
| `ratings_orphaned` | 118,589 | Ratings whose ISBN is missing from `books` |

`ratings` is a **junction table** resolving the many-to-many relationship between
users and books. Its composite primary key encodes a business rule: a user may rate
a given book at most once. That rule was verified against the source before being
enforced.

### Two things every student must know

1. **`rating = 0` is not a score.** The scale is 1–10; `0` means the user interacted
   with the book without rating it. **62% of rows are zeros.** Filter with
   `WHERE is_explicit`. Forgetting this understates every average by 3–4 points —
   *The Da Vinci Code* reads **4.64** instead of **8.44**, and 4.64 looks entirely
   plausible.

2. **`ratings` excludes 118,589 orphaned rows.** They live in `ratings_orphaned`,
   which has no foreign key on `isbn` — that absence is exactly what lets `ratings`
   have one. Any total from `ratings` is a total over the catalogued subset.

---

## 8. What the build notebook teaches

Nine steps, each solving a real defect in the source files:

| Step | Problem | Technique |
|---|---|---|
| 1 | A naive read **silently drops 70% of ratings** | `quote=''`, manual quote-stripping |
| 2 | 8,669 lines of mojibake (`ErzÃÂ¤hlungen`) | Iterative Latin-1 / UTF-8 round trip |
| 3 | `&amp;` contains the `;` delimiter — 20,464 rows shift | Decode entities *before* splitting; read fields from the right |
| 4 | Duplicate keys | `COUNT(*) - COUNT(DISTINCT key)` |
| 5 | Removing them | `QUALIFY ROW_NUMBER()` — and why not `DISTINCT` |
| 6 | Years that are author names; ages of 244 | `try_cast`, range rules, `CHECK` constraints |
| 7 | 118,589 ratings with no matching book | Quarantine table |
| 8 | "Trust me, it worked" | Every claim re-checked in SQL |
| 9 | — | Final report |

The headline lesson is Step 1. The naive load raises **no error** and returns 340,619
of 1,149,830 rows. Every downstream number would have been computed from under a
third of the data and looked entirely reasonable.

Step 3 is the subtle one: `&amp;` is the HTML escape for `&` and it *ends in a
semicolon* — the delimiter. Decoding entities before splitting drops non-numeric
publication years from **6,056 to 30**.

---

## 9. The 18 queries

**Part 1 — Simple (3):** `SELECT` · `LIMIT` · `COUNT` · `GROUP BY` · `UNION ALL`

| # | Question | Chart |
|---|---|---|
| Q1 | What does a book record look like? | |
| Q2 | How big is each table? | |
| Q3 | How are the 1–10 ratings distributed? | 📊 |

**Part 2 — Intermediate (9):** `JOIN` · `LEFT JOIN` · anti-joins (`NOT EXISTS`) · `HAVING` · `CASE` · `COUNT(DISTINCT)`

| # | Question | Chart |
|---|---|---|
| Q4 | Which books have the most ratings? | 📊 |
| Q5 | Which books are rated highest? | |
| Q6 | Which authors dominate the collection? | |
| Q7 | Where in the world are the raters? | 📊 |
| Q8 | When were these books published? | 📊 |
| Q9 | Do older readers rate differently? | |
| Q10 | Which users have never rated a book? | |
| Q11 | Which books have never been rated? | |
| Q12 | How does the user base split by engagement? | 🥧 |

**Part 3 — Intermediate+ (6):** CTEs · window functions · `QUALIFY` · `NTILE` · self-joins · `FILTER`

| # | Question | Chart |
|---|---|---|
| Q13 | How concentrated is rating activity? | 📊 |
| Q14 | Most popular book in each country? | |
| Q15 | How is attention spread across the catalogue? | |
| Q16 | Readers who liked *The Da Vinci Code* also liked…? | |
| Q17 | How concentrated is the author market? | |
| Q18 | The implicit-zero trap | |

Eight exercises follow, from threshold-tuning to correcting Q16's popularity bias.

---

## 10. Findings

Real conclusions, drawn from real data:

- **8 is the most common rating.** Readers are generous; the average is ~7.6, not 5.5.
- **The second most-rated book is disliked.** *Wild Animus* has 581 ratings averaging
  4.39 — its author gave away free copies at scale. Popularity ≠ quality.
- **261 readers (0.3%) produced 29.8% of all ratings.** 51,270 rated exactly one book.
  There is no "average reader" here.
- **Two thirds of registered users never rated anything** (186,755 of 278,862), but
  only 0.4% of books were never rated. Idle accounts are the norm; unread books
  are not.
- **Half the catalogue has exactly one rating.** The top quartile takes 74% of activity.
- **Age predicts nothing.** Every band from under-18 to 65+ averages 7.6–7.9.
- **Reading is local.** Germany's top titles are German (*Der Vorleser*), Spain's are
  Spanish (*El guardián entre el centeno*).
- **The recommender works.** Da Vinci Code fans' top match is *Angels & Demons* — same
  author, same protagonist — found purely from co-rating behaviour.

### Known limitations

Fuller treatment in `database_schema_design.md` §11.

1. **No time dimension.** Ratings carry no timestamp — no trend analysis, no cohorts,
   no moving averages. This is the biggest gap and it cannot be worked around.
2. **631 books remain mojibake-damaged** (0.23%). The bytes are gone; irreversible.
3. **Severe geographic skew.** The USA contributes more ratings than every other
   country combined. "Global" conclusions here are conclusions about American readers.
4. **The catalogue is a 2004 snapshot**, not publishing history — nearly half the
   books are from the 1990s.
5. **Five users and ten books are synthetic** (`user_id` ≥ 900001,
   `isbn LIKE 'ISBA2402%'`). Exclude them with those predicates if a count must
   reflect only real observations.

---

## 11. Conventions

If you extend this unit, keep to these — they are what make the notebooks readable.

- **Query cells are pure SQL.** Every one is a marimo `mo.sql()` cell with no Python.
- **No plotting code in the notebooks.** Charts come from `plot_helpers.py`; the cell
  is a single call.
- **Every query is explained twice** — a markdown cell before it saying what it does
  and which concepts it uses, and one after it interpreting the actual result.
- **Charts use a validated palette.** Adjacent colours clear the colour-vision-
  deficiency separation threshold; all marks meet 3:1 contrast against the surface.
- **No dual-axis charts.** Q13 plots two percentages on one shared scale rather than
  two scales, because a second axis lets you imply any relationship you like.

---

## 12. Requirements

| Package | Purpose |
|---|---|
| `duckdb` ≥ 2.0 | The database engine (the course requires 2.0+) |
| `marimo` ≥ 0.23 | Reactive notebook runtime |
| `matplotlib` ≥ 3.8 | Charts |
| `pandas` ≥ 2.0 | DataFrame interchange |
| `polars` ≥ 1.0 | *Optional* — if installed, `mo.sql()` returns polars instead of pandas |

Verified against DuckDB 2.0.0, marimo 0.25.2, pandas 3.1, Python 3.13 (Python 3.11+ required).

---

## 13. Citation

> Ziegler, C.-N., McNee, S. M., Konstan, J. A., & Lausen, G. (2005).
> *Improving Recommendation Lists Through Topic Diversification.*
> Proceedings of the 14th International World Wide Web Conference (WWW '05).

Collected from bookcrossing.com with permission from Ron Hornbaker. Licensed CC0 on
Kaggle. Note that the Kaggle description calling this "books from Amazon" is
inaccurate — only the cover-image URLs point at Amazon.
