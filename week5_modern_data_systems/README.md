# Week 5 — Modern Data Systems and Database Management

[← Week 4](../week4_web_db_applications/README.md) · [Course home](../README.md) · **Week 5 of 5**

> This module broadens the course beyond SQL and relational databases to
> introduce the modern data landscape and practical database management
> considerations. Students develop general awareness of different types of
> data systems, database technologies, data platforms, and the operational,
> security, performance, and governance issues involved in managing
> organizational data.
>
> — [Department course outline](../5_weeks_outline/department_course_outline.md)

## At a Glance

| Session | Topic | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|
| **9** | Transactions, concurrency, and modern data systems | `week5_lab1/` — transactions and concurrency | Lab A: Marimo notebook (DuckDB). Lab B: Markdown handout with **two** `mysql` sessions at once |
| **10** | Performance, security, and governance | `week5_lab2/` — query plans and indexes; users, grants, and views | Markdown handouts in the `mysql` client |

Both live demos and three of the four graded labs use MySQL with the
`isba_shop` database loaded, as set up before
[Session 7](../week4_web_db_applications/README.md). Lab 2a starts from a
**fresh** load — re-run the same load command before it.

---

## Session 9 — Transactions, Concurrency, and Modern Data Systems

**Topics:** transactions and ACID · autocommit · isolation and snapshots ·
errors inside a transaction · lost updates and locks · isolation levels ·
OLTP vs. OLAP · row vs. column storage · data warehouses and ETL · data lakes
and lakehouses · NoSQL families · cloud databases

| File | What it is |
|---|---|
| [`lecture_slides_01_transactions_modern_data.md`](lecture_slides_01_transactions_modern_data.md) | Slide deck (Marp) |
| [`demo_01_transactions_mysql.sql`](demo_01_transactions_mysql.sql) | Live demo — two terminals (A and B) connected to `isba_shop`: isolation, a consistent snapshot, and a checkout that fails halfway; the expected output is in the comments |
| [`CLASS_DISCUSSION_01.md`](CLASS_DISCUSSION_01.md) | Class discussion — warm-up before the lab |

**Running a MySQL demo:** open two terminals (A and B) and connect each to
the course data with `mysql -u root isba_shop` (Windows:
`mysql -u root -p isba_shop`, then your root password). Run the demo file's
statements **one at a time**, in the terminal each comment names (A or B),
and compare with the expected output in the comments.

## Session 10 — Performance, Security, and Governance

**Topics:** query plans (`EXPLAIN`, `EXPLAIN ANALYZE`) · indexes and
selectivity · threats · authentication vs. authorization · least privilege
with `GRANT` · defense in depth · views and roles · encryption · data
governance and classification · measuring data quality · privacy · backup
and recovery

| File | What it is |
|---|---|
| [`lecture_slides_02_performance_security_governance.md`](lecture_slides_02_performance_security_governance.md) | Slide deck (Marp) |
| [`demo_02_performance_security_mysql.sql`](demo_02_performance_security_mysql.sql) | Live demo — an index on `shipments`, a least-privilege account for the web application (used from a second terminal), and a backup proven by restoring it; the expected output is in the comments |
| [`CLASS_DISCUSSION_02.md`](CLASS_DISCUSSION_02.md) | Class discussion — warm-up before the lab |

> **Note:** run `demo_02_performance_security_mysql.sql` one statement at a
> time, connected as in Session 9 — never as a single script.

---

## Labs

Each session's labs are published in [`LABS/`](../LABS/) during class — a
**Lab A** (core, 40 points, 6 tasks), done and submitted on Camino **before
class ends**, and a **Lab B** (a step more challenging, 30 points, 6 tasks),
due by **11:59 pm Pacific Time** that day ([how](../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab)).
Solutions are added after the deadlines.

## Class Discussions

One short warm-up per session, worked in pairs before the lab. The format is
described in
[`DISCUSSIONS_README.md`](../course_information/DISCUSSIONS_README.md).

## Further Practice

- **Tutorial:** [transactions in action](../tutorials/transactions_in_action/)
  — the same transaction ideas, hands-on in DuckDB.

## Final Exam

The Final Exam covers the whole course: **2 hours, 300 points**, in a
separate exam slot after Session 10, taken in the required lock-down browser
(closed books, notes, software, Internet; no phones). It has **20
questions** — 10 multiple-choice questions on core concepts (60 points), 5
multiple-choice "which query is right?" questions (60), and 5 "write the
SQL" questions specified like the lab tasks (180) — with a reference sheet
of the course database and a list of syntax reminders. Full rules:
[Course Policy #2](../course_information/ASSIGNMENTS_and_GRADING.md#5-course-policies).

---

[← Week 4](../week4_web_db_applications/README.md) · [Course home](../README.md)
