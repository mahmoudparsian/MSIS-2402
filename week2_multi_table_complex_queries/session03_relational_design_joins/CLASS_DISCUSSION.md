# Week 2 — Class Discussion 1 (Relational Modeling & JOINs)

Session 3 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| Primary key | Column whose value uniquely identifies each row of a table |
| Foreign key | Column that points to the primary key of another table |
| `INNER JOIN ... ON` | Combine rows from two tables; keeps only rows that match |
| `LEFT JOIN` | Keep every row of the left table, matched or not (`NULL`s where not) |
| `WHERE ... IS NULL` | After a `LEFT JOIN`, find the rows that had no match |

## Setup

**Dataset:** three small tables in this folder's `data/` — **not** the
course database you'll use in the labs:

| Table | Rows | Columns |
|---|---:|---|
| `customers` | 200 | `customer_id`, `gender`, `country`, `segment`, `signup_date` |
| `orders` | 800 | `order_id`, `customer_id`, `store_id`, `order_date` |
| `products` | 100 | `product_id`, `category`, `price` |

1. Open a terminal **in this folder** (the one that contains this file and
   `data/`).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load the tables once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE customers AS SELECT * FROM read_csv_auto('data/customers.csv');
CREATE OR REPLACE TABLE orders    AS SELECT * FROM read_csv_auto('data/orders.csv');
CREATE OR REPLACE TABLE products  AS SELECT * FROM read_csv_auto('data/products.csv');
```

## Simple

1. **(Discussion)** Suppose someone merged `customers` and `orders` into one
   giant table, repeating each customer's `gender`, `country`, `segment`, and
   `signup_date` on every one of their orders. What goes wrong if that
   customer's country is later corrected — how many rows would need to
   change, and what could go wrong if only some of them do?

2. **(SQL)** Join `customers` to `orders` on `customer_id`.
   - Columns: `order_id`, `country`, `order_date`
   - Sort: `order_id` ascending
   - Limit: 10 rows

## Intermediate

3. **(Discussion)** Look at `customers.customer_id` and `orders.customer_id`.
   Which is a **primary key** (uniquely identifies one row) and which is a
   **foreign key** (points to another table)? Check your answer: in each
   table, compare `COUNT(*)` with `COUNT(DISTINCT customer_id)` — which
   table has a repeated `customer_id`, and what would a repeat mean?

4. **(SQL + Discussion)** `orders` has 800 rows. Write an `INNER JOIN`
   between `customers` and `orders` on `customer_id` and count the rows of
   the result — one column, `n_rows`. Is it 800? If not, what does that tell
   you about how `INNER JOIN` treats rows that don't find a match?

## Intermediate+

5. **(SQL + Discussion)** Use a `LEFT JOIN` with `WHERE ... IS NULL` to
   count, in two queries:
   - (a) `n_orphan_orders` — rows in `orders` whose `customer_id` doesn't
     exist in `customers` (start the join from `orders`);
   - (b) `n_customers_without_orders` — customers who never placed an order
     (start the join from `customers`).

   Are these numbers small (a handful of edge cases) or large enough to be a
   real problem?

6. **(Discussion)** Given what you found in #5: a manager asks for "total
   orders by country" using
   `customers c JOIN orders o ON c.customer_id = o.customer_id`. Would you
   trust that number as "all our orders, by country"? What would you tell
   them the query actually counts, and what would you do differently if they
   needed a count of *every* order?
