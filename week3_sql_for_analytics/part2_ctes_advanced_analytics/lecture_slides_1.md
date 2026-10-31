---
marp: true
title: MSIS-2402 - Week 3
theme: default
paginate: true
---

# Slide 1 — MSIS-2402
## Week 3 — Advanced SQL for Business Analytics

The last of the course's three SQL weeks

---

# Slide 2 — Course Journey

Week 1 — Database concepts & SQL fundamentals  
Week 2 — Multiple tables & complex queries  
Week 3 — SQL for data analytics (Part 1: operational data & window functions; **Part 2: advanced SQL**)  
Week 4 — Web database applications  
Week 5 — Modern data systems & database management

---

# Slide 3 — Learning Goals

By the end of Week 3 students will:

• use CTEs (WITH queries)  
• use window functions  
• perform ranking analytics  
• compute running totals  
• solve complex business analytics queries

---

# Slide 4 — Complex Business Questions

Businesses often ask questions like:

• Who are the top customers?  
• Which products are trending?  
• What are the top sales each month?  
• Which stores outperform others?

Advanced SQL helps answer these.

---

# Slide 5 — Common Table Expressions (CTE)

CTE allows us to create temporary result sets.

Example:

```sql
WITH customer_orders AS (
    SELECT customer_id, 
           COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_orders;
```

---

# Slide 6 — Why CTEs Are Useful

Benefits:

• improves readability  
• simplifies complex queries  
• allows step‑by‑step query building

---

# Slide 7 — CTE Example

Find our most frequent customers (100,000 orders / 1,000 customers, so
each customer has 71–133 orders — `> 120` picks out the top tier):

```sql
WITH customer_orders AS (
    SELECT customer_id, 
           COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT *
FROM customer_orders
WHERE order_count > 120;
```

---

# Slide 8 — Window Functions

Window functions perform calculations across rows without collapsing them.

Example:

ROW_NUMBER()

---

# Slide 9 — ROW_NUMBER Example

Find order-item ranking by sales.

```sql
SELECT order_id,
       sales_amount,
       ROW_NUMBER() OVER (ORDER BY sales_amount DESC) AS rnk
FROM order_items;
```

---

# Slide 10 — RANK Example

```sql
SELECT product_id,
       SUM(sales_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS product_rank
FROM order_items
GROUP BY product_id;
```

---

# Slide 11 — Partitioning

Partitioning groups rows before applying window functions — unlike
`GROUP BY`, no rows are collapsed.

Example:

```sql
ROW_NUMBER() OVER (
    PARTITION BY category
    ORDER BY sales_amount DESC
)
```

---

<style scoped>section { font-size: 21px; } pre, table { font-size: 17px; }</style>

# Slide 12 — Top Product per Category

Combining a CTE (Slide 5) with `PARTITION BY` (Slide 11):

```sql
WITH product_sales AS (
    SELECT p.category,
           p.product_id,
           SUM(oi.sales_amount) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_id
)
SELECT *
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
              PARTITION BY category
              ORDER BY revenue DESC
           ) AS rn
    FROM product_sales
) t
WHERE rn = 1;
```

One row per category — its single best-selling product.

---

# Slide 13 — Running Totals

Calculate cumulative revenue. `order_date` lives on `orders`, not
`order_items` — join first, aggregate revenue per day, *then* apply the
running-total window function:

```sql
SELECT order_date,
       SUM(daily_revenue) OVER (ORDER BY order_date) AS running_revenue
FROM (
    SELECT o.order_date,
           SUM(oi.sales_amount) AS daily_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY o.order_date
) t;
```

---

# Slide 14 — Moving Averages

Example — a trailing 7-day average (today + 6 prior rows):

```sql
AVG(sales_amount) OVER (
    ORDER BY order_date
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
)
```

---

# Slide 15 — Business Insight Example

Top 10 customers by revenue.

```sql
SELECT customer_id,
       SUM(sales_amount) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 10;
```

---

# Slide 16 — Ranking Customers

```sql
SELECT customer_id,
       SUM(sales_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY customer_id;
```

---

<style scoped>section { font-size: 21px; } pre, table { font-size: 17px; }</style>

# Slide 17 — Category Sales Ranking

`order_items` **and** `products` both have a `category` column — leaving
it unqualified is ambiguous:

```sql
SELECT category,   -- ❌ which table's category?
       SUM(sales_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY category;
```

```console
Binder Error:
Ambiguous reference to column name "category"
(use: "oi.category" or "p.category")
```

✅ Qualify it:

```sql
SELECT p.category,
       SUM(oi.sales_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(oi.sales_amount) DESC) AS rnk
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category;
```

---

# Slide 18 — SQL Analytics Pattern

```sql
SELECT dimension,
       metric,
       RANK() OVER (ORDER BY metric DESC)
FROM dataset;
```

This pattern — dimension, metric, rank — appears constantly in analytics.

---

# Slide 19 — Real Analytics Workflow

1. Join tables  
2. Aggregate metrics  
3. Rank results  
4. Extract insights

---

# Slide 20 — SQL Summary (Weeks 1–3)

You can now:

• query relational databases  
• join multiple tables  
• perform analytics with SQL  
• build complex analytical queries

Next: Weeks 4–5 put databases in context — web database
applications, then modern data systems and database management.
