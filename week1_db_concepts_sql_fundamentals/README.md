# Week 1 — Database Concepts and SQL Fundamentals

[← Course home](../README.md) · **Week 1 of 5** · [Week 2 →](../week2_multi_table_complex_queries/README.md)

⬇️ **No git?** Download this week as one ZIP (with the course data): [`week1_db_concepts_sql_fundamentals.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week1_db_concepts_sql_fundamentals.zip) — [how to unzip and run](../course_information/DOWNLOADING_COURSE_FILES.md)

> This module introduces the foundations of relational databases and SQL.
> Students learn how relational data is organized and develop basic skills
> for creating, retrieving, filtering, summarizing, and modifying data. The
> module establishes the core database and SQL concepts used throughout the
> remainder of the course.
>
> — [Department course outline](../5_weeks_outline/department_course_outline.md)

## At a Glance

| Session | Topic | Folder | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|---|
| **1** | Single-table SQL | [`part1_single_table_sql/`](part1_single_table_sql/) | `week1_lab1/` — retrieving and filtering data: `SELECT`, `WHERE`, `ORDER BY`, `DISTINCT`, `LIMIT` | Marimo notebooks (DuckDB) |
| **2** | Aggregation and KPIs | [`part2_aggregation_kpis/`](part2_aggregation_kpis/) | `week1_lab2/` — summarizing and modifying data: `GROUP BY`, `HAVING`, `CASE`, `INSERT` / `UPDATE` / `DELETE` | Marimo notebooks (DuckDB) |

**Before Session 1:** install the course software —
[`software_installation/`](../software_installation/README.md).

---

## Session 1 — Single-Table SQL

**Topics:** what a relational database is · `SELECT`, `WHERE`, `ORDER BY`,
`DISTINCT`, `LIMIT` · `AND` before `OR` (use parentheses) · derived columns ·
a first look at `GROUP BY`

| File | What it is |
|---|---|
| [`lecture_slides_01_sql_basics.md`](part1_single_table_sql/lecture_slides_01_sql_basics.md) | Slide deck — SQL foundations |
| [`notebook_3_duckdb_marimo.py`](part1_single_table_sql/notebook_3_duckdb_marimo.py) | In-class notebook — SQL foundations with a single table |
| [`CLASS_DISCUSSION_01.md`](part1_single_table_sql/CLASS_DISCUSSION_01.md) | Class discussion — warm-up before the lab |
| [`data/`](part1_single_table_sql/data/) | `sales.csv` — 200 sales, used by the notebook and the class discussion |

## Session 2 — Aggregation and KPIs

**Topics:** `COUNT`, `SUM`, `AVG` · `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)` ·
`GROUP BY` and `HAVING` · the order SQL runs a query in · business KPIs ·
modifying data with `INSERT`, `UPDATE`, `DELETE` · cleaning text (`TRIM`, `LOWER`,
`UPPER`, `||`) · working with dates (`YEAR`, `MONTH`, `DATE_TRUNC`, `strftime`,
`date_diff`, `INTERVAL`)

| File | What it is |
|---|---|
| [`lecture_slides_aggregations.md`](part2_aggregation_kpis/lecture_slides_aggregations.md) | Slide deck — aggregation and KPIs |
| [`lecture_slides_sql_tour.md`](part2_aggregation_kpis/lecture_slides_sql_tour.md) | Slide deck — a tour of DuckDB SQL, including `INSERT` / `UPDATE` / `DELETE` |
| [`lecture_slides_text_and_date_functions.md`](part2_aggregation_kpis/lecture_slides_text_and_date_functions.md) | Slide deck — text and date functions for analytics: clean text before grouping, group by year and month, days between dates, the last N days |
| [`notebook_1_marimo.py`](part2_aggregation_kpis/notebook_1_marimo.py) | In-class notebook — aggregation and KPIs, then text and date functions (same examples as the slides) |
| [`notebook_2_marimo.py`](part2_aggregation_kpis/notebook_2_marimo.py) | In-class notebook — `WHERE` vs. `HAVING`, KPIs, and business thinking |
| [`CLASS_DISCUSSION_02.md`](part2_aggregation_kpis/CLASS_DISCUSSION_02.md) | Class discussion — warm-up before the lab |
| [`data/`](part2_aggregation_kpis/data/) | `sales_dataset.csv` (200 transactions — notebooks and class discussion) and `weather.csv` (used in the SQL-tour slides). The text-and-date slides and `notebook_1_marimo.py` also read Session 1's dated sales, [`../part1_single_table_sql/data/sales.csv`](part1_single_table_sql/data/sales.csv) |

---

## Labs

Each session's labs are published in [`LABS/`](../LABS/) during class — a
**Lab A** (core, 40 points, 6 tasks), done and submitted on Camino **before
class ends**, and a **Lab B** (a step more challenging, 30 points, 6 tasks),
due by **11:59 pm Pacific Time** the day after class ([how](../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab)).
Solutions are added after the deadlines.

## Running the Notebooks

All commands start in the **course repository folder** — the folder that
contains `README.md`, `datasets/`, and the `week…` folders (named
`MSIS-2402-main` if you downloaded the ZIP). Each notebook must be opened
from **its own folder**, because it reads its data by a relative path:

| Session | Run (two commands) | Reads |
|:---:|---|---|
| 1 | `cd week1_db_concepts_sql_fundamentals/part1_single_table_sql` then `marimo edit notebook_3_duckdb_marimo.py` | `data/sales.csv` |
| 2 | `cd week1_db_concepts_sql_fundamentals/part2_aggregation_kpis` then `marimo edit notebook_1_marimo.py` (or `notebook_2_marimo.py`) | `data/sales_dataset.csv`; `notebook_1_marimo.py` also reads `../part1_single_table_sql/data/sales.csv` |

## Shared Dataset

This week's **labs** introduce the course-wide 7-table retail database in
[`datasets/oltp_database/`](../datasets/oltp_database/) — `customers`,
`orders`, `order_items`, `products`, `payments`, `shipments`, `stores`. Every
week's labs use it, and in Weeks 4–5 the same data is loaded into MySQL as
the `isba_shop` database.

## Further Practice

- **Data stories:** [`sales_table_200_rows/`](../data_stories/sales_table_200_rows/)
  (Session 1) and [`coffee_shop_149K_records/`](../data_stories/coffee_shop_149K_records/)
  (Session 2) — see [`data_stories/README.md`](../data_stories/README.md).
- **Tutorials:** [creating tables from CSV files](../tutorials/create_tables_from_CSV_files/),
  [DuckDB from the command line](../tutorials/duckdb_from_command_line/README.md),
  and [`GROUP BY`](../tutorials/group_by/).

---

[← Course home](../README.md) · [Week 2 →](../week2_multi_table_complex_queries/README.md)
