# Week 3 — Class Discussion 1 (Window Functions)

Session 5 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `OVER (...)` | Makes a function a window function — computes across rows but keeps every row |
| `RANK()` / `DENSE_RANK()` | Number rows by rank; they differ in the number given after a tie |
| `SUM(...) OVER (ORDER BY ...)` | Running total — a cumulative sum in date order |
| `PARTITION BY` | Restart the window calculation for each group (e.g. per country) |
| `CASE WHEN ... THEN ... END` | Label rows based on conditions (e.g. High / Medium / Low) |

## Setup

**Datasets:**

- Items 1–4 and 6: the table `sales`, from `data/week4_sales.csv` in this
  folder — 200 transactions of 4 products. Columns: `order_id`,
  `order_date`, `product`, `price`, `quantity`, `sales_amount`.
- Item 5: the course database in `../../datasets/oltp_database/` — `stores`
  (50), `orders` (100,000), `order_items` (300,000), `products` (2,000).

1. Open a terminal **in this folder** (the one that contains this file and
   `data/`).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load the tables once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE sales       AS SELECT * FROM read_csv_auto('data/week4_sales.csv');
CREATE OR REPLACE TABLE stores      AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/stores.csv');
CREATE OR REPLACE TABLE orders      AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/orders.csv');
CREATE OR REPLACE TABLE order_items AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/order_items.csv');
CREATE OR REPLACE TABLE products    AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/products.csv');
```

## Simple

1. **(Discussion)** Both `GROUP BY` and a window function (`... OVER (...)`)
   can compute a `SUM()`. What's the difference in how many rows come back?
   If you wanted to show a transaction's `sales_amount` **and** its
   product's total revenue side by side in the same row, which one could do
   that?

2. **(SQL)** Rank the 4 products by total revenue.
   - Columns: `product`, `revenue` = `SUM(sales_amount)`,
     `revenue_rank` = `RANK() OVER (ORDER BY SUM(sales_amount) DESC)`
   - One row per product, sorted by `revenue_rank`

## Intermediate

3. **(SQL + Discussion)** Rank **all 200** transactions by `sales_amount`.
   - Columns: `order_id`, `product`, `sales_amount`,
     `rnk` = `RANK() OVER (ORDER BY sales_amount DESC)`,
     `drnk` = `DENSE_RANK() OVER (ORDER BY sales_amount DESC)`
   - Sort: `sales_amount` descending, then `order_id`

   Seven `sales_amount` values appear twice (ties). Find the two
   transactions with `sales_amount = 2580` and the transaction right below
   them. What do `rnk` and `drnk` give the tied pair, and what does each
   give the next row? Which would you use to say "this is the Nth-highest
   sale" in a report, and which for "there are N distinct sale-value
   tiers"?

4. **(SQL + Discussion)** A running total in date order.
   - Columns: `order_date`, `order_id`, `sales_amount`,
     `running_total` = `SUM(sales_amount) OVER (ORDER BY order_date, order_id)`
   - Sort: `order_date`, then `order_id`

   Skim the result: are there noticeably "flat" stretches (the running total
   barely moves for a few rows) or "steep" ones (it jumps a lot)? What would
   each pattern mean for the business, and what would you check before
   assuming either one is real rather than day-to-day noise?

## Intermediate+

5. **(SQL + Discussion)** Within each store **country**, rank the product
   categories by revenue.
   - Source: `stores s` `JOIN orders o` on `store_id` `JOIN order_items oi`
     on `order_id` `JOIN products p` on `product_id`
   - Columns: `country` (the store's), `category` (from `products`),
     `revenue` = `SUM(oi.sales_amount)`,
     `rank_in_country` =
     `RANK() OVER (PARTITION BY s.country ORDER BY SUM(oi.sales_amount) DESC)`
   - One row per (country, category); sort by `country`, then
     `rank_in_country`

   Is the #1 category the same in every country? What would happen to
   `rank_in_country` if you left out `PARTITION BY`?

6. **(SQL + Discussion — debug it)** A classmate runs:

   ```sql
   SELECT product, RANK()
   FROM sales;
   ```

   DuckDB 2.0 answers `Binder Error: Window functions are not supported
   here`. What is missing from `RANK()`? Without it, what would the ranking
   even be ranking *by*?

   Then write **one** query that ranks the products by revenue **and**
   labels each one:
   - Columns: `product`, `revenue` = `SUM(sales_amount)`,
     `revenue_rank` (as in item 2), `segment`
   - `segment` (use `CASE`): `'High'` if revenue is above 50,000; `'Medium'`
     if above 20,000; otherwise `'Low'`
   - Sort: `revenue_rank`
