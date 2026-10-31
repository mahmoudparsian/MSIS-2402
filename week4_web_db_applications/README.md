# Week 4 — Introduction to Web Database Applications

[← Week 3](../week3_sql_for_analytics/README.md) · [Course home](../README.md) · **Week 4 of 5** · [Week 5 →](../week5_modern_data_systems/README.md)

> This module introduces the role of databases in web and other modern
> applications. Students develop a broad understanding of application
> architecture and the relationship among user interfaces, application
> logic, and databases. Basic web technologies and a simple database-backed
> application are used to demonstrate how data moves through a real
> application.
>
> — [Department course outline](../5_weeks_outline/department_course_outline.md)

## At a Glance

| Session | Topic | Lab (in [`LABS/`](../LABS/)) | Lab format |
|:---:|---|---|---|
| **7** | Client–server databases (MySQL) | `week4_lab1/` — a database server and its clients (1a); constraints and views (1b) | Markdown handouts; you work in the `mysql` command-line client |
| **8** | Web application architecture | `week4_lab2/` — a simple database-backed web application | A small Python + DuckDB web app (`shop_app_starter.py`) and Markdown handouts |

**Before Session 7 starts** (the lab needs both):

1. Install MySQL — [macOS](../software_installation/macbook/step_5_install_mysql.md) ·
   [Windows](../software_installation/windows/step_5_install_mysql.md).
2. Load the course data into it as the `isba_shop` database — the one-line
   command is in [`datasets/oltp_database/mysql/README.md`](../datasets/oltp_database/mysql/README.md).
   It finishes by printing the row count of all 7 tables (1,000 customers …
   100,000 shipments).

---

## Session 7 — Client–Server Databases (MySQL)

**Topics:** embedded vs. client–server databases · connecting and loading
data · data types and `DECIMAL` · constraints · CRUD across two clients · SQL
dialects · views · `information_schema`

| File | What it is |
|---|---|
| [`lecture_slides_01_client_server_mysql.md`](lecture_slides_01_client_server_mysql.md) | Slide deck (Marp) |
| [`demo_01_client_server_mysql.sql`](demo_01_client_server_mysql.sql) | Live demo — run in two terminals (A and B) connected to the `isba_shop` database; the expected output is in the comments |
| [`CLASS_DISCUSSION_01.md`](CLASS_DISCUSSION_01.md) | Class discussion — warm-up before the lab |

**Running a MySQL demo:** open two terminals (A and B) and connect each to
the course data with `mysql -u root isba_shop` (Windows:
`mysql -u root -p isba_shop`, then your root password). Run the demo file's
statements **one at a time**, in the terminal each comment names (A or B),
and compare with the expected output in the comments.

## Session 8 — Web Application Architecture

**Topics:** the three layers (user interface, application logic, database) ·
URLs · HTTP requests, responses, and status codes · forms and `GET` vs.
`POST` · routing · input validation · SQL parameters · turning rows into HTML
· a JSON API · from demo to production

| File | What it is |
|---|---|
| [`lecture_slides_02_web_app_architecture.md`](lecture_slides_02_web_app_architecture.md) | Slide deck (Marp) |
| [`demo_02_store_finder.py`](demo_02_store_finder.py) | Live demo — a small "Store Finder" web app built with the Python standard library and DuckDB |
| [`CLASS_DISCUSSION_02.md`](CLASS_DISCUSSION_02.md) | Class discussion — warm-up before the lab |

**Running the web demo:** from the course repository folder (the one that
contains `README.md` and `datasets/` — `MSIS-2402-main` if you downloaded the
ZIP):

```bash
cd week4_web_db_applications
python3 demo_02_store_finder.py        # Windows: python demo_02_store_finder.py
```

Then open <http://localhost:8001> in your browser. The terminal prints every
request and SQL statement as it happens. Stop the server with **Ctrl+C**.
The demo reads the shared database in `../datasets/oltp_database/`, so it
must be started from this folder.

---

## Labs

Each session's labs are published in [`LABS/`](../LABS/) during class — an
**a** lab (core, 40 points), a **b** lab (a step more challenging, 30 points),
and an optional, ungraded **c** lab. Submit a and b on Camino by **11:00 pm
Pacific Time** that day ([how](../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab));
solutions are added after the deadline.

## Class Discussions

One short warm-up per session, worked in pairs before the lab. The format is
described in
[`DISCUSSIONS_README.md`](../course_information/DISCUSSIONS_README.md).

---

[← Week 3](../week3_sql_for_analytics/README.md) · [Course home](../README.md) · [Week 5 →](../week5_modern_data_systems/README.md)
