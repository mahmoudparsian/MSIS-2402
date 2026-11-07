---
marp: true
title: Week 5 — Performance, Security & Governance
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

# 🛡️ Week 5 — Performance, Security & Governance

Session 10 · Fast enough, safe enough, and trustworthy — running a database
for real

MSIS-2402 — Database Management Systems: Fundamentals of SQL

---

# 🎯 Learning Objectives

By the end of today you can:

* Read a query **plan** with `EXPLAIN` and `EXPLAIN ANALYZE`
* Explain what an **index** does, when it helps, and what it costs
* Apply **least privilege** with users, `GRANT`, and `REVOKE`
* Name the main **threats** to a database and the defense for each
* Describe **data governance**: ownership, classification, quality, privacy
* Plan **backup and recovery** — and prove a backup actually restores

---

# Part 1 — Performance

---

# 🐢 Correct Isn't the Same as Fast

```sql
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';   -- 71
```

* Before running a query, the database's **optimizer** picks a **plan**:
  which tables to read, in what order, and how
* Same SQL, same answer — but one plan can be **hundreds of times** faster
  than another
* `EXPLAIN` shows the plan; `EXPLAIN ANALYZE` runs it and measures

---

## Reading a Plan

```sql
EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';
```

```
-> Aggregate: count(0)
    -> Filter: (shipments.delivery_date = DATE'2024-06-30')
        -> Table scan on shipments  (rows≈100000)
```

* Read it **bottom-up**: scan the table → keep matching rows → count them
* **Table scan** = read **every** row
* `rows` here is the optimizer's **estimate**

---

## Measuring It: `EXPLAIN ANALYZE`

```
-> Aggregate: count(0)  (actual time=7.42..7.42 rows=1)
    -> Filter: (...)  (actual time=0.186..7.42 rows=71)
        -> Table scan on shipments  (actual time=0.0536..5.81 rows=100000)
```

* **actual time** — milliseconds (first row .. last row)
* **actual rows** — what really came out of each step

👉 Read **100,000** rows to find **71**. Fine today — painful at 100 million.

---

# 📇 An Index

Like the index at the back of a book: a **sorted** list of values, each
pointing to where the rows are.

```sql
CREATE INDEX idx_shipments_delivery_date ON shipments(delivery_date);
```

```
-> Aggregate: count(0)  (actual time=0.0132..0.0133 rows=1)
    -> Covering index lookup on shipments using idx_shipments_delivery_date
       (delivery_date = DATE'2024-06-30')  (actual ... rows=71)
```

| | Rows read | Time (verification machine) |
|---|---:|---:|
| Table scan | 100,000 | ≈ 7.4 ms |
| Index lookup | 71 | ≈ 0.013 ms |

---

## How the Index Finds 71 Rows

```
                  [ 2023-01-14 ]
                 /              \
        [ 2022-01-23 ]      [ 2024-02-09 ]
        /       \             /        \
     ...        ...      [2024-06-30] → 71 row pointers
```

* Values are kept **sorted** in a balanced tree (a **B-tree**)
* Each step narrows the search to one branch — a few steps reach any date
* Then it reads only the matching entries

(Illustration — the real tree holds hundreds of values per node.)

---

## Selectivity: When the Index Is Used

Same index, three filters (selecting whole rows):

| `WHERE delivery_date …` | Rows matching | Plan MySQL chose |
|---|---:|---|
| `= '2024-06-30'` | 71 | **index lookup** |
| `>= '2024-12-01'` | 2,293 | **index range scan** |
| `>= '2021-01-01'` | 100,000 (all) | **table scan** — index ignored |

👉 An index pays off when a filter is **selective** (few matches). When most
rows match, reading the whole table is cheaper.

---

# 💸 Indexes Aren't Free

* **Space** — every index is another sorted copy of a column
* **Slower writes** — every `INSERT`, `DELETE`, and change to an indexed
  column must update every index on the table
* MySQL already indexes **some** columns for you — `SHOW INDEX FROM shipments`
  lists two that nobody made with `CREATE INDEX`. Where from? (**Session 10 Lab A, Task 1**)
* One innocent-looking way of writing a `WHERE` makes an index useless
  (**Session 10 Lab A, Task 5**)

👉 Index columns you **filter**, **join**, or **sort** on often — and that are selective.

---

## Performance Habits (Most Cost Nothing)

| Habit | Why |
|---|---|
| Select only the columns you need | less data read and sent |
| Filter and aggregate **in SQL** | 8 summary rows instead of 300,000 raw rows |
| One query, not one per item | 1 round trip instead of 1,001 |
| Index selective `WHERE` / `JOIN` columns | lookup instead of scan |
| Check the plan with `EXPLAIN` | measure, don't guess |

---

# Part 2 — Security

---

## What Can Go Wrong

| Threat | Example | Main defense |
|---|---|---|
| **SQL injection** | user text changes the query | parameters (`?`) |
| **Stolen password** | leaked app config | strong passwords, least privilege |
| **Over-privileged account** | the app logs in as `root` | separate accounts, minimal grants |
| **Insider misuse** | browsing data out of curiosity | least privilege + audit logs |
| **Eavesdropping** | reading traffic on the network | encryption (TLS) |
| **Lost or stolen backup** | a dump file on a laptop | encrypt and control backups |

---

# 🔑 Authentication vs. Authorization

| | Question | In MySQL |
|---|---|---|
| **Authentication** | *Who are you?* | user name + password: `'shop_app'@'localhost'` |
| **Authorization** | *What may you do?* | privileges: `GRANT` / `REVOKE` |

* An account is **user + host** — `'shop_app'@'localhost'` may only connect
  from the server's own machine
* MySQL stores a **hash** of each password (`caching_sha2_password`), never
  the password itself

---

## Least Privilege with `GRANT`

Give each account **only** what its job needs — e.g. the web application:

```sql
CREATE USER 'shop_app'@'localhost' IDENTIFIED BY 'ShopApp#2402';
GRANT SELECT         ON isba_shop.products    TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.orders      TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.order_items TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.payments    TO 'shop_app'@'localhost';
GRANT SELECT (customer_id, country) ON isba_shop.customers TO 'shop_app'@'localhost';
```

Levels: `*.*` (everything) · `isba_shop.*` (a database) · `isba_shop.orders`
(a table) · `SELECT (col, …)` (columns). `REVOKE` takes privileges back.

---

## Logged In as the App

| Statement | Result |
|---|---|
| `SELECT ... FROM products` | ✅ rows |
| `INSERT INTO orders ...` | ✅ 1 row affected |
| `SELECT customer_id, country FROM customers` | ✅ rows |
| `SELECT customer_id, gender FROM customers` | ❌ `ERROR 1143`: denied **for column 'gender'** |
| `DELETE FROM orders ...` | ❌ `ERROR 1142`: DELETE command denied |
| `UPDATE products SET price = 0.01 ...` | ❌ `ERROR 1142`: UPDATE command denied |
| `DROP TABLE orders` | ❌ `ERROR 1142`: DROP command denied |

`SHOW TABLES` lists only the 5 tables it has rights on — `shipments` and
`stores` are invisible.

---

# 🧱 Defense in Depth

Session 8's unsafe search pasted user text into SQL. Suppose an attacker
gets SQL through anyway — what can they do?

| App connects as | Injected `DROP TABLE orders` |
|---|---|
| `root` | the table is **gone** |
| `shop_app` | `ERROR 1142: DROP command denied` |

👉 **Parameters** stop injection; **least privilege** limits the damage if
something else fails. Use both.

---

# 🎭 Views and Roles

* **View** — expose a **slice** of the data: some columns, some rows, or only
  totals. Grant access to the view, not the table underneath.
* **Role** — a named **bundle** of privileges (`reporting`, `support`, …).
  Grant the role to people; change the role once, everyone follows.

🧪 **Session 10 Lab B:** build an analyst account with a privacy-preserving view, add a
role — and discover how easily a role can undo what the view protected.

---

# 🔒 Encryption

| Where | What protects it |
|---|---|
| **In transit** (network) | TLS — check with `SHOW SESSION STATUS LIKE 'Ssl_cipher';` |
| **At rest** (disk) | encrypted storage / tablespace encryption |
| **Passwords** | stored as hashes, never as text |
| **Backups** | encrypt the files; control who can copy them |

Our demo app's connection over TCP, with no extra setup:
`Ssl_cipher = TLS_AES_128_GCM_SHA256`

---

# Part 3 — Governance

---

## Data Governance: The Questions

| Question | Example answer |
|---|---|
| **Who owns** this data? | Sales owns `orders`; Finance owns `payments` |
| **Who may use** it, and for what? | analysts: aggregates only |
| **How good** is it? | measured quality checks (next slides) |
| **How long** do we keep it? | e.g. orders 7 years, web logs 90 days |
| **Which rules apply?** | privacy laws (GDPR in the EU, CCPA in California) |

👉 SQL enforces the answers; **people and processes** decide them.

---

# 🏷️ Classifying Data

| Level | Meaning | Example |
|---|---|---|
| **Public** | anyone may see | product categories and list prices |
| **Internal** | employees only | revenue by store |
| **Confidential** | need-to-know | payment details, individual orders |
| **Restricted** | strictly limited, legally protected | health, financial-account, ID numbers |

Each level comes with rules: who may access, where it may be stored, whether
it must be encrypted or masked. (Session 10 Lab B: you classify the `customers` columns.)

---

## Data Quality: Measured, Not Assumed

Checks you've already run on this course's data:

| Dimension | Check | Result |
|---|---|---|
| **Completeness** | `NULL`s in `customers` | 0 in every column |
| **Referential integrity** | orders/items pointing to missing parents | 0 |
| **Validity** | delivered before shipped · paid before ordered | 0 · 0 |
| **Consistency** | orders with **no** line items | **5,030** |
| **Consistency** | payment = sum of the order's items | **1** of 94,970 |

👉 Constraints catch some problems; others need **regular checks** — and an
owner who fixes them.

---

# 🕵️ Privacy: "Anonymous" Isn't Automatic

`customers` has no names or emails — but grouped by
**country × segment × gender**:

* 72 groups; **25** have fewer than 5 customers
* **5 groups contain exactly one person**

A group of one *is* one person. Defenses:

* **Minimize** — collect and share only what's needed
* **Aggregate** and **suppress** small groups (e.g. show "fewer than 5")
* **Restrict** access to the detail (views, privileges)

---

## Backup & Recovery

* **RPO** — how much data can we afford to lose? (since the last backup)
* **RTO** — how long can we be down while we restore?
* **Full backup** (e.g. nightly `mysqldump`) + the **change log** (binary log)
  → restore to any moment: **point-in-time recovery**
* **3-2-1 rule** — 3 copies, on 2 kinds of storage, 1 off-site

```
mysqldump -u root --single-transaction --set-gtid-purged=OFF isba_shop > isba_shop_backup.sql
```

`--single-transaction` = a consistent snapshot while the shop keeps writing.

---

# ✅ A Backup You Haven't Restored Isn't a Backup

Verified on this course's MySQL version:

* `mysqldump isba_shop` **without** the two flags → a 25.5 MB file, some
  warnings… and restoring it fails at line 24:
  `ERROR 3546: @@GLOBAL.GTID_PURGED cannot be changed`
* **With** the flags → restored into a **new** database in about 2.4 s:

| db | orders | order_items | revenue |
|---|---:|---:|---:|
| isba_shop | 100,000 | 300,000 | 193,700,546.13 |
| isba_shop_restore | 100,000 | 300,000 | 193,700,546.13 |

👉 Test restores regularly, **into a separate database**, and compare.

---

## When Someone Makes a Mistake

The clean-up job from Class Discussion 2:

```sql
DELETE FROM orders WHERE order_date < '2022-01-01';   -- meant 2020
```

| Safeguard | Effect here |
|---|---|
| **Foreign keys** | MySQL refused: `ERROR 1451` — orders still have items |
| **Preview** with `SELECT COUNT(*)` | 25,051 instead of 0 — stop! |
| **Transaction** | check the row count, then `ROLLBACK` |
| **Least privilege** | the job's account has no `DELETE` on `orders` |
| **Backup + log** | point-in-time recovery to just before the mistake |

---

# 🔁 Recap

* `EXPLAIN` / `EXPLAIN ANALYZE` show **how** a query runs — measure, don't guess
* **Indexes** turn scans into lookups for **selective** filters — at a cost
* **Least privilege**: one account per app or person, minimal `GRANT`s
* **Defense in depth**: parameters + privileges + encryption + audits
* **Governance**: owners, classification, measured quality, privacy
* **Backups** only count once you've **restored** one

---

# 🧪 Today's Labs

**Session 10 Lab A — Performance: query plans and indexes**
Read plans, measure a query, add an index, find a filter that can't use it,
and weigh what indexes cost.

**Session 10 Lab B — Security and governance** *(challenge)*
An analyst account, a privacy-preserving view, roles, `REVOKE` — and the
process that keeps access under control.

🎓 That completes the course material — next: the **Final Exam**.
