# Tutorials

[← Course home](../README.md) · **Tutorials**

Standalone, self-paced guides for practicing on your own — each one focuses on a
single technique and can be read in any order. Use them to review a topic from
class, go deeper, or catch up after a missed session.

There are two kinds:

- **Notebook tutorials** (`*.py`) — Marimo notebooks you run and change. Open them
  from **inside their own folder**, since they read files next to them:

  ```bash
  cd tutorials/group_by
  marimo edit Group_By_Notebook.py
  ```

- **Reading tutorials** (`*.md`) — read them on GitHub; copy the SQL into a
  notebook or the DuckDB command line to try it.

---

## By Topic

### Getting started

| Tutorial | Type | What you'll learn |
|---|:---:|---|
| [Getting the course files with Git](git/README.md) | Reading | Clone the course repository once, then pull each week's new material — optional; downloading the ZIP works too |
| [DuckDB from the command line](duckdb_from_command_line/README.md) | Reading | Run DuckDB in a terminal, query a CSV file, and save your work — no Python needed. Separate [macOS](duckdb_from_command_line/duckdb_from_command_line_on_macbook.md) and [Windows](duckdb_from_command_line/duckdb_from_command_line_on_windows.md) guides |
| [Creating tables from CSV files](create_tables_from_CSV_files/TUTORIAL_Create_Tables_from_CSV_Files_marimo.py) | Notebook | Load CSV files with and without headers, and Parquet files, into DuckDB tables — from auto-detection to full schema control. Also as [reading](create_tables_from_CSV_files/TUTORIAL_Create_Tables_from_CSV_Files.md) |

### Querying and summarizing

| Tutorial | Type | What you'll learn |
|---|:---:|---|
| [GROUP BY tutorial 101](group_by/Group_By_Notebook.py) | Notebook | Grouping and aggregate functions, step by step, with charts. Also as [reading](group_by/Group_By_Tutorial.md) |
| [GROUP BY with office supplies](group_by/office_supplies_group_by_tutorial.md) | Reading | The same ideas on a small sales dataset ([`office_supplies.csv`](group_by/office_supplies.csv)) |
| [SQL joins](joins/joins_tutorial.md) | Reading | `INNER`, `LEFT`, and `RIGHT` joins on two small tables ([`employees.csv`](joins/employees.csv), [`departments.csv`](joins/departments.csv)) |
| [Window functions and ranking](window_functions/ranking_tutorial.md) | Reading | `RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`, and `PARTITION BY` |
| [`ROW_NUMBER()` example](window_functions/row_number_example.md) | Reading | A short worked example of numbering rows within groups |

### Data quality and design

| Tutorial | Type | What you'll learn |
|---|:---:|---|
| [Deduplicating data](deduplication/deduplication_tutorial.md) | Reading | Find and remove duplicate rows in DuckDB |
| [Database normalization](normalization/normalization_tutorial.md) | Reading | 1NF through BCNF — why and how to split a table |

### Beyond plain SQL

| Tutorial | Type | What you'll learn |
|---|:---:|---|
| [DuckDB user-defined functions](duckdb_user_defined_functions/duckdb_user_defined_functions_tutorial_marimo.py) | Notebook | Write your own functions — SQL macros and Python functions called from SQL |
| [Transactions in action](transactions_in_action/transactions_in_action_marimo.py) | Notebook | `BEGIN`, `COMMIT`, and `ROLLBACK` through a banking example: why a transfer must be all-or-nothing |

---

## By Week

Each week's README also points to these under **Further Practice**.

| Week | Tutorials |
|---|---|
| **1** — Database Concepts and SQL Fundamentals | Creating tables from CSV files · DuckDB from the command line · `GROUP BY` |
| **2** — Multiple Tables and Complex Queries | Joins · Normalization |
| **3** — SQL for Data Analytics | Window functions · Deduplication · User-defined functions |
| **5** — Modern Data Systems and Database Management | Transactions in action |
| **Any time** | Getting the course files with Git |

---

*MSIS-2402 — Database Management Systems - Fundamentals of SQL — Winter 2027*
