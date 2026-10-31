---

marp: true

title: Installing DuckDB (Windows)

theme: default

paginate: true

---

# slide-1: MSIS-2402 <br> Installing DuckDB (Windows)

* Database Management Systems – Fundamentals of SQL

* Instructor: Dr. Mahmoud Parsian

---

# slide-2: DuckDB Runs Inside Python

DuckDB runs inside Python and is installed using **pip** — no server,
no separate download.

Recommended command:

```bash
python -m pip install "duckdb>=2.0"
```

This avoids many Windows installation issues.

---

# slide-3: Step 1 — Install Python

Download Python:

https://www.python.org/downloads/

During installation make sure to check:

✔ **Add python.exe to PATH**

This step is very important — it's the #1 cause of installation
problems if skipped.

Version needed: **3.11 or higher** (we recommend 3.12+).

---

# slide-4: Step 2 — Verify Python Installation

Open **PowerShell** or **Command Prompt**.

Run:

```bash
python --version
```

Example:

```
Python 3.12.x
```

If you see a version number, Python is installed.

---

# slide-5: Step 3 — Install DuckDB

Run:

```bash
python -m pip install "duckdb>=2.0"
```

Why use this command?

- works even if `pip` is not recognized
- avoids PATH issues
- works on Mac, Windows, and Linux

---

# slide-6: Step 4 — Verify Installation

Start Python:

```bash
python
```

Then run:

```python
import duckdb
print(duckdb.__version__)
```

Example output:

```
2.0.0
```

Any version that starts with **2.** is fine. If it starts with **1.**, upgrade
(the command above with `--upgrade` added).

---

# slide-7: Step 5 — Test DuckDB

Run inside Python:

```python
import duckdb

con = duckdb.connect()

con.execute("SELECT 1+1").fetchall()
```

Output:

```
[(2,)]
```

DuckDB is working.

---

# slide-8: Troubleshooting

If you see:

```
pip : command not recognized
```

Use:

```bash
python -m pip install "duckdb>=2.0"
```

If Python is not recognized:

- reinstall Python
- check **Add python.exe to PATH**

---

# slide-9: This Is Just One Piece

DuckDB is 1 of **9 required tools** for this course — Python, DuckDB,
MySQL, Marimo, Pandas, Matplotlib, sqlglot, Java, and qStudio.

For the full, OS-specific, step-by-step install of everything
(including troubleshooting), see:

**[`software_installation/windows/README.md`](../software_installation/windows/README.md)**
