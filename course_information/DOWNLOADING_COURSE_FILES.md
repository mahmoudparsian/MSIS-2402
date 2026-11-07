# Downloading Course Files

[← Course home](../README.md) · **Course information**

## 📦 One ZIP File per Week and per Session's Labs — No Git Needed

You do **not** need git. Each week of the course, and each session's labs,
is ready as **one ZIP file**. Click a link, unzip the file, and you have
everything for that week or that lab — **including the course data**
(`datasets/oltp_database/`), so the notebooks run without anything else.

## ⬇️ Weeks — Slides, Notebooks, Class Discussions

| Week | Module | Download |
|:---:|---|---|
| 1 | Database Concepts and SQL Fundamentals | [`week1_db_concepts_sql_fundamentals.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week1_db_concepts_sql_fundamentals.zip) |
| 2 | Working with Multiple Tables and Complex Queries | [`week2_multi_table_complex_queries.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week2_multi_table_complex_queries.zip) |
| 3 | SQL for Data Analytics | [`week3_sql_for_analytics.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week3_sql_for_analytics.zip) |
| 4 | Introduction to Web Database Applications | [`week4_web_db_applications.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week4_web_db_applications.zip) |
| 5 | Modern Data Systems and Database Management | [`week5_modern_data_systems.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/week5_modern_data_systems.zip) |

## ⬇️ Labs — One ZIP per Session

A session's lab ZIP exists **from the moment that session's labs are
released** (in class, at the start of the lab block). Until then its link
says "Not Found" — that is expected. When solutions are added after the
deadlines, the same link gives the updated folder (wait about a minute
after the release, then download).

| Session | Download | Session | Download |
|:---:|---|:---:|---|
| 1 | [`session01-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session01-labs.zip) | 6 | [`session06-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session06-labs.zip) |
| 2 | [`session02-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session02-labs.zip) | 7 | [`session07-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session07-labs.zip) |
| 3 | [`session03-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session03-labs.zip) | 8 | [`session08-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session08-labs.zip) |
| 4 | [`session04-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session04-labs.zip) | 9 | [`session09-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session09-labs.zip) |
| 5 | [`session05-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session05-labs.zip) | 10 | [`session10-labs.zip`](https://github.com/mahmoudparsian/MSIS-2402/releases/download/weekly-zips/session10-labs.zip) |

Session *N*'s labs are the `LABS/` folder `weekW_labL` with
N = 2 × (W − 1) + L: Session 1 = `week1_lab1`, Session 2 = `week1_lab2`,
Session 3 = `week2_lab1`, … Session 10 = `week5_lab2`.

## 🗂️ What Is Inside a ZIP File

Each ZIP file holds **one folder**, laid out exactly like the course
repository, so every notebook finds its data. For example:

```
week1_db_concepts_sql_fundamentals.zip
└── MSIS-2402-week1_db_concepts_sql_fundamentals/
    ├── week1_db_concepts_sql_fundamentals/
    │   ├── part1_single_table_sql/      ← Session 1
    │   └── part2_aggregation_kpis/      ← Session 2
    └── datasets/oltp_database/          ← the course data

session01-labs.zip
└── MSIS-2402-session01-labs/
    ├── LABS/week1_lab1/                 ← Lab A, Lab B (and solutions, once added)
    └── datasets/oltp_database/
```

Keep the folders exactly as they come out of the ZIP — don't move a
notebook out of its folder, or it can't find `datasets/`.

## 🍎 On a MacBook

Example: Session 1's lab.

1. Click the link. The file goes to your **Downloads** folder.
2. Double-click the ZIP file. macOS creates the folder
   `MSIS-2402-session01-labs` next to it.
3. Open **Terminal** and go into the lab's folder:

   ```bash
   cd ~/Downloads/MSIS-2402-session01-labs/LABS/week1_lab1
   ```

4. Open the notebook with Marimo:

   ```bash
   marimo edit week1_lab1a_student_marimo.py
   ```

For a week ZIP, the folder to `cd` into is the part folder that holds the
notebook — for Session 1:
`cd ~/Downloads/MSIS-2402-week1_db_concepts_sql_fundamentals/week1_db_concepts_sql_fundamentals/part1_single_table_sql`.
Each week's `README.md` (inside the ZIP) lists the folder and command for
every notebook.

## 🪟 On Windows

Example: Session 1's lab.

1. Click the link. The file goes to your **Downloads** folder.
2. Right-click the ZIP file, choose **Extract All…**, then click **Extract**.

   > ⚠️ Do **not** just double-click the ZIP and open the notebooks from
   > there. Windows only shows a preview, and the notebooks cannot find
   > their data. Always **Extract All** first.

3. Windows puts the files in a folder named after the ZIP file, so the
   path has one extra level. This is normal:

   ```
   Downloads\session01-labs\MSIS-2402-session01-labs\LABS\week1_lab1
   ```

4. Open **PowerShell** and go into that folder:

   ```powershell
   cd $HOME\Downloads\session01-labs\MSIS-2402-session01-labs\LABS\week1_lab1
   ```

5. Open the notebook with Marimo:

   ```powershell
   marimo edit week1_lab1a_student_marimo.py
   ```

If `marimo` is "not recognized", see the installation guide in
[`software_installation/`](../software_installation/README.md).

## 🔄 Getting Updates

The ZIP files are **rebuilt automatically** about one minute after the
course files change. The link always gives the newest version.

If you download a ZIP again, **first save a copy of any file you changed**
(for example your lab notebook, already renamed
`lastname_firstname_…`) — on a Mac the new download unzips into a new
folder (e.g. `MSIS-2402-session01-labs 2`); on Windows **Extract All** may
ask to replace files.

When the files were last updated: the
[Releases page](https://github.com/mahmoudparsian/MSIS-2402/releases/tag/weekly-zips),
line **"Last updated"**.

## ❓ Common Questions

**What are "Source code (zip)" and "Source code (tar.gz)" on the
Releases page?** GitHub adds these two files to every release. They hold
the **whole** course repository. Ignore them and download a `week…` or
`sessionNN-labs` ZIP instead.

**Why is every ZIP about 14–18 MB?** Each one includes the course data
(`datasets/oltp_database/`, 100,000 orders and 300,000 order items), so
it works on its own.

**Can I download `tutorials/`, `data_stories/`, or everything at once?**
Not as these ZIPs. For the whole course, use the green **Code** button
on the [repository page](https://github.com/mahmoudparsian/MSIS-2402) →
**Download ZIP**.

**I already use git. Do I need these ZIPs?** No — `git pull` gives you the
same files.

**A link says "Not Found."** For a lab, the session's labs may not be
released yet. Otherwise, wait a minute and try again; if it still fails,
tell the instructor ([`QUESTIONS_and_OFFICE_HOURS.md`](QUESTIONS_and_OFFICE_HOURS.md)).

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
