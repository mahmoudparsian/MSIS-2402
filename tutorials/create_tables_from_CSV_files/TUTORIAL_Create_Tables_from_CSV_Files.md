# Loading CSV and Parquet Files into DuckDB

[← Tutorials](../README.md) · **Creating tables from CSV files** · [Notebook version](TUTORIAL_Create_Tables_from_CSV_Files_marimo.py)

How to get file data into DuckDB — from automatic detection to full control
of the column types — with CSV files (with and without a header row) and a
Parquet file. DuckDB can query a file directly, often faster than other
databases can import it.

This page is the **reading version** of the notebook
[`TUTORIAL_Create_Tables_from_CSV_Files_marimo.py`](TUTORIAL_Create_Tables_from_CSV_Files_marimo.py)
(same examples, written as plain SQL).

---

## 1. Setup

The three files are in this tutorial's [`data/`](data/) folder:

| File | Contents |
|---|---|
| [`data/users_header.csv`](data/users_header.csv) | 3 users, **with** a header row: `user_id,username,join_date` |
| [`data/logs_no_header.csv`](data/logs_no_header.csv) | 2 log events, **without** a header row |
| `data/users4.parquet` | 4 users (`name`, `city`, `age`) in Parquet format |

Start DuckDB **from this folder** so the `data/...` paths are found. From the
course repository folder (`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/create_tables_from_CSV_files
duckdb
```

(or open the notebook version, or create a Marimo notebook in this folder and
run the SQL in SQL cells).

---

## 2. Reading a CSV File: `read_csv`

DuckDB **sniffs** a CSV file: it detects the header, the delimiter, and each
column's type automatically.

### A. Query the file directly — no table needed

Good for a quick look:

```sql
SELECT *
FROM read_csv('data/users_header.csv');
```

Result:

| user_id | username | join_date |
|---:|---|---|
| 100 | alice | 2023-01-15 |
| 200 | bob | 2023-02-20 |
| 300 | charlie | 2023-03-05 |

*3 rows*

### B. Create a table from it

Wrap the same `SELECT` in `CREATE TABLE ... AS`:

```sql
CREATE OR REPLACE TABLE users AS
SELECT * FROM read_csv('data/users_header.csv');
```

`DESCRIBE` shows the column types the sniffer chose:

```sql
SELECT column_name, column_type
FROM (DESCRIBE users);
```

Result:

| column_name | column_type |
|---|---|
| user_id | BIGINT |
| username | VARCHAR |
| join_date | DATE |

*3 rows*

`join_date` became a `DATE` because every value looks like `YYYY-MM-DD`.

---

## 3. A File Without a Header Row

[`data/logs_no_header.csv`](data/logs_no_header.csv) starts directly with data:

```
101,2023-01-15 10:00:00,LOGIN
102,2023-01-15 10:05:00,LOGOUT
```

Tell DuckDB there is no header (`header = false`) and give the column names
(`names = [...]`):

```sql
CREATE OR REPLACE TABLE access_logs AS
SELECT *
FROM read_csv('data/logs_no_header.csv',
              header = false,
              names  = ['event_id', 'event_timestamp', 'event_type']);

SELECT * FROM access_logs;
```

Result:

| event_id | event_timestamp | event_type |
|---:|---|---|
| 101 | 2023-01-15 10:00:00 | LOGIN |
| 102 | 2023-01-15 10:05:00 | LOGOUT |

*2 rows*

The opposite mistake — `header = false` on a file that **has** a header —
turns the header into a data row, and every column becomes text:

```sql
SELECT *
FROM read_csv('data/users_header.csv', header = false);
```

Result:

| column0 | column1 | column2 |
|---|---|---|
| user_id | username | join_date |
| 100 | alice | 2023-01-15 |
| 200 | bob | 2023-02-20 |
| 300 | charlie | 2023-03-05 |

*4 rows*

---

## 4. Choosing the Column Types Yourself

Sniffing can go wrong. DuckDB guesses each column's type from a **sample of
rows — 20,480 by default** (the `sample_size` option). If a value that doesn't
fit the guess appears only later — say the code `ABC` in row 30,000 of a column
that was all numbers until then — reading the file fails with a
`Conversion Error`. To be safe, give the types yourself with `columns = {...}`,
or let the sniffer read the whole file with `sample_size = -1`.

```sql
CREATE OR REPLACE TABLE strict_users AS
SELECT *
FROM read_csv('data/users_header.csv',
              columns = {'user_id':   'INTEGER',
                         'username':  'VARCHAR',
                         'join_date': 'DATE'});
```

```sql
SELECT column_name, column_type
FROM (DESCRIBE strict_users);
```

Result:

| column_name | column_type |
|---|---|
| user_id | INTEGER |
| username | VARCHAR |
| join_date | DATE |

*3 rows*

`user_id` is now `INTEGER` (the sniffer had chosen `BIGINT`).

---

## 5. The Shortcut: Just Name the File

When you don't need any options, put the file name in quotes where a table
name would go — DuckDB picks the reader from the file extension:

```sql
CREATE OR REPLACE TABLE auto_users AS
SELECT * FROM 'data/users_header.csv';

SELECT * FROM auto_users;
```

Result:

| user_id | username | join_date |
|---:|---|---|
| 100 | alice | 2023-01-15 |
| 200 | bob | 2023-02-20 |
| 300 | charlie | 2023-03-05 |

*3 rows*

`read_csv_auto('...')` — used throughout the course — does the same
(`read_csv` with automatic detection).

---

## 6. Parquet Files

**Parquet** is a column-oriented, compressed file format built for analytics.
The file stores its own column names and types, so there is nothing to sniff,
and DuckDB reads only the columns a query needs.

Query it directly:

```sql
SELECT *
FROM 'data/users4.parquet';
```

Result:

| name | city | age |
|---|---|---:|
| alex | Sunnyvale | 20 |
| jane | Cupertino | 30 |
| max | Sunnyvale | 27 |
| terry | Stanford | 60 |

*4 rows*

Filter it like a table:

```sql
SELECT *
FROM 'data/users4.parquet'
WHERE age > 27;
```

Result:

| name | city | age |
|---|---|---:|
| jane | Cupertino | 30 |
| terry | Stanford | 60 |

*2 rows*

Copy it into a table (the column types come from the file):

```sql
CREATE OR REPLACE TABLE users4 AS
SELECT * FROM 'data/users4.parquet';
```

Or create a **view** — a saved query, not a copy: the data stays in the file and
is read each time you query the view:

```sql
CREATE OR REPLACE VIEW users4_view AS
SELECT * FROM 'data/users4.parquet';
```

### Many files at once (globbing)

A `*` in the file name reads every matching file as one table — as long as the
files have the **same columns**. These are patterns to adapt; this folder holds
only one Parquet file:

```sql
-- every Parquet file in a folder named 'uploads'
CREATE TABLE all_data AS SELECT * FROM 'uploads/*.parquet';

-- every Parquet file in a folder tree split by, e.g., year=2024/month=01/
SELECT * FROM read_parquet('data/**/*.parquet', hive_partitioning = true);
```

### Files on the web

With the `httpfs` extension, DuckDB reads a Parquet file from a URL or an S3
bucket without downloading the whole file first (the URL below is a
placeholder):

```sql
INSTALL httpfs;
LOAD httpfs;

SELECT * FROM 'https://data.example.com/transactions.parquet' LIMIT 10;
```

---

## 7. CSV vs. Parquet

| | CSV | Parquet |
|---|---|---|
| **Column types** | guessed by sniffing, or given by you | stored in the file |
| **Size** | larger (plain text) | smaller (compressed) |
| **Reading** | every line must be parsed | only the needed columns are read |

## Summary

- `read_csv('file.csv')` reads a CSV file; `read_csv_auto(...)` and plain
  `'file.csv'` do the same with automatic detection.
- **Sniffing** detects the delimiter, the header, and the types — from the
  first 20,480 rows by default.
- `header = false` plus `names = [...]` for files without a header row;
  `columns = {...}` to fix the types yourself.
- `'file.parquet'` reads Parquet; its types come from the file.

## Exercises

1. **Header mix-up:** read `data/users_header.csv` with `header = false`
   (section 3) and look at the first row and the column types. Why are all the
   columns text?
2. **Globbing:** create `data/users_more.csv` with the **same three columns** as
   `users_header.csv` — for example the rows `400,dana,2023-04-10` and
   `500,erin,2023-05-12` — then run
   `SELECT * FROM read_csv('data/users*.csv') ORDER BY user_id;`.
   **Self-check:** 5 rows. (`read_csv('data/*.csv')` fails with
   `Schema mismatch between globbed files` — `logs_no_header.csv` has
   different columns.)

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
