# Week 4 — Class Discussion 2 (Web Application Architecture)

Session 8 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `WHERE 1 = 1` | Always-true start, so optional filters can be appended with `AND` |
| `ORDER BY ... DESC LIMIT` | Sort and cap the rows a web page shows |
| `CAST(... AS VARCHAR)` | Convert a value's type — numbers compared as text sort differently |
| `COUNT(*) FILTER (WHERE ...)` | Count only rows meeting a condition; several counts in one query |
| Query parameters (`?`) | Send user input separately from the SQL text, never pasted into it |

## Setup

**Dataset:** the shared OLTP tables in `../../datasets/oltp_database/`
— mainly `products` (2,000 rows: `product_id, category, price`), plus
`customers`, `orders`, and `order_items`. Work in DuckDB — the web app in
today's lab uses DuckDB too.

1. Open a terminal **in this folder** (the one that contains this file).
2. Start a notebook with `marimo edit my_discussion.py` — or the DuckDB
   command line with `duckdb`.
3. Load all seven tables once (in Marimo: add a SQL cell):

```sql
CREATE OR REPLACE TABLE customers   AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/customers.csv');
CREATE OR REPLACE TABLE stores      AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/stores.csv');
CREATE OR REPLACE TABLE products    AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/products.csv');
CREATE OR REPLACE TABLE orders      AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/orders.csv');
CREATE OR REPLACE TABLE order_items AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/order_items.csv');
CREATE OR REPLACE TABLE payments    AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/payments.csv');
CREATE OR REPLACE TABLE shipments   AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/shipments.csv');
```

## Simple

1. **(Discussion)** On a shop's product page, a shopper picks the
   category **Toys**, types **100** into a "max price" box, and clicks
   Search. Trace that request through the three layers — the
   **browser** (user interface), the **application** (Python code on a
   server), and the **database**. What does each layer receive, and what
   does it send back? Which layer is the only one that actually holds
   the data?

2. **(SQL)** For that search, the app you'll run today builds this
   query:

   ```sql
   SELECT product_id, category, price
   FROM products
   WHERE 1 = 1
     AND category = 'Toys'
     AND price <= 100
   ORDER BY price DESC
   LIMIT 50;
   ```

   Run it. How many rows come back, and what is the most expensive
   product shown? Then count all Toys products with no price limit — one
   column, `n_toys`. Why might a programmer start the `WHERE` with
   `1 = 1`?

## Intermediate

3. **(SQL + Discussion)** Everything a browser sends arrives at the app
   as **text**: the max-price box sends the string `'50'`, not the
   number 50. Run both counts:

   ```sql
   SELECT COUNT(*) FILTER (WHERE price <= 50)                    AS as_number,
          COUNT(*) FILTER (WHERE CAST(price AS VARCHAR) <= '50') AS as_text
   FROM products;
   ```

   Why are the two answers so different? List the products the text
   comparison counts but the number comparison doesn't — columns
   `product_id`, `price`; sorted by `price`, then `product_id`; first 5
   rows. What must the application do with the
   value from the form before it reaches SQL?

4. **(SQL + Discussion)** An admin page lists all 1,000 customers with
   their number of orders. The first version of the app runs one query
   for the customer list, then — in a Python loop — one more query per
   customer: `SELECT COUNT(*) FROM orders WHERE customer_id = ?`. How
   many queries does one page view send to the database? Write a
   **single** query that returns the same 1,000 rows — columns
   `customer_id`, `n_orders` (0 for a customer with no orders: `LEFT JOIN`
   and `COUNT(o.order_id)`). Then add `ORDER BY n_orders DESC,
   customer_id LIMIT 5` for the top 5 customers by order count. Why does the
   number of queries matter more once the database is on a separate
   server?

## Intermediate+

5. **(SQL + Discussion)** A dashboard page shows revenue by category.
   **Option A:** the app runs `SELECT * FROM order_items` and adds up
   `sales_amount` per category in a Python loop. **Option B:** the
   database does the work with `GROUP BY`. Write Option B — columns
   `category` (from `order_items`), `revenue` = `SUM(sales_amount)`
   rounded to 2 decimals; sorted by `revenue` descending. How many rows
   does each option send from the database to the app? Which is the top
   category? When would Option A ever be the right choice?

6. **(Discussion — debug it)** A bug report says: *"I searched for the
   category `Kid's Toys` and the page crashed with a SQL syntax error."*
   The search code is:

   ```python
   sql = f"SELECT product_id, category, price FROM products WHERE category = '{category}'"
   ```

   Write out the exact SQL string the app sent to the database when
   `category` was `Kid's Toys`. Why does it fail? A classmate suggests
   "just remove apostrophes from the input." Why isn't that a real fix —
   and what else could a user type into that box? (You'll explore this
   properly in today's Session 8 Lab B.)
