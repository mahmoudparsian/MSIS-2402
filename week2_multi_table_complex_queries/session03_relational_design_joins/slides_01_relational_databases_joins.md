---
marp: true
title: MSIS-2402 - Week 2
theme: default
paginate: true
---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Week 2 — Relational Databases and JOINs

Santa Clara University

---

# Slide 2 — Review of Week 1

Last week we learned:

• What a database is  
• What a relational database is  
• What an RDBMS is  
• What SQL is  
• Basic SQL queries using one table
• Summarizing data with `GROUP BY`, `HAVING`, and aggregate functions

Example:

```sql
SELECT *
FROM sales;
```

---

# Slide 3 — Learning Goals for Week 2

By the end of Week 2 students will:

• understand relationships between tables  
• understand primary keys and foreign keys  
• write SQL JOIN queries  
• combine information from multiple tables  
• perform simple aggregations using GROUP BY

---

# Slide 4 — Why Multiple Tables?

Real business databases rarely store everything in one table.

Instead we separate data into logical tables.

Example:

Customers  
Orders  
Products

This prevents data duplication.

---

# Slide 5 — Example Tables

customers

| customer_id | country |
|---|---|
| 1 | Germany |
| 2 | Canada |

orders

| order_id | customer_id |
|---|---|
| 101 | 1 |
| 102 | 2 |

---

# Slide 6 — Primary Keys

A **primary key** uniquely identifies a row.

Example:

customers

| customer_id | country |
|---|---|
| 1 | Germany |
| 2 | Canada |

customer_id is the primary key.

---

# Slide 7 — Foreign Keys

A **foreign key** references another table.

Example:

orders

| order_id | customer_id |
|---|---|
| 101 | 1 |
| 102 | 2 |

customer_id refers to the customers table.

---

# Slide 8 — What Is a JOIN?

A JOIN combines rows from two tables using a related column.

Example:

customers.customer_id = orders.customer_id

This lets us connect customers with their orders.

---

# Slide 9 — Example JOIN Query

```sql
SELECT *
FROM customers
JOIN orders
  ON customers.customer_id = orders.customer_id;
```

This combines both tables: each order is paired with **its** customer.
`JOIN` means `INNER JOIN`: only rows that have a match in **both** tables are kept.

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 10 — Week 2 Dataset

Three tables in `data/`. Load them from this deck's folder (`session03_relational_design_joins/`):

```sql
CREATE OR REPLACE TABLE customers AS SELECT * FROM read_csv_auto('data/customers.csv');  -- 200 rows
CREATE OR REPLACE TABLE orders    AS SELECT * FROM read_csv_auto('data/orders.csv');     -- 800 rows
CREATE OR REPLACE TABLE products  AS SELECT * FROM read_csv_auto('data/products.csv');   -- 100 rows
```

| Table | Columns |
|---|---|
| `customers` | `customer_id` (PK), `gender`, `country`, `segment`, `signup_date` |
| `orders` | `order_id` (PK), `customer_id` (FK → customers), `store_id`, `order_date` |
| `products` | `product_id` (PK), `category`, `price` |

---

# Slide 11 — JOIN Example

Find all orders with customer information.

```sql
SELECT *
FROM orders
JOIN customers
  ON orders.customer_id = customers.customer_id;
```

---

# Slide 12 — Selecting Useful Columns

```sql
SELECT orders.order_id, 
       customers.country
FROM orders
JOIN customers
  ON orders.customer_id = customers.customer_id;
```

---

# Slide 13 — GROUP BY

GROUP BY summarizes data.

Example:

```sql
SELECT country,
       COUNT(*) AS customers
FROM customers
GROUP BY country
ORDER BY customers DESC, country;
```

| country | customers |
|---|---:|
| UK | 43 |
| Germany | 42 |
| Australia | 34 |
| France | 28 |
| USA | 27 |
| Canada | 26 |

---

# Slide 14 — Aggregation Functions

Common functions:

COUNT()  
SUM()  
AVG()  
MAX()  
MIN()

Example:

```sql
SELECT COUNT(*)
FROM orders;
```

---

# Slide 15 — GROUP BY Example

Orders per customer

```sql
SELECT customer_id, 
       COUNT(*)
FROM orders
GROUP BY customer_id;
```

---

# Slide 16 — JOIN + GROUP BY

Orders per country

```sql
SELECT c.country, 
       COUNT(o.order_id)
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id
GROUP BY c.country;
```

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 17 — Business Insight Example

Which countries generate the most orders?

```sql
SELECT c.country,
       COUNT(o.order_id) AS total_orders
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id
GROUP BY c.country
ORDER BY total_orders DESC, c.country;
```

| country | total_orders |
|---|---:|
| UK | 40 |
| Germany | 31 |
| France | 23 |
| Canada | 21 |
| Australia | 20 |
| USA | 14 |

👉 These add up to **149**, but `orders` has **800** rows. Where did the others go? (Class Discussion, Q4.)

---

<style scoped>section { font-size: 21px; } pre, pre code, table { font-size: 16px; }</style>

# Slide 18 — Another Example

Average product price by category

```sql
SELECT category,
       ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
ORDER BY avg_price DESC;
```

| category | avg_price |
|---|---:|
| Computers | 330.81 |
| Electronics | 321.29 |
| Sports | 317.31 |
| Office | 306.39 |
| Beauty | 274.67 |
| Clothing | 245.15 |
| Toys | 201.99 |
| Home | 200.12 |

---

# Slide 19 — Why JOINs Are Powerful

JOINs allow us to:

• combine related tables  
• answer complex questions  
• analyze relationships

Without JOINs we could not analyze relational data.

---

# Slide 20 — Week 2 Summary

Today we learned:

• relational table relationships  
• primary keys and foreign keys  
• SQL JOIN  
• GROUP BY  
• aggregation functions

Next (Session 4):

More complex joins and multi-table queries.
