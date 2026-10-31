# Database Schema Design

**Course:** MSIS-2402 · Santa Clara University
**Database:** `books.duckdb`
**Source:** Book-Crossing dataset — Cai-Nicolas Ziegler, 2004

This document explains **why** the schema looks the way it does. `database_schema.sql`
is the DDL; this is the reasoning behind it. Every non-obvious decision is recorded
here together with the alternatives that were rejected and the cost of choosing them.

---

## Contents

1. [The source data](#1-the-source-data)
2. [Entity-relationship model](#2-entity-relationship-model)
3. [Decision 1 — Orphaned ratings: quarantine](#3-decision-1--orphaned-ratings-quarantine)
4. [Decision 2 — Implicit zeros: keep with a flag](#4-decision-2--implicit-zeros-keep-with-a-flag)
5. [Decision 3 — CSVs copied into the project](#5-decision-3--csvs-copied-into-the-project)
6. [Decision 4 — Deduplication with QUALIFY ROW_NUMBER](#6-decision-4--deduplication-with-qualify-row_number)
7. [Decision 5 — Parsing a hostile CSV](#7-decision-5--parsing-a-hostile-csv)
8. [Decision 6 — Repairing the character encoding](#8-decision-6--repairing-the-character-encoding)
9. [Column-level cleaning rules](#9-column-level-cleaning-rules)
10. [Keys and constraints](#10-keys-and-constraints)
11. [Known limitations](#11-known-limitations)

---

## 1. The source data

Three semicolon-delimited CSV files, downloaded from Kaggle:

| File | Lines | Contents |
|---|---|---|
| `books.csv` | 271,379 | ISBN, title, author, year, publisher, 3 cover-image URLs |
| `users.csv` | 278,857 | User ID, free-text location, age |
| `ratings.csv` | 1,149,780 | User ID, ISBN, rating 0–10 |

The dataset was compiled in 2004 from bookcrossing.com. It is **real observational
data**, not synthetic — which is why it carries genuine defects worth teaching with.

> **Note on provenance.** The Kaggle page describes these as "books from Amazon".
> That is inaccurate. The ratings come from the Book-Crossing community; only the
> cover-image URLs point at Amazon. The academic citation is Ziegler et al., WWW 2005.

### Deliberate additions before the build

`inject_duplicates.py` appends exact duplicate rows to all three files **before**
the database is built:

| File | Duplicates added | Key duplicated |
|---|---|---|
| `users.csv` | 20 | `User-ID` |
| `books.csv` | 30 | `ISBN` |
| `ratings.csv` | 50 | `(User-ID, ISBN)` |

The originals have **zero** duplicate keys, so without this step there would be
nothing to deduplicate and the `QUALIFY ROW_NUMBER()` lesson would be theoretical.
A fixed random seed (2402) makes the injection reproducible, and
`duplicates_injected.json` records exactly which keys were duplicated so the build
can prove it removed the right rows.

`inject_unrated.py` then appends records that **no one rates**, so the anti-join
queries have a small, checkable answer:

| File | Rows added | Keys |
|---|---|---|
| `users.csv` | 5 | `user_id` 900001–900005 |
| `books.csv` | 10 | `isbn` `ISBA2402001`–`ISBA2402010` |

Nothing is added to `ratings.csv`, so these records are unrated by construction.

**This is about traceability, not necessity.** The real data already contains 186,750
users with no ratings and 1,209 books with none — the anti-join queries return plenty
of rows without any help. What the synthetic records add is a handful of rows a
student can point at by eye and confirm. The keys were chosen to be unmistakable:
`ISBA` matches zero real ISBNs, and the highest real `user_id` is 278,858.

Final table sizes after both injectors and deduplication: **271,389 books,
278,862 users**.

---

## 2. Entity-relationship model

```
        users                                    books
   ┌──────────────────┐                  ┌────────────────────┐
   │ user_id      PK  │                  │ isbn           PK  │
   │ location_raw     │                  │ title              │
   │ city             │                  │ author             │
   │ state            │                  │ publication_year   │
   │ country          │                  │ publisher          │
   │ age              │                  │ image_url          │
   └────────┬─────────┘                  └─────────┬──────────┘
            │ 1                                    │ 1
            │                                      │
            │ N                                    │ N
            │        ┌──────────────────┐          │
            └────────┤    ratings       ├──────────┘
                     │ user_id   PK FK  │
                     │ isbn      PK FK  │
                     │ rating           │
                     │ is_explicit      │
                     └──────────────────┘

            │ N
            │        ┌─────────────────────┐
            └────────┤ ratings_orphaned    │   isbn deliberately
                     │ user_id     PK FK   │   NOT a foreign key
                     │ isbn        PK      │
                     │ rating              │
                     │ is_explicit         │
                     └─────────────────────┘
```

`ratings` is a **junction (bridge) table** resolving the many-to-many relationship
between users and books. Its primary key is the composite `(user_id, isbn)`, which
also encodes a business rule: **a user may rate a given book at most once.**

That rule was verified against the source before being enforced — zero natural
duplicates on the pair, and zero cases where the same pair carried two different
ratings. Enforcing a constraint the data cannot satisfy is a common way to make a
build script fail mysteriously six months later.

---

## 3. Decision 1 — Orphaned ratings: quarantine

### The problem

**118,589 ratings (10.3%) reference an ISBN that does not exist in `books.csv`.**

These are not corrupt rows. The user ID is valid, the rating is in range, the ISBN
is well-formed. The book simply is not in the catalogue extract — the two files were
exported from different snapshots.

This blocks the foreign key. `FOREIGN KEY (isbn) REFERENCES books (isbn)` cannot be
declared while 118,589 rows violate it.

### The options

| Option | Data kept | FK possible | Cost |
|---|---|---|---|
| Delete the orphans | ✗ 118,589 rows destroyed | ✓ | Evidence gone; totals silently understated with no record of why |
| Keep them, drop the FK | ✓ | ✗ | Nothing prevents future corruption; every `JOIN` silently loses 10% of rows |
| **Quarantine** ← chosen | ✓ | ✓ | One extra table to explain |

### Why quarantine

The two goals — *keep all observations* and *enforce referential integrity* — look
mutually exclusive, but they are only in conflict **within a single table**. Routing
the orphans to a second table satisfies both:

- `ratings` is referentially perfect, so both foreign keys are declared and enforced.
  Every `JOIN` from `ratings` is guaranteed lossless.
- `ratings_orphaned` retains all 118,589 rows, fully queryable and countable.

`ratings_orphaned` deliberately has **no** foreign key on `isbn` — that absence is
the entire purpose of the table. It does keep the `user_id` foreign key, because
every orphan's user does exist.

### What this teaches

Referential integrity is a property you *engineer*, not one you hope for. And the
right response to data that violates a constraint is rarely to delete it or to
abandon the constraint — it is to separate the clean from the unclean and be
explicit about which is which. Exercise 5 in the analysis notebook asks students to
compare the two populations.

---

## 4. Decision 2 — Implicit zeros: keep with a flag

### The problem

In this dataset, **`rating = 0` does not mean "zero out of ten"**. The scale is 1–10.
A `0` records that a user interacted with a book — had it, listed it, passed it on —
without scoring it. The documentation calls these *implicit* ratings.

**716,106 of 1,149,780 rows (62.3%) are implicit zeros.**

Anyone who writes `AVG(rating)` without excluding them gets a number that is wrong by
three to four points, and — this is the dangerous part — **still looks reasonable**.
*The Da Vinci Code* averages 4.64 with the zeros and 8.44 without. Both are plausible
numbers on a ten-point scale. Nothing about 4.64 announces itself as a mistake.

### The options

| Option | Can students get it wrong? | Do they learn the filter? |
|---|---|---|
| Two tables — `ratings_explicit` / `ratings_implicit` | No | No |
| Raw column, no flag | Yes, easily | Only after being burned |
| **Keep + `is_explicit` flag** ← chosen | Yes, but the schema warns them | Yes |

### Why the flag

Splitting into two tables makes the mistake impossible — and therefore makes the
lesson impossible too. Students would never learn that a rating scale can contain a
non-rating, which is a pattern they will meet constantly (`-1` for unknown, `999` for
not-applicable, `0` for "no response").

Leaving the raw column with no help is the opposite failure: realistic, but the error
is invisible until someone catches it downstream.

A derived `is_explicit BOOLEAN` column keeps one table and one join path, while making
the distinction impossible to overlook when reading the schema. These are equivalent:

```sql
WHERE is_explicit     -- self-documenting
WHERE rating > 0      -- identical result, easier to forget
```

A `CHECK` constraint keeps the flag honest:

```sql
CONSTRAINT ck_ratings_explicit CHECK (is_explicit = (rating > 0))
```

The flag can never drift out of agreement with the column it describes.

Query 18 in the analysis notebook is built entirely around this, showing both averages
side by side with the difference in a third column.

---

## 5. Decision 3 — CSVs copied into the project

The three source files (~120 MB) are copied into `data/` rather than referenced from
a shared `datasets/` directory elsewhere in the repository.

**Why:** the project is self-contained. A student can clone this one folder and run
both notebooks with no path configuration and nothing else on disk.

**The cost:** ~120 MB that should not enter version control. `.gitignore` therefore
excludes `data/*.csv`, the generated `*.utf8.csv`, and `books.duckdb` itself. The
repository carries the code and the documentation; anyone can regenerate the data by
downloading the source and running the two scripts.

`data/data.source.URL` records the download location so the raw files can always be
recovered.

---

## 6. Decision 4 — Deduplication with QUALIFY ROW_NUMBER

Two standard techniques remove duplicate rows. They are **not** interchangeable.

### `SELECT DISTINCT`

```sql
SELECT DISTINCT * FROM books_raw;
```

Collapses rows identical across **every column**. Its limitation is decisive: if two
rows share an ISBN but differ in any other column — a trailing space in the publisher,
a different edition year — `DISTINCT` keeps both and the primary key still fails.

### `QUALIFY ROW_NUMBER()` ← chosen

```sql
SELECT * FROM books_raw
QUALIFY ROW_NUMBER() OVER (PARTITION BY isbn ORDER BY title) = 1;
```

| Clause | Job |
|---|---|
| `PARTITION BY isbn` | one bucket per ISBN |
| `ORDER BY title` | rank rows within each bucket |
| `= 1` | keep the top-ranked row from each |

`QUALIFY` filters on a window function's result — it is to window functions what
`HAVING` is to aggregates. `WHERE ROW_NUMBER() ... = 1` is a syntax error, because at
`WHERE` time the window has not been computed.

### Why this one

It guarantees exactly one row per key **regardless of how much the duplicates
disagree**, and the `ORDER BY` lets you state which survivor you want — the newest
record, the most complete one, the highest rating. `DISTINCT` offers no such control.

Because the injected duplicates here are byte-identical, both techniques happen to
give the same answer. `QUALIFY` is used because it is the technique that keeps working
when the data gets worse — which it will.

### Verification

The build proves the deduplication rather than asserting it:

| Table | Staged | Loaded | Removed | Expected |
|---|---|---|---|---|
| `books` | 271,409 | 271,379 | 30 | 30 ✓ |
| `users` | 278,877 | 278,857 | 20 | 20 ✓ |
| `ratings` | 1,149,814 | 1,149,764 | 50 | 50 ✓ |

---

## 7. Decision 5 — Parsing a hostile CSV

These files break the CSV standard in two independent ways, and both failures are
silent.

### Failure 1 — unbalanced quotes lose 70% of the rows

Fields are quoted, but some contain a stray unmatched `"`. Under strict CSV rules
that quote opens a field that never closes, and the parser discards everything until
it recovers.

```
Rows a naive read returns :    340,619
Rows actually in the file :  1,149,830
Silently discarded        :    809,211  (70.4%)
```

**No error is raised.** The load "succeeds" with less than a third of the data.

**Fix:** `quote = ''` tells DuckDB that `"` is an ordinary character. Quotes are then
stripped explicitly with `trim(both '"' from ...)`. A stray quote cannot unbalance
anything that is not treated as a quote.

### Failure 2 — HTML entities contain the delimiter

```
"0393045218";"The Mummies of Urumchi";"E. J. W. Barber";"1999";"W. W. Norton &amp; Company";...
```

`&amp;` is the HTML escape for `&` — **and it ends in a semicolon**, the delimiter.
The parser splits inside the escape and every subsequent field shifts one position left.

**20,464 books (7.5%) contain `&amp;`.** This is the true origin of the notorious
"author names in the publication-year column" — values like `'Ashley Olsen'` and
`'Faye Kellerman'` sitting in a column that should hold integers.

**Fix:** read each line **whole** using a delimiter byte that appears nowhere in the
file (`\x01`), decode the entities (`&amp;` → `&`, `&lt;` → `<`), and split on `;`
afterwards. Order matters absolutely — decoding after the split is too late.

Effect on data quality:

| Metric | Before | After |
|---|---|---|
| Non-numeric `publication_year` | 6,056 | **30** |
| `publication_year` ending as NULL | 10,715 | **4,720** |

### Reading fields from the right

After decoding, 99.6% of book lines split into exactly 8 fields. The remaining 988
contain a **genuine** semicolon inside the title, so counting from the left
misaligns them. The last three fields are always image URLs, so the parser counts
from the **right**, where the layout is stable:

| Field | Position |
|---|---|
| `image_url` | `f[len]` |
| `publisher` | `f[len-3]` |
| `publication_year` | `f[len-4]` |
| `author` | `f[len-5]` |
| `title` | `f[2] … f[len-6]`, rejoined with `;` |

One expression handles clean and messy rows identically. `users.csv` gets the same
treatment for its ~137 multi-semicolon locations.

---

## 8. Decision 6 — Repairing the character encoding

3.2% of lines in `books.csv` carry **mojibake**:

| Stored | Should read |
|---|---|
| `Der illustrierte Mann. ErzÃÂ¤hlungen.` | `Erzählungen` |
| `El guardiÃ¡n entre el centeno` | `guardián` |
| `LÃ?Â¼bbe` | `Lübbe` |

UTF-8 bytes were decoded as Latin-1 and re-encoded as UTF-8 — **twice**. A later
lossy conversion also replaced control byte `0x83` with a literal `?`, producing the
`Ã?` sequences.

`repair_encoding.py` reverses this in three steps: restore the clobbered byte at the
byte level, decode as Latin-1, then apply `encode('latin-1').decode('utf-8')`
repeatedly until the text stops changing. Two passes are needed.

**Result: 8,004 of 8,669 damaged lines (92.3%) fully recovered.** The remaining 665
(0.24% of the file) lost bytes permanently and are left untouched rather than guessed
at — a repair that invents plausible characters is worse than visible damage.

Repaired copies are written as `data/*.utf8.csv`; the originals stay in place so the
"before" remains inspectable.

---

## 9. Column-level cleaning rules

Every rule below **nulls a value rather than dropping a row**. A book with an
unusable year is still a book.

### `books.publication_year`

| Source value | Action |
|---|---|
| 1376–2004 | keep |
| `0` (4,589 rows) | → `NULL` — the source's "unknown" marker |
| > 2004 (25 rows, up to 2050) | → `NULL` — impossible; data collected in 2004 |
| non-numeric (30 rows) | → `NULL` — residual corruption |

1376 is the earliest year present; 2004 is when the dataset was compiled. A `CHECK`
constraint encodes the rule so it is enforced on any future insert, not just applied
once at load.

**4,720 books (1.7%) end with a NULL year.**

### `users.age`

| Source value | Action |
|---|---|
| 5–100 | keep |
| absent | → `NULL` |
| < 5 or > 100 | → `NULL` — the source contains ages of 0 and 244 |

**112,131 users (40.2%) have no usable age.** That is a large share, and every
age-based query in the analysis notebook silently excludes them. Q9 says so explicitly.

### `users` location → `city`, `state`, `country`

The source has one free-text field shaped roughly `'city, state, country'`.

Parsing takes the **first** comma-separated element as city and the **last** as
country, rather than positions 1/2/3, because 1,667 rows do not have exactly two
commas. `state` is populated only when there are three or more elements.

Placeholder strings are nulled: `''`, `'n/a'`, `'none'`, `'unknown'`, `'universe'`,
`'space'`, `'quit'`, `'...'` and similar. This matters more than the tiny row count
suggests — only 3 users give `'n/a'` as their country, but between them they
contributed nearly 7,000 ratings, enough to place `'n/a'` in a top-ten country list.

`location_raw` retains the original string so the split can always be audited.

**Not normalised:** `'usa'` (139,712) and `'us'` (4) remain distinct, as do `'uk'` and
`'united kingdom'`. Building a country-alias lookup table would be a reasonable
extension; the affected counts here are trivial.

### `books.image_url`

The source has three cover-image URLs per book (small, medium, large) that differ
only by a size code in the filename. Only the large one is stored — the other two are
derivable, and storing all three would triple a column that no query uses.

---

## 10. Keys and constraints

### Natural keys, no surrogates

`books.isbn` and `users.user_id` are **natural primary keys** — they come from the
source and are genuinely unique (271,379 / 271,379 and 278,857 / 278,857 after
deduplication). Adding surrogate integer keys would introduce a layer with no benefit.

`ratings` uses the **composite** key `(user_id, isbn)`.

### Full constraint inventory

| Constraint | Table | Meaning |
|---|---|---|
| `pk_books` | books | ISBN unique |
| `pk_users` | users | User ID unique |
| `pk_ratings` | ratings | One rating per user per book |
| `pk_ratings_orphaned` | ratings_orphaned | Same rule for quarantined rows |
| `fk_ratings_user` | ratings | Every rating belongs to a real user |
| `fk_ratings_book` | ratings | Every rating belongs to a real book |
| `fk_orphaned_user` | ratings_orphaned | Orphans still have real users |
| `ck_books_year` | books | Year NULL or 1376–2004 |
| `ck_users_age` | users | Age NULL or 5–100 |
| `ck_ratings_scale` | ratings | Rating 0–10 |
| `ck_ratings_explicit` | ratings | `is_explicit = (rating > 0)` |

The constraints are **enforced, not decorative**:

```sql
INSERT INTO ratings VALUES (999999999, 'NOPE', 5, true);
-- Constraint Error: Violates foreign key constraint because key
-- "user_id: 999999999" does not exist in the referenced table
```

Every table and the non-obvious columns also carry `COMMENT ON` metadata, readable via
`duckdb_tables()` and `duckdb_columns()`.

---

## 11. Known limitations

Stated plainly, because a schema document that only lists strengths is not useful.

0. **Five users and ten books are synthetic** (`user_id` ≥ 900001, `isbn LIKE
   'ISBA2402%'`), added by `inject_unrated.py` for the anti-join queries. Exclude
   them with those predicates if a count must reflect only real observations.

1. **No time dimension.** Ratings carry no timestamp. Trend analysis, cohort analysis,
   moving averages and any `LAG`/`LEAD` over time are impossible. This is the single
   biggest gap and it cannot be worked around — it is absent from the source.

2. **631 books remain mojibake-damaged** (0.23%). Irreversible; the bytes are gone.

3. **988 book titles contain a genuine semicolon** and are reconstructed positionally.
   The reconstruction is correct for the standard 8-field layout but is unverifiable
   row by row.

4. **`ratings` excludes 118,589 orphans.** Any total computed from `ratings` is a total
   over the catalogued subset. This is correct behaviour, but it must be stated
   whenever a total is reported.

5. **Popularity is not quality.** *Wild Animus* is the second most-rated book with an
   average of 4.39, because its author distributed free copies at scale. Rating counts
   measure exposure, not merit.

6. **Severe geographic skew.** The USA contributes more ratings than all other
   countries combined. Conclusions described as global are conclusions about American
   readers.

7. **Extreme participation skew.** 261 users (0.3%) produced 29.8% of all ratings,
   while 51,270 users rated exactly one book. Per-user averages are dominated by a few
   hundred accounts.

8. **The catalogue is a 2004 snapshot.** Nearly half of all books were published in
   the 1990s. The distribution reflects what was in circulation when the data was
   collected, not publishing history.
