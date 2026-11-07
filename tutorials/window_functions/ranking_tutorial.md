# Window Functions: `ROW_NUMBER`, `RANK`, and `DENSE_RANK`

[← Tutorials](../README.md) · **Window functions** · [`ROW_NUMBER()` example →](row_number_example.md)

The differences between the three ranking functions, shown on 10 employees —
several of them with the **same salary** (ties), because ties are exactly where
the three functions differ.

---

## 1. The Data

[`employees_by_country.csv`](employees_by_country.csv), in this folder:

```
country,gender,employee,salary
USA,M,John,5000
USA,F,Sarah,5000
USA,M,Mike,4000
UK,F,Emma,6000
UK,M,Liam,6000
UK,F,Olivia,5500
CAN,M,Alex,7000
CAN,F,Zoe,7000
CAN,M,Ryan,5000
CAN,F,Maya,4500
```

---

## 2. Setup

Start DuckDB **from this folder**. From the course repository folder
(`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/window_functions
duckdb
```

(or create a Marimo notebook in this folder and run the SQL in SQL cells). Then:

```sql
CREATE OR REPLACE TABLE staff AS
SELECT * FROM read_csv_auto('employees_by_country.csv');

SELECT COUNT(*) AS n_rows FROM staff;
```

Result:

| n_rows |
|---:|
| 10 |

*1 row*

---

## 3. One Ranking for Everybody (no `PARTITION BY`)

Without `PARTITION BY`, the whole table is one group.

```sql
SELECT employee,
       salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC, employee) AS row_num,
       RANK()       OVER (ORDER BY salary DESC)           AS rnk,
       DENSE_RANK() OVER (ORDER BY salary DESC)           AS dense_rnk
FROM staff
ORDER BY row_num;
```

Result:

| employee | salary | row_num | rnk | dense_rnk |
|---|---:|---:|---:|---:|
| Alex | 7000 | 1 | 1 | 1 |
| Zoe | 7000 | 2 | 1 | 1 |
| Emma | 6000 | 3 | 3 | 2 |
| Liam | 6000 | 4 | 3 | 2 |
| Olivia | 5500 | 5 | 5 | 3 |
| John | 5000 | 6 | 6 | 4 |
| Ryan | 5000 | 7 | 6 | 4 |
| Sarah | 5000 | 8 | 6 | 4 |
| Maya | 4500 | 9 | 9 | 5 |
| Mike | 4000 | 10 | 10 | 6 |

*10 rows*

Read the ties:

- **Alex and Zoe** (7000) share `rnk` 1 and `dense_rnk` 1. `ROW_NUMBER` still
  gives them 1 and 2 — it never repeats a number.
- **Emma** (6000) is `rnk` **3** — `RANK` skips 2 because two people are ahead of
  her — but `dense_rnk` **2**: `DENSE_RANK` never skips.
- **John, Ryan, Sarah** (5000) tie three ways: `rnk` 6, `dense_rnk` 4; the next
  salary, Maya's, is `rnk` **9** (6 + 3).

**The tie-breaker rule.** `ROW_NUMBER()` must put tied rows in *some* order. If
the `ORDER BY` inside `OVER (...)` doesn't decide it, the order — and so which
tied row gets which number — can change from run to run. Always add a
tie-breaker column (here `employee`) so the numbering is repeatable. `RANK` and
`DENSE_RANK` don't need one: tied rows get the same number on purpose.

---

## 4. A Ranking per Country (`PARTITION BY country`)

`PARTITION BY` restarts the numbering in every country.

```sql
SELECT country,
       employee,
       salary,
       ROW_NUMBER() OVER (PARTITION BY country ORDER BY salary DESC, employee) AS row_num,
       RANK()       OVER (PARTITION BY country ORDER BY salary DESC)           AS rnk,
       DENSE_RANK() OVER (PARTITION BY country ORDER BY salary DESC)           AS dense_rnk
FROM staff
ORDER BY country, row_num;
```

Result:

| country | employee | salary | row_num | rnk | dense_rnk |
|---|---|---:|---:|---:|---:|
| CAN | Alex | 7000 | 1 | 1 | 1 |
| CAN | Zoe | 7000 | 2 | 1 | 1 |
| CAN | Ryan | 5000 | 3 | 3 | 2 |
| CAN | Maya | 4500 | 4 | 4 | 3 |
| UK | Emma | 6000 | 1 | 1 | 1 |
| UK | Liam | 6000 | 2 | 1 | 1 |
| UK | Olivia | 5500 | 3 | 3 | 2 |
| USA | John | 5000 | 1 | 1 | 1 |
| USA | Sarah | 5000 | 2 | 1 | 1 |
| USA | Mike | 4000 | 3 | 3 | 2 |

*10 rows*

---

## 5. Which One Should I Use?

| Function | Ties get … | Numbers after a tie | Typical use |
|---|---|---|---|
| `ROW_NUMBER()` | different numbers (needs a tie-breaker) | 1, 2, 3, 4 | pick exactly one row; pagination |
| `RANK()` | the same number | skips: 1, 1, 3, 4 | "top 10" lists where ties take up places |
| `DENSE_RANK()` | the same number | no gaps: 1, 1, 2, 3 | "the 2nd-highest salary" |

---

## 6. Partitioning by Two Columns

`PARTITION BY country, gender` makes smaller groups: the numbering restarts for
every **combination** of country and gender.

**Question:** *who is the top earner among the men in Canada, the women in
Canada, the men in the USA, and so on?*

```sql
SELECT country,
       gender,
       employee,
       salary,
       ROW_NUMBER() OVER (PARTITION BY country, gender ORDER BY salary DESC, employee) AS row_num,
       RANK()       OVER (PARTITION BY country, gender ORDER BY salary DESC)           AS rnk
FROM staff
ORDER BY country, gender, row_num;
```

Result:

| country | gender | employee | salary | row_num | rnk |
|---|---|---|---:|---:|---:|
| CAN | F | Zoe | 7000 | 1 | 1 |
| CAN | F | Maya | 4500 | 2 | 2 |
| CAN | M | Alex | 7000 | 1 | 1 |
| CAN | M | Ryan | 5000 | 2 | 2 |
| UK | F | Emma | 6000 | 1 | 1 |
| UK | F | Olivia | 5500 | 2 | 2 |
| UK | M | Liam | 6000 | 1 | 1 |
| USA | F | Sarah | 5000 | 1 | 1 |
| USA | M | John | 5000 | 1 | 1 |
| USA | M | Mike | 4000 | 2 | 2 |

*10 rows*

- **More columns, smaller groups:** instead of ranking against everyone in the
  country, each person is ranked against people of the same gender in that
  country.
- **The reset:** `row_num` starts again at 1 for each new country + gender
  combination.
- **A typical use:** the most expensive product in every category *and*
  sub-category.

---

## 7. Filtering on a Rank: `QUALIFY`

A window function is computed **after** `WHERE`, so you can't write
`WHERE ROW_NUMBER() OVER (...) = 1`. The standard way is a CTE (or subquery):

```sql
WITH ranked_staff AS (
    SELECT country, gender, employee, salary,
           ROW_NUMBER() OVER (PARTITION BY country, gender
                              ORDER BY salary DESC, employee) AS rn
    FROM staff
)
SELECT country, gender, employee, salary
FROM ranked_staff
WHERE rn = 1
ORDER BY country, gender;
```

Result:

| country | gender | employee | salary |
|---|---|---|---:|
| CAN | F | Zoe | 7000 |
| CAN | M | Alex | 7000 |
| UK | F | Emma | 6000 |
| UK | M | Liam | 6000 |
| USA | F | Sarah | 5000 |
| USA | M | John | 5000 |

*6 rows*

DuckDB also has a shortcut, `QUALIFY` — a `WHERE` for window functions — so no
CTE is needed (and the rank need not be in the `SELECT` list):

```sql
SELECT country,
       gender,
       employee,
       salary
FROM staff
QUALIFY ROW_NUMBER() OVER (PARTITION BY country, gender
                           ORDER BY salary DESC, employee) = 1
ORDER BY country, gender;
```

Result:

| country | gender | employee | salary |
|---|---|---|---:|
| CAN | F | Zoe | 7000 |
| CAN | M | Alex | 7000 |
| UK | F | Emma | 6000 |
| UK | M | Liam | 6000 |
| USA | F | Sarah | 5000 |
| USA | M | John | 5000 |

*6 rows*

Both return the same 6 rows. Use `WHERE` to filter raw rows and `QUALIFY` to
filter on window results; `QUALIFY` works with `RANK`, `DENSE_RANK`,
`ROW_NUMBER`, or any other window function. (`QUALIFY` is not standard SQL —
MySQL, for example, doesn't have it; there, use the CTE.)

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
