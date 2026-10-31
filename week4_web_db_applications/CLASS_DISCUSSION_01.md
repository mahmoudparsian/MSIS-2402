# Week 4 — Class Discussion 1 (Client–Server Databases)

Session 7 · work in pairs, just before the lab · **not graded — nothing to submit**

## SQL Features to Learn

| SQL Feature | Description |
|---|---|
| `UNION ALL` | Stack the results of several queries into one result |
| `NOT EXISTS` | Find rows with no matching row in another table (orphans) |
| `FOREIGN KEY` constraint | A rule the server enforces: a row can't point to a missing parent |
| `EXTRACT(YEAR FROM ...)` | Pull one part (year, month, …) out of a date |
| `GROUP BY ALL` vs. `GROUP BY col` | DuckDB-only shortcut vs. the portable form MySQL also accepts |

## Setup

**Dataset:** the shared OLTP tables in `../datasets/oltp_database/` —
`customers` (1,000 rows), `orders` (100,000), `order_items` (300,000),
`products` (2,000), `payments` (100,000), `shipments` (100,000),
`stores` (50). Work in DuckDB; today's lab loads the same data into MySQL.

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

1. **(Discussion)** All quarter, DuckDB has run *inside* your own
   Python/Marimo process, reading files on your laptop. A real online
   shop has a website, a warehouse app, and 40 analysts all using the
   same data at the same time. Name three jobs a database **server**
   (like MySQL) has to do that DuckDB-in-your-notebook never had to.

2. **(SQL)** Write **one** query (hint: `UNION ALL`) that returns the
   row count of all seven tables — columns `table_name` (the table's name,
   typed as text) and `n_rows`, one row per table, in this order:
   `customers`, `stores`, `products`, `orders`, `order_items`, `payments`,
   `shipments`. Keep the numbers —
   in today's lab you'll load the same data into MySQL, and these counts
   are how you'll know the load worked.

## Intermediate

3. **(SQL + Discussion)** The CSV files carry no rules: nothing stops a
   row in `orders` from pointing to a `customer_id` that doesn't exist.
   Using `NOT EXISTS` (or `LEFT JOIN ... IS NULL`), write **one** query
   that returns one row with four counts: `orders_missing_customer`,
   `orders_missing_store`, `items_missing_order` (`order_items` rows whose
   order doesn't exist), and `items_missing_product`. What do you find?
   If a web app with no checks had been typing this data in for a year,
   would you expect the same answer? Who should be responsible for
   keeping it true — the application, or the database?

4. **(Discussion — try it)** Open two terminal windows and start
   `python3` in each.

   ```python
   # Window 1 — create a database file and keep the connection open
   import duckdb
   con = duckdb.connect('shop.duckdb')
   con.execute("CREATE TABLE t AS SELECT 42 AS x")
   ```

   ```python
   # Window 2 — try to read the same file
   import duckdb
   duckdb.connect('shop.duckdb', read_only=True)
   ```

   What happens in Window 2 — even though it only wants to *read*? What
   does that tell you about using a DuckDB file as the database behind a
   website that many people use at once? (Close Window 1 and delete
   `shop.duckdb` afterwards.)

## Intermediate+

5. **(SQL + Discussion — debug it)** This query works in DuckDB:

   ```sql
   SELECT EXTRACT(YEAR FROM order_date) AS yr,
          COUNT(*) AS n_orders
   FROM orders
   GROUP BY ALL
   ORDER BY yr;
   ```

   Run it and note the four yearly counts. MySQL rejects this exact
   query with a syntax error. Which part is DuckDB-only, and how would
   you rewrite it so the same query runs on both? Name two other DuckDB
   features you've used this quarter that you would *not* expect to
   work in MySQL.

6. **(Discussion)** Two people use the shop's database at the same
   moment. An analyst starts a long revenue report over all 300,000
   `order_items`; halfway through, a customer's checkout adds 3 new
   `order_items` rows and a payment. Should the analyst's report include
   the new rows? What would go wrong if it included *some* of them —
   say, the line items but not the payment? What does that tell you the
   server has to do when many users read and write at the same time?
