---

marp: true

title: Installing DuckDB (Mac)

theme: default

paginate: true

---

# slide-1: MSIS-2402 <br> Installing DuckDB (Mac)

* Database Management Systems – Fundamentals of SQL

* Instructor: Dr. Mahmoud Parsian

---

# slide-2: DuckDB Runs Inside Python

DuckDB runs inside Python and is installed using **pip** — no server,
no separate download.

Recommended command:

```bash
python3 -m pip install "duckdb>=2.0"
```

This method works reliably across Mac, Windows, and Linux.

---

# slide-3: Step 1 — Install Python (if needed)

Download Python:

https://www.python.org/downloads/

Or install using Homebrew:

```bash
brew install python
```

Version needed: **3.11 or higher** (we recommend 3.12+).

---

# slide-4: Step 2 — Verify Python Installation

Open **Terminal** and run:

```bash
python3 --version
```

Example output:

```
Python 3.12.x
```

If you see a version number, Python is installed correctly.

---

# slide-5: Step 3 — Install DuckDB

Run in Terminal:

```bash
python3 -m pip install "duckdb>=2.0"
```

Why this command?

- Works even if `pip3` is not on PATH
- Works across Mac, Windows, Linux
- Avoids common environment issues

---

# slide-6: If You See "externally-managed-environment"

Homebrew's own Python blocks a plain `pip install` to protect itself
— this is normal, not a broken computer. Add one flag:

```bash
python3 -m pip install --break-system-packages "duckdb>=2.0"
```

(`software_installation/`'s setup script handles this automatically
— see slide 9.)

---

# slide-7: Step 4 — Verify Installation

Start Python:

```bash
python3
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

# slide-8: Step 5 — Test DuckDB

Example Python test:

```python
import duckdb

con = duckdb.connect()

con.execute("SELECT 1+1").fetchall()
```

Output:

```
[(2,)]
```

DuckDB is now ready.

---

# slide-9: This Is Just One Piece

DuckDB is 1 of **9 required tools** for this course — Python, DuckDB,
MySQL, Marimo, Pandas, Matplotlib, sqlglot, Java, and qStudio.

For the full, OS-specific, step-by-step install of everything
(including troubleshooting), see:

**[`software_installation/macbook/README.md`](../software_installation/macbook/README.md)**

---

# slide-10: Where We Will Use DuckDB

In this course DuckDB will be used for:

- running SQL queries
- exploring CSV datasets
- analytics in Marimo notebooks
- connecting SQL with Python visualization
