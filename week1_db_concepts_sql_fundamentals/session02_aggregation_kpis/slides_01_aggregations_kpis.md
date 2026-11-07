---
marp: true
title: MSIS-2402 - Session 2 - Aggregation & KPIs
theme: default
paginate: true
---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Session 2 — Aggregation & KPIs

From Rows → Metrics → Decisions

---

# Slide 2 — Learning Objectives

By the end of today:

* Use aggregate functions (`SUM`, `COUNT`, `AVG`) — and the three kinds of `COUNT`
* Understand `GROUP BY`
* Distinguish `WHERE` vs `HAVING`
* Know the order SQL runs a query in
* Think in business metrics (KPIs)

---

# Slide 3 — Key Shift

Session 1:

👉 Look at rows

Session 2:

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
`order_id, country, product, price, quantity, sales_amount`. Load it from
this deck's folder (`session02_aggregation_kpis/`):

```sql
CREATE OR REPLACE TABLE sales AS
SELECT * FROM read_csv_auto('data/sales_dataset.csv');
```

---

# Slide 6 — `COUNT()`

```sql
SELECT COUNT(*) AS total_transactions
FROM sales;
```

Business meaning:

"How many transactions do we have?"

---

<style scoped>section { font-size: 24px; } pre { font-size: 20px; }</style>

# Slide 7 — Three Kinds of `COUNT`

A small table where two contacts have **no email** (`NULL`):

```sql
CREATE OR REPLACE TABLE contacts AS
SELECT * FROM (VALUES
    (1, 'ana@shop.com', 'USA'),
    (2, NULL,           'USA'),
    (3, 'li@shop.com',  'UK'),
    (4, NULL,           'Germany'),
    (5, 'sam@shop.com', 'USA')
) AS t(contact_id, email, country);

SELECT COUNT(*)                AS all_rows,
       COUNT(email)            AS with_email,
       COUNT(DISTINCT country) AS countries
FROM contacts;
```

| all_rows | with_email | countries |
|---:|---:|---:|
| 5 | 3 | 3 |

---

<style scoped>section { font-size: 24px; } table { font-size: 21px; }</style>

# Slide 8 — Which `COUNT` Do I Need?

| You write | It counts | Business question |
|---|---|---|
| `COUNT(*)` | every row | "How many contacts?" → 5 |
| `COUNT(email)` | rows where `email` is **not** `NULL` | "How many can we email?" → 3 |
| `COUNT(DISTINCT country)` | **different** values (no `NULL`s) | "How many countries?" → 3 |

👉 Same table, three different answers. Pick the one that matches the question.

💼 In our `sales` table: `COUNT(*)` = 200 transactions,
`COUNT(DISTINCT country)` = 4 markets.

---

# Slide 9 — `SUM()`

```sql
SELECT SUM(sales_amount) AS total_revenue
FROM sales;
```

Business meaning:

"What is total revenue?"

---

# Slide 10 — `AVG()`

```sql
SELECT AVG(price) AS avg_price
FROM sales;
```

Business meaning:

"What is the average price?"

---

# Slide 11 — ⚠️ Important Limitation

`COUNT`/`SUM`/`AVG` alone give:

👉 ONE number for the whole table

But businesses need:

👉 A breakdown by category (country, product, ...)

---

# Slide 12 — `GROUP BY` (Core Concept)

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
ORDER BY revenue DESC;
```

---

# Slide 13 — What `GROUP BY` Does

* Splits data into groups (one group per distinct `country`)
* Computes the aggregate (`SUM`) separately, per group

Business question:

"What is revenue, by country?"

---

# Slide 14 — Interpretation

Output (real data, `data/sales_dataset.csv`):

| country | revenue  |
|---------|---------:|
| Germany | 98,630   |
| UK      | 95,928   |
| Canada  | 93,016   |
| USA     | 76,647   |

👉 Compare performance across markets

---

# Slide 15 — ⚠️ Common Mistake

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

# Slide 16 — 🧪 Practice

Ask students to write:

* Revenue by product
* Count of transactions by country
* Average quantity per product

---

# Slide 17 — `WHERE` vs `HAVING`

Both filter rows — but at different stages of the query.

---

# Slide 18 — `WHERE`

Filters rows **before** grouping:

```sql
SELECT *
FROM sales
WHERE price > 500;
```

---

# Slide 19 — `HAVING`

Filters groups **after** aggregation:

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
HAVING revenue > 95000
ORDER BY revenue DESC;
```

| country | revenue |
|---------|--------:|
| Germany | 98,630  |
| UK      | 95,928  |

(Canada and USA are grouped and summed too, but filtered out by `HAVING`.)

---

# Slide 20 — Side-by-Side

| | `WHERE` | `HAVING` |
|---|---|---|
| Runs | Before aggregation | After aggregation |
| Filters | Rows | Groups |
| Can use aggregate functions? | ❌ No | ✅ Yes |

---

# Slide 21 — ❌ Classic Mistake

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

# Slide 22 — ✅ Correct Version

```sql
SELECT country,
       SUM(sales_amount) AS revenue
FROM sales
GROUP BY country
HAVING revenue > 95000
ORDER BY revenue DESC;
```

Business meaning:

"Show only our highest-performing markets."

---

# Slide 23 — 🧭 How SQL Runs a Query

You **write** `SELECT` first, but SQL **runs** the clauses in this order:

| Step | Clause | What happens |
|:---:|---|---|
| 1 | `FROM` | pick the table |
| 2 | `WHERE` | keep only some **rows** |
| 3 | `GROUP BY` | make the groups |
| 4 | `HAVING` | keep only some **groups** |
| 5 | `SELECT` | compute the output columns (and aliases) |
| 6 | `ORDER BY` | sort |
| 7 | `LIMIT` | keep the first *n* rows |

---

# Slide 24 — What the Order Explains

* **No aggregates in `WHERE`:** `WHERE` (step 2) runs **before** the groups
  exist (step 3) → filter on `SUM(...)` with `HAVING` (step 4)
* **`ORDER BY` can sort by any alias:** it runs **after** `SELECT` (step 5)
* **`LIMIT` is last:** "top 3" means *sort first, then keep 3*

👉 When a query surprises you, walk through the 7 steps in order.

---

<style scoped>section { font-size: 24px; }</style>

# Slide 25 — ⚠️ Aliases: DuckDB Is Friendlier Than Most

Can you use a `SELECT` alias (like `revenue`) in another clause?

| Clause | DuckDB | MySQL (Weeks 4–5) |
|---|:---:|:---:|
| `WHERE` (plain alias, e.g. `amount`) | ✅ | ❌ *Unknown column* |
| `WHERE` (aggregate alias, e.g. `revenue`) | ❌ | ❌ |
| `GROUP BY`, `HAVING` | ✅ | ✅ |
| `ORDER BY` | ✅ | ✅ |

👉 **Works everywhere:** in `WHERE`, repeat the expression instead of the alias:
`WHERE price * quantity > 5000` — not `WHERE amount > 5000`.

---

# Slide 26 — 📊 KPI Thinking

Key metrics:

* Revenue (`SUM`)
* Volume (`COUNT`)
* Average value (`AVG`)

---

# Slide 27 — Insight Example

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

# Slide 28 — 📈 Visualization (Concept)

Bar chart:

* X → country
* Y → revenue

👉 Makes comparison across markets easy at a glance

---

# Slide 29 — 🧪 In-Class Exercise

Write queries for:

1. Revenue by country
2. Revenue by product
3. Countries with revenue > 95,000
4. Products with average price > 500

---

# Slide 30 — 💬 Discussion

Ask:

* Which country is strongest?
* Which product dominates revenue?
* Are we volume-driven or value-driven?

---

# Slide 31 — 🔥 Advanced Thinking

Compare:

* High revenue + low transaction count (few big-ticket sales)

vs.

* Low revenue + high transaction count (many small sales)

👉 These call for different business strategies

---

# Slide 32 — What Did We Learn?

* `COUNT`, `SUM`, `AVG` — `COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`
* `GROUP BY`
* `WHERE` vs `HAVING`
* The order SQL runs a query in
* KPI thinking

---

# Slide 33 — 🎯 Most Important Idea

SQL transforms raw rows into business metrics.

---

# Slide 34 — 🚀 Next Week

👉 JOINs (combining datasets)

👉 Customers + Products + Orders

---

# Slide 35 — 🙌 End of Week 1

Questions?
