---

marp: true

title: Week 1 — SQL Foundations, Deck 2 (DuckDB Tour)

theme: default

paginate: true

---

# slide-1: SQL Introduction — A Deeper Tour

**MSIS-2402 — SQL Fundamentals**

Reference deck, adapted from the
[DuckDB SQL introduction](https://duckdb.org/docs/current/sql/introduction)
(itself adapted from the
[PostgreSQL tutorial](https://www.postgresql.org/docs/current/tutorial-sql-intro.html)).

> DuckDB's SQL dialect closely follows PostgreSQL conventions.

This deck previews **JOIN**, **GROUP BY/HAVING**, **UPDATE**, and **DELETE**
using DuckDB's own classic `weather` / `cities` example — some of this
material is covered in depth in later weeks. Every query on this deck has
been run and verified against a real DuckDB connection.

---

# slide-2: Concepts

* DuckDB is a **relational database management system (RDBMS)** — it manages
  data stored in *relations*.
* A **relation** is the mathematical term for a **table**.
* Each table is a named collection of **rows**.
* Every row in a table shares the same set of named **columns**, each with a
  specific data type.
* Tables live inside **schemas**; a collection of schemas is a **database**.

---

# slide-3: Schemas Act as Namespaces

```
schemas: s1 and s2

s1
  table1
  table2
  ...
s2
  table1
  table2
  table4
  table5
```

---

# slide-4: Example — Creating Schemas

```sql
CREATE SCHEMA s1;
CREATE SCHEMA s2;

CREATE TABLE s1.table1 (id INT);
CREATE TABLE s2.table1 (id INT);
```

Same table name (`table1`), two different schemas — no conflict.

---

# slide-5: Creating a New Table

Specify the table name, then each column's name and type:

```sql
CREATE TABLE weather (
    city    VARCHAR,
    temp_lo INTEGER, -- minimum temperature on a day
    temp_hi INTEGER, -- maximum temperature on a day
    prcp    FLOAT,
    date    DATE
);
```

`--` starts a comment (ignored to end of line). SQL keywords are
case-insensitive; whitespace is free-form.

---

# slide-6: Reading the `CREATE TABLE` Statement

* `CREATE TABLE` — the command
* `weather` — the table name
* `city VARCHAR` — a column named `city`, storing text of arbitrary length
* `temp_lo`, `temp_hi` — `INTEGER` columns (whole numbers)
* `prcp` — `FLOAT`, a single-precision number with a decimal point
* `date` — `DATE`, stores year/month/day only (no time)

---

# slide-7: DuckDB's Standard SQL Types

```
  INTEGER
  SMALLINT
  FLOAT
  DOUBLE
  DECIMAL
  CHAR(n)
  VARCHAR(n)
  DATE
  TIME
  TIMESTAMP
```

---

# slide-8: A Second Table — `cities`

```sql
CREATE TABLE cities (
    name VARCHAR,
    lat  DECIMAL,
    lon  DECIMAL
);
```

To remove a table you no longer need:

```sql
DROP TABLE ⟨tablename⟩;
```

---

# slide-9: Populating a Table with Rows

`INSERT INTO ... VALUES` adds rows:

```sql
INSERT INTO weather
VALUES ('San Francisco', 46, 50, 0.25, '1994-11-27');
```

Text and dates need single quotes (`'...'`). Dates must be `'YYYY-MM-DD'`.

```sql
INSERT INTO cities
VALUES ('San Francisco', -194.0, 53.0);
```

---

# slide-10: `INSERT` with an Explicit Column List

Naming columns explicitly avoids relying on column order:

```sql
INSERT INTO weather (city, temp_lo, temp_hi, prcp, date)
VALUES ('San Francisco', 43, 57, 0.0, '1994-11-29');
```

You can reorder columns, or omit ones you don't have yet:

```sql
INSERT INTO weather (date, city, temp_hi, temp_lo)
VALUES ('1994-11-29', 'Hayward', 54, 37);
```

👉 Many developers consider explicit column lists better style.

---

# slide-11: Bulk Loading with `COPY`

For large amounts of data, `COPY` is faster than repeated `INSERT`s — it's
optimized for bulk loading (with less flexibility):

```sql
COPY weather
FROM 'data/weather.csv';
```

The source file must be readable from the machine running DuckDB. (DuckDB
also offers `read_csv_auto()` — see the `duckdb_101_slides.md` deck.)

---

# slide-12: Querying a Table — `SELECT *`

A `SELECT` statement has: a **select list** (columns), a **table list**
(`FROM`), and an optional **qualification** (`WHERE`).

```sql
SELECT *
FROM weather;
```

`*` is shorthand for "all columns" — equivalent to:

```sql
SELECT city, temp_lo, temp_hi, prcp, date
FROM weather;
```

---

# slide-13: Query Result

|     city      | temp_lo | temp_hi | prcp |    date    |
|---------------|--------:|--------:|-----:|------------|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 |
| San Francisco | 43      | 57      | 0.0  | 1994-11-29 |
| Hayward       | 37      | 54      | NULL | 1994-11-29 |

---

# slide-14: Expressions in the Select List

You aren't limited to plain column references:

```sql
SELECT city, 
       (temp_hi + temp_lo) / 2 AS temp_avg, 
       date
FROM weather;
```

|     city      | temp_avg |    date    |
|---------------|---------:|------------|
| San Francisco | 48.0     | 1994-11-27 |
| San Francisco | 50.0     | 1994-11-29 |
| Hayward       | 45.5     | 1994-11-29 |

`AS` relabels the output column (and is optional).

---

# slide-15: The `WHERE` Clause

`WHERE` keeps only rows where a Boolean expression is true. `AND`, `OR`,
`NOT` are all allowed:

```sql
SELECT *
FROM weather
WHERE city = 'San Francisco'
  AND prcp > 0.0;
```

|     city      | temp_lo | temp_hi | prcp |    date    |
|---------------|--------:|--------:|-----:|------------|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 |

---

# slide-16: `ORDER BY`

```sql
SELECT *
FROM weather
ORDER BY city;
```

|     city      | temp_lo | temp_hi | prcp |    date    |
|---------------|--------:|--------:|-----:|------------|
| Hayward       | 37      | 54      | NULL | 1994-11-29 |
| San Francisco | 43      | 57      | 0.0  | 1994-11-29 |
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 |

⚠️ Sorting only by `city` doesn't fully order the two San Francisco rows —
their relative order isn't guaranteed.

---

# slide-17: `ORDER BY` — Breaking Ties

Add a second sort key for a fully deterministic order:

```sql
SELECT *
FROM weather
ORDER BY city, temp_lo;
```

Now the San Francisco rows always come out in the same order (43 before 46).

---

# slide-18: `DISTINCT`

Remove duplicate rows from the result:

```sql
SELECT DISTINCT city
FROM weather;
```

|     city      |
|---------------|
| San Francisco |
| Hayward       |

Row order isn't guaranteed here either.

---

# slide-19: `DISTINCT` + `ORDER BY`

For consistent, repeatable output, combine them:

```sql
SELECT DISTINCT city
FROM weather
ORDER BY city;
```

---

# slide-20: Joins Between Tables

A query that reads multiple tables (or the same table multiple times) at
once is a **join query**.

Goal: list each weather record together with its city's location — compare
`weather.city` to `cities.name`, and keep the pairs that match.

```sql
SELECT *
FROM weather, cities
WHERE city = name;
```

---

# slide-21: Join Result

|     city      | temp_lo | temp_hi | prcp |    date    |     name      |   lat    |  lon   |
|---------------|--------:|--------:|-----:|------------|---------------|---------:|-------:|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 | San Francisco | -194.000 | 53.000 |
| San Francisco | 43      | 57      | 0.0  | 1994-11-29 | San Francisco | -194.000 | 53.000 |

Two things to notice:

* **No Hayward row** — there's no matching `cities` entry, so the join
  drops it (fixed next, with an outer join).
* **Two city-name columns** — `*` concatenates both tables' columns.

---

# slide-22: Naming Columns Explicitly

In practice, list output columns rather than using `*`:

```sql
SELECT city, temp_lo, temp_hi, prcp, date, lon, lat
FROM weather, cities
WHERE city = name;
```

If both tables had a column with the *same* name, you'd need to qualify it
(`weather.city`, `cities.name`) so the parser knows which one you mean:

```sql
SELECT weather.city, weather.temp_lo, weather.temp_hi,
       weather.prcp, weather.date, cities.lon, cities.lat
FROM weather, cities
WHERE cities.name = weather.city;
```

👉 Good style: qualify all column names in a join query.

---

# slide-23: `INNER JOIN` Syntax

The join above can also be written with explicit `JOIN ... ON`:

```sql
SELECT *
FROM weather
INNER JOIN cities ON weather.city = cities.name;
```

Same result as `FROM weather, cities WHERE weather.city = cities.name`.
This ANSI form is less common in older code, but is the standard way to
write joins going forward — we'll use it exclusively starting Week 2.

---

# slide-24: Bringing Hayward Back — `LEFT OUTER JOIN`

We want to scan `weather` and, for each row, find matching `cities` rows —
substituting **NULL** for `cities` columns when nothing matches. This is
called an **outer join** (vs. the **inner joins** seen so far):

```sql
SELECT *
FROM weather
LEFT OUTER JOIN cities ON weather.city = cities.name;
```

---

# slide-25: `LEFT OUTER JOIN` Result

|     city      | temp_lo | temp_hi | prcp |    date    |     name      |   lat    |  lon   |
|---------------|--------:|--------:|-----:|------------|---------------|---------:|-------:|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 | San Francisco | -194.000 | 53.000 |
| San Francisco | 43      | 57      | 0.0  | 1994-11-29 | San Francisco | -194.000 | 53.000 |
| Hayward       | 37      | 54      | NULL | 1994-11-29 | NULL          | NULL     | NULL   |

**Left** table (`weather`) keeps every row at least once. **Right** table
(`cities`) only contributes rows that match.

---

# slide-26: Aggregate Functions

Like most relational databases, DuckDB supports **aggregate functions** —
they compute a single result from many input rows: `count`, `sum`, `avg`,
`max`, `min`, and more.

The highest low-temperature reading anywhere:

```sql
SELECT max(temp_lo)
FROM weather;
```

| max(temp_lo) |
|-------------:|
| 46           |

---

# slide-27: ⚠️ Aggregates Can't Go in `WHERE`

Tempting, but wrong:

```sql
SELECT city
FROM weather
WHERE temp_lo = max(temp_lo);
```

```console
Binder Error:
WHERE clause cannot contain aggregates!
```

Why: `WHERE` decides which rows *feed into* the aggregate — it must run
**before** the aggregate is computed, so it can't reference the aggregate's
own result.

---

# slide-28: Fixing It with a Subquery

```sql
SELECT city
FROM weather
WHERE temp_lo = (SELECT max(temp_lo) FROM weather);
```

|     city      |
|---------------|
| San Francisco |

The subquery computes its own, independent aggregate — separate from the
outer query — so this is perfectly legal.

---

# slide-29: Aggregates + `GROUP BY`

The maximum low temperature observed **in each city**:

```sql
SELECT city, 
       max(temp_lo)
FROM weather
GROUP BY city;
```

|     city      | max(temp_lo) |
|---------------|--------------|
| San Francisco | 46           |
| Hayward       | 37           |

One output row per city; each aggregate is computed over just that city's rows.

---

# slide-30: Filtering Groups with `HAVING`

```sql
SELECT city, 
       max(temp_lo)
FROM weather
GROUP BY city
HAVING max(temp_lo) < 40;
```

Same result, with the aggregate aliased for readability:

```sql
SELECT city, 
       max(temp_lo) AS max_temp_lo
FROM weather
GROUP BY city
HAVING max_temp_lo < 40;
```

|  city   | max(temp_lo) |
|---------|-------------:|
| Hayward | 37           |

---

# slide-31: Combining `WHERE`, `GROUP BY`, `HAVING`

Only care about cities starting with `S`? Filter early, with `WHERE`:

```sql
SELECT city, 
       max(temp_lo) AS max_temp_lo
FROM weather
WHERE city LIKE 'S%'
GROUP BY city
HAVING max_temp_lo < 40;
```

Result: **empty** — San Francisco's `max_temp_lo` is 46, not `< 40`. That's
expected, not an error — a good moment to show students that a valid query
can correctly return zero rows.

---

# slide-32: `WHERE` vs. `HAVING`

* `WHERE` selects **input rows**, before groups/aggregates are computed —
  it decides what feeds the aggregate. It **cannot** use aggregate functions.
* `HAVING` selects **group rows**, after groups/aggregates are computed —
  it **always** involves aggregate functions.
* Prefer `WHERE` when you can: filtering rows before grouping is more
  efficient than grouping everything and filtering afterward with `HAVING`.

---

# slide-33: `UPDATE`

Suppose the temperature readings after Nov 28 are all off by 2 degrees:

```sql
UPDATE weather
SET temp_hi = temp_hi - 2,  
    temp_lo = temp_lo - 2
WHERE date > '1994-11-28';
```

Always use `WHERE` with `UPDATE` — without it, **every** row is modified.

---

# slide-34: State After `UPDATE`

```sql
SELECT *
FROM weather;
```

|     city      | temp_lo | temp_hi | prcp |    date    |
|---------------|--------:|--------:|-----:|------------|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 |
| San Francisco | 41      | 55      | 0.0  | 1994-11-29 |
| Hayward       | 35      | 52      | NULL | 1994-11-29 |

---

# slide-35: `DELETE`

No longer interested in Hayward's weather? Remove those rows:

```sql
DELETE FROM weather
WHERE city = 'Hayward';
```

```sql
SELECT *
FROM weather;
```

|     city      | temp_lo | temp_hi | prcp |    date    |
|---------------|--------:|--------:|-----:|------------|
| San Francisco | 46      | 50      | 0.25 | 1994-11-27 |
| San Francisco | 41      | 55      | 0.0  | 1994-11-29 |

---

# slide-36: ⚠️ `DELETE` Without `WHERE`

```sql
DELETE FROM ⟨table_name⟩;
```

Without a qualification, `DELETE` removes **all** rows from the table,
leaving it empty — DuckDB will **not** ask for confirmation first.

👉 Same rule as `UPDATE`: always double-check your `WHERE` clause first.

---

# slide-37: What We Covered

* schemas & table creation (`CREATE TABLE`, data types)
* loading data (`INSERT`, `COPY`)
* querying (`SELECT`, `WHERE`, `ORDER BY`, `DISTINCT`)
* joins (implicit, `INNER JOIN`, `LEFT OUTER JOIN`)
* aggregates (`MAX`, `GROUP BY`, `HAVING`, subqueries)
* modifying data (`UPDATE`, `DELETE`)

`GROUP BY`/`HAVING` return in depth later this week (Part 2), and joins in Week 2 — this was a
preview, using DuckDB's own reference example.
