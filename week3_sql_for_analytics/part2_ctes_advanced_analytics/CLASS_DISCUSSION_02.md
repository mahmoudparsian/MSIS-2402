# Week 3 — Class Discussion 2 (CTEs & Ranking Analytics)

Session 6 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `WITH` (CTE) | Name an intermediate result and query it like a table |
| Multiple CTEs | Build a query in steps: `WITH a AS (...), b AS (...) SELECT ...` |
| `ROW_NUMBER()` | Number rows 1, 2, 3 … with no ties — exactly one winner per group |
| `SUM(...) OVER ()` | Empty window = the whole result; used for share-of-total |
| Filtering on a window result | Not allowed in `WHERE`/`HAVING` — wrap the query and filter outside it |

## Setup

**Dataset:** the course database in `../../datasets/oltp_database/`:

| Table | Rows | Columns |
|---|---:|---|
| `customers` | 1,000 | `customer_id`, `gender`, `country`, `segment`, `signup_date` |
| `orders` | 100,000 | `order_id`, `customer_id`, `store_id`, `order_date` |
| `order_items` | 300,000 | `order_item_id`, `order_id`, `product_id`, `quantity`, `category`, `price`, `sales_amount` |
| `products` | 2,000 | `product_id`, `category`, `price` |

1. Open a terminal **in this folder** (the one that contains this file).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load the tables once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE customers   AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/customers.csv');
CREATE OR REPLACE TABLE orders      AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/orders.csv');
CREATE OR REPLACE TABLE order_items AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/order_items.csv');
CREATE OR REPLACE TABLE products    AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/products.csv');
```

## Simple

1. **(Discussion)** A CTE (`WITH x AS (...) SELECT ... FROM x`) can almost
   always be rewritten as a subquery (`SELECT ... FROM (...) x`). If they
   compute the same result, why bother with `WITH`? Think about a query that
   needs the *same* intermediate result twice, or one built from three or
   four logical steps.

2. **(SQL)** A CTE called `customer_orders` with one row per customer:
   `customer_id`, `n_orders` = `COUNT(*)` from `orders`. Then
   `SELECT * FROM customer_orders ORDER BY customer_id`.

## Intermediate

3. **(SQL + Discussion)** How many customers bring in more than the average
   customer? Use **two** CTEs:
   - `cust_rev`: one row per customer — `customer_id`, `revenue` =
     `SUM(oi.sales_amount)` from `orders o JOIN order_items oi` on `order_id`
   - `avg_rev`: one row — `avg_revenue` = `AVG(revenue)` from `cust_rev`
   - Final query: one column, `n_above_avg` = the number of `cust_rev` rows
     with `revenue > avg_revenue`

   Out of 1,000 customers, is it close to half, or noticeably more or fewer?
   What does that tell you about whether revenue is evenly spread or skewed
   by a few big spenders?

4. **(SQL + Discussion)** The single best-selling product in each of the 8
   categories.
   - CTE `product_sales`: one row per (`category`, `product_id`) —
     `category` from `products`, `revenue` = `SUM(oi.sales_amount)` from
     `order_items oi JOIN products p` on `product_id`
   - Rank: `rn` =
     `ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC, product_id)`
   - Keep `rn = 1`; columns `category`, `product_id`, `revenue` (rounded to
     2 decimals); sort by `category`

   Why is `ROW_NUMBER()` (rather than `RANK()`) the right choice when you
   want *exactly one* winner per group, even if there's a tie?

## Intermediate+

5. **(SQL + Discussion)** Each category's share of total revenue.
   - Inner query: one row per `category` (from `products`), `revenue` =
     `SUM(oi.sales_amount)`
   - Columns: `category`, `revenue`, `revenue_share` =
     `revenue / SUM(revenue) OVER ()`, rounded to 4 decimals (a fraction:
     0.1374 means 13.74%)
   - Sort: `revenue` descending

   What does an empty `OVER ()` mean? How would `PARTITION BY category`
   change `revenue_share`, and why would that be wrong here?

6. **(SQL + Discussion — debug it)** A classmate wants the top 5 products and
   writes:

   ```sql
   SELECT product_id,
          SUM(sales_amount) AS revenue,
          RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk
   FROM order_items
   GROUP BY product_id
   HAVING rnk <= 5;
   ```

   It fails. Week 1 showed that `WHERE` can't use an aggregate; this is a
   cousin of that rule, for `HAVING` and window functions. Why is `HAVING`
   *also* too early for a window function's result to exist? Then rewrite
   it: wrap the query (subquery or CTE) and filter with an outer
   `WHERE rnk <= 5` — columns `product_id`, `revenue`, `rnk`; sort by
   `rnk`, then `product_id`.
