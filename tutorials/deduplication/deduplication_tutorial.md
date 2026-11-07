# Deduplicating Data in DuckDB

[← Tutorials](../README.md) · **Deduplication**

Two ways to handle duplicate rows:

1. removing **exact** duplicates — every column is the same;
2. removing **business** duplicates — the identifying columns match (here: the
   same employee), even if other columns differ.

---

## 1. The Data

[`raw_data.csv`](raw_data.csv), in this folder — imagine a system log where
some entries were saved twice and some were updated:

```
department,employee,salary
Sales,Alice,5000
Sales,Alice,5000
Sales,Alice,8000
HR,Bob,6000
HR,Bob,6000
IT,Charlie,7000
IT,Charlie,7000
IT,Eve,4000
IT,Eve,4000
HR,David,4500
```

10 rows: 5 employees, 4 of them saved twice, and Alice also has a second salary.

---

## 2. Setup

Start DuckDB **from this folder**. From the course repository folder
(`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/deduplication
duckdb
```

(or create a Marimo notebook in this folder and run the SQL in SQL cells). Then:

```sql
CREATE OR REPLACE TABLE staff AS
SELECT * FROM read_csv_auto('raw_data.csv');

SELECT COUNT(*) AS n_rows FROM staff;
```

Result:

| n_rows |
|---:|
| 10 |

*1 row*

---

## 3. Example 1: Remove Exact Duplicates

Use this when two rows are identical twins: if every column matches, keep one.

**The logic:** number the rows within each group of identical rows
(`PARTITION BY` **every** column) and keep row number 1.

```sql
SELECT department,
       employee,
       salary
FROM staff
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY department, employee, salary   -- every column
) = 1
ORDER BY employee, salary;
```

Result:

| department | employee | salary |
|---|---|---:|
| Sales | Alice | 5000 |
| Sales | Alice | 8000 |
| HR | Bob | 6000 |
| IT | Charlie | 7000 |
| HR | David | 4500 |
| IT | Eve | 4000 |

*6 rows*

Alice still appears **twice**: her 5000 and 8000 rows are different records
(the salary differs). Every other employee keeps one row.

For exact duplicates, `SELECT DISTINCT department, employee, salary FROM staff`
gives the same 6 rows. The `ROW_NUMBER()` form is shown because the next
example needs it.

---

## 4. Example 2: One Row per Employee (Keep the Highest Salary)

Use this when one person has several records and you want only the latest —
or, here, the highest-paid — one.

**The logic:** `PARTITION BY` the identifying column (`employee`),
`ORDER BY salary DESC`, keep row number 1.

```sql
SELECT department,
       employee,
       salary
FROM staff
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY employee
    ORDER BY salary DESC
) = 1
ORDER BY employee;
```

Result:

| department | employee | salary |
|---|---|---:|
| Sales | Alice | 8000 |
| HR | Bob | 6000 |
| IT | Charlie | 7000 |
| HR | David | 4500 |
| IT | Eve | 4000 |

*5 rows*

Alice is now one row — her highest salary, 8000. Bob, Charlie, and Eve had two
identical rows each; which of the two is kept doesn't matter, because they are
the same.

---

## 5. Summary

| Goal | `PARTITION BY` | `ORDER BY` inside `OVER (...)` |
|---|---|---|
| Remove exact copies | all columns | not needed — the copies are identical |
| Keep the newest record | the identifying column(s), e.g. `employee` | the timestamp column `DESC` |
| Keep the oldest record | the identifying column(s) | the timestamp column `ASC` |
| Keep the highest value | the identifying column(s) | that value `DESC` |

If two rows tie on the `ORDER BY` value but differ elsewhere, add a
tie-breaker column (for example `ORDER BY salary DESC, department`), or
`ROW_NUMBER()` may keep a different row each time you run the query.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
