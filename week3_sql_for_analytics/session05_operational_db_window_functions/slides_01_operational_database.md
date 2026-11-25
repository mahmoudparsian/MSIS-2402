---
marp: true
title: MSIS-2402 - Week 3
theme: default
paginate: true
---

# Slide 1 — MSIS-2402
## Week 3 — Real Operational Databases

Today we move from simplified teaching datasets to a **full operational schema**.

---

# Slide 2 — Review

Week 1
Database concepts & SQL fundamentals

Week 2
Multiple tables & complex queries (joins, transaction analytics)

Week 3
SQL for data analytics — starting with **real operational databases**

---

# Slide 3 — Learning Goals

By the end of Week 3 students will:

• explore a real multi-table schema  
• analyze operational business data  
• perform multi-table joins  
• write analytical SQL queries  
• explore data quality issues  

---

# Slide 4 — Full Operational Schema

Tables used:

customers  
products  
stores  
orders  
order_items  
payments  
shipments

This resembles real production databases.

---

# Slide 5 — Customers Table

Example:

| customer_id | gender | country | segment | signup_date |
|---|---|---|---|---|
| 1 | Female | Germany | Consumer | 2021-09-01 |

Questions:

• Where do customers live?
• Which segments generate most orders?

---

# Slide 6 — Orders Table

orders

| order_id | customer_id | store_id | order_date |

Each row represents one order.

---

# Slide 7 — Order Items Table

order_items

| order_item_id | order_id | product_id | quantity | category | price | sales_amount |

Each order can contain multiple items.

---

# Slide 8 — Products Table

products

| product_id | category | price |

This allows product analytics.

---

# Slide 9 — Stores Table

stores

| store_id | store_type | country |

Stores are one of three types: `Online` (17), `Retail` (14), `Warehouse` (19).

---

# Slide 10 — Payments Table

payments

| payment_id | order_id | payment_method | payment_date | payment_amount |

Allows financial analysis.

---

# Slide 11 — Shipments Table

shipments

| shipment_id | order_id | carrier | shipment_date | delivery_date |

Used for logistics analysis.

---

# Slide 12 — Exploring the Data

Load each table once, from this deck's folder (`session05_operational_db_window_functions/`):
`CREATE OR REPLACE TABLE orders AS SELECT * FROM read_csv_auto('../../datasets/oltp_database/orders.csv');`
— the same for the other six (`notebook_03_full_database_exploration.py` does it for you).

Example query:

```sql
SELECT COUNT(*) AS num_orders
FROM orders;
```

How many orders exist? → **100,000** (2021-01-01 to 2024-12-31).

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 13 — Orders by Country

```sql
SELECT c.country,
       COUNT(o.order_id) AS num_orders
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY num_orders DESC;
```

| country | num_orders |
|---|---:|
| Germany | 19,621 |
| Australia | 17,702 |
| USA | 17,069 |
| France | 16,215 |
| UK | 15,835 |
| Canada | 13,558 |

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 14 — Revenue by Product Category

```sql
SELECT p.category,
       ROUND(SUM(oi.sales_amount), 0) AS revenue
FROM order_items oi
JOIN products p
  ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC;
```

Clothing leads with **26,607,218**, Home is last with **22,100,912**: all 8 categories are within ±10% of each other.

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 15 — Revenue by Store

```sql
SELECT s.store_type,
       ROUND(SUM(oi.sales_amount), 0) AS revenue
FROM stores s
JOIN orders o ON s.store_id = o.store_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_type
ORDER BY revenue DESC;
```

| store_type | revenue |
|---|---:|
| Warehouse | 73,222,434 |
| Online | 65,807,138 |
| Retail | 54,670,974 |

👉 Warehouse leads partly because there are more of them (19 stores vs 17 and 14): compare **per store** too.

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 16 — Payment Method Analysis

```sql
SELECT payment_method,
       COUNT(*)                         AS payments,
       ROUND(SUM(payment_amount), 0)    AS amount
FROM payments
GROUP BY payment_method
ORDER BY amount DESC;
```

Four methods, each about 25,000 payments and about 4.0 million: PayPal 4,033,088 · Gift Card 4,010,471 ·
Credit Card 3,984,269 · Bank Transfer 3,971,141.

---

# Slide 17 — Shipping Analysis

```sql
SELECT carrier,
       COUNT(*) AS shipments
FROM shipments
GROUP BY carrier
ORDER BY shipments DESC;
```

UPS 25,108 · FedEx 25,028 · USPS 25,003 · DHL 24,861 (one shipment per order).

---

# Slide 18 — Data Quality Checks

Check for missing values:

```sql
SELECT *
FROM orders
WHERE customer_id IS NULL;
```

(This returns 0 rows: a normal, healthy outcome for a data quality check, not a sign the query is broken.)

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 19 — Data Quality: Do Two Tables Agree?

A deeper check: does each order's **payment** equal the value of its **items**?

```sql
SELECT ROUND((SELECT SUM(payment_amount) FROM payments), 0)  AS total_paid,
       ROUND((SELECT SUM(sales_amount)   FROM order_items), 0) AS total_items;
```

| total_paid | total_items |
|---:|---:|
| 15,998,970 | 193,700,546 |

⚠️ They don't agree: in this teaching dataset `payments` was generated **independently** of the items
(payments are 20–300 each). Lesson: use `sales_amount` for **revenue**, use `payments` only for
payment questions (method, timing), and **always reconcile two tables before combining their numbers**.

---

# Slide 20 — Large Dataset Thinking

Real databases contain:

• millions of rows
• many tables
• many relationships

SQL allows us to explore these efficiently.

---

# Slide 21 — Week 3 Summary

Today we learned:

• working with operational schemas  
• multi-table joins across many tables  
• analytics queries  
• data exploration and quality checks

Next: window functions (`slides_02_window_functions_ranking.md`), then advanced SQL analytics
in Session 6
