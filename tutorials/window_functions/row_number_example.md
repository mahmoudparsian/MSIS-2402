# A `ROW_NUMBER()` Example

[← Tutorials](../README.md) · [← Window functions](ranking_tutorial.md) · **`ROW_NUMBER()` example**

`ROW_NUMBER()` numbers rows 1, 2, 3, … in the order you choose — over the whole
table, or restarting in every group (`PARTITION BY`). Two short examples: one on
a table typed in directly, one on a CSV file.

Start DuckDB **from this folder** (the second example reads a file here). From
the course repository folder (`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/window_functions
duckdb
```

(or create a Marimo notebook in this folder and run the SQL in SQL cells).

---

## Example 1: Laptops Ranked by Price Within Each Brand

Create a small table with `VALUES` — no file needed:

```sql
CREATE OR REPLACE TABLE laptops AS
SELECT *
FROM (VALUES
    ('Apple', 'MacBook Air', 999),
    ('Apple', 'MacBook Pro', 2499),
    ('Dell',  'XPS 13',      1100),
    ('Dell',  'Inspiron',     600),
    ('Dell',  'Alienware',   2100)
) AS t(brand, model, price);
```

Number the laptops of each brand from the most to the least expensive:

```sql
SELECT brand,
       model,
       price,
       ROW_NUMBER() OVER (
           PARTITION BY brand
           ORDER BY price DESC
       ) AS price_rank
FROM laptops
ORDER BY brand, price_rank;
```

Result:

| brand | model | price | price_rank |
|---|---|---:|---:|
| Apple | MacBook Pro | 2499 | 1 |
| Apple | MacBook Air | 999 | 2 |
| Dell | Alienware | 2100 | 1 |
| Dell | XPS 13 | 1100 | 2 |
| Dell | Inspiron | 600 | 3 |

*5 rows*

`price_rank` starts again at 1 for every brand. (No two laptops of the same
brand have the same price, so no tie-breaker is needed here — compare Example 2.)

**The most common use:** keep only row number 1 — the most expensive laptop of
each brand — with a CTE:

```sql
WITH ranked_laptops AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY brand
               ORDER BY price DESC
           ) AS price_rank
    FROM laptops
)
SELECT brand, model, price
FROM ranked_laptops
WHERE price_rank = 1
ORDER BY brand;
```

Result:

| brand | model | price |
|---|---|---:|
| Apple | MacBook Pro | 2499 |
| Dell | Alienware | 2100 |

*2 rows*

---

## Example 2: Employees, Straight from a CSV File

[`employees_by_department.csv`](employees_by_department.csv), in this folder:

```
department,employee,salary
Sales,Alice,5000
Sales,Bob,6000
HR,Charlie,4500
HR,David,4500
IT,Eve,7000
```

Charlie and David earn the same (4500) — a **tie**. `ROW_NUMBER()` still has to
give them different numbers, so the `ORDER BY` inside `OVER (...)` adds a
**tie-breaker** column (`employee`): without it, which of the two gets the lower
number is not guaranteed and can change between runs.

DuckDB can query a CSV file directly with `read_csv_auto(...)` — no table needed.

**One numbering for the whole file** (no `PARTITION BY`):

```sql
SELECT *,
       ROW_NUMBER() OVER (ORDER BY salary DESC, employee) AS global_rank
FROM read_csv_auto('employees_by_department.csv')
ORDER BY global_rank;
```

Result:

| department | employee | salary | global_rank |
|---|---|---:|---:|
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 2 |
| Sales | Alice | 5000 | 3 |
| HR | Charlie | 4500 | 4 |
| HR | David | 4500 | 5 |

*5 rows*

**A numbering per department** (`PARTITION BY department`):

```sql
SELECT *,
       ROW_NUMBER() OVER (
           PARTITION BY department
           ORDER BY salary DESC, employee
       ) AS dept_rank
FROM read_csv_auto('employees_by_department.csv')
ORDER BY department, dept_rank;
```

Result:

| department | employee | salary | dept_rank |
|---|---|---:|---:|
| HR | Charlie | 4500 | 1 |
| HR | David | 4500 | 2 |
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 1 |
| Sales | Alice | 5000 | 2 |

*5 rows*

To query the data many times, load it into a table once —
`CREATE OR REPLACE TABLE staff AS SELECT * FROM read_csv_auto('employees_by_department.csv');`
— and then write `FROM staff` instead of `FROM read_csv_auto(...)`. The results
are the same.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
