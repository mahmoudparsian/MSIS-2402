# Week 3 — SQL for Data Analytics

[← Week 2](../week2_multi_table_complex_queries/README.md) · [Course home](../README.md) · **Week 3 of 5** · [Week 4 →](../week4_web_db_applications/README.md)

> This module explores how SQL can be used for contemporary data analysis.
> Students apply SQL to transform, summarize, compare, and analyze data and
> are introduced to more advanced analytical capabilities of modern
> relational database systems.
>
> — [Department course outline](../5_weeks_outline/department_course_outline.md)

## At a Glance

| Session | Topic | Folder | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|---|
| **5** | Operational databases and window functions | [`part1_operational_db_window_functions/`](part1_operational_db_window_functions/) | `week3_lab1/` — window functions, ranking, and data-quality checks | Marimo notebooks (DuckDB) |
| **6** | CTEs and advanced analytics | [`part2_ctes_advanced_analytics/`](part2_ctes_advanced_analytics/) | `week3_lab2/` — running totals, trends, and segmentation | Marimo notebooks (DuckDB) |

---

## Session 5 — Operational Databases and Window Functions

**Topics:** the full 7-table operational schema · data-quality checks and
deduplication · window functions · ranking with `ROW_NUMBER`, `RANK`, and
`DENSE_RANK` (ties, top N per group, the Nth-highest value, `QUALIFY`) ·
trends and segmentation

| File | What it is |
|---|---|
| [`lecture_slides_1_joins_reviewed.md`](part1_operational_db_window_functions/lecture_slides_1_joins_reviewed.md) | Slide deck — real operational databases |
| [`lecture_slides_2_window_functions.md`](part1_operational_db_window_functions/lecture_slides_2_window_functions.md) | Slide deck — window functions and advanced analytics |
| [`notebook_1_ranking_marimo.py`](part1_operational_db_window_functions/notebook_1_ranking_marimo.py) | In-class notebook — ranking |
| [`notebook_2_Trends_Segmentation_marimo.py`](part1_operational_db_window_functions/notebook_2_Trends_Segmentation_marimo.py) | In-class notebook — trends and segmentation |
| [`notebook_3_duckdb_analysis_marimo.py`](part1_operational_db_window_functions/notebook_3_duckdb_analysis_marimo.py) | In-class notebook — exploring the full operational database |
| [`CLASS_DISCUSSION_01.md`](part1_operational_db_window_functions/CLASS_DISCUSSION_01.md) | Class discussion — warm-up before the lab |
| [`data/`](part1_operational_db_window_functions/data/) | `week4_sales.csv` — 200 transactions, used by notebooks 1 and 2 and the class discussion |

## Session 6 — CTEs and Advanced Analytics

**Topics:** common table expressions (`WITH`) · running totals · `LAG` ·
top-N per group · end-to-end analysis

| File | What it is |
|---|---|
| [`lecture_slides_1.md`](part2_ctes_advanced_analytics/lecture_slides_1.md) | Slide deck — advanced SQL for business analytics |
| [`lecture_slides_2.md`](part2_ctes_advanced_analytics/lecture_slides_2.md) | Slide deck — case study: *From SQL to Decision*, an end-to-end analysis from query to business recommendation |
| [`notebook_ecommerce/`](part2_ctes_advanced_analytics/notebook_ecommerce/) | Example notebook — CTE and window-function questions on the course's retail schema |
| [`notebook_diabetic/`](part2_ctes_advanced_analytics/notebook_diabetic/) | Example notebook — advanced SQL and charts on the UCI *Diabetes 130-US Hospitals* dataset (about 100,000 hospital encounters) |
| [`CLASS_DISCUSSION_02.md`](part2_ctes_advanced_analytics/CLASS_DISCUSSION_02.md) | Class discussion — warm-up before the lab |

Each example notebook folder has its own `README.md`.

---

## Labs

Each session's labs are published in [`LABS/`](../LABS/) during class — a
**Lab A** (core, 40 points, 6 tasks), done and submitted on Camino **before
class ends**, and a **Lab B** (a step more challenging, 30 points, 6 tasks),
due by **11:59 pm Pacific Time** that day ([how](../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab)).
Solutions are added after the deadlines.

## Running the Notebooks

All commands start in the **course repository folder** — the folder that
contains `README.md`, `datasets/`, and the `week…` folders (named
`MSIS-2402-main` if you downloaded the ZIP). Each notebook must be opened
from **its own folder**, because it reads its data by a relative path:

| Session | Run (two commands) | Reads |
|:---:|---|---|
| 5 | `cd week3_sql_for_analytics/part1_operational_db_window_functions` then `marimo edit notebook_1_ranking_marimo.py` (or `notebook_2_Trends_Segmentation_marimo.py`) | `data/week4_sales.csv` |
| 5 | same folder, `marimo edit notebook_3_duckdb_analysis_marimo.py` | `../../datasets/oltp_database/` |
| 6 | `cd week3_sql_for_analytics/part2_ctes_advanced_analytics/notebook_ecommerce` then `marimo edit notebook_ecommerce.py` | `../../../datasets/oltp_database/` |
| 6 | `cd week3_sql_for_analytics/part2_ctes_advanced_analytics/notebook_diabetic` then `python3 build_database.py` **once** (Windows: `python`), then `marimo edit notebook_diabetic_marimo.py` | `diabetic_hospitals.duckdb`, built from the folder's `data/` (see its README) |

## Further Practice

- **Data stories:** [`taxi_210K_trips/`](../data_stories/taxi_210K_trips/)
  (Session 5 — real timestamps for time-based questions) and
  [`nova_retail/`](../data_stories/nova_retail/) (Session 6 — notebook 3 is
  built on CTEs and window functions). See
  [`data_stories/README.md`](../data_stories/README.md).
- **Tutorials:** [window functions](../tutorials/window_functions/),
  [deduplication](../tutorials/deduplication/deduplication_tutorial.md), and
  [DuckDB user-defined functions](../tutorials/duckdb_user_defined_functions/).

---

[← Week 2](../week2_multi_table_complex_queries/README.md) · [Course home](../README.md) · [Week 4 →](../week4_web_db_applications/README.md)
