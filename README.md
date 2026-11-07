# MSIS-2402 — Database Management Systems: Fundamentals of SQL

**Santa Clara University · Leavey School of Business**
**Information Systems & Business Analytics — Graduate Program**

![Course: MSIS-2402](https://img.shields.io/badge/Course-MSIS--2402-862633) ![Level: Graduate](https://img.shields.io/badge/Level-Graduate-555555) ![Units: 2](https://img.shields.io/badge/Units-2-555555) ![Duration: 5 weeks, 10 sessions](https://img.shields.io/badge/Duration-5%20weeks%2C%2010%20sessions-555555) ![Quarter: Winter 2027](https://img.shields.io/badge/Quarter-Winter%202027-555555)  
[![SQL engine: DuckDB](https://img.shields.io/badge/SQL%20engine-DuckDB-FFF000?logo=duckdb&logoColor=black)](https://duckdb.org) [![Notebooks: Marimo](https://img.shields.io/badge/Notebooks-Marimo-1C7ED6)](https://marimo.io) [![Language: Python](https://img.shields.io/badge/Language-Python-3776AB?logo=python&logoColor=white)](https://www.python.org) [![Client-server: MySQL](https://img.shields.io/badge/Client--server-MySQL-4479A1?logo=mysql&logoColor=white)](https://www.mysql.com)  
[![Next course: MSIS-2407](https://img.shields.io/badge/Next%20course-MSIS--2407-2E7D32)](https://github.com/mahmoudparsian/MSIS-2407)

| | |
|---|---|
| **Format** | 5 weeks · 10 sessions (2 per week, 95 minutes each) |
| **Credit** | 2 units |
| **Quarter** | Winter 2027 |
| **Instructor** | Dr. Mahmoud Parsian |
| **Prerequisite** | None |
| **Primary tools** | [DuckDB](https://duckdb.org) · [Marimo](https://marimo.io) notebooks · Python · MySQL |

---

## Contents

1. [Course Description](#course-description)
2. [Course Schedule](#course-schedule)
3. [Grading at a Glance](#grading-at-a-glance)
4. [Getting Started](#getting-started)
5. [Repository Structure](#repository-structure)
6. [Course Policies & Information](#course-policies--information)
7. [About the Notebooks](#about-the-notebooks)

---

## Course Description

From the [SCU Graduate Bulletin](https://www.scu.edu/bulletin/graduate/leavey-school-of-business/chapter-7/information-systems-and-business-analytics-isba.html):

> This course aims to give an understanding of hands-on experience with the
> most widely used database tools. The objective of this course is to convey
> intermediate to advanced database concepts and to acquaint students with
> state-of-the-art software tools.
>
> The course will rely on classroom discussions, media articles and cases, as
> well as programming exercises and an integrative group project. Use of
> database software is required. […]
>
> Introduces database management and database management systems (DBMS).
> Teaches technical and managerial skills in database planning, analysis,
> logical design, physical design, implementation, and maintenance. Features
> hands-on training in database design, development, and implementation using
> relational DBMS software. Emphasizes designing and developing reliable
> databases to support organizational management.

**This term's coursework** consists of ten in-class labs and a final exam —
see [Grading at a Glance](#grading-at-a-glance).

### Why DuckDB?

The course is taught hands-on with **DuckDB**, a modern analytical database
that runs inside Python with no server to install or configure:

```python
import duckdb
con = duckdb.connect()
con.sql("SELECT 'Hello, SQL!' AS greeting").show()
```

That lets every student — whatever their technical background — spend class
time writing SQL rather than troubleshooting a database server. **MySQL** is
introduced in Weeks 4–5 to show how a traditional client–server database
behaves in real applications (connections, transactions, locking, security).

---

## Course Schedule

The five weeks follow the department's
[official course outline](5_weeks_outline/department_course_outline.md).

| Week | Module | Session | Lab topic |
|:---:|---|:---:|---|
| **1** | [Database Concepts and SQL Fundamentals](week1_db_concepts_sql_fundamentals/) | 1 | Retrieving and filtering data — `SELECT`, `WHERE`, `ORDER BY`, `DISTINCT`, `LIMIT` |
| | | 2 | Summarizing and modifying data — `GROUP BY`, `HAVING`, `CASE`, `INSERT` / `UPDATE` / `DELETE` |
| **2** | [Working with Multiple Tables and Complex Queries](week2_multi_table_complex_queries/) | 3 | Keys, relationships, and joins |
| | | 4 | Multi-table queries, subqueries, and CTEs |
| **3** | [SQL for Data Analytics](week3_sql_for_analytics/) | 5 | Window functions, ranking, and data-quality checks |
| | | 6 | Running totals, trends, and segmentation |
| **4** | [Introduction to Web Database Applications](week4_web_db_applications/) | 7 | Client–server databases (MySQL) |
| | | 8 | A simple database-backed web application |
| **5** | [Modern Data Systems and Database Management](week5_modern_data_systems/) | 9 | Transactions and concurrency; modern data systems |
| | | 10 | Performance, security, and governance |

**A typical session:**

| Time | Activity |
|---|---|
| First ~55 minutes | Lecture and live demo |
| Last ~40 minutes | **Lab A** in class, with the instructor available — submit it before class ends |
| By **11:59 pm Pacific Time the day after class** (Wednesday for a Tuesday session, Friday for a Thursday session) | Finish and submit **Lab B** on Camino |

---

## Grading at a Glance

| Component | Points |
|---|---:|
| **Labs** — two per session, 10 × 70 points (Lab A 40 + Lab B 30) | 700 |
| **Final Exam** — 2 hours, closed book, lock-down browser, separate exam slot after Session 10 | 300 |
| **Total** | **1,000** |

- Each session has a **Lab A** (core, 40 points, 6 tasks — done and
  submitted **in class**) and a **Lab B** (a step more challenging,
  30 points, 6 tasks — due **11:59 pm Pacific Time** the day after class).
- Labs are published in [`LABS/`](LABS/) at the start of each lab block;
  Lab A solutions are added after class, Lab B solutions after its late
  window closes.
- The lowest lab score is replaced by the average of the other nine.

How to submit (Camino, file names), the Lab B late penalty (−3 points per started
24 hours), attendance, letter grades, and the Final Exam format are
in [`ASSIGNMENTS_and_GRADING.md`](course_information/ASSIGNMENTS_and_GRADING.md).

---

## Getting Started

**Before the first session:**

1. **Install the course software.** Follow the step-by-step guide for your
   operating system — [macOS](software_installation/macbook/) or
   [Windows](software_installation/windows/) — starting from
   [`software_installation/README.md`](software_installation/README.md).
   It ends with a verification script that confirms everything works.
2. **Bring a laptop to every session** — labs start in class. See
   [`LAPTOP.md`](course_information/LAPTOP.md).
3. **Read the grading policy** in
   [`ASSIGNMENTS_and_GRADING.md`](course_information/ASSIGNMENTS_and_GRADING.md).
4. **Skim the course roadmap** and try the two orientation notebooks in
   [`5_weeks_outline/`](5_weeks_outline/README.md) — `sql_notebook_01.py` is the
   best first notebook to open.

**Getting the course files:** download this repository as a ZIP from GitHub
(**Code → Download ZIP**), or — optionally — clone it with Git
([guide](tutorials/git/README.md)). Download again (or `git pull`) each
session to pick up newly released labs.

---

## Repository Structure

### Curriculum

| Folder | Contents |
|---|---|
| [`5_weeks_outline/`](5_weeks_outline/README.md) | Course introduction — the course roadmap ([PDF](5_weeks_outline/5_weeks_outline.pdf)), the [official course outline](5_weeks_outline/department_course_outline.md), DuckDB 101 slides, and two orientation notebooks |
| [`week1_db_concepts_sql_fundamentals/`](week1_db_concepts_sql_fundamentals/) | Week 1 — Database Concepts and SQL Fundamentals |
| [`week2_multi_table_complex_queries/`](week2_multi_table_complex_queries/) | Week 2 — Working with Multiple Tables and Complex Queries |
| [`week3_sql_for_analytics/`](week3_sql_for_analytics/) | Week 3 — SQL for Data Analytics |
| [`week4_web_db_applications/`](week4_web_db_applications/) | Week 4 — Introduction to Web Database Applications |
| [`week5_modern_data_systems/`](week5_modern_data_systems/) | Week 5 — Modern Data Systems and Database Management |
| [`LABS/`](LABS/README.md) | **This term's labs**, published during each session (one folder per session); solutions are added after the deadlines |

### Course information and setup

| Folder | Contents |
|---|---|
| [`course_information/`](course_information/) | Grading, discussion format, academic conduct, office hours, and required software — [see below](#course-policies--information) |
| [`software_installation/`](software_installation/) | Step-by-step macOS and Windows setup for Python, DuckDB, Marimo, qStudio, MySQL, and the lock-down browser, with troubleshooting guides |

### Data and self-study

| Folder | Contents |
|---|---|
| [`datasets/`](datasets/README.md) | Shared datasets, led by [`oltp_database/`](datasets/oltp_database/) — the 7-table retail database (`customers`, `orders`, `order_items`, `products`, `payments`, `shipments`, `stores`) used in Weeks 1–3, the Weeks 4–5 MySQL labs, and the Final Exam |
| [`tutorials/`](tutorials/README.md) | Standalone self-study guides, by topic and by week: loading CSV/Parquet files, `GROUP BY`, joins, window functions, deduplication, normalization, user-defined functions, transactions, the DuckDB command line, and [Git](tutorials/git/README.md) |
| [`data_stories/`](data_stories/README.md) | Eight end-to-end case studies on real-world-sized datasets — Book-Crossing, Citi Bike, coffee shop, Olympics, Shopify, NYC taxi, Nova Retail, and a 200-row sales table. Its README maps each story to a week and says which ones need a build step first |
| [`books/`](books/) | Reference material |
| [`tools/`](tools/) | Notebook conversion and validation scripts |

### Inside a week folder

**Weeks 1–3** are each split into two self-contained **part** folders (for
example, `week1_db_concepts_sql_fundamentals/part1_single_table_sql/`). Every
part folder has the same layout; the examples below link to Week 1, Part 1.

| File / folder | Contents |
|---|---|
| `lecture_slides_*.md` | Slide decks — e.g. [`lecture_slides_01_sql_basics.md`](week1_db_concepts_sql_fundamentals/part1_single_table_sql/lecture_slides_01_sql_basics.md) |
| `notebook_*_marimo.py` | In-class teaching notebooks — e.g. [`notebook_3_duckdb_marimo.py`](week1_db_concepts_sql_fundamentals/part1_single_table_sql/notebook_3_duckdb_marimo.py) |
| `CLASS_DISCUSSION_0N.md` | The session's class discussion — a short warm-up before the lab — e.g. [`CLASS_DISCUSSION_01.md`](week1_db_concepts_sql_fundamentals/part1_single_table_sql/CLASS_DISCUSSION_01.md) |
| [`data/`](week1_db_concepts_sql_fundamentals/part1_single_table_sql/data/) | The part's datasets |

> **Tip:** notebooks find their data by relative path — the part's own
> `data/` folder or the shared [`datasets/`](datasets/README.md) — so run
> `marimo edit` from inside the part folder.

**Weeks 4–5** have no part folders. Each holds, directly in the week folder,
one lecture deck, one live-demo script, and one class discussion per session
— e.g. [`week4_web_db_applications/`](week4_web_db_applications/).

Every week folder has its own `README.md` with the details.

---

## Course Policies & Information

All in [`course_information/`](course_information/):

| Document | What it covers |
|---|---|
| [`SYLLABUS.md`](course_information/SYLLABUS.md) ([PDF](course_information/SYLLABUS.pdf)) | The whole course on one page — schedule, outcomes, grading, policies |
| [`ASSIGNMENTS_and_GRADING.md`](course_information/ASSIGNMENTS_and_GRADING.md) | Grading weights, how each session's lab works, attendance and late policies, Final Exam format |
| [`DISCUSSIONS_README.md`](course_information/DISCUSSIONS_README.md) | How the class discussions work |
| [`ACADEMIC_CONDUCT.md`](course_information/ACADEMIC_CONDUCT.md) | Academic integrity expectations |
| [`QUESTIONS_and_OFFICE_HOURS.md`](course_information/QUESTIONS_and_OFFICE_HOURS.md) | How to get help; office hours (days, times, room; the Zoom link is on Camino) |
| [`LAB_FORMAT_ANNOUNCEMENT.md`](course_information/LAB_FORMAT_ANNOUNCEMENT.md) | **Announcement:** how the labs work — Lab A in class, Lab B by 11:59 pm the next day, 6 tasks each |
| [`LAPTOP.md`](course_information/LAPTOP.md) | Laptop requirement for in-class labs |
| [`REQUIRED_SOFTWARE.md`](course_information/REQUIRED_SOFTWARE.md) | Every tool used in the course and why |
| [`installing_duckdb_on_macbook.md`](course_information/installing_duckdb_on_macbook.md) | DuckDB install guide — macOS |
| [`installing_duckdb_on_windows.md`](course_information/installing_duckdb_on_windows.md) | DuckDB install guide — Windows |
| [`marimo_duckdb_notebooks.md`](course_information/marimo_duckdb_notebooks.md) | Setting up and running the course's Marimo notebooks |

---

## About the Notebooks

Every notebook in this course is a **[Marimo](https://marimo.io)** notebook — a
plain `.py` file (most end in `_marimo.py`), not a Jupyter `.ipynb` file. Marimo notebooks are plain
Python files with **reactive** cells — change one cell and everything that
depends on it re-runs automatically, so results are never stale — and they
include native **SQL cells** that run directly against DuckDB.

```bash
marimo edit path/to/notebook_marimo.py   # open and edit interactively
marimo run  path/to/notebook_marimo.py   # view as a read-only app
```

> **Tip:** open a notebook from **inside its own folder** — notebooks find their
> data by relative path.

See [`marimo_duckdb_notebooks.md`](course_information/marimo_duckdb_notebooks.md)
for setup details.

---

<sub>MSIS-2402 · Santa Clara University · Leavey School of Business</sub>
