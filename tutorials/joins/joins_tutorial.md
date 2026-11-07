# SQL Joins: Connecting the Dots

[← Tutorials](../README.md) · **Joins**

A hands-on tour of `INNER JOIN`, `LEFT JOIN`, and `RIGHT JOIN` in DuckDB, using two
small CSV files in this folder: 12 employees and 4 departments.

In a relational database, data is split into several tables to avoid
redundancy. Joins are how we stitch that data back together to answer
business questions.

---

## 1. The Data

Both files are in this folder: [`employees.csv`](employees.csv) (the **left**
table in the examples) and [`departments.csv`](departments.csv) (the **right**
table).

**`employees.csv`** — 12 rows. John and Sarah have `dept_id` 99, which is
**not** in the department list: they are "orphaned" records.

```
emp_id,name,dept_id
1,Alice,10
2,Bob,10
3,Charlie,10
4,David,20
5,Eve,20
6,Frank,20
7,Grace,30
8,Heidi,30
9,Ivan,30
10,Judy,30
11,John,99
12,Sarah,99
```

**`departments.csv`** — 4 rows. Marketing (`dept_id` 40) has **no** employees.

```
dept_id,dept_name
10,Sales
20,IT
30,HR
40,Marketing
```

---

## 2. Setup

Start DuckDB **from this folder**, so the file names below are found. From the
course repository folder (`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/joins
duckdb
```

(or create a Marimo notebook in this folder and run the SQL in SQL cells). Then
load both files:

```sql
CREATE OR REPLACE TABLE employees AS
SELECT * FROM read_csv_auto('employees.csv');

CREATE OR REPLACE TABLE departments AS
SELECT * FROM read_csv_auto('departments.csv');
```

Check the row counts:

```sql
SELECT (SELECT COUNT(*) FROM employees)   AS employees,
       (SELECT COUNT(*) FROM departments) AS departments;
```

Result:

| employees | departments |
|---:|---:|
| 12 | 4 |

*1 row*

---

## 3. `INNER JOIN`: Only the Matches

An `INNER JOIN` returns only the rows that have a match in **both** tables. An
employee without a valid department, or a department without employees, is
left out.

**Business question:** *"List the employees and their department names."*

```sql
SELECT e.name,
       d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id
ORDER BY e.emp_id;
```

Result:

| name | dept_name |
|---|---|
| Alice | Sales |
| Bob | Sales |
| Charlie | Sales |
| David | IT |
| Eve | IT |
| Frank | IT |
| Grace | HR |
| Heidi | HR |
| Ivan | HR |
| Judy | HR |

*10 rows*

**Why 10 rows, not 12?** John and Sarah (department 99) are missing because
department 99 is not in `departments`. Marketing (department 40) is missing
because nobody works there.

---

## 4. `LEFT JOIN`: Keep Every Employee

A `LEFT JOIN` returns **every** row of the left table (`employees`), plus the
matching row from the right table. When there is no match, the right side's
columns are `NULL`.

**Business question:** *"List every employee. If they belong to a department,
show it; if not, show them anyway so we can fix their record."*

```sql
SELECT e.name,
       d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id
ORDER BY e.emp_id;
```

Result:

| name | dept_name |
|---|---|
| Alice | Sales |
| Bob | Sales |
| Charlie | Sales |
| David | IT |
| Eve | IT |
| Frank | IT |
| Grace | HR |
| Heidi | HR |
| Ivan | HR |
| Judy | HR |
| John | NULL |
| Sarah | NULL |

*12 rows*

**Insight:** John and Sarah appear with `dept_name` = `NULL`. That tells a
manager: *"These two people are on the payroll but not assigned to a valid
department."*

---

## 5. `RIGHT JOIN`: Keep Every Department

A `RIGHT JOIN` returns **every** row of the right table (`departments`), plus
the matching employees. A department with no employees shows `NULL` on the
employee side.

**Business question:** *"Show all departments and who works in them —
including departments that are empty."*

```sql
SELECT e.name,
       d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id
ORDER BY d.dept_id, e.emp_id;
```

Result:

| name | dept_name |
|---|---|
| Alice | Sales |
| Bob | Sales |
| Charlie | Sales |
| David | IT |
| Eve | IT |
| Frank | IT |
| Grace | HR |
| Heidi | HR |
| Ivan | HR |
| Judy | HR |
| NULL | Marketing |

*11 rows*

**11 rows:** the 10 matched employees plus 1 empty department. Marketing
appears with a `NULL` name: *"We have a Marketing department, but nobody works
in it yet."*

A `RIGHT JOIN` is the same as a `LEFT JOIN` with the two tables swapped —
`departments d LEFT JOIN employees e` gives the same rows. Most people write
`LEFT JOIN`s only.

---

## 6. Summary

| Join | Rows from `employees` (left) | Rows from `departments` (right) | Use it to … |
|---|---|---|---|
| `INNER` | only matched | only matched | see only complete relationships |
| `LEFT` | **all** | only matched | find orphaned records on the left (`NULL`s on the right) |
| `RIGHT` | only matched | **all** | find empty categories on the right (`NULL`s on the left) |
| `FULL OUTER` | **all** | **all** | see every record from both sides, matched or not |

---

## 7. Joins + Aggregation: A Department Report

**Business question:** *"For each department: how many people work there, and
who are they?"*

```sql
SELECT d.dept_name,
       COUNT(e.emp_id)                          AS head_count,
       STRING_AGG(e.name, ', ' ORDER BY e.name) AS staff_list
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_name
ORDER BY head_count DESC, d.dept_name;
```

Result:

| dept_name | head_count | staff_list |
|---|---:|---|
| HR | 4 | Grace, Heidi, Ivan, Judy |
| IT | 3 | David, Eve, Frank |
| Sales | 3 | Alice, Bob, Charlie |
| Marketing | 0 | NULL |

*4 rows*

- `COUNT(e.emp_id)` counts only non-`NULL` values, so Marketing gets **0**
  (`COUNT(*)` would count its one `NULL` row and give 1).
- `STRING_AGG(..., ', ' ORDER BY e.name)` lists the names alphabetically —
  without the `ORDER BY` inside it, the order of names is not guaranteed.

**The lesson:** this report starts from `departments` and uses a `LEFT JOIN`.
With an `INNER JOIN`, Marketing would vanish from the report — and give the
false impression that the department doesn't exist.

---

## 8. Exercise

Write a query that returns **only** the employees who are not assigned to a
valid department: columns `emp_id`, `name`, `dept_id`, sorted by `emp_id`.

*Hint:* `LEFT JOIN` and `WHERE d.dept_id IS NULL`. **Self-check:** 2 rows.

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
