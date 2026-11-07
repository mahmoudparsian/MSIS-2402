# Week 2 — Working with Multiple Tables and Complex Queries

[← Week 1](../week1_db_concepts_sql_fundamentals/README.md) · [Course home](../README.md) · **Week 2 of 5** · [Week 3 →](../week3_sql_for_analytics/README.md)

⬇️ **No git?** Download this week as one ZIP (with the course data): [`week2_multi_table_complex_queries.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week2_multi_table_complex_queries.zip) — [how to unzip and run](../course_information/DOWNLOADING_COURSE_FILES.md)

> This module develops students' ability to work with related data across
> multiple tables and to solve more complex information needs using SQL.
> Students learn strategies for combining, structuring, and decomposing
> queries and for reasoning carefully about query results.
>
> — [Department course outline](../00_start_here/department_course_outline.md)

## At a Glance

| Session | Topic | Folder | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|---|
| **3** | Relational design and joins | [`session03_relational_design_joins/`](session03_relational_design_joins/) | `week2/session03/` — keys, relationships, and joins | Marimo notebooks (DuckDB) |
| **4** | Multi-table joins, subqueries, CTEs and set operations | [`session04_multi_table_joins/`](session04_multi_table_joins/) | `week2/session04/` — multi-table queries, subqueries, and CTEs | Marimo notebooks (DuckDB) |

---

## Session 3 — Relational Design and Joins

**Topics:** primary and foreign keys · one-to-many relationships · ER
diagrams · normalization · `INNER JOIN` and `LEFT JOIN`

| File | What it is |
|---|---|
| [`slides_01_relational_databases_joins.md`](session03_relational_design_joins/slides_01_relational_databases_joins.md) | Slide deck — relational databases and joins |
| [`slides_02_er_diagrams.md`](session03_relational_design_joins/slides_02_er_diagrams.md) | Slide deck — ER diagrams |
| [`notebook_01_relational_joins.py`](session03_relational_design_joins/notebook_01_relational_joins.py) | In-class notebook — relational databases and joins |
| [`CLASS_DISCUSSION.md`](session03_relational_design_joins/CLASS_DISCUSSION.md) | Class discussion — warm-up before the lab |
| [`data/`](session03_relational_design_joins/data/) | `customers.csv`, `orders.csv`, `products.csv` — a small 3-table dataset (200 / 800 / 100 rows), used by the notebook and the class discussion |

## Session 4 — Multi-Table Joins and Transaction Analytics

**Topics:** joining through the `order_items` junction table · insights from
`LEFT JOIN` · `USING` · `FULL OUTER JOIN` for reconciling two lists · transaction analytics on the shared retail schema · subqueries
(`IN`, `EXISTS`, correlated) · CTEs (`WITH`) · `UNION` / `INTERSECT` / `EXCEPT`
· `NOT IN` with `NULL` and join fan-out

| File | What it is |
|---|---|
| [`slides_01_joins_transaction_analytics.md`](session04_multi_table_joins/slides_01_joins_transaction_analytics.md) | Slide deck — joins and transaction analytics |
| [`slides_02_subqueries_ctes_set_ops.md`](session04_multi_table_joins/slides_02_subqueries_ctes_set_ops.md) | Slide deck — subqueries, CTEs and set operations (decomposing queries) |
| [`notebook_01_transaction_analytics.py`](session04_multi_table_joins/notebook_01_transaction_analytics.py) | In-class notebook — transaction analytics |
| [`CLASS_DISCUSSION.md`](session04_multi_table_joins/CLASS_DISCUSSION.md) | Class discussion — warm-up before the lab |
| [`data/`](session04_multi_table_joins/data/) | `customers.csv`, `products.csv`, `sales.csv` — the small tables used in the joins slides. The notebook and class discussion use the shared database in [`datasets/oltp_database/`](../datasets/oltp_database/) instead |

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
| 3 | `cd week2_multi_table_complex_queries/session03_relational_design_joins` then `marimo edit notebook_01_relational_joins.py` | `data/customers.csv`, `data/orders.csv`, `data/products.csv` |
| 4 | `cd week2_multi_table_complex_queries/session04_multi_table_joins` then `marimo edit notebook_01_transaction_analytics.py` | `../../datasets/oltp_database/` (the shared database) |

## Further Practice

- **Data story:** [`books_users_ratings/`](../data_stories/books_users_ratings/)
  — four real tables with enforced keys and orphaned foreign keys to reason
  about. See [`data_stories/README.md`](../data_stories/README.md).
- **Tutorials:** [joins](../tutorials/joins/joins_tutorial.md) and
  [normalization](../tutorials/normalization/normalization_tutorial.md).

---

[← Week 1](../week1_db_concepts_sql_fundamentals/README.md) · [Course home](../README.md) · [Week 3 →](../week3_sql_for_analytics/README.md)
