# Week 3 — SQL for Data Analytics

[← Week 2](../week2_multi_table_complex_queries/README.md) · [Course home](../README.md) · **Week 3 of 5** · [Week 4 →](../week4_web_db_applications/README.md)

⬇️ **No git?** Download this week as one ZIP (with the course data): [`week3_sql_for_analytics.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week3_sql_for_analytics.zip) — [how to unzip and run](../course_information/DOWNLOADING_COURSE_FILES.md)

> This module explores how SQL can be used for contemporary data analysis.
> Students apply SQL to transform, summarize, compare, and analyze data and
> are introduced to more advanced analytical capabilities of modern
> relational database systems.
>
> — [Department course outline](../00_start_here/department_course_outline.md)

## At a Glance

| Session | Topic | Folder | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|---|
| **5** | Operational databases and window functions | [`session05_operational_db_window_functions/`](session05_operational_db_window_functions/) | `week3/session05/` — window functions, ranking, and data-quality checks | Marimo notebooks (DuckDB) |
| **6** | CTEs and advanced analytics | [`session06_ctes_advanced_analytics/`](session06_ctes_advanced_analytics/) | `week3/session06/` — running totals, trends, and segmentation | Marimo notebooks (DuckDB) |

---

## Session 5 — Operational Databases and Window Functions

**Topics:** the full 7-table operational schema · data-quality checks and
deduplication · window functions · ranking with `ROW_NUMBER`, `RANK`, and
`DENSE_RANK` (ties, top N per group, the Nth-highest value, `QUALIFY`) ·
trends and segmentation

| File | What it is |
|---|---|
| [`slides_01_operational_database.md`](session05_operational_db_window_functions/slides_01_operational_database.md) | Slide deck — real operational databases |
| [`slides_02_window_functions_ranking.md`](session05_operational_db_window_functions/slides_02_window_functions_ranking.md) | Slide deck — window functions and advanced analytics |
| [`notebook_01_ranking.py`](session05_operational_db_window_functions/notebook_01_ranking.py) | In-class notebook — ranking |
| [`notebook_02_trends_segmentation.py`](session05_operational_db_window_functions/notebook_02_trends_segmentation.py) | In-class notebook — trends and segmentation |
| [`notebook_03_full_database_exploration.py`](session05_operational_db_window_functions/notebook_03_full_database_exploration.py) | In-class notebook — exploring the full operational database |
| [`CLASS_DISCUSSION.md`](session05_operational_db_window_functions/CLASS_DISCUSSION.md) | Class discussion — warm-up before the lab |
| [`data/`](session05_operational_db_window_functions/data/) | `product_orders.csv` — 200 transactions, used by notebooks 1 and 2 and the class discussion |

## Session 6 — CTEs and Advanced Analytics

**Topics:** common table expressions (`WITH`) · running totals · `LAG` ·
top-N per group · end-to-end analysis

| File | What it is |
|---|---|
| [`slides_01_ctes_advanced_sql.md`](session06_ctes_advanced_analytics/slides_01_ctes_advanced_sql.md) | Slide deck — advanced SQL for business analytics |
| [`slides_02_case_study_sql_to_decision.md`](session06_ctes_advanced_analytics/slides_02_case_study_sql_to_decision.md) | Slide deck — case study: *From SQL to Decision*, an end-to-end analysis from query to business recommendation |
| [`notebook_ecommerce/`](session06_ctes_advanced_analytics/notebook_ecommerce/) | Example notebook — CTE and window-function questions on the course's retail schema |
| [`notebook_diabetic/`](session06_ctes_advanced_analytics/notebook_diabetic/) | Example notebook — advanced SQL and charts on the UCI *Diabetes 130-US Hospitals* dataset (about 100,000 hospital encounters) |
| [`CLASS_DISCUSSION.md`](session06_ctes_advanced_analytics/CLASS_DISCUSSION.md) | Class discussion — warm-up before the lab |

Each example notebook folder has its own `README.md`.

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
| 5 | `cd week3_sql_for_analytics/session05_operational_db_window_functions` then `marimo edit notebook_01_ranking.py` (or `notebook_02_trends_segmentation.py`) | `data/product_orders.csv` |
| 5 | same folder, `marimo edit notebook_03_full_database_exploration.py` | `../../datasets/oltp_database/` |
| 6 | `cd week3_sql_for_analytics/session06_ctes_advanced_analytics/notebook_ecommerce` then `marimo edit notebook_ecommerce.py` | `../../../datasets/oltp_database/` |
| 6 | `cd week3_sql_for_analytics/session06_ctes_advanced_analytics/notebook_diabetic` then `python3 build_database.py` **once** (Windows: `python`), then `marimo edit notebook_diabetic_marimo.py` | `diabetic_hospitals.duckdb`, built from the folder's `data/` (see its README) |

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
