---
marp: true
title: MSIS-2402 - Week 1 (Part 2) - Aggregation & KPIs
theme: default
paginate: true
---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Week 1 (Part 2) — Aggregation & KPIs

From Rows → Metrics → Decisions

---

# Slide 2 — Learning Objectives

By the end of today:

* Use aggregate functions (`SUM`, `COUNT`, `AVG`)
* Understand `GROUP BY`
* Distinguish `WHERE` vs `HAVING`
* Think in business metrics (KPIs)

---

# Slide 3 — Key Shift

Part 1:

👉 Look at rows

Part 2:

👉 Summarize data

---

# Slide 4 — Business Reality

Executives don't ask:

❌ "Show me all transactions"

They ask:

✅ "What is total revenue?"

✅ "Which market performs best?"

---

# Slide 5 — Aggregate Functions

Core functions:

* `COUNT()`
* `SUM()`
* `AVG()`

Dataset for today: the `sales` table (`data/sales_dataset.csv`) —
`order_id, country, product, price, quantity, sales_amount`.

---

# Slide 6 — `COUNT()`

```sql
SELECT COUNT(*) AS total_transactions
FROM sales;
```

Business meaning:

"How many transactions do we have?"

---

# Slide 7 — `SUM()`

```sql
SELECT SUM(sales_amount) AS total_revenue
FROM sales;
```

Business meaning:

"What is total revenue?"

---

# Slide 8 — `AVG()`

```sql
SELECT AVG(price) AS avg_price
FROM sales;
```

Business meaning:

"What is the average price?"

---

# Slide 9 — ⚠️ Important Limitation

`COUNT`/`SUM`/`AVG` alone give:

👉 ONE number for the whole table

But businesses need:

👉 A breakdown by category (country, product, ...)

---

# Slide 10 — `GROUP BY` (Core Concept)

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
ORDER BY revenue DESC;
```

---

# Slide 11 — What `GROUP BY` Does

* Splits data into groups (one group per distinct `country`)
* Computes the aggregate (`SUM`) separately, per group

Business question:

"What is revenue, by country?"

---

# Slide 12 — Interpretation

Output (real data, `data/sales_dataset.csv`):

| country | revenue  |
|---------|---------:|
| Germany | 98,630   |
| UK      | 95,928   |
| Canada  | 93,016   |
| USA     | 76,647   |

👉 Compare performance across markets

---

# Slide 13 — ⚠️ Common Mistake

```sql
SELECT country, SUM(sales_amount)
FROM sales;
```

```console
Binder Error:
column "country" must appear in the GROUP BY clause
or must be part of an aggregate function.
```

❌ Selecting a non-aggregated column without `GROUP BY` → error.

---

# Slide 14 — 🧪 Practice

Ask students to write:

* Revenue by product
* Count of transactions by country
* Average quantity per product

---

# Slide 15 — `WHERE` vs `HAVING`

Both filter rows — but at different stages of the query.

---

# Slide 16 — `WHERE`

Filters rows **before** grouping:

```sql
SELECT *
FROM sales
WHERE price > 500;
```

---

# Slide 17 — `HAVING`

Filters groups **after** aggregation:

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
HAVING revenue > 95000;
```

| country | revenue |
|---------|--------:|
| Germany | 98,630  |
| UK      | 95,928  |

(Canada and USA are grouped and summed too, but filtered out by `HAVING`.)

---

# Slide 18 — Side-by-Side

| | `WHERE` | `HAVING` |
|---|---|---|
| Runs | Before aggregation | After aggregation |
| Filters | Rows | Groups |
| Can use aggregate functions? | ❌ No | ✅ Yes |

---

# Slide 19 — ❌ Classic Mistake

```sql
SELECT country, SUM(sales_amount) AS revenue
FROM sales
WHERE revenue > 5000;
```

```console
Binder Error:
WHERE clause cannot contain aggregates!
```

👉 `revenue` doesn't exist yet when `WHERE` runs — use `HAVING` instead.

---

# Slide 20 — ✅ Correct Version

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
HAVING revenue > 95000;
```

Business meaning:

"Show only our highest-performing markets."

---

# Slide 21 — 📊 KPI Thinking

Key metrics:

* Revenue (`SUM`)
* Volume (`COUNT`)
* Average value (`AVG`)

---

# Slide 22 — Insight Example

* High revenue ≠ high volume
* A few expensive products can outsell many cheap ones

```sql
SELECT product,
       SUM(sales_amount) AS revenue,
       COUNT(*)          AS num_transactions,
       AVG(price)        AS avg_price
FROM sales
GROUP BY product
ORDER BY revenue DESC;
```

---

# Slide 23 — 📈 Visualization (Concept)

Bar chart:

* X → country
* Y → revenue

👉 Makes comparison across markets easy at a glance

---

# Slide 24 — 🧪 In-Class Exercise

Write queries for:

1. Revenue by country
2. Revenue by product
3. Countries with revenue > 95,000
4. Products with average price > 500

---

# Slide 25 — 💬 Discussion

Ask:

* Which country is strongest?
* Which product dominates revenue?
* Are we volume-driven or value-driven?

---

# Slide 26 — 🔥 Advanced Thinking

Compare:

* High revenue + low transaction count (few big-ticket sales)

vs.

* Low revenue + high transaction count (many small sales)

👉 These call for different business strategies

---

# Slide 27 — What Did We Learn?

* `COUNT`, `SUM`, `AVG`
* `GROUP BY`
* `WHERE` vs `HAVING`
* KPI thinking

---

# Slide 28 — 🎯 Most Important Idea

SQL transforms raw rows into business metrics.

---

# Slide 29 — 🚀 Next Week

👉 JOINs (combining datasets)

👉 Customers + Products + Orders

---

# Slide 30 — 🙌 End of Week 1

Questions?
