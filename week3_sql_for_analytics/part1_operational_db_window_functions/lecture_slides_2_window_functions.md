---
marp: true
title: Week 3 — Window Functions & Advanced Analytics
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
---

# 📊 Week 3 — Window Functions

From Aggregation → Advanced Analytics

---

# 🎯 Learning Objectives

By the end of today:

* Understand window functions
* Use `RANK()`, `ROW_NUMBER()`, `DENSE_RANK()`
* Compute running totals
* Segment data using `CASE`
* Apply `PARTITION BY`

Dataset for the ranking/trend examples: the `sales` table
(`data/week4_sales.csv` — `order_id, order_date, product, price,
quantity, sales_amount`).

---

# 🧠 The Limitation of `GROUP BY`

`GROUP BY`:

👉 collapses many rows into one row per group

---

# ❌ Problem with `GROUP BY`

You lose row-level detail.

Example: you want **both**

* total revenue per product, **and**
* every individual transaction, side by side

👉 `GROUP BY` alone cannot show both at once.

---

# 🔥 Solution: Window Functions

Window functions perform calculations **without collapsing rows** — every
input row stays in the output, with a computed column added alongside it.

---

# 🧠 Key Idea

### `GROUP BY` → reduces rows

### `WINDOW` (`OVER(...)`) → keeps rows

---

# 🏆 `RANK()`

Rank all rows:

```sql
RANK() OVER (ORDER BY revenue DESC)
```

Rank rows separately within each group ("partition"):

```sql
RANK() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

---

# 💼 Business Meaning

"Who are the top performers?"

---

# 🧪 Example — `RANK()` After Aggregation

```sql
SELECT product,
       SUM(sales_amount) AS revenue,
       RANK() OVER (
          ORDER BY SUM(sales_amount) DESC
       ) AS rnk
FROM sales
GROUP BY product;
```

| product | revenue | rnk |
|---|---:|---:|
| Laptop | 216,940 | 1 |
| Phone  | 113,860 | 2 |
| Tablet |  35,752 | 3 |
| Watch  |  29,821 | 4 |

---

# ⚠️ Important

`RANK() OVER (...)` can be applied to the result of an aggregate
(`SUM(sales_amount)`) — the ranking happens **after** the `GROUP BY`
has computed each group's total.

---

# 🔢 `ROW_NUMBER()`

`ROW_NUMBER()` assigns a unique, sequential integer to each row —
starting at 1 — in the order you specify. Unlike `RANK()`, it never
produces ties.

```sql
SELECT *,
       ROW_NUMBER() OVER (ORDER BY sales_amount DESC) AS rn
FROM sales;
```

---

# 🧠 `RANK` vs. `DENSE_RANK` vs. `ROW_NUMBER`

| Function | Behavior |
|---|---|
| `RANK()` | ties allowed, **gaps** after a tie (1, 2, 2, 4) |
| `DENSE_RANK()` | ties allowed, **no gaps** (1, 2, 2, 3) |
| `ROW_NUMBER()` | always unique, no ties (1, 2, 3, 4) |

---

# 🔥 `PARTITION BY` (Game Changer)

```sql
RANK() OVER (
    PARTITION BY country
    ORDER BY revenue DESC
)
```

💼 Business meaning: **"Top categories WITHIN each country"** — not
just overall.

---

<style scoped>section { font-size: 21px; } pre, table { font-size: 17px; }</style>

# 🧪 Example — `RANK()` With `PARTITION BY`

Using the full operational schema (`stores`, `orders`, `order_items`,
`products`):

```sql
SELECT s.country,
       p.category,
       SUM(oi.sales_amount) AS revenue,
       RANK() OVER (
          PARTITION BY s.country
          ORDER BY SUM(oi.sales_amount) DESC
       ) AS rank_in_country
FROM stores s
JOIN orders o ON s.store_id = o.store_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY s.country, p.category
ORDER BY s.country, rank_in_country;
```

---

# 🧪 `RANK()` With `PARTITION BY` — Result

| country | category | revenue | rank_in_country |
|---|---|---:|---:|
| Australia | Clothing | 5,828,090.64 | 1 |
| Australia | Toys | 5,732,588.30 | 2 |
| Canada | Clothing | 3,178,918.19 | 1 |
| Canada | Sports | 3,103,846.12 | 2 |

👉 The rank **resets to 1** at the start of every new country — that's
what `PARTITION BY` does.

---

# 💥 Why This Matters

Without `PARTITION BY`, "Clothing" being #1 in Australia would be
invisible — it might rank #5 or #6 globally, hidden behind bigger
countries' totals. `PARTITION BY` gives every group its own ranking.

---

# 📈 Running Totals

```sql
SUM(sales_amount) OVER (ORDER BY order_date)
```

The most efficient way to compute a running (cumulative) total is a
`SUM()` window function combined with an `ORDER BY` clause inside
`OVER(...)` — each row's total includes every prior row's value.

---

# 💼 Business Meaning

"How is revenue growing over time?"

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# 🧪 Example — Running Total (Small Illustration)

Table: `daily_sales`

| sale_date  | revenue |
|---|---:|
| 2024-01-01 | 100.00 |
| 2024-01-02 | 250.00 |
| 2024-01-03 | 150.00 |

```sql
SELECT sale_date,
       revenue,
       SUM(revenue) OVER (ORDER BY sale_date) AS running_total
FROM daily_sales;
```

| sale_date | revenue | running_total | how |
|---|---:|---:|---|
| 2024-01-01 | 100.00 | 100.00 | 100 (first row) |
| 2024-01-02 | 250.00 | 350.00 | 100 + 250 |
| 2024-01-03 | 150.00 | 500.00 | 350 + 150 |

---

# 🧪 Same Idea, Real Data

```sql
SELECT order_date,
       sales_amount,
       SUM(sales_amount) OVER (ORDER BY order_date) AS running_total
FROM sales
ORDER BY order_date;
```

| order_date | sales_amount | running_total |
|---|---:|---:|
| 2025-01-01 | 939 | 939 |
| 2025-01-02 | 218 | 1,157 |
| 2025-01-03 | 2,396 | 3,553 |
| 2025-01-04 | 795 | 4,348 |

---

# 📊 Trend Visualization

Line chart:

* X → `order_date`
* Y → `running_total`

👉 Turns a table of numbers into a visible growth trend

---

# 🔁 Moving from Static → Dynamic

* `GROUP BY` → a snapshot (one number per group)
* `WINDOW` → a trend (one number per row, building on the rows before it)

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# 🧩 Segmentation with `CASE`

```sql
SELECT product,
       SUM(sales_amount) AS revenue,
       CASE WHEN SUM(sales_amount) > 50000 THEN 'High'
            WHEN SUM(sales_amount) > 20000 THEN 'Medium'
            ELSE 'Low'
       END AS segment
FROM sales
GROUP BY product;
```

| product | revenue | segment |
|---|---:|---|
| Laptop | 216,940 | High |
| Phone  | 113,860 | High |
| Tablet |  35,752 | Medium |
| Watch  |  29,821 | Medium |

---

# 💼 Business Meaning

"Classify products (or customers) into tiers automatically."

---

# 🔥 Combine Everything

`RANK()` and `CASE` in the same query — a rank *and* a business label,
side by side:

```sql
SELECT product,
       SUM(sales_amount) AS revenue,
       RANK() OVER (ORDER BY SUM(sales_amount) DESC) AS rnk,
       CASE WHEN SUM(sales_amount) > 50000 THEN 'High'
            WHEN SUM(sales_amount) > 20000 THEN 'Medium'
            ELSE 'Low'
       END AS segment
FROM sales
GROUP BY product;
```

---

# ⚠️ Common Mistakes

---

# ❌ Mistake 1 — Using a Window Function Without `OVER()`

```sql
SELECT product, RANK()  -- ❌ RANK needs OVER(...)
FROM sales;
```

```console
Catalog Error:
Scalar Function with name rank does not exist!
Did you mean "range"?
```

👉 Without `OVER(...)`, DuckDB doesn't even recognize `RANK` as a window
function — it looks for (and fails to find) a plain scalar function of
that name.

---

# ❌ Mistake 2 — Confusing `GROUP BY` and `PARTITION BY`

`GROUP BY` **removes** rows (one row per group).
`PARTITION BY` **keeps** every row — it only changes how the window
function's calculation is scoped.

---

# ❌ Mistake 3 — Forgetting `PARTITION BY`

```sql
RANK() OVER (ORDER BY revenue DESC)          -- one global ranking
RANK() OVER (PARTITION BY country ORDER BY revenue DESC)  -- per-country
```

Leaving out `PARTITION BY` silently changes the business question you're
answering — from "top overall" to "top per group," or vice versa.

---

# 🧪 In-Class Exercise

Write queries:

1. Rank products by total revenue
2. Top 5 individual transactions by `sales_amount`
3. Running total of revenue over time
4. Rank product categories within each store country
5. Segment products into High / Medium / Low revenue tiers

---

# 💬 Discussion

Ask:

* Which product is dominant overall?
* Is revenue growing consistently over time, or in bursts?
* Which segments matter most to the business?

---

# 🔥 Advanced Thinking

👉 Combine joins + aggregation + window functions — this is what a real
analytics pipeline looks like.

---

# 🧠 What Did We Learn?

* `RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`
* `PARTITION BY`
* Running totals (`SUM(...) OVER (ORDER BY ...)`)
* Segmentation with `CASE`

---

# 🎯 Most Important Idea

Window functions enable deep analytical insight — without giving up
row-level detail the way `GROUP BY` does.

---

# 🙌 End of Week 3, Part 1

Questions?

---

Next (Part 2, later this week):

**CTEs and advanced SQL analytics — then a case study combining everything into a full business analysis.**
