# Assignments and Grading

[← Course home](../README.md) · **Course information**

| | |
|---|---|
| **Course** | MSIS-2402 — Database Management Systems: Fundamentals of SQL |
| **Quarter** | Winter 2027 |

**Contents:** 

[1. Grading Policy](#1-grading-policy) <br>
[2. Labs](#2-labs--how-each-session-works) <br>
[3. How to Submit a Lab](#3-how-to-submit-a-lab) <br>
[4. Attendance](#4-class-attendance) <br>
[5. Course Policies](#5-course-policies) <br>
[6. The 1,000-Point System and Letter Grades](#6-the-1000-point-system-and-letter-grades)

---

## 1. Grading Policy

| Component | Details | Points |
|---|---|---:|
| 🧪 **Labs** | Two labs per class session · 10 sessions × 70 points (Lab **A** 40 + Lab **B** 30) | 700 |
| ✏️ **Final Exam** | Separate scheduled exam slot after Session 10 · 2 hours · closed books, notes, software, Internet, and phone · lock-down browser required | 300 |
| | **Total** | **1,000** |

- **Labs** (two per session — see [Section 2](#2-labs--how-each-session-works)):
  you **finish and submit Lab A in class**, and submit **Lab B by 11:59 pm
  Pacific Time the same day** (see [Section 3](#3-how-to-submit-a-lab)).
- **Final Exam:** one exam covering the whole course, held in a separate
  scheduled exam slot after the last class session (not during Session 10).
  It is 2 hours, closed books/notes/software/Internet/phone, and taken in a
  lock-down browser — see [Course Policy #2](#5-course-policies).

---

## 2. Labs — How Each Session Works

The course meets for **10 sessions** over 5 weeks (2 per week), **95
minutes** each. Every session follows the same pattern:

| Time | Activity |
|---|---|
| First ~55 minutes | Lecture and live demo of the session's topic |
| Last ~40 minutes | Students do **Lab A** in class, with the instructor available for questions, and **submit it before class ends** |
| By **11:59 pm Pacific Time** the same day | Students finish and **submit Lab B** on Camino |

Every session has **two graded labs, 6 tasks each**:

| Lab | What it is | Points | Where and when |
|---|---|---:|---|
| **A** | The core lab — practice of what was just taught and demonstrated | **40** (Tasks 1–4: 7 points each; Tasks 5–6: 6 points each) | **In class.** Submit before class ends |
| **B** | A step more challenging — apply the session's SQL to new questions | **30** (5 points per task) | **After class.** Submit by **11:59 pm Pacific Time** the same day |

The session's lab score is **A + B**, out of **70**. Each **task** is graded
on its own: full points, partial points for logic that is partly right, or 0.
See Course Policy #4 for what is graded.

**Lab A is a timed, in-class lab.** What you have uploaded when class ends is
graded; Lab A cannot be submitted late. If the Office of Accessible Education
(OAE) has approved **extra time on timed tests** for you, it applies to Lab A:
your Lab A time is extended by that amount, and Camino stays open for you
until then. Send the instructor your OAE letter **before Session 1** so this
is set up for every session.

**Where to find them:** each session's labs (A and B) are published in the
course repository's [`LABS/`](../LABS/) folder **during class**, at the start
of the lab block. **Lab A solutions** are added to the same folder after the
Lab A time is over (including any extended time). **Lab B solutions** are
added after Lab B's late window closes — 72 hours after its deadline (see
Course Policy #6).

| Week | Session | Lab topic |
|---|:---:|---|
| **1** — Database Concepts and SQL Fundamentals | 1 | Retrieving and filtering data (`SELECT`, `WHERE`, `ORDER BY`, `DISTINCT`, `LIMIT`) |
| | 2 | Summarizing and modifying data (`GROUP BY`, `HAVING`, `CASE`, `INSERT` / `UPDATE` / `DELETE`) |
| **2** — Working with Multiple Tables and Complex Queries | 3 | Keys, relationships, and joins |
| | 4 | Multi-table queries, subqueries, and CTEs |
| **3** — SQL for Data Analytics | 5 | Window functions, ranking, and data-quality checks |
| | 6 | Running totals, trends, and segmentation |
| **4** — Introduction to Web Database Applications | 7 | Client–server databases (MySQL) |
| | 8 | A simple database-backed web application |
| **5** — Modern Data Systems and Database Management | 9 | Transactions and concurrency; modern data systems |
| | 10 | Performance, security, and governance |

---

## 3. How to Submit a Lab

| Item | Rule |
|---|---|
| **Where** | Camino — two assignments per session (N = 1 … 10): **Session N Lab A** and **Session N Lab B**. Upload each lab's files to its own assignment. |
| **Deadline** | **Lab A:** before class ends (the assignment closes when class ends). **Lab B:** **11:59 pm Pacific Time** on the day of the session. |
| **What** | Your Lab A file(s) and your **finished** Lab B file(s), renamed as below. Don't submit the data files or the solutions. |
| **File names** | `lastname_firstname_` + the lab's released file name **without `_student`** — all lower case, no spaces (a two-part last name joined with `-`). Save your working copy under this name from the start ([LABS/](../LABS/README.md)). |
| **Re-uploading** | Allowed until that lab's deadline. The **last** upload counts, and its time is your submission time. |

File names for each lab format (example student: Maria Lopez, Session 1):

| Lab format (sessions) | Submit for Lab A | Submit for Lab B |
|---|---|---|
| Marimo notebook (1–6, and 9 Lab A) | `lopez_maria_week1_lab1a_marimo.py` — your completed notebook | `lopez_maria_week1_lab1b_marimo.py` |
| MySQL handout (7, 9 Lab B, 10) | `lopez_maria_week4_lab1a.md` — for each task: the SQL you ran, the output, your written answers | `lopez_maria_week4_lab1b.md` |
| Web application (8) | `lopez_maria_week4_lab2a_shop_app.py` (your modified app) **and** `lopez_maria_week4_lab2a.md` (answers) | `lopez_maria_week4_lab2b_shop_app.py` **and** `lopez_maria_week4_lab2b.md` |

Session 9 mixes formats: `lopez_maria_week5_lab1a_marimo.py` and
`lopez_maria_week5_lab1b_mysql.md`.
A `.txt` file is accepted wherever `.md` is shown. Before uploading a
notebook, run it top to bottom once (in `marimo edit`, **Run all**) so every
cell works.

---

## 4. Class Attendance

**Attendance is mandatory.**

Lab A is done during the class session in which it is assigned. If you are
absent, you receive a zero (`0`) on that session's labs (A and B, 70 points).
There is no way to make up a missed lab, because the in-class lab, with
instructor support, is part of the session.

> **Exception:** students with a documented emergency, illness, or
> university-approved absence (disability accommodation, religious
> observance, etc.) may arrange an alternative with the instructor before
> the session or within 48 hours after it. The "lowest lab replaced" policy (Course Policy #1) is
> intended to absorb ordinary, undocumented absences — it is not a substitute
> for accommodation.

---

## 5. Course Policies

1. **Lowest lab replaced.** The lowest lab score is replaced by the average of
   your other nine lab scores, so labs still total 700 points.

2. **Final Exam.** The Final Exam is **2 hours**, proctored in person in a
   separately scheduled exam slot, and **closed books, closed notes, closed
   software, closed Internet, and no phones**. You take it on your laptop in
   a **lock-down browser, which is required** — install it and run a test
   before the exam. It has **20 questions, 300 points**:

   | Part | Questions | Points |
   |---|---|---:|
   | A — core concepts, all five weeks | 10 multiple choice × 6 | 60 |
   | B — which of four queries is right for a scenario | 5 multiple choice × 12 | 60 |
   | C — write one SQL query for a scenario, specified like the lab tasks (columns, filter, grouping, sort) | 5 × 36 | 180 |

   The exam shows a **reference sheet** of the course database (tables,
   columns, keys) and a list of **syntax reminders** (date functions,
   `CASE`, CTE and window-function syntax). Part C is graded on logic;
   minor syntax slips cost at most 2 points per question. Unlike the labs,
   the exam asks for no written business insights.

3. **Focus of the labs.** Labs emphasize hands-on SQL, database design, and
   analytical problem solving.

4. **What is graded.** Clear SQL logic and problem-solving approach are
   graded more heavily than minor formatting or syntax issues.

5. **No copy-paste.** You may use any appropriate resources to help you
   understand and complete your labs. However, the work you submit must
   reflect your own understanding and effort. Discussing general SQL concepts
   with classmates is fine; sharing queries or notebooks is not.

6. **Late policy (labs).** **Lab A** cannot be submitted late — it is done
   and submitted in class (see [Section 2](#2-labs--how-each-session-works)
   for extended time). A late **Lab B** loses **3 points** (10% of 30) for **each started
   24-hour period** after the 11:59 pm Pacific Time deadline, counted from your
   last Lab B upload:

   | Last Lab B upload | Penalty |
   |---|---:|
   | by 11:59 pm on the session day | none |
   | up to 24 hours late (e.g. 12:30 am) | −3 |
   | 24–48 hours late | −6 |
   | 48–72 hours late | −9 |
   | more than 72 hours late | not graded: 0 for Lab B |

   The penalty comes off Lab B's 30 points (never below 0). An extension must
   be arranged with the instructor **before** the deadline.

---

## 6. The 1,000-Point System and Letter Grades

The 1,000-point scale keeps grading simple, transparent, and easy to
understand:

- You always know exactly where you stand.
- No percentage conversions are required — divide by 10:

| Points | Percentage |
|---:|---:|
| 850 | 85% |
| 950 | 95% |

**Letter grades** (total points out of 1,000):

| Letter | Points (out of 1,000) | Percentage |
|:---:|---|---|
| A | 940 – 1,000 | 94% – 100% |
| A− | 900 – 939 | 90% – 93.9% |
| B+ | 870 – 899 | 87% – 89.9% |
| B | 830 – 869 | 83% – 86.9% |
| B− | 800 – 829 | 80% – 82.9% |
| C+ | 770 – 799 | 77% – 79.9% |
| C | 730 – 769 | 73% – 76.9% |
| C− | 700 – 729 | 70% – 72.9% |
| D+ | 670 – 699 | 67% – 69.9% |
| D | 630 – 669 | 63% – 66.9% |
| D− | 600 – 629 | 60% – 62.9% |
| F | below 600 | below 60% |

Fractional totals are rounded to the nearest whole point before this table
is applied (939.5 → 940 → A; 939.4 → 939 → A−).

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
