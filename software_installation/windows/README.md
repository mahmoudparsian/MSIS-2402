# MSIS-2402 — Software Installation & Verification (Windows)

[← Course home](../../README.md) · [Software installation](../README.md) · **Windows guide**

**Course:** MSIS-2402 — Database Management Systems - Fundamentals of SQL  
**Quarter:** Winter 2027  
**Author:** Dr. Mahmoud Parsian  

---

## Overview

This folder contains everything you need to set up your Windows computer for MSIS-2402. Follow **Step 0 → Step 1 → Step 2 → Step 3 → Step 4 → Step 5 below, in order** — don't skip ahead or run any install command until its step tells you to. By the end, you will have **Python**, **DuckDB**, **Marimo**, **Pandas**, **Matplotlib**, **sqlglot**, **Java**, **qStudio**, and **MySQL** installed and verified.

**Set aside about an hour and fifteen minutes**, and do this **before the first class**. If you get stuck at any step, stop there and bring it to office hours — don't skip a step and hope the next one works.

## What You'll End Up With

| Software | What It Is | Minimum Version | Installed In | Verified In |
|----------|-----------|-----------------|---------------|-------------|
| [Python](https://www.python.org) | Programming language — the foundation everything else runs on | 3.11+ (3.12+ recommended) | Step 1 | Steps 1, 2, 3 |
| [DuckDB](https://duckdb.org) | In-process SQL database engine — no server to install or configure | 2.0+ | Step 2 | Steps 2, 3 |
| [Marimo](https://marimo.io) | Interactive notebook environment (replaces Jupyter for this course) | any recent | Step 2 | Steps 2, 3 |
| [Pandas](https://pandas.pydata.org) | Data manipulation library — DuckDB query results come back as Pandas tables | any recent | Step 2 | Steps 2, 3 |
| [Matplotlib](https://matplotlib.org) | Charting library — the class notebooks that draw charts import it | any recent | Step 2 | Steps 2, 3 |
| [sqlglot](https://github.com/tobymao/sqlglot) | SQL parser Marimo itself needs to run SQL cells | any recent | Step 2 | Steps 2, 3 |
| [Java](https://adoptium.net) | Required by qStudio — qStudio is written in Java and won't open without it | 21 (recommended) | Step 4 | Step 4 |
| [qStudio](https://www.timestored.com/qstudio/download) | Free SQL editor for writing and exploring queries visually | any recent | Step 4 | Step 4 |
| [MySQL](https://dev.mysql.com/downloads/) | Client–server relational database — the multi-user counterpart to DuckDB's in-process design | 8.0+ | Step 5 | Step 5 |

This table is just a reference — **the actual install commands are in the steps below, not here.**

---

## Step 0 — Get the Course Files

Steps 2 and 3 run files that live in this folder, so you need a copy on your own computer first.

1. Go to **https://github.com/mahmoudparsian/MSIS-2402**
2. Click the green **`< > Code`** button near the top right
3. Click **Download ZIP**. It is a large file — give it a minute to finish
4. Find **`MSIS-2402-main.zip`** in your **Downloads** folder, right-click it, and choose **Extract All...**
5. You now have a folder called **`MSIS-2402-main`**. Inside it, open **`software_installation`**, then open **`windows`** — that is where Steps 2 and 3 live

> **Already know Git?** You can `git clone` the repository instead of downloading the ZIP — then a single `git pull` gets you each week's new material. See [`tutorials/git/README.md`](../../tutorials/git/README.md). If that sentence means nothing to you, ignore it and use the ZIP.

### Now open a Command Prompt *in that folder*

This trick matters: Steps 2 and 3 only work if your Command Prompt is pointed at the `windows` folder. You do **not** need to type any folder names.

1. Open the **`windows`** folder in File Explorer
2. Click once on the **address bar** at the top (the strip showing the folder path)
3. Type `cmd` and press Enter

A Command Prompt opens already pointed at the right folder.

### Check that it worked

Type this and press Enter:

```
dir
```

You should see `step_2_setup_software.py` in the list. If you do, you are in the right place. If you don't, repeat the address-bar step above.

---

## Step 1 — Install and Verify Python

* Python is the only piece of software you download and install manually from a website.
* Steps 2 and 3 are handled by scripts; Step 4 (qStudio) and Step 5 (MySQL) are the other manual installs.

Follow [`step_1_install_python.md`](step_1_install_python.md) — it walks through checking for Python, downloading and installing it, and verifying it works.

Each guide ends with a "Verify Your Installation" 
section — run those commands before moving on. 
Do not continue to Step 2 until Python is confirmed working.

## Step 2 — Install and Verify DuckDB, Marimo, Pandas, Matplotlib, and sqlglot

One script does all of it: installs the five packages, 
then verifies each one, then runs a real DuckDB query 
to prove it all works together.

Use the Command Prompt window you opened in **Step 0** — the one already pointed at the `windows` folder.

> **Did you close that window while installing Python?** Step 1 asks you to close and reopen your Command Prompt, so it is probably gone. Just redo the short trick in **Step 0** — type `cmd` in the address bar — to open a new one in the right place.

Type this and press Enter:

```
python step_2_setup_software.py
```

> **If you see `can't open file ... No such file or directory`,** your Command Prompt is not in the right folder. Go back to Step 0 and redo the address-bar trick.

Watch for **`[+] PASS`** next to DuckDB, Pandas, Marimo, Matplotlib, and sqlglot, and **"ALL CHECKS PASSED"** at the end. If you see any `[X] FAIL`, follow the fix instructions the script prints and run it again — don't move on until every check passes.

## Step 3 — Verify Everything Together in Marimo

Step 2 verifies the packages individually; this step opens a real Marimo notebook to confirm Python, DuckDB, and Marimo all work together the way you'll use them in class.

In the same Command Prompt window, type:

```
marimo edit step_3_verification.py
```

Marimo opens in your web browser. The notebook runs a few checks and then executes a real SQL query. If you can see the query results, **your Python + DuckDB + Marimo setup is complete.**

When you are finished looking at it, go back to the Command Prompt and press `Ctrl + C` to stop Marimo.

> **If you see `marimo: command not found`,** Marimo installed correctly but your computer doesn't know where to find it. Use this instead — it always works:
>
> ```
> python -m marimo edit step_3_verification.py
> ```

## Step 4 — Install Java, Then Install and Verify qStudio

qStudio is a free SQL editor you download separately (it's a desktop application, not a `pip` package), and it requires **Java** to run — qStudio won't open without it.

Follow [`step_4_install_qstudio.md`](step_4_install_qstudio.md) — it walks through installing Java, installing qStudio, connecting it to DuckDB, and running a quick test query to confirm it works.

## Step 5 — Install and Verify MySQL

MySQL is a client–server database — a real database server running in
the background, unlike DuckDB's in-process design. You'll install it,
confirm the server is running, and run a quick test query.

Follow [`step_5_install_mysql.md`](step_5_install_mysql.md) — it walks through downloading the MySQL installer, setting a root password in MySQL Configurator, and verifying it with a test query.

## Step 6 — Before the Final Exam: Install the Lock-Down Browser

**Not needed for the first class.** The Final Exam runs in a required
lock-down browser. Install it and take the practice quiz **at least one
week before the exam**.

Follow [`step_6_install_lockdown_browser.md`](step_6_install_lockdown_browser.md).

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `step_1_install_python.md` | Python installation guide |
| `step_2_setup_software.py` | Script that installs and verifies DuckDB, Marimo, Pandas, Matplotlib, and sqlglot |
| `step_3_verification.py` | Marimo notebook that verifies everything works together |
| `step_4_install_qstudio.md` | Java + qStudio installation, connection, and verification guide |
| `step_5_install_mysql.md` | MySQL installation, server verification, and test-query guide |
| `step_6_install_lockdown_browser.md` | Lock-down browser for the Final Exam — install it and take the practice quiz before the exam (not needed for the first class) |
| `installation_trouble_shooting.md` | Fixes for common Day-1 problems (qStudio needing Java, PATH issues, getting the files) |

---

## Quick Summary

```
Step 0:  Download ZIP from GitHub, unzip, open Command Prompt in software_installation\windows\
Step 1:  Install Python                          (follow the guide, then verify)
Step 2:  python step_2_setup_software.py         (installs + verifies DuckDB, Pandas, Marimo, Matplotlib, sqlglot)
Step 3:  marimo edit step_3_verification.py      (final check — everything together, in Marimo)
Step 4:  Install Java, then qStudio              (Java via winget, qStudio from timestored.com, then verify)
Step 5:  Install MySQL                           (MSI + MySQL Configurator, then verify)

Before the Final Exam:
Step 6:  Install the lock-down browser            (then take the practice quiz)
```

---

## First-Day Success Checklist

By the end of the first class, every student should be able to do
all three of these:

**1. Command Prompt check:**

```
python -c "import duckdb; print(duckdb.__version__)"
```

It must print a version starting with **2.** (for example `2.0.0`). If it
starts with `1.`, run `python -m pip install --upgrade "duckdb>=2.0"`.

**2. Marimo check** — run this in a Marimo cell:

```python
import duckdb
con = duckdb.connect()
con.execute("SELECT 42 AS answer").df()
```

**3. MySQL check:**

```
mysql -u root -p -e "SELECT 42 AS answer;"
```

If all three work, your environment is fully ready for MSIS-2402.

---

## DuckDB CLI (Optional)

The DuckDB command-line interface is optional but useful for quick
SQL testing outside of Python.

Download it from [DuckDB CLI for Windows](https://duckdb.org/install/?platform=windows&environment=cli)
(`duckdb-cli-windows-amd64.tar.gz` for most PCs). **Don't use WinGet yet:**
as of October 2026 `winget install DuckDB.cli` installs 1.5.6, below the
course's 2.0 requirement.

**Verify** — it must print a version starting with `v2.`:

```
duckdb --version
```

Step-by-step install (extracting the `.tar.gz`, PATH), and a first CLI lesson:
[DuckDB from the Command Line (Windows)](../../tutorials/duckdb_from_command_line/duckdb_from_command_line_on_windows.md).

---

## Getting Help

If you run into problems:

1. Check the **Troubleshooting** section in the relevant guide, or the
   consolidated [`installation_trouble_shooting.md`](installation_trouble_shooting.md)
   for common Day-1 issues (qStudio needing Java, PATH problems,
   getting the setup files onto your computer)
2. Take a **screenshot** of the error message
3. Note your **Windows version** and **Python version**
4. Bring these to **office hours** (see
   [`course_information/QUESTIONS_and_OFFICE_HOURS.md`](../../course_information/QUESTIONS_and_OFFICE_HOURS.md))
   or post on **Camino Discussions**

Remember: you must also bring a fully charged laptop to every class
session (see
[`course_information/LAPTOP.md`](../../course_information/LAPTOP.md)).

---

*MSIS-2402 — Database Management Systems - Fundamentals of SQL — Winter 2027*
