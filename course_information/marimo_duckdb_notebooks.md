# Marimo Notebooks

[← Course home](../README.md) · **Course information**

Every notebook in this course is a [Marimo](https://marimo.io) notebook — a
plain Python file (`*_marimo.py`) with reactive cells and native SQL cells
that run against DuckDB. You'll find them in each week's folders, in
[`LABS/`](../LABS/), and in [`data_stories/`](../data_stories/).

---

## Requirements

Install:

```bash
pip install duckdb pandas matplotlib
pip install "marimo[sql]"
```

For the complete, step-by-step setup on your Mac or Windows computer, see
[`software_installation/`](../software_installation/README.md).

## Keep the Folder Structure

Notebooks read their data by **relative path** — from a `data/` folder next to
them, or from the shared [`datasets/`](../datasets/) folder. Keep the
repository's folders exactly as downloaded, and don't move a notebook away
from its folder.

## Run

Open a notebook from **inside its own folder**:

```bash
cd week1_db_concepts_sql_fundamentals/part1_single_table_sql
marimo edit notebook_3_duckdb_marimo.py
```

Or start Marimo with no file name to browse and open notebooks from the
current folder:

```bash
marimo edit
```

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
