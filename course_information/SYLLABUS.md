# MSIS-2402 — Database Management Systems: Fundamentals of SQL

[← Course home](../README.md) · **Course information** · Syllabus

**Santa Clara University · Leavey School of Business · Information Systems & Business Analytics — Graduate Program**<br>
**Winter 2027 · 2 units · 5 weeks, 10 sessions**

This syllabus collects, in one document, what the course repository
publishes in its separate pages. If this page and a linked page ever
disagree, the linked page in [`course_information/`](./) is the one that
applies, and the instructor will correct this page.

---

## 1. Course Information

| | |
|---|---|
| **Course** | MSIS-2402 — Database Management Systems: Fundamentals of SQL |
| **Units** | 2 |
| **Quarter** | Winter 2027 |
| **Format** | 5 weeks · 10 sessions (2 per week) · 95 minutes per session |
| **Meetings** | Tuesday and Thursday, 7:35–9:10 pm Pacific Time |
| **Session dates** | *To be announced on Camino* <!-- TODO(syllabus): add the 10 session dates from the Leavey graduate calendar (My Leavey Portal), not the undergraduate Registrar calendar --> |
| **Classroom** | *To be announced on Camino* <!-- TODO(syllabus): room --> |
| **Prerequisite** | None |
| **Learning management system** | Camino (Canvas) — lab submissions, Final Exam, announcements, Zoom link |
| **Course materials** | Course repository: <https://github.com/mahmoudparsian/MSIS-2402> — or one ZIP per week and per session's labs ([`DOWNLOADING_COURSE_FILES.md`](DOWNLOADING_COURSE_FILES.md)) |
| **Follow-on course** | MSIS-2407 — <https://github.com/mahmoudparsian/MSIS-2407> |

### Instructor

| | |
|---|---|
| **Instructor** | Dr. Mahmoud Parsian |
| **Email** | [mparsian@scu.edu](mailto:mparsian@scu.edu) |
| **Office hours** | Mondays and Wednesdays, 4:15–5:00 pm Pacific Time |
| **Where** | In person at Lucas Hall, Room 316U, or on Zoom (the Zoom link and passcode are posted on Camino) |
| **First / last office hour** | *To be announced on Camino* <!-- TODO(syllabus): same dates as QUESTIONS_and_OFFICE_HOURS.md --> |

Details: [`QUESTIONS_and_OFFICE_HOURS.md`](QUESTIONS_and_OFFICE_HOURS.md).

---

## 2. Course Description

From the [SCU Graduate Bulletin](https://www.scu.edu/bulletin/graduate/leavey-school-of-business/chapter-7/information-systems-and-business-analytics-isba.html):

> Introduces database management and database management systems (DBMS).
> Teaches technical and managerial skills in database planning, analysis,
> logical design, physical design, implementation, and maintenance. Features
> hands-on training in database design, development, and implementation using
> relational DBMS software. Emphasizes designing and developing reliable
> databases to support organizational management.

**This term's coursework** consists of **20 labs** (two per session) and a
**Final Exam** (Section 6).

The course is taught hands-on with **DuckDB**, an analytical SQL database
that runs inside Python with no server to install, so class time goes to
writing SQL rather than configuring a server. **MySQL** is introduced in
Weeks 4–5 to show how a client–server database behaves in real applications
(connections, transactions, locking, security).

---

## 3. Learning Outcomes

The five weeks follow the department's
[official course outline](../5_weeks_outline/department_course_outline.md).
By the end of the course, students will be able to:

| # | Outcome | Week |
|:---:|---|:---:|
| 1 | Explain how relational data is organized (tables, rows, columns, primary and foreign keys) and write SQL to create, retrieve, filter, sort, summarize, and modify data in a single table | 1 |
| 2 | Combine related tables with joins, and break a complex question into steps with subqueries, common table expressions (CTEs), and set operations — and check that a result is correct (row counts, `NULL`s, join fan-out) | 2 |
| 3 | Use SQL for data analysis: aggregation, ranking and other window functions, running totals, shares of a total, trends, segmentation, and data-quality checks | 3 |
| 4 | Describe the architecture of a database-backed application (user interface, application logic, database), work with a client–server database (MySQL), and explain how parameterized SQL prevents SQL injection | 4 |
| 5 | Describe the modern data landscape (OLTP vs. OLAP, warehouses, lakes, NoSQL, cloud databases) and the main database-management concerns: transactions and concurrency, performance and indexes, security and privileges, governance, and backup | 5 |

---

## 4. Course Schedule

Every session: **lecture and live demo** (first ~55 minutes), then **Lab A**
in class (last ~40 minutes). **Lab B** is due **11:59 pm Pacific Time the day
after class** (Wednesday for a Tuesday session, Friday for a Thursday session).

| Week | Module | Session | Topics | Labs |
|:---:|---|:---:|---|---|
| **1** | Database Concepts and SQL Fundamentals | 1 | What a relational database is · `SELECT`, `WHERE`, `ORDER BY`, `DISTINCT`, `LIMIT` · `AND` before `OR` · derived columns · `CASE` · a first look at `GROUP BY` | Retrieving and filtering data |
| | | 2 | `COUNT`, `SUM`, `AVG` · `GROUP BY` and `HAVING` · the order SQL runs a query in · business KPIs · `INSERT`, `UPDATE`, `DELETE` · text functions (`TRIM`, `LOWER`, `UPPER`, `\|\|`) · date functions (`YEAR`, `MONTH`, `DATE_TRUNC`, `strftime`, `date_diff`, `INTERVAL`) | Summarizing and modifying data |
| **2** | Working with Multiple Tables and Complex Queries | 3 | Primary and foreign keys · one-to-many relationships · ER diagrams · normalization · `INNER JOIN` and `LEFT JOIN` | Keys, relationships, and joins |
| | | 4 | Joining through a junction table · `USING` · `FULL OUTER JOIN` · subqueries (`IN`, `EXISTS`, correlated) · CTEs (`WITH`) · `UNION` / `INTERSECT` / `EXCEPT` · `NOT IN` with `NULL` · join fan-out | Multi-table queries, subqueries, and CTEs |
| **3** | SQL for Data Analytics | 5 | The 7-table operational schema · data-quality checks and deduplication · window functions · `ROW_NUMBER`, `RANK`, `DENSE_RANK` (ties, top N per group, `QUALIFY`) · trends and segmentation | Window functions, ranking, and data-quality checks |
| | | 6 | CTEs · running totals · top N per group · an end-to-end analysis | Running totals, trends, and segmentation |
| **4** | Introduction to Web Database Applications | 7 | Embedded vs. client–server databases · MySQL: connecting and loading data · data types · constraints · CRUD from two clients · SQL dialects · views · `information_schema` | Client–server databases (MySQL) |
| | | 8 | The three layers (user interface, application logic, database) · HTTP requests and responses · forms, `GET` vs. `POST` · routing · input validation · SQL parameters and SQL injection · a JSON API | A simple database-backed web application |
| **5** | Modern Data Systems and Database Management | 9 | Transactions and ACID · autocommit · isolation · lost updates and row locks · OLTP vs. OLAP · row vs. column storage · data warehouses and ETL · data lakes and lakehouses · NoSQL · cloud databases | Transactions and concurrency; modern data systems |
| | | 10 | Query plans (`EXPLAIN`, `EXPLAIN ANALYZE`) · indexes · authentication vs. authorization · least privilege with `GRANT` · views and roles · encryption · data governance, data quality, privacy · backup and recovery | Performance, security, and governance |
| — | **Final Exam** | — | All five weeks (Section 6) | Separate exam slot after Session 10 — date and time *to be announced on Camino* <!-- TODO(syllabus): exam date/time --> |

Each week's folder in the repository has a `README.md` listing that week's
slide decks, notebooks, class discussions, and data.

---

## 5. Required Materials

**No textbook is required.** All course materials — slide decks, notebooks,
datasets, tutorials, labs — are in the course repository. Optional reading:
*DuckDB in Action* ([`books/`](../books/)).

**A laptop at every session** (fully charged, with its charger): every
session ends with an in-class lab. A dead battery, a forgotten charger, or
software that was not installed beforehand is not an excused reason to miss a
lab ([`LAPTOP.md`](LAPTOP.md)).

**Software** — install **before Session 1**, following the step-by-step guide
for macOS or Windows in [`software_installation/`](../software_installation/README.md)
(it ends with a verification script):

| # | Tool | Used for |
|:---:|---|---|
| 1 | Python 3.11 or newer | Runs the notebooks |
| 2 | DuckDB 2.0 or newer (`pip install "duckdb>=2.0"`) | The course's main SQL engine (Weeks 1–5) |
| 3 | MySQL | Client–server database (Weeks 4–5) |
| 4 | Marimo | Reactive Python notebooks with SQL cells |
| 5 | Pandas | Query results as data frames |
| 6 | Matplotlib | Charts in the notebooks |
| 7 | sqlglot | SQL parser used by Marimo's SQL cells |
| 8 | Java 21 | Runtime for qStudio |
| 9 | qStudio | Desktop SQL editor |
| 10 | Respondus LockDown Browser | **Final Exam only** — install it and take the practice quiz at least one week before the exam |

Why each tool is used: [`REQUIRED_SOFTWARE.md`](REQUIRED_SOFTWARE.md).

---

## 6. Assessment and Grading

| Component | Details | Points |
|---|---|---:|
| **Labs** | 10 sessions × 70 points: **Lab A** 40 + **Lab B** 30 | 700 |
| **Final Exam** | 2 hours · closed books, notes, software, Internet, and phone · LockDown Browser · separate exam slot after Session 10 | 300 |
| | **Total** | **1,000** |

### Labs

Every session has two graded labs of **6 tasks** each:

| Lab | What it is | Points | When it is due |
|---|---|---:|---|
| **A** | Core practice of what was just taught and demonstrated | **40** (Tasks 1–4: 7 each; Tasks 5–6: 6 each) | **In class** — submit before class ends; the Camino assignment closes when class ends |
| **B** | A step more challenging — the session's SQL on new questions | **30** (5 per task) | **11:59 pm Pacific Time the day after class** (Wednesday for a Tuesday session, Friday for a Thursday session) |

- Each task is graded on its own: full points, partial points for logic that
  is partly right, or 0. Clear SQL logic and problem-solving approach count
  more than minor formatting or syntax issues.
- **Lowest lab replaced:** the lowest session lab score (out of 70) is
  replaced by the average of the other nine, so labs still total 700 points.
- Labs are published in the repository's [`LABS/`](../LABS/README.md) folder
  at the start of each lab block. Lab A solutions are added after the Lab A
  time is over; Lab B solutions after Lab B's 72-hour late window closes.

### Final Exam

| Part | Questions | Points |
|---|---|---:|
| A — core concepts, all five weeks | 10 multiple choice × 6 | 60 |
| B — which of four queries is right for a scenario | 5 multiple choice × 12 | 60 |
| C — write one SQL query for a scenario, specified like the lab tasks | 5 × 36 | 180 |
| | **20 questions** | **300** |

The exam is taken on your laptop in Camino inside **Respondus LockDown
Browser** (required), proctored in person, in a separately scheduled exam
slot after Session 10. It shows a reference sheet of the course database
(tables, columns, keys) and a list of syntax reminders. Part C is graded on
logic; minor syntax slips cost at most 2 points per question. Install the
LockDown Browser and take the practice quiz (**Camino → Quizzes →
LockDown Browser Practice Quiz**) at least one week before the exam:
[macOS guide](../software_installation/macbook/step_6_install_lockdown_browser.md) ·
[Windows guide](../software_installation/windows/step_6_install_lockdown_browser.md).

### Letter grades

Total points out of 1,000, rounded to the nearest whole point first
(939.5 → 940 → A; 939.4 → 939 → A−):

| Letter | Points | Letter | Points | Letter | Points |
|:---:|---|:---:|---|:---:|---|
| A | 940 – 1,000 | B− | 800 – 829 | D+ | 670 – 699 |
| A− | 900 – 939 | C+ | 770 – 799 | D | 630 – 669 |
| B+ | 870 – 899 | C | 730 – 769 | D− | 600 – 629 |
| B | 830 – 869 | C− | 700 – 729 | F | below 600 |

---

## 7. Lab Submission and Late Policy

| Item | Rule |
|---|---|
| **Where** | Camino — two assignments per session (N = 1 … 10): **Session N Lab A** and **Session N Lab B** |
| **File names** | `lastname_firstname_` + the lab's released file name without `_student`, all lower case, no spaces (e.g. `lopez_maria_week1_lab1a_marimo.py`). Each lab's header lists its exact files |
| **Re-uploading** | Allowed until the deadline; the **last** upload counts, and its time is the submission time |
| **Lab A late** | Not accepted — Lab A is done and submitted in class |
| **Lab B late** | −3 points (10% of 30) for each started 24-hour period after the deadline, counted from the last upload: up to 24 h late −3, 24–48 h −6, 48–72 h −9, more than 72 h late: 0 for Lab B. The penalty never takes Lab B below 0 |
| **Extensions** | Must be arranged with the instructor **before** the deadline |

Full rules and examples: [`ASSIGNMENTS_and_GRADING.md`](ASSIGNMENTS_and_GRADING.md) §2–3, §5.

---

## 8. Attendance

**Attendance is mandatory.** Lab A is done during the session in which it is
assigned; a student who is absent receives 0 on that session's labs (A and B,
70 points), and a missed lab cannot be made up. The "lowest lab replaced"
policy is meant to absorb an ordinary, undocumented absence.

**Exception:** a student with a documented emergency, illness, or
university-approved absence (disability accommodation, religious observance,
and similar) may arrange an alternative with the instructor **before** the
session or **within 48 hours** after it.

---

## 9. Accessibility and Accommodations

If you have a documented disability for which accommodations may be required
in this class, contact the **Office of Accessible Education (OAE)** —
<https://www.scu.edu/oae/> — in advance (at least two weeks' notice is
recommended) to arrange accommodations and proctored exams.

**Extra time on timed tests also applies to Lab A** (a timed, in-class lab):
your Lab A time is extended by the approved amount, and
Camino stays open for you until then. Send the instructor your OAE letter
**before Session 1** so this is set up for every session.

---

## 10. Academic Integrity and Conduct

- **Your own work.** You may use any appropriate resources to help you
  understand and complete your labs, but the work you submit must reflect
  your own understanding and effort. Discussing general SQL concepts with
  classmates is fine; sharing queries or notebooks is not (Course Policy #5).
- **SCU Academic Integrity:** <https://www.scu.edu/academic-integrity/> —
  the university's pledge, policy, and resources.
- **Classroom conduct:** respect, resourcefulness, honesty, and constructive
  feedback — see [`ACADEMIC_CONDUCT.md`](ACADEMIC_CONDUCT.md).
- **Discrimination, harassment, and sexual misconduct:** Santa Clara
  University does not tolerate them. Information, reporting options, and
  support: <https://www.scu.edu/title-ix/>.

---

## 11. Getting Help

| Need | Where |
|---|---|
| A question about course content | Ask in class, come to office hours, post on **Camino Discussions** (students, the TA, and the instructor respond), or [email the instructor](mailto:mparsian@scu.edu) |
| Installing the course software | [`software_installation/`](../software_installation/README.md) and its troubleshooting pages |
| LockDown Browser or other SCU technology | SCU Technology Help: (408) 554-5700, or a [Computing Support Request](https://help.scu.edu/TDClient/111/Portal/Home/) |

---

## 12. Course Documents

| Document | Contents |
|---|---|
| [`ASSIGNMENTS_and_GRADING.md`](ASSIGNMENTS_and_GRADING.md) | Grading, labs, submission, attendance, course policies, letter grades |
| [`LAB_FORMAT_ANNOUNCEMENT.md`](LAB_FORMAT_ANNOUNCEMENT.md) | How Lab A and Lab B work |
| [`DISCUSSIONS_README.md`](DISCUSSIONS_README.md) | The class discussions (a short, ungraded warm-up before each lab) |
| [`QUESTIONS_and_OFFICE_HOURS.md`](QUESTIONS_and_OFFICE_HOURS.md) | Office hours and how to ask questions |
| [`LAPTOP.md`](LAPTOP.md) | Laptop requirement |
| [`REQUIRED_SOFTWARE.md`](REQUIRED_SOFTWARE.md) | Every tool and why it is used |
| [`ACADEMIC_CONDUCT.md`](ACADEMIC_CONDUCT.md) | Classroom conduct |
| [`5_weeks_outline/`](../5_weeks_outline/README.md) | Course roadmap and the department's course outline |

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
