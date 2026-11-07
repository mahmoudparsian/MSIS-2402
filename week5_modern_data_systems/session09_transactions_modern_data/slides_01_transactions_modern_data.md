---
marp: true
title: Week 5 — Transactions, Concurrency & Modern Data Systems
theme: default
paginate: true
style: |
  h2 {
    background: linear-gradient(90deg, #2c3e50, #4ca1af);
    color: white;
    padding: 10px 18px;
    border-radius: 6px;
    width: fit-content;
  }
  h3 {
    background: #ecf0f1;
    padding: 6px 10px;
    border-radius: 4px;
  }
  pre code {
    font-size: 20px;
  }
  table {
    font-size: 22px;
  }
---

# 🔐 Week 5 — Transactions & Modern Data Systems

Session 9 · Keeping data correct when many people write at once — and where
data goes after the checkout

MSIS-2402 — Database Management Systems: Fundamentals of SQL

---

# 🎯 Learning Objectives

By the end of today you can:

* Explain what a **transaction** is and use `START TRANSACTION`, `COMMIT`,
  `ROLLBACK`
* Describe **ACID** with a real checkout
* Explain **isolation**, **snapshots**, and why the app must `ROLLBACK` on errors
* Describe a **lost update** and how **locks** prevent it
* Tell **OLTP** from **OLAP**, and **row** from **column** storage
* Place **warehouses**, **lakes**, **NoSQL** and **cloud** databases on the map

---

# Part 1 — Transactions

---

# 🛒 The Checkout Problem

One checkout writes **four** things:

```
orders        1 row    (who, which store, when)
order_items   n rows   (what was bought)
payments      1 row    (how it was paid)
shipments     1 row    (how it ships)
```

What if the server crashes — or one statement fails — **halfway through**?

* an order with no items?
* items with no payment?

👉 These four writes must happen **all together, or not at all**.

---

## A Transaction = One Unit of Work

```sql
START TRANSACTION;                     -- MySQL (also: BEGIN)
INSERT INTO orders      VALUES (...);
INSERT INTO order_items VALUES (...);
INSERT INTO payments    VALUES (...);
COMMIT;                                -- make it permanent, for everyone
```

…or, if anything goes wrong:

```sql
ROLLBACK;                              -- undo everything since START
```

DuckDB uses the same statements (`BEGIN TRANSACTION` or `START TRANSACTION`).

---

## ACID — Four Promises

| Letter | Promise | In our checkout |
|---|---|---|
| **A**tomicity | all or nothing | never an order without its items and payment |
| **C**onsistency | every rule still holds afterwards | foreign keys, `NOT NULL`, `CHECK` stay true |
| **I**solation | others don't see half-done work | an analyst never counts a half-written order |
| **D**urability | committed = survives a crash | once "Order confirmed", it stays confirmed |

---

# ⚙️ Autocommit: the Default

```sql
SELECT @@autocommit;      -- 1
```

* With autocommit **on**, every statement is its own tiny transaction —
  saved the moment it succeeds (what you saw in Week 4)
* `START TRANSACTION` switches that off **until** `COMMIT` or `ROLLBACK`
* Use an explicit transaction whenever **two or more** statements belong
  together

---

## Isolation: Nobody Sees It Until `COMMIT`

| Step | Terminal A | Terminal B |
|---:|---|---|
| 1 | `START TRANSACTION;` | |
| 2 | `UPDATE customers SET segment = 'VIP' WHERE customer_id = 42;` | |
| 3 | `SELECT ...` → **VIP** | |
| 4 | | `SELECT ...` → **Consumer** (old value) |
| 5 | `ROLLBACK;` → back to **Consumer** | |
| 6 | (again, but) `COMMIT;` | |
| 7 | | `SELECT ...` → **VIP** |

👉 B answered **immediately** at step 4 — reading never waits for a writer;
it just sees the last **committed** value.

---

## A Consistent Snapshot for Readers

An analyst's report must not change halfway through:

| Step | Terminal A (the shop) | Terminal B (the analyst) |
|---:|---|---|
| 1 | | `START TRANSACTION;` |
| 2 | | `SELECT COUNT(*) FROM orders;` → **100000** |
| 3 | `INSERT` order 100001 (autocommit) → A sees **100001** | |
| 4 | | `SELECT COUNT(*) FROM orders;` → still **100000** |
| 5 | | `COMMIT;` then count → **100001** |

👉 MySQL's default isolation level, **`REPEATABLE READ`**, gives each
transaction a snapshot taken at its first read.

---

# 💥 An Error in the Middle

```sql
START TRANSACTION;
INSERT INTO orders      VALUES (100001, 42, 7, '2026-10-04');                -- OK
INSERT INTO order_items VALUES (300001, 100001, 1, 2, 'Office', 347.31, 694.62); -- OK
INSERT INTO payments    VALUES (100001, 100001, NULL, '2026-10-04', 694.62);
-- ERROR 1048: Column 'payment_method' cannot be null
```

Rows now pending in this transaction: order **1**, items **1**, payments **0**

* **MySQL** undoes only the **failed statement** — a `COMMIT` now would save
  an order with no payment
* **DuckDB** aborts the **whole** transaction (Class Discussion 1, item 5)

👉 Never rely on the default: **on any error, `ROLLBACK`.**

---

## The Rule, in Application Code

```python
def sell(con, items):
    con.execute("BEGIN TRANSACTION")
    try:
        for product_id, qty in items:
            con.execute("UPDATE inventory SET stock = stock - ? WHERE product_id = ?",
                        [qty, product_id])
        con.execute("COMMIT")
        return "committed"
    except duckdb.Error:
        con.execute("ROLLBACK")          # undo every statement, not just the failed one
        return "rolled back"
```

With stock `(1: 10, 2: 3)` and `CHECK (stock >= 0)`:

* `sell(con, [(1, 1), (2, 5)])` → **rolled back**, stock unchanged `(10, 3)`
* `sell(con, [(1, 1), (2, 2)])` → **committed**, stock `(9, 1)`

---

# 👥 Two Writers, One Row: the Lost Update

One Watch left. Two clerks, no protection:

| time | Clerk A | Clerk B |
|---:|---|---|
| 1 | reads stock → **1** | |
| 2 | | reads stock → **1** |
| 3 | "OK to sell" | "OK to sell" |
| 4 | writes stock = **0** | |
| 5 | | writes stock = **0** |

👉 **Two** Watches sold, **one** existed — and the data *looks* fine (0).

---

## Locks: Writers Take Turns

* When a transaction **changes** a row, MySQL **locks** that row until
  `COMMIT` or `ROLLBACK`
* A second transaction that wants to **change the same row** must **wait**
  (MySQL gives up after `innodb_lock_wait_timeout` — 50 seconds by default)
* **Readers** don't wait — they see the last committed version (two slides back)
* Locks are per **row**: other customers' orders flow through untouched

🧪 **Session 9 Lab B:** you'll make a second session wait on a lock, watch it
continue the instant the first commits — and discover that locks alone
still aren't enough to stop the Watch overselling.

---

## Isolation Levels (SQL Standard)

| Level | A transaction might see… |
|---|---|
| `READ UNCOMMITTED` | others' **uncommitted** changes ("dirty reads") |
| `READ COMMITTED` | new committed data **between** its own reads |
| **`REPEATABLE READ`** | one consistent snapshot — **MySQL's default** |
| `SERIALIZABLE` | as if transactions ran one at a time — safest, slowest |

👉 Higher isolation = fewer surprises, more waiting.

---

# Part 2 — Modern Data Systems

---

## OLTP vs. OLAP

| | **OLTP** — run the business | **OLAP** — analyze the business |
|---|---|---|
| Typical work | checkout, update an address | revenue by country by month |
| Rows per query | a few | millions |
| Users | thousands of customers | tens of analysts |
| Cares most about | correctness under concurrency | scanning speed |
| Our course | **MySQL** `isba_shop` | **DuckDB** notebooks |

👉 Most companies run **both** — and copy data from the first to the second.

---

## Row Storage vs. Column Storage

```
Row store (MySQL):     [1,48956,1645,3,Home,202.86,608.58] [2,68631,189,1,Sports,...] ...
Column store:          order_item_id: 1,2,3,...   category: Home,Sports,...   sales_amount: ...
```

`order_items` (300,000 rows, 7 columns) saved both ways:

| File | Size |
|---|---:|
| `order_items.csv` (rows of text) | 12,376,480 bytes |
| `order_items.parquet` (columnar, compressed) | 4,370,271 bytes |

DuckDB's plan for revenue by category on the Parquet file:
`PARQUET_SCAN — Projections: category, sales_amount` → reads **2 of 7** columns.

---

# 🏛️ The Data Warehouse

A separate database built for **analysis**:

* **Integrated** — data from many systems (shop, CRM, marketing) in one place
* **Historical** — years of history, rarely updated, mostly appended
* **Column-oriented** and massively parallel
* Usually modeled as **star schemas** (facts + dimensions)

Examples: **Snowflake**, **Google BigQuery**, **Amazon Redshift**

---

## Getting Data There: ETL / ELT

```
 MySQL (OLTP)  ──extract──>  transform  ──load──>  warehouse  ──>  dashboards
 CRM, web logs ──┘           (clean, join,                         & reports
                              reshape)
```

* **ETL** — transform *before* loading (classic)
* **ELT** — load raw data first, transform *inside* the warehouse with SQL
* Runs on a schedule (nightly, hourly) or continuously
* The OLTP database stays fast; analysts never slow down the checkout

---

# 🌊 The Data Lake

* **Files** — CSV, JSON, Parquet, logs, images — in cheap **object storage**
  (Amazon S3, Azure Blob Storage, Google Cloud Storage)
* Store first, decide the structure later (**schema-on-read**)
* Query the files **where they are** — no load step:

```sql
SELECT category, ROUND(SUM(sales_amount), 2) AS revenue
FROM '../../datasets/oltp_database/order_items.csv'
GROUP BY category
ORDER BY revenue DESC
LIMIT 3;
```

→ Clothing **26,607,217.96** · Toys **25,909,756.51** · Office **25,160,829.12**
(same answer as from the Parquet file, or from a loaded table)

---

# 🏠 The Lakehouse

Lake **files** + warehouse **features**:

* Open table formats — **Delta Lake**, **Apache Iceberg** — add tables,
  schemas, and **transactions** on top of Parquet files
* One copy of the data serves BI dashboards **and** data science
* Example platforms: **Databricks**, Snowflake and BigQuery reading Iceberg

👉 The same ideas you learned this quarter — tables, SQL, ACID — showing up
on top of plain files.

---

## NoSQL: Four Families

| Family | Data looks like | Good for | Examples |
|---|---|---|---|
| **Key-value** | `key → value` | shopping carts, sessions, caches | Redis, DynamoDB |
| **Document** | JSON documents | catalogs with varying attributes | MongoDB |
| **Wide-column** | huge sparse tables | massive write volume (clicks, sensors) | Cassandra |
| **Graph** | nodes + relationships | "bought X also bought Y", fraud rings | Neo4j |

Trade-offs: flexible schemas and easy scale-out — but joins, constraints
and multi-row transactions are often weaker than in a relational database.

---

## Relational Rows vs. One Document

Order 1, relational — **3 tables**, joined by keys:

```
orders:       (1, customer 993, store 36, 2021-08-11)
order_items:  (24814, order 1, product 681, 3 × 493.50) (42838, ...) (240228, ...)
payments:     (1, order 1, PayPal, 2021-08-11, 143.45)
```

The same order as **one** document:

```json
{ "order_id": 1, "customer_id": 993, "store_id": 36, "order_date": "2021-08-11",
  "items": [ { "product_id": 681, "category": "Office",    "quantity": 3, "price": 493.50 },
             { "product_id": 68,  "category": "Toys",      "quantity": 2, "price": 19.62 },
             { "product_id": 947, "category": "Computers", "quantity": 3, "price": 156.81 } ],
  "payment": { "method": "PayPal", "amount": 143.45 } }
```

👉 One read gets the whole order — but "revenue by category" must open every document.

---

# ☁️ Cloud Databases

| | Run it yourself | Managed cloud service |
|---|---|---|
| Install, patch, back up | **you** | the provider |
| Scale up | buy a bigger machine | change a setting |
| Pay for | the hardware | usage (hours, storage, queries) |
| Examples | MySQL on your laptop | Amazon RDS / Aurora, Google Cloud SQL, Azure SQL Database, BigQuery |

👉 Same SQL — someone else runs the server. The trade-off: cost control and
**vendor lock-in**.

---

## Choosing the Right System

| Need | Good fit |
|---|---|
| Checkout, bookings, bank transfers | relational OLTP (MySQL, PostgreSQL) |
| Five-year revenue dashboard | data warehouse (or DuckDB at small scale) |
| Raw logs, files, data science | data lake / lakehouse |
| Shopping cart, user session | key-value store |
| Product catalog with varying fields | document database |
| Recommendations, networks | graph database |

👉 Real systems combine several — joined together by **ETL** and **SQL**.

---

# 🔁 Recap

* A **transaction** groups statements: `START TRANSACTION` → `COMMIT` / `ROLLBACK`
* **ACID**: all-or-nothing, rules hold, isolated, durable
* Readers see a **snapshot**; writers to the same row take turns via **locks**
* On any error: **`ROLLBACK`** — engines differ in what they undo
* **OLTP** runs the business; **OLAP** analyzes it — rows vs. columns
* Warehouses, lakes, lakehouses, NoSQL, cloud: pick by **workload**

---

# 🧪 Today's Labs

**Session 9 Lab A — Transactions and the order fulfillment lifecycle** (DuckDB)
`BEGIN` / `COMMIT` / `ROLLBACK`, and the order → payment → shipment chain.

**Session 9 Lab B — MySQL transactions and locking** *(challenge)*
Two live sessions, one row: watch a real lock wait — and fix an oversold
product.

Next session: **performance, security, and governance**.
