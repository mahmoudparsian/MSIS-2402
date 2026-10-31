# Required Software

[← Course home](../README.md) · **Course information**

This course requires **nine tools**, plus a lock-down browser for the Final
Exam. Each is described below.

> **Installing?** Follow the step-by-step guide for your computer in
> [`software_installation/`](../software_installation/README.md) — it covers
> every tool on this page, with troubleshooting. This page explains *what*
> each tool is and *why* the course uses it.

## At a Glance

| # | Tool | What it is | Install |
|:---:|---|---|---|
| 1 | [Python](#1-python) | The language the notebooks run on | [python.org](https://www.python.org/downloads/) — 3.11+ |
| 2 | [DuckDB](#2-duckdb) | The course's main SQL engine (in-process) | `pip install "duckdb>=2.0"` |
| 3 | [MySQL](#3-mysql) | A client–server database (Weeks 4–5) | [dev.mysql.com](https://dev.mysql.com/downloads/) |
| 4 | [Marimo](#4-marimo-notebook) | Reactive Python notebooks with SQL cells | `pip install "marimo[sql]"` |
| 5 | [Pandas](#5-pandas) | DataFrames for query results | `pip install pandas` |
| 6 | [Matplotlib](#6-matplotlib) | Charts in the notebooks | `pip install matplotlib` |
| 7 | [sqlglot](#7-sqlglot) | SQL parser behind Marimo's SQL cells | `pip install sqlglot` |
| 8 | [Java](#8-java) | Runtime needed by qStudio | [adoptium.net](https://adoptium.net) — version 21 |
| 9 | [qStudio](#9-qstudio) | Desktop SQL editor | [timestored.com](https://www.timestored.com/qstudio/download) |
| 10 | [Lock-down browser](#10-lock-down-browser-final-exam-only) | Required for the Final Exam only | See below |

---

## 1. Python

🔗 [python.org](https://www.python.org)

Python is a programming language that lets you work quickly and integrate
systems more effectively. We use Python as the foundation for running
notebooks, loading data, and executing SQL.

**Version:** 3.11 or higher (we recommend 3.12+).

---

## 2. DuckDB

🔗 [duckdb.org](https://duckdb.org)

DuckDB is an open-source, in-process SQL database engine designed for fast
analytical query workloads. It runs entirely inside your Python process — no
server to install or configure.

**Version:** 2.0 or newer (required — every course notebook is tested on
DuckDB 2.0).

```bash
pip install "duckdb>=2.0"
```

Already have DuckDB 1.x from another course? Upgrade it:
`pip install --upgrade "duckdb>=2.0"`. Two things to know about 2.0:

- A `.duckdb` **file** written by DuckDB 2.0 cannot be opened by DuckDB 1.x
  (including an older qStudio). Older files still open in 2.0.
- In Python, use `con.execute(sql).fetchall()` (or `.df()`) to read results.
  `con.sql(sql).fetchone()` no longer exists in 2.0.

---

## 3. MySQL

🔗 [mysql.com](https://www.mysql.com) · download the free **MySQL Community
Server** from [dev.mysql.com](https://dev.mysql.com/downloads/)

- A client–server, multi-user relational database management system.
- Designed for transactional workloads, with concurrency, locking, isolation
  levels, and access control.
- Supports server-side features such as stored procedures, triggers,
  replication, and administration.

Step-by-step install: Step 5 of the
[installation guide](../software_installation/README.md).

### DuckDB vs. MySQL

Why the course uses both:

| Topic | DuckDB | MySQL | Importance |
|---|---|---|---|
| SQL queries, joins, aggregation, subqueries, CTEs, and window functions | Strong support | Strong support | **Essential** |
| Tables, keys, constraints, and normalization | Supported, with some limitations | Supported | **Essential** |
| Basic ACID transactions | Supported with snapshot isolation | Supported | **Essential** |
| Concurrent client sessions and locking | Limited; primarily designed for concurrency within one process | Multi-user concurrency with row locking, blocking, and deadlocks | **High** |
| Transaction isolation levels and anomalies | Uses a fixed snapshot-isolation-oriented model | Supports `READ UNCOMMITTED`, `READ COMMITTED`, `REPEATABLE READ`, and `SERIALIZABLE` | **High** |
| Client–server architecture | Embedded and in-process by default | Networked database server with multiple clients | **High** |
| Users, roles, and privileges | No native server-style account-management system | Supports `CREATE USER`, roles, `GRANT`, and `REVOKE` | **Medium** |
| Triggers | No general SQL trigger support | Supports `BEFORE` and `AFTER` row triggers | **Medium** |
| Server administration | Minimal, because DuckDB is embedded | Includes connection management, logging, configuration, backup, and monitoring | **Medium** |
| Stored procedures | No MySQL-style stored-procedure facility | Supports procedures, variables, cursors, handlers, and `CALL` | **Low** |
| Scheduled database events | No comparable built-in event scheduler | Includes the MySQL Event Scheduler | **Low** |
| Multiple storage engines | No comparable feature | Supports engines such as InnoDB, MyISAM, and MEMORY | **Low** |
| Replication and binary logging | No traditional built-in database-server replication | Supports binary logging and source/replica replication | **Low** for an introductory course |

---

## 4. Marimo Notebook

🔗 [marimo.io](https://marimo.io)

Marimo is an interactive notebook environment for Python. It replaces Jupyter
in this course and provides a reactive, reproducible workflow with built-in
SQL support.

**Version:** the latest.

```bash
pip install "marimo[sql]"
```

| To… | Run |
|---|---|
| Open a notebook | `marimo edit <notebook>.py` |
| Check that a notebook runs correctly | `python3 <notebook>.py` |

---

## 5. Pandas

🔗 [pandas.pydata.org](https://pandas.pydata.org)

Pandas is a data manipulation library for Python. DuckDB query results are
returned as Pandas DataFrames, which Marimo renders as clean tables.

**Version:** the latest.

```bash
pip install pandas
```

---

## 6. Matplotlib

🔗 [matplotlib.org](https://matplotlib.org)

Matplotlib is a charting library for Python. Several of this course's
notebooks import it directly to draw charts — install it even if you don't
plan to write your own plotting code.

**Version:** the latest.

```bash
pip install matplotlib
```

---

## 7. sqlglot

🔗 [github.com/tobymao/sqlglot](https://github.com/tobymao/sqlglot)

sqlglot is a SQL parser that Marimo uses internally to power its native SQL
cells. It's not a dependency of `duckdb`/`pandas`/`marimo`'s core install, so
it must be installed separately — without it, Marimo shows an error the
moment you try to run a SQL cell.

**Version:** the latest.

```bash
pip install sqlglot
```

---

## 8. Java

🔗 [adoptium.net](https://adoptium.net)

Java is required by qStudio — qStudio is written in Java and will not open
without a working Java runtime installed. This is a desktop-application
dependency, not a Python package.

**Version:** 21 (recommended). See
[`software_installation/`](../software_installation/README.md) for
OS-specific instructions (Homebrew + Temurin on Mac, winget/Adoptium on
Windows).

---

## 9. qStudio

🔗 [timestored.com/qstudio](https://www.timestored.com/qstudio/download)

qStudio is a free, open-source SQL editor for writing and testing queries.
You will use it alongside Marimo to practice SQL and explore databases
visually.

**Version:** the latest. Download it from the link above — qStudio is a
desktop application, not a pip package.

---

## 10. Lock-down browser (Final Exam only)

**Respondus LockDown Browser** — [SCU LockDown Browser download](https://download.respondus.com/lockdown/download.php?ID=597745928)

The Final Exam is taken on your own laptop in a **required lock-down
browser**, which blocks other applications and websites during the exam. You
**don't** need it for the first class: install it and take the **practice
quiz** at least **one week before the exam**. Step-by-step instructions are
in Step 6 of the [installation guide](../software_installation/README.md).

---

## Quick Install Summary

| Step | What to do |
|:---:|---|
| **1** | Install Python from [python.org](https://www.python.org/downloads/) |
| **2** | Install the Python packages (command below) |
| **3** | Install Java, then download and install qStudio from [timestored.com](https://www.timestored.com/qstudio/download) |
| **4** | Install MySQL Community Server from [dev.mysql.com](https://dev.mysql.com/downloads/) |

```bash
pip install "duckdb>=2.0" "marimo[sql]" pandas matplotlib sqlglot
```

This summary is only a quick reference. For detailed, OS-specific,
step-by-step guides — including troubleshooting — see
[`software_installation/`](../software_installation/README.md), which picks
the right walkthrough for your Mac or Windows computer.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
