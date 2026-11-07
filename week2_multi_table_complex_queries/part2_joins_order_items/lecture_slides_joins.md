---

marp: true

title: MSIS-2402 - Week 2 - Joins & Transaction Analytics

theme: default

paginate: true

---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Week 2 — Multi-Table Queries & Transaction Analysis

* From Isolated Tables → Integrated Insights

---

# Slide 2 — Review of Part 1

Earlier this week (Part 1) we learned:

* relational databases
* primary keys
* foreign keys
* `JOIN` operations
* `GROUP BY` and aggregation

```sql
SELECT c.country, 
       COUNT(o.order_id)
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id
GROUP BY c.country;
```

---

# Slide 3 — 🎯 Learning Objectives

By the end of today:

* Understand why joins exist
* Use `INNER JOIN`, `LEFT JOIN`, and `FULL OUTER JOIN`
* Write a join with `USING` when the key names match
* Avoid common join mistakes
* Combine data for business insights

---

# Slide 4 — 🧠 The Big Problem

Real-world data is **NOT** in one table.

---

# Slide 5 — 📦 Today's Data Model

* `customers`
* `products`
* `sales`

👉 Three separate tables (`data/customers.csv`, `data/products.csv`,
`data/sales.csv`)

---

# Slide 6 — ❓ Why Split Data Into Many Tables?

* Reduce duplication
* Improve efficiency
* Maintain consistency

---

# Slide 7 — 💥 The Challenge

Each table alone is incomplete.

💼 Business question:

**"Who bought what product?"**

❌ Can we answer this with one table alone? → **No.**

---

# Slide 8 — 🔥 Solution: JOIN

* `JOIN` combines tables based on a relationship
* Relationships are defined by primary keys (PK) and foreign keys (FK)

---

# Slide 9 — 🔗 `INNER JOIN`

```sql
SELECT *
FROM sales s
JOIN customers c
  ON s.customer_id = c.customer_id;
```

* Matches rows where the key values are equal
* Combines columns from both tables

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# Slide 10 — ⚠️ The Most Common Mistake

A join with the **wrong** condition:

```sql
SELECT s.order_id, 
       s.customer_id AS actual_customer_id,
       c.customer_id AS matched_customer_id, 
       c.customer_name
FROM sales s
JOIN customers c
  ON s.order_id = c.customer_id    -- 🚨 wrong column!
ORDER BY s.order_id;
```

⚠️ This **runs without error** — DuckDB has no way to know `order_id`
wasn't meant to equal `customer_id`. It silently returns 60 rows of
**nonsense matches** (real correct join: 300 rows).

| order_id | actual_customer_id | matched_customer_id | customer_name |
|---|---|---|---|
| 1 | 11 | 1 | Customer_1 |
| 2 | 57 | 2 | Customer_2 |

👉 Order #1's real customer is #11 — not Customer_1!

---

# Slide 11 — 🔍 Teaching Moment

Ask students:

👉 "Does this output make sense?"

The join condition — not the syntax — determines whether a query is
**correct**, not just whether it **runs**.

---

# Slide 12 — ✅ Correct Join

```sql
SELECT *
FROM sales s
JOIN customers c
  ON s.customer_id = c.customer_id;   -- ✅ matching keys
```

300 rows — one per sale, correctly matched to its customer.

🧠 **Key idea:** the join condition defines correctness, not just the
`JOIN` keyword.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 13 — ✂️ Shortcut: `USING`

When the key column has the **same name** in both tables:

```sql
SELECT *
FROM sales s
JOIN customers c
  USING (customer_id);   -- same as ON s.customer_id = c.customer_id
```

| | `ON` | `USING` |
|---|:---:|:---:|
| Rows | 300 | 300 |
| `customer_id` columns in `SELECT *` | **2** | **1** |

👉 Same rows, shorter to write, and the key appears only once.
⚠️ Only works when the names match — otherwise use `ON`.

---

# Slide 14 — 🔗 Multi-Table Join

Find customers who bought a Laptop:

```sql
SELECT c.customer_name, 
       p.product
FROM sales s
JOIN customers c
  ON s.customer_id = c.customer_id
JOIN products p
  ON s.product_id = p.product_id
WHERE p.product = 'Laptop';
```

(Our catalog has just 4 products — Laptop, Phone, Tablet, Watch —
intentionally simplified so you can focus on the JOIN mechanics.)

---

# Slide 15 — 💼 Business Meaning

"Which customers bought a Laptop?"

```
p.product = 'Laptop'
=>
Customer_3, Customer_22, Customer_55, Customer_4, Customer_12, ...
```

---

# Slide 16 — 🔥 Derived Insight

```sql
SELECT s.order_id, 
       p.product, 
       s.quantity, 
       p.price,
       s.quantity * p.price AS total_value
FROM sales s
JOIN products p
  ON s.product_id = p.product_id;
```

💼 Business question: **"What is the revenue per transaction?"**

---

# Slide 17 — 🔍 `LEFT JOIN`

```sql
SELECT c.customer_name, 
       s.order_id
FROM customers c
LEFT JOIN sales s
  ON c.customer_id = s.customer_id;
```

* Keeps **ALL** rows from the left table (`customers`)
* Fills unmatched `sales` columns with `NULL`

---

# Slide 18 — 🧠 A Small Illustration

3 customers, 3 sales rows — Cara has never bought anything:

| customer_name | order_id |
|---|---|
| Alice | 102 |
| Alice | 101 |
| Bob   | 103 |
| Cara  | `NULL` |

```sql
SELECT c.customer_name
FROM customers c
LEFT JOIN sales s
  ON c.customer_id = s.customer_id
WHERE s.order_id IS NULL;
```

👉 **"Who never purchased?"**

---

# Slide 19 — 💼 Real Use Case

* Customer churn
* Inactive users
* Target marketing

⚠️ Run this same query against our real `data/customers.csv` +
`data/sales.csv` (60 customers, 300 sales) and it returns **0 rows** —
every customer here has purchased at least once. That's not a bug: a
correct `LEFT JOIN` + `IS NULL` check can legitimately report "nobody's
missing." Try inserting a customer with no matching sales row to see a
non-empty result.

---

# Slide 20 — 🔄 `FULL OUTER JOIN`

* `INNER JOIN` → only rows that match in **both** tables
* `LEFT JOIN` → **all** rows from the left table
* `FULL OUTER JOIN` → **all** rows from **both** tables;
  `NULL` wherever the other side has no match

💼 Use it to **reconcile two lists**: CRM vs. billing, orders vs. shipments,
this month's customers vs. last month's.

---

<style scoped>section { font-size: 24px; } pre { font-size: 20px; }</style>

# Slide 21 — Example: CRM vs. Billing

```sql
CREATE OR REPLACE TABLE crm_customers AS
SELECT * FROM (VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Cara'), (4, 'Dev'))
    AS t(customer_id, name);

CREATE OR REPLACE TABLE billing_accounts AS
SELECT * FROM (VALUES (2, 'Basic'), (3, 'Pro'), (5, 'Pro'))
    AS t(customer_id, plan);

SELECT c.customer_id AS crm_id,
       c.name,
       b.customer_id AS billing_id,
       b.plan
FROM crm_customers AS c
FULL OUTER JOIN billing_accounts AS b
  ON c.customer_id = b.customer_id
ORDER BY crm_id, billing_id;
```

---

# Slide 22 — Example: CRM vs. Billing (cont.)

| crm_id | name | billing_id | plan |
|---:|---|---:|---|
| 1 | Alice | `NULL` | `NULL` |
| 2 | Bob | 2 | Basic |
| 3 | Cara | 3 | Pro |
| 4 | Dev | `NULL` | `NULL` |
| `NULL` | `NULL` | 5 | Pro |

* Alice and Dev are in the CRM but have **no billing account**
* Customer 5 is **billed** but **not in the CRM**

👉 A `LEFT JOIN` from either side would miss one of these problems.

---

<style scoped>section { font-size: 24px; } pre { font-size: 20px; }</style>

# Slide 23 — Show Only the Problems

```sql
SELECT c.customer_id AS crm_id,
       b.customer_id AS billing_id,
       CASE
           WHEN b.customer_id IS NULL THEN 'missing in billing'
           ELSE 'missing in CRM'
       END AS problem
FROM crm_customers AS c
FULL OUTER JOIN billing_accounts AS b
  ON c.customer_id = b.customer_id
WHERE c.customer_id IS NULL
   OR b.customer_id IS NULL
ORDER BY crm_id, billing_id;
```

| crm_id | billing_id | problem |
|---:|---:|---|
| 1 | `NULL` | missing in billing |
| 4 | `NULL` | missing in billing |
| `NULL` | 5 | missing in CRM |

---

<style scoped>section { font-size: 24px; } pre { font-size: 20px; }</style>

# Slide 24 — ⚠️ MySQL Has No `FULL OUTER JOIN`

In MySQL (Weeks 4–5) it is a syntax error (`ERROR 1064`).
Combine two `LEFT JOIN`s — one from each side — with `UNION`:

```sql
SELECT c.customer_id AS crm_id, b.customer_id AS billing_id
FROM crm_customers AS c
LEFT JOIN billing_accounts AS b ON c.customer_id = b.customer_id
UNION
SELECT c.customer_id AS crm_id, b.customer_id AS billing_id
FROM billing_accounts AS b
LEFT JOIN crm_customers AS c ON c.customer_id = b.customer_id;
```

👉 Same 5 rows as the `FULL OUTER JOIN`. `UNION` is covered in this week's
next deck (subqueries, CTEs, and set operations).

---

# Slide 25 — 🔥 Join + Aggregation

```sql
SELECT c.customer_name,
       SUM(s.quantity * p.price) AS revenue
FROM sales s
JOIN customers c
  ON s.customer_id = c.customer_id
JOIN products p
  ON s.product_id = p.product_id
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 10;
```

Top result (real data): Customer_30 — $24,400.

---

# Slide 26 — 🧠 Key Transition

## Joins → Aggregation

👉 This is real analytics.

---

# Slide 27 — 📊 Business Insight

* Top customers
* Revenue concentration
* High-value segments

---

# Slide 28 — ⚠️ Another Common Mistake

Forgetting `GROUP BY` after a join that mixes aggregate and
non-aggregate columns:

```sql
SELECT c.customer_name, SUM(s.quantity * p.price) AS revenue
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN products p ON s.product_id = p.product_id;
-- ❌ missing GROUP BY c.customer_name
```

```console
Binder Error:
column "customer_name" must appear in the GROUP BY clause
or must be part of an aggregate function.
```

---

# Slide 29 — 🧪 In-Class Exercise

Write queries for:

1. customer + product + quantity, for every sale
2. `total_value` per sale (`quantity * price`)
3. customers with no purchases
4. top 5 customers by revenue

---

# Slide 30 — 💬 Discussion

Ask:

* Who are our top customers?
* Are a few customers driving most of the revenue?
* What strategy would you suggest?

---

# Slide 31 — 🔥 Advanced Thinking

👉 Pareto Principle:

* Roughly 20% of customers → 80% of revenue

---

# Slide 32 — 🎯 Most Important Idea (So Far)

SQL integrates data across tables → enables insight.

---

# Slide 33 — 📦 A Bigger, Real-World Dataset

Everything so far used a small teaching table (`sales`, 300 rows).

Real operational systems split a "sale" into **two** tables:

* `orders` — one row per checkout
* `order_items` — one row **per line item** within an order

We'll now use the shared OLTP dataset (`datasets/oltp_database/`) — the
same one Week 3 completes with `stores`, `payments`, and `shipments`. From
this folder, load it with `read_csv_auto('../../datasets/oltp_database/orders.csv')`
(and the same for each table) — `notebook_3_joins_marimo.py` does it for you.

---

# Slide 34 — Slide — Real Retail Data Model

Retail systems often store data in multiple tables:

* `customers`
* `orders`
* `order_items`
* `products`

This design avoids data duplication and enables detailed analytics.

---

# Slide 35 — Transaction Tables

**`orders`**:

| `order_id` | `customer_id` | `store_id` | `order_date` |
|---|---|---|---|

**`order_items`**:

| `order_item_id` | `order_id` | `product_id` | `quantity` | `category` | `price` | `sales_amount` |
|---|---|---|---|---|---|---|

Each order can contain multiple items.

---

# Slide 36 — Product Table

**`products`**:

| `product_id` | `category` | `price` |
|---|---|---|

This table stores product attributes.

---

# Slide 37 — Understanding Relationships

```
orders → order_items
order_items → products
orders → customers
```

This lets us answer questions about:

* customer behavior
* product performance
* revenue patterns

---

# Slide 38 — Example Join (Orders + Items)

```sql
SELECT *
FROM orders o
JOIN order_items oi
  ON o.order_id = oi.order_id;
```

Shows which items belong to each order.

---

# Slide 39 — Join with Products

```sql
SELECT *
FROM order_items oi
JOIN products p
  ON oi.product_id = p.product_id;
```

Connects sales line items to product information.

---

# Slide 40 — Multi-Table Join

```sql
SELECT *
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;
```

Now we can analyze sales by product.

---

# Slide 41 — Sales by Category

```sql
SELECT p.category, 
       SUM(oi.sales_amount) AS total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;
```

This calculates revenue by category.

---

# Slide 42 — Orders per Customer

```sql
SELECT customer_id, 
       COUNT(order_id) AS num_orders
FROM orders
GROUP BY customer_id;
```

Shows customer purchasing frequency.

---

# Slide 43 — Top Selling Categories

```sql
SELECT p.category, 
       SUM(oi.sales_amount) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

---

# Slide 44 — Average Order-Item Size

```sql
SELECT AVG(sales_amount) AS avg_line_item_value
FROM order_items;
```

Shows the average value of a single line item (not a whole order).

---

# Slide 45 — Customer Order Activity

```sql
SELECT c.country, 
       COUNT(o.order_id) AS num_orders
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.country;
```

---

# Slide 46 — Revenue by Country

```sql
SELECT c.country, 
       SUM(oi.sales_amount) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.country;
```

---

# Slide 47 — Top Products by Revenue

```sql
SELECT p.product_id, 
       SUM(oi.sales_amount) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10;
```

---

# Slide 48 — Business Insights

Using SQL we can now answer:

* Which product categories sell the most?
* Which customers order the most?
* Which countries generate the most revenue?

---

# Slide 49 — Common Query Pattern

```sql
SELECT dimension, 
       AGG(metric)
FROM table_a
JOIN table_b ON table_a.key = table_b.key
GROUP BY dimension
ORDER BY metric DESC;
```

This pattern — join, then group, then order — appears constantly in
business analytics.

---

# Slide 50 — Week 2 Summary

Today we learned:

* `INNER JOIN`, `LEFT JOIN`, and `FULL OUTER JOIN` (reconciling two lists)
* `USING` as a shortcut for `ON` when the key names match
* why the join condition (not just the `JOIN` keyword) determines
  correctness
* multi-table joins across a bigger, real transaction schema
* `SUM`, `COUNT`, `AVG` combined with joins
* business insight queries (top customers, revenue by category/country)

---

# Slide 51 — ➡️ Next: Decomposing Queries

Questions?

---

Next deck (same session):

**Subqueries, CTEs (`WITH`) and set operations —
`lecture_slides_subqueries_ctes_set_ops.md`.**
