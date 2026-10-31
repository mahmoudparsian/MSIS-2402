# Data Stories

[← Course home](../README.md) · **Data stories**

A **data story** is one real dataset taken end to end: a notebook that builds a
DuckDB database from raw files, and a notebook that asks it a tiered set of SQL
questions — simple, then intermediate, then harder. Each story is self-contained.

They complement the week folders rather than replace them. A week folder teaches a
technique; a data story shows that technique doing real work on data that
misbehaves — missing values, duplicates, broken keys, and type surprises.

**Contents:** [Stories at a glance](#stories-at-a-glance) ·
[Which story for which week](#which-story-for-which-week) ·
[How to run a story](#how-to-run-a-story) ·
[Notebook by notebook](#notebook-by-notebook) ·
[Why each story lands where it does](#why-each-story-lands-where-it-does) ·
[Inside a data story](#inside-a-data-story)

---

## Stories at a Glance

Eight stories. Five belong to a single week; three span several.

| Data story | Rows | Tables | Week | Role |
|---|---:|:---:|---|---|
| [`sales_table_200_rows/`](sales_table_200_rows/) | 200 | 1 | **1 · Part 1** | **Primary** — first SQL; small enough to check by hand |
| [`nova_retail/`](nova_retail/) | 20K orders | 4 | **1 · 2 · 3 Part 2** | Spans weeks: notebook 1 basics, notebook 2 joins, notebook 3 advanced |
| [`coffee_shop_149K_records/`](coffee_shop_149K_records/) | 149K | 1 | **1 · Part 2** | **Primary** — the aggregation workhorse |
| [`olympic_120_years/`](olympic_120_years/) | 271K | 1 | **1 · Part 2** | Alternative — adds a data-typing trap |
| [`books_users_ratings/`](books_users_ratings/) | 1.0M ratings | 4 | **2 · 3 Part 2** | Spans weeks: build + joins in Week 2; Part 3 in Week 3, Part 2 |
| [`taxi_210K_trips/`](taxi_210K_trips/) | 210K | 1 | **3 · Part 1** | **Primary** — time-series |
| [`shopify_sales_60k_records/`](shopify_sales_60k_records/) | 60K | 2 | **3 · Part 1** | Alternative — adds profit and a quarantine table |
| [`citi_bike_one_million/`](citi_bike_one_million/) | 1.0M | 1 | **3 · Part 1 → Part 2** | Alternative — the largest, and adds maps |

Every story folder has its own `README.md` with the full details.

---

## Which Story for Which Week

### If you only pick one per week

| Week | Topic | Story | Why this one |
|---|---|---|---|
| **1 · Part 1** | SQL foundations — `SELECT`, `WHERE`, `ORDER BY` | **`sales_table_200_rows/`** | 200 rows — the only story you can verify by counting |
| **1 · Part 2** | Aggregation & KPIs | **`coffee_shop_149K_records/`** | 149K rows, rich grouping columns; almost every query is a `GROUP BY` |
| **2** | Multiple tables — keys, joins, referential integrity | **`books_users_ratings/`** | 4 real tables, enforced keys, and 10.3% orphaned foreign keys to reason about |
| **3 · Part 1** | Operational analysis, window functions | **`taxi_210K_trips/`** | Real timestamps — the questions are genuinely time-based |
| **3 · Part 2** | Advanced SQL, CTEs | **`nova_retail/`** (notebook 3) | 13 CTEs and 12 window functions across 20 queries |

Week 4 (web database applications) and Week 5 (modern data systems) are not
SQL-analysis weeks, so no data story is mapped to them.

### By week, with alternatives

**Week 1, Part 1 — SQL foundations**

- **`sales_table_200_rows/`** — 200 rows, one table. Start here.
- `nova_retail/` notebook 1 — a 4-table schema visible from day one.

**Week 1, Part 2 — Aggregation & KPIs**

- **`coffee_shop_149K_records/`** — store, category, hour, day: every question is a grouping.
- `olympic_120_years/` — same shape, plus a deliberately broken query about type inference.

**Week 2 — Multiple tables & complex queries**

- **`books_users_ratings/`** — the build notebook shows schema design and
  constraints; the analysis notebook covers joins, anti-joins, and real
  referential integrity.
- `nova_retail/` notebook 2 — 12 joins over a cleaner, synthetic schema.

> ⚠️ **These are the only two options for Week 2.** Every other story is
> effectively single-table, so it can't show joins honestly.

**Week 3, Part 1 — Operational analysis & window functions**

- **`taxi_210K_trips/`** — real timestamps, rush-hour patterns, messy operational records.
- `shopify_sales_60k_records/` — adds profit, returns, and a bad-row quarantine table.
- `citi_bike_one_million/` — 1M rows and a third notebook of maps.

**Week 3, Part 2 — Advanced SQL & CTEs**

- **`nova_retail/`** notebook 3 — the purpose-built advanced tier.
- `citi_bike_one_million/` Part 4 — "Ranking Queries with CTEs".
- `books_users_ratings/` Part 3 — `QUALIFY`, `NTILE`, self-joins, window frames.
- `coffee_shop_149K_records/` Part D — window functions, if you used it in Week 1.

---

## How to Run a Story

Open every notebook from **inside its story folder** — the notebooks find their
data by relative path:

```bash
cd data_stories/taxi_210K_trips
marimo edit taxi_rides_queries_marimo.py
```

Built databases (`*.duckdb`) are **not** included in the repository, so some
stories need a build step first:

| Story | Before the analysis notebook |
|---|---|
| `sales_table_200_rows/` | Nothing — the notebook builds its own database |
| `olympic_120_years/` | Nothing — the notebook builds its own database |
| `taxi_210K_trips/` | Nothing — the notebook builds its own database |
| `coffee_shop_149K_records/` | Run `coffee_shop_build_db_marimo.py` first |
| `shopify_sales_60k_records/` | Run `01_data_setup_marimo.py` first |
| `citi_bike_one_million/` | Run `notebook1_build_database_marimo.py` first |
| `nova_retail/` | Build the database once (command below) |
| `books_users_ratings/` | Copy the three CSVs from [`datasets/books_dataset/`](../datasets/books_dataset/) into its `data/` folder (`./build_books_db.sh --clean` does this for you), then build — see [its README](books_users_ratings/README.md#5-quick-start) |

**Building `nova_retail`** — from inside `data_stories/nova_retail`, on any
computer (takes about 15 seconds):

```bash
python3 -c "import duckdb; con = duckdb.connect('nova_db.duckdb'); [con.execute(open(f).read()) for f in ('data/schema.sql', 'data/data.sql')]"
```

On Windows, type `python` instead of `python3`. (The story's own
`build_nova_db.sh` does the same thing, but needs a bash shell and the DuckDB
command-line tool.)

---

## Notebook by Notebook

For stories with several notebooks, this is the exact mapping. Build notebooks
run just before their analysis partner.

| Data story — notebook | Week |
|---|---|
| `sales_table_200_rows/` — `sales_queries_marimo.py` | **1 · Part 1** |
| `nova_retail/` — `notebook_1_basics_marimo.py` | **1** |
| `coffee_shop_149K_records/` — `coffee_shop_sql_analysis_marimo.py` | **1 · Part 2** |
| `olympic_120_years/` — `olympics_analysis_marimo.py` | **1 · Part 2** |
| `books_users_ratings/` — `build_database.py` | **2** |
| `nova_retail/` — `notebook_2_intermediate_marimo.py` | **2** |
| `books_users_ratings/` — `analyze_data.py` | **2** (its Part 3 → **3 · Part 2**) |
| `taxi_210K_trips/` — `taxi_rides_queries_marimo.py` | **3 · Part 1** |
| `shopify_sales_60k_records/` — `02_queries_marimo.py` | **3 · Part 1** |
| `citi_bike_one_million/` — `notebook2_analyze_data_marimo.py` | **3 · Part 1** |
| `citi_bike_one_million/` — `notebook3_maps_marimo.py` | **3 · Part 1** |
| `nova_retail/` — `notebook_3_advanced_marimo.py` | **3 · Part 2** |

---

## Why Each Story Lands Where It Does

### What each week needs from a story

| Week | Topic | What a story needs to fit |
|---|---|---|
| **1 · Part 1** | Single-table SQL — `SELECT`, `WHERE`, `ORDER BY` | Small enough to read by eye; no joins required |
| **1 · Part 2** | Aggregation & KPIs | Rich columns to `GROUP BY` and `HAVING` |
| **2** | Multiple tables & complex queries | **More than one table**, with real keys |
| **3 · Part 1** | Operational analysis, window functions | `OVER()`, ranking, time-series or operational data |
| **3 · Part 2** | CTEs & advanced analytics | `WITH`, window frames, `QUALIFY`, multi-stage logic |

### What each story contains

| Story | Tables | Rows | Queries | Dominant techniques | Week |
|---|:---:|---:|---:|---|---|
| `sales_table_200_rows` | 1 | 200 | 25 | `GROUP BY` ×17, light CTE/window | 1 · Part 1 |
| `nova_retail` notebook 1 | 4 | 20K orders | 16 | `GROUP BY` ×8, one join | 1 |
| `coffee_shop_149K_records` | 1 | 149K | 10 | `GROUP BY`, CTE ×4, window ×4 | 1 · Part 2 |
| `olympic_120_years` | 1 | 270K | 24 | `GROUP BY` ×20, `HAVING`, `CASE` | 1 · Part 2 |
| `books_users_ratings` build | 4 | 1.0M ratings | — | ETL, constraints, dedup, quarantine | 2 |
| `nova_retail` notebook 2 | 4 | 20K orders | 16 | **`JOIN` ×12**, `LEFT JOIN` ×2 | 2 |
| `books_users_ratings` analyze | 4 | 1.0M ratings | 18 | **`JOIN` ×11**, anti-joins, CTE ×6, `QUALIFY` | 2 → 3 · Part 2 |
| `taxi_210K_trips` | 1 | 210K | 31 | Time-based, window ×7, ranking + CTEs | 3 · Part 1 |
| `shopify_sales_60k_records` | 2 | 60K | 26 | `GROUP BY` ×21, window ×5, explicit ranking section | 3 · Part 1 |
| `citi_bike_one_million` | 1 | 1.0M | 30 | window ×9, CTE ×8, ranking section, maps | 3 · Part 1 |
| `nova_retail` notebook 3 | 4 | 20K orders | 20 | **CTE ×13, window ×12**, advanced tier | 3 · Part 2 |

Counts come from scanning each notebook's SQL cells, not from its prose.

### The reasoning in one line each

- **Week 1, Part 1 · `sales_table_200_rows`** — 200 rows is the only story small
  enough to verify a result by hand, which is exactly what first SQL needs.
- **Week 1, Part 2 · `coffee_shop`, `olympic_120_years`** — one big table each, and
  nearly every query is an aggregation. `olympic_120_years` also contains a
  deliberately broken query about type inference (`'NA'` strings forcing a
  `VARCHAR` column) that is worth discussing.
- **Week 2 · `nova_retail` notebook 2, `books_users_ratings`** — the only two stories
  with several genuinely related tables. `books_users_ratings` goes further: 10.3%
  of its ratings reference a missing book, so referential integrity has to be
  *engineered* rather than assumed.
- **Week 3, Part 1 · `taxi`, `shopify`, `citi_bike`** — operational data (trips,
  orders, rides) with explicit ranking and window-function sections. `citi_bike`
  adds a third notebook of maps.
- **Week 3, Part 2 · `nova_retail` notebook 3** — the advanced tier: 13 CTEs and 12
  window functions across 20 queries.

### Stories that span weeks

- **`books_users_ratings`** is tiered 3 simple / 9 intermediate / 6 intermediate+.
  Parts 1–2 fit Week 2; Part 3 (CTEs, `ROW_NUMBER` + `QUALIFY`, `NTILE`,
  self-joins, window frames) is Week 3, Part 2 material.
- **`citi_bike_one_million`** ends with "Ranking Queries with CTEs", which also
  serves Week 3, Part 2 as a second example.

---

## Inside a Data Story

Most stories follow the same shape:

| File | Role |
|---|---|
| `*build*_marimo.py` / `build_database.py` | Raw files → DuckDB, with the cleaning explained |
| `*queries*_marimo.py` / `analyze_data.py` | The tiered SQL questions |
| `plot_helpers.py` / `plot_utils.py` / `map_helpers.py` | All plotting code, kept **out** of the notebooks |
| `README.md` | What the story is and how to run it |
| `BUILD_PROMPT.md` | The original build specification, where one exists |

`books_users_ratings/` is the most fully documented: it adds
`database_schema.sql` (DDL with constraints), `database_schema_design.md` (every
design decision, with the alternatives rejected), and `build_books_db.sh` (a
one-command build with integrity checks).

> **Note:** in `coffee_shop_149K_records/`, `taxi_210K_trips/`, and `nova_retail/`,
> files named `build_notebook*.py` / `build_notebooks.py` are generator scripts
> kept for reference — they are **not** notebooks. The notebooks you open are the
> `*_marimo.py` files.

---

*MSIS-2402 — Database Management Systems - Fundamentals of SQL — Winter 2027*
