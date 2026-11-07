# Labs

[← Course home](../README.md) · **Labs — 10 sessions × 70 points (Lab A 40 + Lab B 30)**

Every class session has a hands-on lab. Labs are where you practice the
session's SQL on real business questions, and they make up **700 of the
course's 1,000 points**.

> **This folder fills up during the term.** Each session's labs appear here
> during class, at the start of the lab block. Before Session 1 it holds only
> this page.

⬇️ **No git?** Each released session is also one ZIP (`session01-labs.zip` …
`session10-labs.zip`, with the course data) —
[links and steps](../course_information/DOWNLOADING_COURSE_FILES.md#-labs--one-zip-per-session).

---

## How a Lab Works

| When | What happens |
|---|---|
| **In class** — last ~40 minutes | The session's labs are published here. You do **Lab A** with the instructor available for questions, and upload it to the Camino assignment **Session N Lab A** **before class ends** |
| **By 11:59 pm Pacific Time the day after class** (Wednesday for a Tuesday session, Friday for a Thursday session) | Finish **Lab B** and upload it to the Camino assignment **Session N Lab B** |
| **After class** | Lab A solutions — and, for most notebook labs, the in-class demo notebook — are added to the same session folder |
| **72 hours after the Lab B deadline** | Lab B solutions are added (after Lab B's late window closes) |

**Two graded labs per session, 6 tasks each:**

| Lab | What it is | Points | Submit |
|---|---|---:|---|
| **A** | The core lab — practice of what was just demonstrated | 40 (Tasks 1–4: 7 each; Tasks 5–6: 6 each) | **In class**, before class ends — no late submission |
| **B** | A step more challenging | 30 (5 per task) | By **11:59 pm Pacific Time** the day after class |

Each task is graded on its own. Students with OAE-approved extra time on
timed tests get that extra time for Lab A —
[details](../course_information/ASSIGNMENTS_and_GRADING.md#2-labs--how-each-session-works).

**What you submit:** your Lab A and your finished Lab B files, renamed
`lastname_firstname_` + the lab's file name — for example
`lopez_maria_week1_lab1a_marimo.py` and `lopez_maria_week1_lab1b_marimo.py`.
Each lab's first lines name its exact files. The full table (notebook,
MySQL, and web-app labs) is in
[How to Submit a Lab](../course_information/ASSIGNMENTS_and_GRADING.md#3-how-to-submit-a-lab).

---

## Lab Formats

| Sessions | Format | What you need |
|---|---|---|
| 1–6, and 9 (Lab A) | [Marimo](https://marimo.io) notebook with DuckDB — each task has an empty SQL cell for your query | The core course software |
| 7, 9 (Lab B), and 10 | Markdown handout — you work in the `mysql` command-line client | MySQL with the course data loaded ([how](../datasets/oltp_database/mysql/README.md)) |
| 8 | A small Python + DuckDB web application you modify (`shop_app_starter.py`), with a Markdown handout | The core course software |

### Running a notebook lab

Open it from **inside its session folder** — the notebooks read the course
data by relative path:

```bash
cd LABS/week1_lab1
marimo edit week1_lab1a_student_marimo.py
```

If you haven't set up the course software yet, see
[`software_installation/`](../software_installation/README.md).

### Getting new labs

- **Downloaded the ZIP?** Download the repository again after each session's
  labs are released.
- **Cloned with Git?** Run `git pull` — see the
  [Git guide](../tutorials/git/README.md).

Either way, **work on your own copy, saved under its submission name** —
for example, save `week1_lab1a_student_marimo.py` as
`lopez_maria_week1_lab1a_marimo.py` (your name in front, `_student` dropped)
**in the same folder** — so an update never overwrites your work, the data
paths still work, and the file is ready to upload.

---

## Lab Schedule

| Week | Session | Folder | Topic |
|:---:|:---:|---|---|
| **1** | 1 | `week1_lab1/` | Retrieving and filtering data |
| | 2 | `week1_lab2/` | Summarizing and modifying data |
| **2** | 3 | `week2_lab1/` | Keys, relationships, and joins |
| | 4 | `week2_lab2/` | Multi-table queries, subqueries, and CTEs |
| **3** | 5 | `week3_lab1/` | Window functions, ranking, and data quality |
| | 6 | `week3_lab2/` | Running totals, trends, and segmentation |
| **4** | 7 | `week4_lab1/` | A client–server database (MySQL) |
| | 8 | `week4_lab2/` | A database-backed web application |
| **5** | 9 | `week5_lab1/` | Transactions and concurrency |
| | 10 | `week5_lab2/` | Performance, security, and governance |

Each session folder also gets its own `README.md` listing its files when it is
released.

---

## Grading and Policies

| Policy | In short |
|---|---|
| **Points** | 10 sessions × 70 points = 700 (Lab A 40 + Lab B 30) |
| **Lowest lab** | Replaced by the average of your other nine |
| **Late work** | Lab A: none — it is submitted in class. Lab B: −3 points for each started 24 hours after the deadline (11:59 pm Pacific Time the day after class; by your last upload); more than 72 hours late scores 0 for Lab B |
| **Absence** | A missed session's labs (A and B) score zero — the in-class lab is part of the session. Documented emergencies and approved absences: contact the instructor |
| **Your own work** | Discussing SQL concepts is fine; sharing queries or notebooks is not |

The full policy is in
[`ASSIGNMENTS_and_GRADING.md`](../course_information/ASSIGNMENTS_and_GRADING.md).

---

[← Course home](../README.md)
