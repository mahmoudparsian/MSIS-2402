# Week 5 — Class Discussion 1 (Transactions and Modern Data Systems)

Session 9 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `START TRANSACTION` / `COMMIT` / `ROLLBACK` | Group statements so they all happen, or none do |
| `CHECK` constraint | A rule every row must satisfy, e.g. `stock >= 0` |
| `COUNT(DISTINCT ...)` | Count unique values, e.g. orders that have a payment |
| CTE + `JOIN` to reconcile | Total one table per key, then compare it with another table |
| `COPY ... TO ... (FORMAT parquet)` | Export a table to a columnar file |

## Setup

**Dataset:** the shared OLTP tables in `../../datasets/oltp_database/`
— `orders` (100,000 rows), `order_items` (300,000), `payments` (100,000:
`payment_id, order_id, payment_method, payment_date, payment_amount`),
`shipments` (100,000). Work in DuckDB; item 5 also uses MySQL (the
`isba_shop` database you loaded in Week 4).

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

1. **(Discussion)** A checkout writes four things: one row in `orders`,
   several rows in `order_items`, one in `payments`, and one in
   `shipments`. The server loses power after the `order_items` rows are
   written but before the payment is. When the server restarts, what
   should the database contain for this order? Which letter of
   **ACID** promises that?

2. **(SQL)** In one query (scalar subqueries), return one row with:
   `n_orders`, `n_payments`, `n_shipments` (row counts), `n_paid_orders`
   (distinct `order_id`s in `payments`), and `n_shipped_orders` (distinct
   `order_id`s in `shipments`). Does every order have exactly one
   payment and exactly one shipment?

## Intermediate

3. **(SQL + Discussion)** Does the money add up? For each order, compare
   its `payment_amount` with the total `sales_amount` of its line items:
   - CTE `item_totals`: one row per `order_id` — `items_total` =
     `SUM(sales_amount)` from `order_items`
   - Join `payments p` to `item_totals t` on `order_id`
   - Columns (one row): `orders_compared` (`COUNT(*)`), `exact_matches`
     (orders where `ROUND(p.payment_amount, 2) = ROUND(t.items_total, 2)`),
     `avg_payment` and `avg_items_total` (each rounded to 2 decimals)

   How many orders match to the cent? How do the two averages compare? This
   dataset was generated one table at a time, so nothing tied the
   tables together. In a real shop, what would make the payment and the
   line items agree — and is "wrap it in a transaction" the whole
   answer?

4. **(Discussion)** The shop has one Watch left. Two staff members
   process two orders for it at almost the same moment. Each one runs
   *read the stock → it's 1, so OK to sell → set the stock to 0*. Draw
   the timeline, step by step, for both people. How many Watches were
   sold, and how many existed? What would the database have to do to
   stop this? (Today's Session 9 Lab B reproduces this with two live MySQL
   sessions.)

## Intermediate+

5. **(SQL + Discussion — debug it)** Run this script **line by line**,
   first in DuckDB, then in MySQL (at the `mysql>` prompt, after
   `CREATE DATABASE scratch; USE scratch;`):

   ```sql
   CREATE TABLE inventory (
       product_id INT PRIMARY KEY,
       stock      INT NOT NULL CHECK (stock >= 0)
   );
   INSERT INTO inventory VALUES (1, 10), (2, 3);

   START TRANSACTION;
   UPDATE inventory SET stock = stock - 1 WHERE product_id = 1;
   UPDATE inventory SET stock = stock - 5 WHERE product_id = 2;   -- fails
   COMMIT;

   SELECT * FROM inventory ORDER BY product_id;
   ```

   The second `UPDATE` fails in both systems. Compare the final stock
   for product 1. Which system kept the first `UPDATE`, and which threw
   it away? If your application's code ignored the error and carried on
   to `COMMIT`, what would happen in each system? What should the code
   do instead?

6. **(SQL + Discussion)** Save `order_items` in a **columnar** format:

   ```sql
   COPY order_items TO 'order_items.parquet' (FORMAT parquet);
   ```

   It is written to this folder. Compare its size with
   `../../datasets/oltp_database/order_items.csv` (Mac: `ls -l` in Terminal;
   Windows: `dir` in Command Prompt). Then see how much
   space each column takes inside the Parquet file:

   ```sql
   SELECT path_in_schema AS column_name,
          SUM(total_compressed_size) AS bytes
   FROM parquet_metadata('order_items.parquet')
   GROUP BY column_name
   ORDER BY bytes DESC;
   ```

   A "revenue by category" query needs only two columns. Roughly what
   share of the Parquet file does it need to read? Why do data
   warehouses (Snowflake, BigQuery, Redshift) store data by column,
   while MySQL stores it by row? Which kind of system would you pick
   for (a) the checkout, (b) a 5-year sales dashboard? (Delete the
   `.parquet` file afterwards.)
