# Week 2 — Class Discussion 2 (Transaction Analytics, Bigger Dataset)

Session 4 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| Multi-table `JOIN` | Chain joins, e.g. `orders` → `order_items` → `products` |
| Table aliases (`oi.category`) | Say which table a column comes from — required when two tables share a column name |
| `SUM` + `GROUP BY` after a join | Aggregate the joined rows, e.g. revenue per customer |
| `ORDER BY ... LIMIT` | Keep the top N rows, e.g. the 5 biggest customers |
| Two-step aggregation | Sum per order first (subquery or CTE), then average those sums |

## Setup

**Dataset:** the course database in `../../datasets/oltp_database/` (the
same data `notebook_01_transaction_analytics.py` uses):

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

1. **(Discussion)** 300,000 `order_items` rows across 100,000 `orders` is
   about 3 items per order. Why does a real e-commerce system split "order"
   and "order item" into two tables instead of one row per order with a list
   of products crammed into it?

2. **(SQL)** Join `order_items` to `products` on `product_id`.
   - Columns: every column of both tables (`SELECT *`)
   - Sort: `order_item_id` ascending
   - Limit: 10 rows

   Which column names appear twice in the result? Keep that in mind for #5.

## Intermediate

3. **(SQL + Discussion)** Revenue by category.
   - Source: `order_items`
   - Columns: `category`, `revenue` = `SUM(sales_amount)` rounded to 2
     decimals
   - Sort: `revenue` descending

   The 8 categories land within about 20% of each other (roughly $22.1M to
   $26.6M). In Week 1 Discussion 2's "revenue by country", the strongest
   market beat the weakest by about 29%. What would you tell a manager who
   wants to know if this business has a "star" category?

4. **(SQL + Discussion)** The top 5 customers by total revenue.
   - Source: `orders` `JOIN` `order_items` on `order_id`
   - Columns: `customer_id`, `revenue` = `SUM(sales_amount)` rounded to 2
     decimals
   - Grouping: one row per `customer_id`
   - Sort: `revenue` descending; ties by `customer_id` ascending
   - Limit: 5 rows

   Then compute their share: (sum of the 5 revenues) ÷ (total revenue,
   `SUM(sales_amount)` over all of `order_items`) × 100. What percentage of
   revenue do these 5 of 1,000 customers bring in? Is the business dependent
   on a handful of big customers, or is revenue spread out?

## Intermediate+

5. **(SQL + Discussion — debug it)** Run this query:

   ```sql
   SELECT category, SUM(sales_amount) AS revenue
   FROM order_items oi
   JOIN products p ON oi.product_id = p.product_id
   GROUP BY category;
   ```

   It fails. Look at the columns of both `order_items` and `products` — why
   does SQL refuse to run it, and what small change (a table alias in front
   of one column name, twice) fixes it?

6. **(SQL + Discussion)** The *average sales amount*, two ways, both rounded
   to 2 decimals:
   - (a) `avg_line_amount` = `AVG(sales_amount)` directly on `order_items`;
   - (b) `avg_order_value` = the average **order** total: first
     `SUM(sales_amount)` per `order_id` (a subquery or CTE), then `AVG` of
     those sums.

   The two numbers are very different. What business question does each
   answer, and which one would you report if asked "what's our average
   order value?"
