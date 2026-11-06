# Week 2 — Working with Multiple Tables and Complex Queries

[← Week 1](../week1_db_concepts_sql_fundamentals/README.md) · [Course home](../README.md) · **Week 2 of 5** · [Week 3 →](../week3_sql_for_analytics/README.md)

> This module develops students' ability to work with related data across
> multiple tables and to solve more complex information needs using SQL.
> Students learn strategies for combining, structuring, and decomposing
> queries and for reasoning carefully about query results.
>
> — [Department course outline](../5_weeks_outline/department_course_outline.md)

## At a Glance

| Session | Topic | Folder | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|---|
| **3** | Relational design and joins | [`part1_relational_design_joins/`](part1_relational_design_joins/) | `week2_lab1/` — keys, relationships, and joins | Marimo notebooks (DuckDB) |
| **4** | Multi-table joins, subqueries, CTEs and set operations | [`part2_joins_order_items/`](part2_joins_order_items/) | `week2_lab2/` — multi-table queries, subqueries, and CTEs | Marimo notebooks (DuckDB) |

---

## Session 3 — Relational Design and Joins

**Topics:** primary and foreign keys · one-to-many relationships · ER
diagrams · normalization · `INNER JOIN` and `LEFT JOIN`

| File | What it is |
|---|---|
| [`lecture_slides_joins.md`](part1_relational_design_joins/lecture_slides_joins.md) | Slide deck — relational databases and joins |
| [`lecture_slides_er_diagram.md`](part1_relational_design_joins/lecture_slides_er_diagram.md) | Slide deck — ER diagrams |
| [`notebook_3_marimo.py`](part1_relational_design_joins/notebook_3_marimo.py) | In-class notebook — relational databases and joins |
| [`CLASS_DISCUSSION_01.md`](part1_relational_design_joins/CLASS_DISCUSSION_01.md) | Class discussion — warm-up before the lab |
| [`data/`](part1_relational_design_joins/data/) | `customers.csv`, `orders.csv`, `products.csv` — a small 3-table dataset (200 / 800 / 100 rows), used by the notebook and the class discussion |

## Session 4 — Multi-Table Joins and Transaction Analytics

**Topics:** joining through the `order_items` junction table · insights from
`LEFT JOIN` · `USING` · `FULL OUTER JOIN` for reconciling two lists · transaction analytics on the shared retail schema · subqueries
(`IN`, `EXISTS`, correlated) · CTEs (`WITH`) · `UNION` / `INTERSECT` / `EXCEPT`
· `NOT IN` with `NULL` and join fan-out

| File | What it is |
|---|---|
| [`lecture_slides_joins.md`](part2_joins_order_items/lecture_slides_joins.md) | Slide deck — joins and transaction analytics |
| [`lecture_slides_subqueries_ctes_set_ops.md`](part2_joins_order_items/lecture_slides_subqueries_ctes_set_ops.md) | Slide deck — subqueries, CTEs and set operations (decomposing queries) |
| [`notebook_3_joins_marimo.py`](part2_joins_order_items/notebook_3_joins_marimo.py) | In-class notebook — transaction analytics |
| [`CLASS_DISCUSSION_02.md`](part2_joins_order_items/CLASS_DISCUSSION_02.md) | Class discussion — warm-up before the lab |
| [`data/`](part2_joins_order_items/data/) | `customers.csv`, `products.csv`, `sales.csv` — the small tables used in the joins slides. The notebook and class discussion use the shared database in [`datasets/oltp_database/`](../datasets/oltp_database/) instead |

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
| 3 | `cd week2_multi_table_complex_queries/part1_relational_design_joins` then `marimo edit notebook_3_marimo.py` | `data/customers.csv`, `data/orders.csv`, `data/products.csv` |
| 4 | `cd week2_multi_table_complex_queries/part2_joins_order_items` then `marimo edit notebook_3_joins_marimo.py` | `../../datasets/oltp_database/` (the shared database) |

## Further Practice

- **Data story:** [`books_users_ratings/`](../data_stories/books_users_ratings/)
  — four real tables with enforced keys and orphaned foreign keys to reason
  about. See [`data_stories/README.md`](../data_stories/README.md).
- **Tutorials:** [joins](../tutorials/joins/joins_tutorial.md) and
  [normalization](../tutorials/normalization/normalization_tutorial.md).

---

[← Week 1](../week1_db_concepts_sql_fundamentals/README.md) · [Course home](../README.md) · [Week 3 →](../week3_sql_for_analytics/README.md)
