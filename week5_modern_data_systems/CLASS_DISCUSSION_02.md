# Week 5 — Class Discussion 2 (Performance, Security, and Governance)

Session 10 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `COUNT(*) FILTER (WHERE ...)` | Measure how many rows a condition matches (its selectivity) |
| Index | A sorted lookup structure that lets the database skip rows that can't match |
| `HAVING COUNT(*) < 5` | Find small groups — a privacy check on group counts |
| `CREATE VIEW` + `GRANT` | Give a user a limited, pre-shaped slice of the data |
| `DELETE ... WHERE` | Remove rows — preview the same `WHERE` with `SELECT COUNT(*)` first |

## Setup

**Dataset:** the shared OLTP tables in `../datasets/oltp_database/`
— `customers` (1,000 rows: `customer_id, gender, country, segment,
signup_date`), `orders` (100,000), `order_items` (300,000), `payments`,
`shipments`, `stores` (50). Work in DuckDB.

1. Open a terminal **in this folder** (the one that contains this file).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load all seven tables once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE customers   AS SELECT * FROM read_csv_auto('../datasets/oltp_database/customers.csv');
CREATE OR REPLACE TABLE stores      AS SELECT * FROM read_csv_auto('../datasets/oltp_database/stores.csv');
CREATE OR REPLACE TABLE products    AS SELECT * FROM read_csv_auto('../datasets/oltp_database/products.csv');
CREATE OR REPLACE TABLE orders      AS SELECT * FROM read_csv_auto('../datasets/oltp_database/orders.csv');
CREATE OR REPLACE TABLE order_items AS SELECT * FROM read_csv_auto('../datasets/oltp_database/order_items.csv');
CREATE OR REPLACE TABLE payments    AS SELECT * FROM read_csv_auto('../datasets/oltp_database/payments.csv');
CREATE OR REPLACE TABLE shipments   AS SELECT * FROM read_csv_auto('../datasets/oltp_database/shipments.csv');
```

## Simple

1. **(Discussion)** The shop's database has three kinds of users: the
   **web application**, a **marketing analyst**, and the **database
   administrator** (DBA). For each one, which of these should it be
   allowed to do: read data, insert rows, update rows, delete rows,
   create or drop tables? Why not simply give all three the `root`
   password?

2. **(SQL)** In one query (`COUNT(*) FILTER (WHERE ...)`), count how many
   `orders` match each condition — one row, these columns:
   - `customer_42`: `customer_id = 42`
   - `store_7`: `store_id = 7`
   - `one_day`: `order_date = DATE '2023-03-03'`
   - `since_2021`: `order_date >= DATE '2021-01-01'`

   Then turn each count into a percentage of all 100,000 orders
   (count ÷ 100,000 × 100).

## Intermediate

3. **(Discussion)** An **index** lets the database jump straight to the
   matching rows instead of reading the whole table. Using your numbers
   from item 2: for which of the four conditions would an index help
   the most, and for which would it not help at all? In MySQL,
   `orders` already has indexes on `customer_id` and `store_id`, even
   though nobody ran `CREATE INDEX` — where did they come from?

4. **(SQL + Discussion)** A report shows how many customers fall in
   each **country × segment × gender** group. The `customers` table has
   no names or emails, so it looks anonymous. Find the groups with fewer
   than 5 customers:

   ```sql
   SELECT country, segment, gender, COUNT(*) AS n_customers
   FROM customers
   GROUP BY country, segment, gender
   HAVING COUNT(*) < 5
   ORDER BY n_customers, country, segment, gender;
   ```

   How many such groups are there, and how many contain exactly **one**
   customer? Why is a group of one a privacy problem even with no name
   attached? Suggest two ways to change the report so it's safe to
   share.

## Intermediate+

5. **(SQL + Discussion)** A marketing intern needs **monthly revenue by
   store country** — nothing else. Write the query that would sit
   behind a view for them:
   - Source: `orders o` `JOIN stores s` on `store_id` `JOIN order_items oi`
     on `order_id`
   - Columns: `country` (the store's), `month` =
     `date_trunc('month', o.order_date)`, `revenue` = `SUM(oi.sales_amount)`
     rounded to 2 decimals
   - One row per (`country`, `month`); sorted by `country`, then `month`

   How many rows does it return?
   Why is granting the intern access to this view safer than granting
   them `SELECT` on `orders`, `order_items`, and `customers`? What can
   they no longer find out?

6. **(SQL + Discussion — debug it)** A clean-up job was meant to delete
   orders from before 2020, but the date was mistyped:

   ```sql
   DELETE FROM orders WHERE order_date < DATE '2022-01-01';
   ```

   **Don't run it.** Instead, preview it with two queries:
   - one row with `intended` (orders with `order_date < DATE '2020-01-01'`)
     and `mistyped` (orders with `order_date < DATE '2022-01-01'`);
   - one row with `order_items`, `payments`, `shipments` — how many rows of
     each table belong to the orders the mistyped statement would delete. In DuckDB (tables
   loaded from CSV) the `DELETE` would simply succeed. In the MySQL
   `isba_shop` database from Week 4, it would not — why? List three
   other safeguards that would have caught or undone this mistake.
