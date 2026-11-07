# Class Discussions

[← Course home](../README.md) · **Course information**

Every class session has a short **class discussion** — a warm-up worked in
pairs or small groups just before the session's lab. Discussions are **not
graded** and not take-home work (that's what each session's lab in
[`LABS/`](../LABS/) is for); they're a chance to think out loud, predict
results, and catch misconceptions before the lab.

---

## Format

Each discussion has three parts:

1. A **SQL Features to Learn** table — up to five features, each with a
   one-line description.
2. A **Setup** section — the dataset (tables, rows, columns), the folder to
   start from, and the exact statements that load the data into DuckDB (in
   a Marimo notebook or the `duckdb` command line). Run them once, then
   every item works.
3. Exactly **six items** of increasing difficulty. Every SQL item names the
   columns to return, their names, and the sort order, so you can compare
   your result with your partner's row for row.

| Level | Items | What to expect |
|---|:---:|---|
| **Simple** | 2 | Usually one pure-discussion prompt and one short SQL warm-up |
| **Intermediate** | 2 | SQL paired with a "what does this tell you?" follow-up question |
| **Intermediate+** | 2 | Multi-step SQL, a real bug or error to debug, or a finding that only shows up when you compare two queries |

**Grounded in real data.** Every query runs against the course's real
datasets — nothing is staged. Some items return a "boring" or empty result
on purpose, and some exist because of something genuinely surprising in the
data.

---

## Where to Find Them

Each discussion is the `CLASS_DISCUSSION.md` file in its session folder
(for example, `week1_db_concepts_sql_fundamentals/session01_single_table_sql/CLASS_DISCUSSION.md`).

| Week | Session | Discussion | Topics |
|:---:|:---:|---|---|
| **1** | 1 | [Foundations](../week1_db_concepts_sql_fundamentals/session01_single_table_sql/CLASS_DISCUSSION.md) | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT` — predicting a filtered row count before running it; what a top-10 list really shows; low- vs. high-cardinality columns |
| | 2 | [Aggregation & KPIs](../week1_db_concepts_sql_fundamentals/session02_aggregation_kpis/CLASS_DISCUSSION.md) | `COUNT` / `SUM` / `AVG`, `GROUP BY`, `WHERE` vs. `HAVING`; volume vs. value; debugging an aggregate inside `WHERE` |
| **2** | 3 | [Relational Modeling & JOINs](../week2_multi_table_complex_queries/session03_relational_design_joins/CLASS_DISCUSSION.md) | Primary and foreign keys, `INNER JOIN` vs. `LEFT JOIN`, and checking referential integrity with `LEFT JOIN … IS NULL` |
| | 4 | [Transaction Analytics](../week2_multi_table_complex_queries/session04_multi_table_joins/CLASS_DISCUSSION.md) | Revenue by category, revenue concentration, an ambiguous-column bug, and line-item vs. order-level averages |
| **3** | 5 | [Window Functions](../week3_sql_for_analytics/session05_operational_db_window_functions/CLASS_DISCUSSION.md) | `RANK()` vs. `DENSE_RANK()` on a tie, reading a running total, ranking with `PARTITION BY`, debugging a missing `OVER()` |
| | 6 | [CTEs & Ranking Analytics](../week3_sql_for_analytics/session06_ctes_advanced_analytics/CLASS_DISCUSSION.md) | Multi-CTE queries, `ROW_NUMBER()` for one winner per group, `SUM(…) OVER ()` for shares of a total, and why `HAVING` can't see a window function's result |
| **4** | 7 | [Client–Server Databases](../week4_web_db_applications/session07_client_server_mysql/CLASS_DISCUSSION.md) | What a database server does that an embedded database doesn't; checking a MySQL load; who keeps data clean; SQL that works in DuckDB but not in MySQL |
| | 8 | [Web Application Architecture](../week4_web_db_applications/session08_web_app_architecture/CLASS_DISCUSSION.md) | One search traced from browser to database; form values arriving as text; how many queries a page really runs; aggregating in SQL vs. Python; a search that crashes |
| **5** | 9 | [Transactions and Modern Data Systems](../week5_modern_data_systems/session09_transactions_modern_data/CLASS_DISCUSSION.md) | Atomicity in a checkout, data that doesn't add up, the lost-update timeline, a failed statement inside a transaction in DuckDB vs. MySQL, row vs. column storage |
| | 10 | [Performance, Security, and Governance](../week5_modern_data_systems/session10_performance_security_governance/CLASS_DISCUSSION.md) | Least privilege, selectivity and when an index helps, re-identification in "anonymous" counts, a view for an intern, a mistyped `DELETE` |

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
