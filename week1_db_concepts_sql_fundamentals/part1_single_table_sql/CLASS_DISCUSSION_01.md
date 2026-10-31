# Week 1 — Class Discussion 1 (SELECT, WHERE, ORDER BY, LIMIT)

Session 1 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `SELECT` / `SELECT *` | Choose which columns to return (`*` = every column) |
| `WHERE` with `AND` | Keep only the rows that meet every condition |
| `ORDER BY ... DESC` | Sort the result; `DESC` puts the highest values first |
| `LIMIT` | Return only the first N rows |
| `DISTINCT` | Remove duplicates so each value appears once |

## Setup

**Dataset:** the table `sales`, from `data/sales.csv` in this folder — 200
rows, one per sale, dated 2021-01-03 to 2024-12-28.

| Column | Meaning |
|---|---|
| `sale_id` | one number per sale |
| `sale_date` | the day of the sale |
| `product_id` | the product sold |
| `product_category` | one of 8 categories |
| `quantity` | units sold |
| `unit_price` | price of one unit |
| `total_amount` | `unit_price × quantity` |

1. Open a terminal **in this folder** (the one that contains this file and
   `data/`).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load the table once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE sales AS
SELECT * FROM read_csv_auto('data/sales.csv');
```

Items marked **(Discussion)** have no SQL: be ready to explain your
reasoning out loud.

## Simple

1. **(Discussion)** Pick one row of `sales` in your head. What real-world
   event does that one row represent? Name one thing a *column* tells you
   about that event, and one thing a *row* tells you that a single column
   alone couldn't.

2. **(SQL)** Write two queries:
   - (a) every column and every row of `sales`;
   - (b) only `sale_date`, `product_category`, and `total_amount` (in that
     order), sorted by `sale_date` ascending, ties by `sale_id`.

   Why might an analyst prefer (b) in a real report?

## Intermediate

3. **(SQL + Discussion)** **Before running anything**, guess: are there
   more or fewer than 50 rows with `quantity >= 3` **and**
   `product_category = 'Electronics'`? Then count them — one column,
   `n_rows`. Was your guess right?

4. **(SQL + Discussion)** The 10 highest-value sales.
   - Columns: `sale_id`, `product_category`, `quantity`, `unit_price`,
     `total_amount`
   - Sort: `total_amount` descending; ties by `sale_id` ascending
   - Limit: 10 rows

   Look at the `quantity` column in your result. What do you notice across
   all 10 rows? Explain *why*, using `total_amount = unit_price × quantity`.

## Intermediate+

5. **(SQL + Discussion)** Run both:

   ```sql
   SELECT COUNT(DISTINCT product_category) AS n_categories FROM sales;
   SELECT COUNT(DISTINCT product_id)       AS n_products   FROM sales;
   ```

   The first returns **8**; the second returns **192** (out of 200 rows).
   What does that difference tell you about how `product_category` and
   `product_id` are used in this table? Would you expect a real retailer's
   catalog to have almost as many distinct products as sales? Why or why
   not?

6. **(SQL + Discussion)** A classmate claims: *"`WHERE total_amount > 300`
   and `WHERE unit_price > 300` are basically the same filter."* Count both
   in **one** query — columns `n_total_over_300` (rows with
   `total_amount > 300`) and `n_price_over_300` (rows with
   `unit_price > 300`). Are they the same? Use
   `total_amount = unit_price × quantity` to explain the difference.
