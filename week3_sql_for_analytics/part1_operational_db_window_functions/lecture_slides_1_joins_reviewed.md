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

| customer_id | country | segment |
|---|---|---|
| 1 | Germany | Consumer |

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

| order_item_id | order_id | product_id | quantity | sales_amount |

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

Stores can be:

• online  
• retail  
• warehouse  

---

# Slide 10 — Payments Table

payments

| payment_id | order_id | payment_method | payment_amount |

Allows financial analysis.

---

# Slide 11 — Shipments Table

shipments

| shipment_id | order_id | carrier | shipment_date |

Used for logistics analysis.

---

# Slide 12 — Exploring the Data

Example query:

```sql
SELECT COUNT(*)
FROM orders;
```

How many orders exist?

---

# Slide 13 — Orders by Country

```sql
SELECT c.country, 
       COUNT(o.order_id)
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id
GROUP BY c.country;
```

---

# Slide 14 — Revenue by Product Category

```sql
SELECT p.category, 
       SUM(oi.sales_amount)
FROM order_items oi
JOIN products p
  ON oi.product_id = p.product_id
GROUP BY p.category;
```

---

# Slide 15 — Revenue by Store

```sql
SELECT s.store_type, 
       SUM(oi.sales_amount)
FROM stores s
JOIN orders o ON s.store_id = o.store_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_type;
```

---

# Slide 16 — Payment Method Analysis

```sql
SELECT payment_method, 
       SUM(payment_amount)
FROM payments
GROUP BY payment_method;
```

---

# Slide 17 — Shipping Analysis

```sql
SELECT carrier, 
       COUNT(*)
FROM shipments
GROUP BY carrier;
```

---

# Slide 18 — Data Quality Checks

Check for missing values:

```sql
SELECT *
FROM orders
WHERE customer_id IS NULL;
```

(Our dataset is clean — this returns 0 rows. That's a normal, healthy
outcome for a data quality check, not a sign the query is broken.)

---

# Slide 19 — Large Dataset Thinking

Real databases contain:

• millions of rows
• many tables
• many relationships

SQL allows us to explore these efficiently.

---

# Slide 20 — Week 3 Summary

Today we learned:

• working with operational schemas  
• multi-table joins across many tables  
• analytics queries  
• data exploration and quality checks

Next: window functions (Deck 2), then advanced SQL analytics
in Part 2, later this week
