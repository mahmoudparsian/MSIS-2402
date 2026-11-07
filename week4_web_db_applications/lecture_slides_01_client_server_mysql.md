---
marp: true
title: Week 4 — Client–Server Databases (MySQL)
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

# 🖥️ Week 4 — Client–Server Databases

Session 7 · From a database *in your notebook* → a database *on a server*

MSIS-2402 — Database Management Systems: Fundamentals of SQL

---

# 🎯 Learning Objectives

By the end of today you can:

* Explain the difference between an **embedded** database (DuckDB) and a
  **client–server** database (MySQL)
* Name the jobs a database **server** does for many users at once
* Connect to MySQL with a **client** and load the course data
* Read a table's design: **data types**, `NOT NULL`, **keys**
* Run the same SQL on two engines — and spot the **dialect** differences
* Use the server's catalog: **`information_schema`** and **views**

---

# 🧭 Where We've Been (Weeks 1–3)

```
┌──────────────── your laptop ────────────────┐
│  Marimo / Python process                    │
│   ┌─────────────────────────────────────┐   │
│   │ DuckDB  (a library, running inside) │   │
│   └──────────────────┬──────────────────┘   │
│                      │ reads                │
│           CSV files / .duckdb file          │
└─────────────────────────────────────────────┘
```

* `import duckdb; con = duckdb.connect()` — no install, no server, no login
* **One program, one user**, data on your own disk
* Perfect for **analysis** — that's why we started here

---

# 🤔 The New Question

An online shop has:

* a **website** taking orders all day
* a **warehouse app** marking orders as shipped
* **40 analysts** running reports
* a **finance** team issuing refunds

👉 All of them read and write **the same orders table**, at the same time.

Where does that table live, and who keeps it correct?

---

## Embedded vs. Client–Server

```
 EMBEDDED (DuckDB)                CLIENT–SERVER (MySQL)

 ┌─────────────┐                 web app ──┐
 │ your program│                 analyst ──┤   network      ┌──────────────┐
 │  + DuckDB   │                 mysql CLI ┼─────────────> │ MySQL server │
 └──────┬──────┘                 BI tool ──┘   connections  │  (mysqld)    │
        │                                                   └──────┬───────┘
     file on disk                                            data files
```

* **Embedded:** the database engine runs *inside* your program
* **Client–server:** one **server** process owns the data; many **clients**
  connect to it and send SQL

---

# 🔒 Evidence: Why DuckDB Can't Be "The Shop's Database"

Two Python processes, one DuckDB file. Process 1 opens `shop.duckdb` to
write. Process 2 tries to open it — **even read-only**:

```
IO Error: Could not set lock on file "shop.duckdb":
Conflicting lock is held in .../Python (PID 7346) ...
```

👉 While one process is writing, **nobody else can even open the file.**

(You tried this in Class Discussion 1, item 4.)

---

## What a Database Server Does

| Job | What it means |
|---|---|
| 🔌 **Connections** | Accepts many clients over the network at once |
| 🚦 **Concurrency** | Keeps simultaneous reads and writes from corrupting each other |
| 👤 **Users & privileges** | Logins, passwords, who may read or change what |
| 🛡️ **Rules** | Enforces keys, `NOT NULL`, `CHECK` — for *every* client |
| 💾 **Durability** | Survives crashes; supports backups and recovery |

Today: connections and rules. Week 5: concurrency, privileges, performance.

---

## DuckDB vs. MySQL — Not Better, Different

| | DuckDB | MySQL |
|---|---|---|
| Runs as | a library inside your program | a separate server process |
| Users at once | one writing process | many connections (151 by default; configurable) |
| Setup | `pip install duckdb` | install + start a server |
| Login / privileges | none | users, passwords, `GRANT` |
| Built for | **analytics** (scan millions of rows) | **transactions** (many small reads/writes) |
| Typical use | notebooks, data science | websites, business applications |

👉 Real companies use **both**: MySQL runs the shop, an analytics engine
answers the big questions.

---

# 🗂️ Inside a MySQL Server

```
MySQL server (one running mysqld process)
├── isba_shop            ← our database (MySQL also calls it a "schema")
│   ├── customers
│   ├── orders
│   ├── order_items
│   └── ...
├── information_schema   ← the server's catalog (read-only)
├── mysql                ← the server's own settings and users
└── ...
```

* One server holds **many databases**; each database holds **tables**
* `USE isba_shop;` picks the database your statements run in

---

## Connecting: Anatomy of a Client

```
mysql  -u root  -p  isba_shop
  │      │       │      └── database to start in
  │      │       └── ask for a password
  │      └── user name
  └── the command-line client program
```

Every connection also has a **host** and a **port**:

* host `localhost` — the server is on your own machine (today)
* port **3306** — MySQL's default port

In production the host is another machine — the client works the same way.

---

# 🧪 Each Client Gets Its Own Session

Two terminals, two connections to the same server:

```sql
SELECT CONNECTION_ID() AS my_connection,
       USER()          AS logged_in_as,
       DATABASE()      AS current_db;
```

| | my_connection | logged_in_as | current_db |
|---|---:|---|---|
| Terminal A | 17 | root@localhost | isba_shop |
| Terminal B | 18 | root@localhost | isba_shop |

👉 Same user, same database — **two separate sessions**. The server tracks
each one (your numbers will differ).

---

# 📦 Loading the Course Data into MySQL

From the course repository's root folder:

```
# macOS
mysql -u root < datasets/oltp_database/mysql/isba_shop_mysql.sql

# Windows (PowerShell)
cmd /c "mysql -u root -p < datasets\oltp_database\mysql\isba_shop_mysql.sql"
```

* Takes about **3 seconds**; rebuilds `isba_shop` from scratch every time
* Load with `<` (a shell redirect) — it works the same on every MySQL version

---

# ✅ How Do You Know the Load Worked?

The script ends by counting every table:

| tbl | n |
|---|---:|
| customers | 1,000 |
| products | 2,000 |
| stores | 50 |
| orders | 100,000 |
| order_items | 300,000 |
| payments | 100,000 |
| shipments | 100,000 |

👉 Same counts as the CSVs in DuckDB (Class Discussion 1, item 2).
**Always check a load against a number you trust.**

---

## A Table, Designed — Not Guessed

DuckDB *guessed* types from the CSV. In MySQL we **declare** them:

```sql
CREATE TABLE orders (
    order_id     INT PRIMARY KEY,
    customer_id  INT NOT NULL,
    store_id     INT NOT NULL,
    order_date   DATE NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (store_id)    REFERENCES stores(store_id)
);
```

(From `isba_shop_mysql.sql` — the actual table you load.)

---

# 🔤 Data Types You'll See

| Type | Holds | Example column |
|---|---|---|
| `INT` | whole numbers | `order_id`, `quantity` |
| `DECIMAL(10,2)` | exact numbers, 2 decimal places | `price`, `sales_amount` |
| `VARCHAR(30)` | text, up to 30 characters | `country`, `category` |
| `DATE` | a calendar date | `order_date` |

* The type is a **rule**: `'abc'` into an `INT` column →
  `ERROR 1366: Incorrect integer value: 'abc'`
* The length is a **limit**: 18 characters into `VARCHAR(10)` →
  `ERROR 1406: Data too long for column 'gender'`

(MySQL's default *strict* mode refuses the row instead of quietly changing it.)

---

# 💰 Why `DECIMAL` for Money?

Same query, both engines — revenue for the top category:

| Engine | Column type | `SUM(sales_amount)` for Clothing |
|---|---|---:|
| DuckDB (from CSV) | `DOUBLE` | 26607217.960000124 |
| MySQL | `DECIMAL(12,2)` | 26607217.96 |

`DOUBLE` stores binary approximations: in DuckDB,
`0.1::DOUBLE + 0.2::DOUBLE` = `0.30000000000000004`.

👉 Money in a business system is stored as **`DECIMAL`** — exact to the cent.

---

## The Same Table in Two Engines

**DuckDB** — `customers` loaded from CSV:

| column_name | column_type | null |
|---|---|---|
| customer_id | BIGINT | YES |
| gender | VARCHAR | YES |

**MySQL** — `DESCRIBE customers;`

| Field | Type | Null | Key |
|---|---|---|---|
| customer_id | int | NO | PRI |
| gender | varchar(10) | NO | |
| country | varchar(30) | NO | |
| segment | varchar(30) | NO | |
| signup_date | date | NO | |

👉 DuckDB: no key, anything may be empty. MySQL: a **primary key** and
**`NOT NULL`** on every column.

---

# 🛡️ Constraints: Rules the Server Enforces

| Constraint | Prevents |
|---|---|
| `PRIMARY KEY` | two rows with the same ID |
| `FOREIGN KEY` | a row pointing to a parent that doesn't exist |
| `NOT NULL` | a required value left empty |
| `CHECK (...)` | values that break a business rule (e.g. price ≤ 0) |
| `UNIQUE` | duplicates in a non-key column (e.g. email) |

👉 In Week 2 you **checked** for orphans with anti-joins.
A server **refuses** them — for every client, every time.

---

# 🚫 The Server Says No

An order item for an order that doesn't exist:

```sql
INSERT INTO order_items
VALUES (300001, 999999, 1, 1, 'Office', 347.31, 347.31);
```

```
ERROR 1452 (23000): Cannot add or update a child row: a foreign key
constraint fails (`isba_shop`.`order_items`, CONSTRAINT
`order_items_ibfk_1` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`))
```

* Nothing was saved
* The message names the **table**, the **constraint**, and the **rule**
* Lab 1b: you'll break keys and constraints on purpose and read the errors

---

# ✍️ CRUD: Create, Read, Update, Delete

```sql
-- Create
INSERT INTO customers VALUES (1001, 'Female', 'Canada', 'Consumer', '2026-10-04');

-- Read
SELECT * FROM customers WHERE customer_id = 1001;

-- Update
UPDATE customers SET segment = 'VIP' WHERE customer_id = 1001;

-- Delete
DELETE FROM customers WHERE customer_id = 1001;
```

⚠️ `UPDATE` and `DELETE` **without** `WHERE` change **every row**.

---

# 👀 One Client Writes, Another Reads

| Step | Terminal A | Terminal B |
|---:|---|---|
| 1 | | `SELECT COUNT(*) FROM customers;` → **1000** |
| 2 | `INSERT` customer 1001 → `1 row affected` | |
| 3 | | `SELECT` customer 1001 → **found** |
| 4 | `UPDATE` segment to `'VIP'` | |
| 5 | | `SELECT` → segment is **VIP** |
| 6 | `DELETE` customer 1001 | |
| 7 | | `SELECT COUNT(*)` → **1000** |

👉 MySQL runs with **autocommit** on: each statement is saved the moment it
succeeds, and every other client sees it. (Week 5: when that's *not* enough.)

---

## Same SQL, Different Engine

Revenue by store country — the identical query in DuckDB and MySQL:

```sql
SELECT s.country,
       ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM stores s
JOIN orders o       ON o.store_id  = s.store_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY s.country
ORDER BY revenue DESC;
```

USA **42,738,573.55** · Australia **42,106,400.08** · France **38,831,155.02** ·
UK 26,898,706.48 · Canada 23,446,005.44 · Germany 19,679,705.56

👉 Same six numbers on both engines — standard SQL **travels**.

---

# 🗣️ …But Every Engine Has a Dialect

DuckDB features you've used that MySQL rejects (`ERROR 1064`, syntax error):

| DuckDB | Portable / MySQL version |
|---|---|
| `GROUP BY ALL` | `GROUP BY country, segment` (list the columns) |
| `read_csv_auto('file.csv')` | `CREATE TABLE` + `INSERT` / `LOAD DATA` |
| `COUNT(*) FILTER (WHERE x)` | `SUM(CASE WHEN x THEN 1 ELSE 0 END)` |
| `order_date::VARCHAR` | `CAST(order_date AS CHAR)` |

👉 Write the **standard** form when a query has to run in more than one place.

---

# 🪟 Views: A Saved Query with a Name

```sql
CREATE VIEW v_country_revenue AS
SELECT s.country,
       ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM stores s
JOIN orders o       ON o.store_id  = s.store_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY s.country;
```

Any client can now just run:

```sql
SELECT * FROM v_country_revenue ORDER BY revenue DESC LIMIT 3;
```

* A view stores the **query**, not a copy of the data — always up to date
* It lives **on the server**, so every client and application shares it
* Week 5: views also **hide** columns from users who shouldn't see them

---

# 📚 The Server Describes Itself: `information_schema`

```sql
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'isba_shop'
ORDER BY table_name;
```

| TABLE_NAME | TABLE_ROWS |
|---|---:|
| customers | 1000 |
| order_items | 300000 |
| **orders** | **97604** |

⚠️ `orders` really has **100,000** rows. `table_rows` is an **estimate** —
your number will differ (97,604 here; 100,113 on another load) — use
`COUNT(*)` when you need the truth.

---

# 🧰 MySQL Command-Line Survival Kit

| Command | Does |
|---|---|
| `SHOW DATABASES;` | list databases on the server |
| `USE isba_shop;` | switch database |
| `SHOW TABLES;` | list tables in the current database |
| `DESCRIBE orders;` | columns, types, keys |
| `SHOW CREATE TABLE orders;` | the full `CREATE TABLE` statement |
| end with `\G` instead of `;` | print a wide row **vertically** |
| `\c` | throw away the statement you're typing |
| `exit` | disconnect |

Every statement ends with `;` — without it, MySQL waits for more.
(`\G` and `\c` work at the `mysql>` prompt, not in piped scripts.)

---

# 🔁 Recap

* **Embedded** (DuckDB): engine inside your program — one user, great for analysis
* **Client–server** (MySQL): one server, many clients, over connections
* The server enforces **types**, **keys**, and **constraints** for everyone
* `DECIMAL` for money; `DOUBLE` is approximate
* Standard SQL runs on both — **dialect** extras don't
* **Views** share queries; **`information_schema`** describes the server

---

# 🧪 Today's Labs

**Lab 1a — A database server and its clients**
Load the data, explore the server, two clients at once, CRUD, and the same
query on two engines.

**Lab 1b — The server protects the data** *(challenge)*
Break keys and constraints on purpose and read the errors, add your own
rule, query `information_schema`, and build a view for an application.

Next session: a **web application** that talks to a database.
