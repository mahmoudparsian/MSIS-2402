---

marp: true

title: MSIS-2402 - Week 2 - Subqueries, CTEs & Set Operations

theme: default

paginate: true

---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Week 2 (Part 2) — Decomposing Queries: Subqueries, CTEs & Set Operations

* One hard question → several easy steps

---

# Slide 2 — 🎯 Learning Objectives

By the end of today you can:

* Put a query **inside** another query (subqueries)
* Use `IN`, `EXISTS` and `NOT EXISTS` to filter by another table
* Write a **correlated** subquery
* Name your steps with `WITH` (**CTEs**)
* Attach a grand total with `CROSS JOIN`
* Combine result sets with `UNION`, `INTERSECT`, `EXCEPT`
* Spot two classic traps: `NOT IN` with `NULL`, and join **fan-out**

---

# Slide 3 — 🧠 Why Decompose?

Business questions often come in steps:

> *"Which months beat our average month?"*

1. Compute revenue **per month**
2. Compute the **average** of those months
3. Keep the months **above** it

👉 One `SELECT` can't do all three at once.
👉 Today: ways to **chain** queries together.

---

# Slide 4 — 📦 Today's Data

The shared retail database (`datasets/oltp_database/`):

| Table | Rows | Key columns |
|---|---:|---|
| `customers` | 1,000 | `customer_id`, `country`, `segment` |
| `orders` | 100,000 | `order_id`, `customer_id`, `store_id`, `order_date` |
| `order_items` | 300,000 | `order_id`, `product_id`, `sales_amount` |
| `products` | 2,000 | `product_id`, `category`, `price` |
| `payments` | 100,000 | `order_id`, `payment_amount` |
| `stores` | 50 | `store_id`, `store_type`, `country` |

Orders run from **2021-01-01** to **2024-12-31**.

---

# Slide 5 — Loading It in DuckDB

```sql
CREATE TABLE orders AS
SELECT * FROM read_csv_auto('datasets/oltp_database/orders.csv');
-- repeat for customers, order_items, products, payments, stores
```

(The Session 4 notebook already does this for you.)

---

# Slide 6 — 🔢 Scalar Subquery

A subquery that returns **one value** can be used like a number.

> *How many payments were larger than the average payment?*

```sql
SELECT COUNT(*) AS big_payments
FROM payments
WHERE payment_amount > (SELECT AVG(payment_amount) FROM payments);
```

| big_payments |
|---:|
| 49961 |

👉 The inner query runs first and returns **159.99**.
👉 You never type the number in — it updates when the data does.

---

# Slide 7 — ⚠️ Why Not Just `WHERE payment_amount > AVG(payment_amount)`?

```sql
-- ❌ Error: aggregate functions are not allowed in WHERE
SELECT COUNT(*) FROM payments
WHERE payment_amount > AVG(payment_amount);
```

* `WHERE` looks at **one row at a time**
* `AVG()` needs **all rows**

👉 The subquery computes the average **separately**, then `WHERE` compares
each row to it.

---

# Slide 8 — 📋 `IN` with a Subquery

A subquery that returns **one column of many rows** is a list.

> *How many orders were placed at **Online** stores?*

```sql
SELECT COUNT(*) AS online_orders
FROM orders
WHERE store_id IN (
    SELECT store_id
    FROM stores
    WHERE store_type = 'Online'
);
```

| online_orders |
|---:|
| 33906 |

👉 Read it as: *"keep orders whose store is **in** the list of online stores."*

---

# Slide 9 — `IN` vs. `JOIN`

Both answer the question. Which to use?

| | `IN (SELECT ...)` | `JOIN` |
|---|---|---|
| Need columns from the other table? | ❌ No | ✅ Yes |
| Can it duplicate rows? | ❌ Never | ⚠️ Yes, if the match isn't unique |
| Reads like | "is it in the list?" | "combine the tables" |

👉 Use `IN` when the other table is only a **filter**.

---

# Slide 10 — 🔍 `EXISTS` / `NOT EXISTS`

`EXISTS` asks: *"is there **at least one** matching row?"*

> *How many customers placed **no** orders in December 2024?*

```sql
SELECT COUNT(*) AS quiet_in_december
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
      AND o.order_date >= DATE '2024-12-01'
);
```

| quiet_in_december |
|---:|
| 119 |

---

# Slide 11 — 🧠 Reading `NOT EXISTS`

```sql
WHERE NOT EXISTS (
    SELECT 1 FROM orders AS o
    WHERE o.customer_id = c.customer_id   -- ← refers to the OUTER row
      AND o.order_date >= DATE '2024-12-01'
)
```

* For **each** customer `c`, look for a December order
* Found one → `EXISTS` is true → customer dropped
* Found none → customer kept

👉 `SELECT 1` is a convention: `EXISTS` only cares **whether** a row exists,
not what's in it.

💼 Business use: win-back campaigns, inactive accounts, churn lists.

---

# Slide 12 — 🔁 Correlated Subqueries

The subquery on the last slide mentioned `c.customer_id` from the **outer**
query. That makes it **correlated**: it is re-evaluated for each outer row.

> *Which product is the most expensive in **its own** category?*

```sql
SELECT p.category, p.product_id, p.price
FROM products AS p
WHERE p.price = (
    SELECT MAX(p2.price)
    FROM products AS p2
    WHERE p2.category = p.category   -- same category as the outer row
)
ORDER BY p.category;
```

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 13 — Correlated Subquery — Result

| category | product_id | price |
|---|---:|---:|
| Beauty | 600 | 499.93 |
| Clothing | 286 | 497.59 |
| Computers | 414 | 499.74 |
| Electronics | 1247 | 497.58 |
| Home | 1210 | 498.36 |
| Office | 822 | 497.32 |
| Sports | 439 | 499.24 |
| Toys | 673 | 499.70 |

👉 A plain subquery would give **one** maximum for all 2,000 products.
👉 The correlated one gives a maximum **per category**.

---

# Slide 14 — 🧱 Subquery in `FROM` (Derived Table)

A subquery can also act as a **temporary table**.

> *Which months of 2024 beat the average month?*

```sql
SELECT month, revenue
FROM (
    SELECT DATE_TRUNC('month', o.order_date) AS month,
           SUM(oi.sales_amount)              AS revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE YEAR(o.order_date) = 2024
    GROUP BY month
) AS monthly
WHERE revenue > ( /* ...the SAME subquery again, wrapped in AVG... */ );
```

⚠️ We need the monthly numbers **twice** — so we'd copy the whole subquery.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 15 — ✨ `WITH`: Common Table Expressions (CTEs)

Give the step a **name**, then use it as often as you like:

```sql
WITH monthly AS (
    SELECT DATE_TRUNC('month', o.order_date) AS month,
           SUM(oi.sales_amount)              AS revenue
    FROM orders AS o
    JOIN order_items AS oi ON oi.order_id = o.order_id
    WHERE YEAR(o.order_date) = 2024
    GROUP BY month
)
SELECT strftime(month, '%Y-%m') AS month,
       ROUND(revenue, 0)        AS revenue
FROM monthly
WHERE revenue > (SELECT AVG(revenue) FROM monthly)
ORDER BY month;
```

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 16 — CTE — Result

Average month in 2024: **4,008,173**

| month | revenue |
|---|---:|
| 2024-01 | 4,144,627 |
| 2024-03 | 4,037,588 |
| 2024-05 | 4,118,858 |
| 2024-07 | 4,086,981 |
| 2024-08 | 4,067,669 |
| 2024-10 | 4,189,741 |

👉 6 of 12 months beat the average.
👉 `monthly` is defined **once** and used **twice**.

---

# Slide 17 — 🧠 Why Analysts Love CTEs

* **Readable** — top to bottom, like a recipe
* **Named steps** — `monthly`, `per_customer`, `vip_total`...
* **Reusable** — refer to a step more than once
* **Debuggable** — run each step on its own to check it

Several CTEs: separate them with commas:

```sql
WITH step_one AS (...),
     step_two AS (SELECT ... FROM step_one ...)
SELECT ... FROM step_two;
```

👉 You'll use CTEs constantly in Week 3.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 18 — ✖️ A One-Row CTE + `CROSS JOIN`

> *What share of 2024 revenue did each category bring in?*

```sql
WITH by_category AS (
    SELECT oi.category, SUM(oi.sales_amount) AS revenue
    FROM order_items AS oi
    JOIN orders AS o ON o.order_id = oi.order_id
    WHERE YEAR(o.order_date) = 2024
    GROUP BY oi.category
),
grand_total AS (
    SELECT SUM(revenue) AS total FROM by_category   -- exactly ONE row
)
SELECT b.category,
       ROUND(b.revenue, 0)                    AS revenue,
       ROUND(100.0 * b.revenue / g.total, 2)  AS pct_of_total
FROM by_category AS b
CROSS JOIN grand_total AS g
ORDER BY pct_of_total DESC;
```

---

<style scoped>section { font-size: 23px; } pre, table { font-size: 19px; }</style>

# Slide 19 — `CROSS JOIN` — Result

| category | revenue | pct_of_total |
|---|---:|---:|
| Clothing | 6,584,540 | 13.69 |
| Toys | 6,424,155 | 13.36 |
| Office | 6,296,172 | 13.09 |
| Sports | 6,182,521 | 12.85 |
| … | … | … |

* `CROSS JOIN` pairs **every** row with **every** row — no `ON`
* Usually dangerous: 8 rows × a 1,000-row table = 8,000 rows!
* But `grand_total` has **one** row, so it just attaches the total to each
  of the 8 categories
* The 8 rounded shares add up to **99.99%** — rounding, not an error

---

# Slide 20 — ➕ Set Operations

Combine the **rows** of two queries that have the **same columns**:

| Operation | Keeps |
|---|---|
| `UNION` | rows in **either** (duplicates removed) |
| `UNION ALL` | rows in either (**duplicates kept**) |
| `INTERSECT` | rows in **both** |
| `EXCEPT` | rows in the first **but not** the second |

```sql
SELECT customer_id FROM orders
WHERE order_date >= DATE '2024-11-01' AND order_date < DATE '2024-12-01'
INTERSECT
SELECT customer_id FROM orders
WHERE order_date >= DATE '2024-12-01';
```

---

# Slide 21 — Set Operations on Real Customers

**November 2024 buyers** vs. **December 2024 buyers**:

| Operation | Customers | Business meaning |
|---|---:|---|
| `UNION` | 989 | Active in Nov **or** Dec |
| `UNION ALL` | 4,112 | ⚠️ One row per *order*, not per customer |
| `INTERSECT` | 753 | Bought in **both** months — repeat buyers |
| Nov `EXCEPT` Dec | 108 | Bought in Nov, **not** Dec — lapsing |
| Dec `EXCEPT` Nov | 128 | New or returning in Dec |

✅ Check: 753 + 108 + 128 = **989**

---

# Slide 22 — ⚠️ Trap 1: `NOT IN` and `NULL`

```sql
SELECT x FROM (VALUES (1), (2), (3)) AS t(x)
WHERE x NOT IN (SELECT y FROM (VALUES (1), (NULL)) AS u(y));
```

Result: **0 rows** 😱 — not `2, 3`.

* `2 NOT IN (1, NULL)` means `2 <> 1 AND 2 <> NULL`
* `2 <> NULL` is **unknown**, so the whole test is unknown → row dropped

```sql
-- ✅ NOT EXISTS ignores the NULL and returns 2, 3
WHERE NOT EXISTS (
    SELECT 1 FROM (VALUES (1), (NULL)) AS u(y) WHERE u.y = t.x
);
```

👉 Prefer `NOT EXISTS` when the list could contain `NULL`.

---

# Slide 23 — ⚠️ Trap 2: Join Fan-Out

Two orders, totals 100 and 50. Order 1 has **3** items, order 2 has 1.

```sql
SELECT SUM(o.total)
FROM ord AS o
JOIN items AS i ON i.order_id = o.order_id;
```

| right_total | fanned_out_total |
|---:|---:|
| 150 | **350** |

* Joining to `items` repeats order 1's row **3 times**
* `SUM(total)` then counts 100 three times

👉 Aggregate **before** you join (in a subquery or CTE), or sum the
table the number really lives in.

---

# Slide 24 — 🩹 `LEFT JOIN` + `COALESCE`

A `LEFT JOIN` keeps unmatched rows — with `NULL`s. `COALESCE` turns them
into a usable value:

```sql
WITH dec_orders AS (
    SELECT customer_id, COUNT(*) AS n
    FROM orders
    WHERE order_date >= DATE '2024-12-01'
    GROUP BY customer_id
)
SELECT COALESCE(d.n, 0) AS december_orders, COUNT(*) AS customers
FROM customers AS c
LEFT JOIN dec_orders AS d ON d.customer_id = c.customer_id
GROUP BY december_orders
ORDER BY december_orders;
```

---

# Slide 25 — `LEFT JOIN` + `COALESCE` — Result

| december_orders | customers |
|---:|---:|
| **0** | **119** |
| 1 | 280 |
| 2 | 250 |
| 3 | 182 |
| … | … |

👉 Same **119** as the `NOT EXISTS` query — two methods, one answer.

---

# Slide 26 — 🧠 Reasoning About Results

Before trusting a number, ask:

* **Grain:** one row per *what*? Customer? Order? Item?
* **Duplicates:** did a join multiply my rows?
* **Missing rows:** did an `INNER JOIN` silently drop some?
* **`NULL`s:** did `NOT IN` or `=` hide some rows?
* **Cross-check:** do two different methods agree? (119 = 119 ✅)

---

# Slide 27 — 🧭 Choosing a Tool

| You want to... | Use |
|---|---|
| Compare to one computed value | scalar subquery |
| Filter by membership in another table | `IN` / `EXISTS` |
| Find what's **missing** | `NOT EXISTS` (or `LEFT JOIN ... IS NULL`) |
| Compare each row to its own group | correlated subquery |
| Build an answer in steps | CTE (`WITH`) |
| Divide by a grand total | one-row CTE + `CROSS JOIN` |
| Combine or compare two lists | `UNION` / `INTERSECT` / `EXCEPT` |

---

# Slide 28 — 🧪 In-Class Exercise

Use a CTE and a scalar subquery:

1. In a CTE, count the orders per **store**.
2. List the stores with **more** orders than the average store,
   with their `store_type` and `country`.
3. How many are there? Which `store_type` appears most?

Bonus: rewrite step 1 as a derived table instead of a CTE.
Which version is easier to read?

---

# Slide 29 — 💬 Discussion

* When would you choose `NOT EXISTS` over `LEFT JOIN ... IS NULL`?
* A manager says "revenue doubled after we added the shipments table to the
  report." What would you check first?
* Why might `UNION ALL` be the *right* choice sometimes?

---

# Slide 30 — 🎯 Most Important Idea

> **Break a hard question into named steps — then check each step's grain.**

---

# Slide 31 — Today's Summary

* Scalar, `IN`, `EXISTS`, and correlated subqueries
* Derived tables and **CTEs** (`WITH`)
* A one-row CTE + `CROSS JOIN` for share-of-total
* `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT`
* `NOT IN` + `NULL`, and join fan-out
* `COALESCE` after a `LEFT JOIN`
* Cross-checking results with a second method

---

# Slide 32 — 🙌 End of Week 2

Questions?

---

Next week:

**A full operational database — `stores`, `payments`, `shipments` — and
window functions for ranking and running totals.**
