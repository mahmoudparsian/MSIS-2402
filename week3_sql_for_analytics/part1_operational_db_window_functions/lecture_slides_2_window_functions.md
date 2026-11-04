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

<style scoped>section { font-size: 24px; } pre { font-size: 19px; } table { font-size: 20px; }</style>

# 🔢 `ROW_NUMBER()`

`ROW_NUMBER()` assigns a unique, sequential integer to each row —
starting at 1 — in the order you specify. Unlike `RANK()`, it never
produces ties.

```sql
SELECT order_id, product, sales_amount,
       ROW_NUMBER() OVER (ORDER BY sales_amount DESC, order_id) AS rn
FROM sales
ORDER BY rn
LIMIT 5;
```

| order_id | product | sales_amount | rn |
|---:|---|---:|---:|
| 112 | Laptop | 6,295 | 1 |
| 86 | Laptop | 6,245 | 2 |
| 28 | Laptop | 6,135 | 3 |
| 87 | Laptop | 5,990 | 4 |
| 79 | Laptop | 5,980 | 5 |

👉 `order_id` is the **tie-breaker**: if two orders had the same
`sales_amount`, it decides which one gets the lower number.

---

# 🧠 `RANK` vs. `DENSE_RANK` vs. `ROW_NUMBER`

| Function | Behavior |
|---|---|
| `RANK()` | ties allowed, **gaps** after a tie (1, 2, 2, 4) |
| `DENSE_RANK()` | ties allowed, **no gaps** (1, 2, 2, 3) |
| `ROW_NUMBER()` | always unique, no ties (1, 2, 3, 4) |

---

<style scoped>section { font-size: 24px; } pre { font-size: 19px; } table { font-size: 20px; }</style>

# 🧪 All Three on Ties — a Small Illustration

Eight stores; three are tied at 750 and two at 500:

```sql
CREATE OR REPLACE TABLE store_sales AS
SELECT * FROM (VALUES
    ('S1', 'North', 900), ('S2', 'North', 750),
    ('S3', 'North', 750), ('S4', 'North', 600),
    ('S5', 'South', 980), ('S6', 'South', 750),
    ('S7', 'South', 500), ('S8', 'South', 500)
) AS t(store, region, revenue);

SELECT store, revenue,
       ROW_NUMBER() OVER (ORDER BY revenue DESC, store) AS row_num,
       RANK()       OVER (ORDER BY revenue DESC)        AS rnk,
       DENSE_RANK() OVER (ORDER BY revenue DESC)        AS dense_rnk
FROM store_sales
ORDER BY row_num;
```

---

# 🧪 All Three on Ties — Result

| store | revenue | row_num | rnk | dense_rnk |
|---|---:|---:|---:|---:|
| S5 | 980 | 1 | 1 | 1 |
| S1 | 900 | 2 | 2 | 2 |
| S2 | 750 | 3 | 3 | 3 |
| S3 | 750 | 4 | 3 | 3 |
| S6 | 750 | 5 | 3 | 3 |
| S4 | 600 | 6 | 6 | 4 |
| S7 | 500 | 7 | 7 | 5 |
| S8 | 500 | 8 | 7 | 5 |

---

# 🧠 Reading the Three Columns

* `row_num` — **1 to 8**, always different; ties are broken by `store`
* `rnk` — S2, S3, S6 share **3**; the next store gets **6** (a gap)
* `dense_rnk` — S2, S3, S6 share **3**; the next store gets **4** (no gap)

⚠️ **`ROW_NUMBER` needs a tie-breaker.** Without `, store` in its
`ORDER BY`, S2, S3, and S6 could get 3, 4, 5 in **any** order — and a
different order on the next run.

---

# 🎯 Which One When?

| The question says… | Use |
|---|---|
| "exactly N per group", "the first / latest order" | `ROW_NUMBER()` + a tie-breaker |
| "the top N, **including ties**" (competition ranking) | `RANK()` |
| "the Nth-highest **value**", "the top N price levels" | `DENSE_RANK()` |

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

<style scoped>section { font-size: 24px; } pre { font-size: 19px; } table { font-size: 20px; }</style>

# 🏆 Top 2 Orders per Product

Rank inside a CTE, then filter **outside** it:

```sql
WITH ranked AS (
    SELECT product, order_id, sales_amount,
           ROW_NUMBER() OVER (PARTITION BY product
                              ORDER BY sales_amount DESC, order_id) AS rn
    FROM sales
)
SELECT product, order_id, sales_amount, rn
FROM ranked
WHERE rn <= 2
ORDER BY product, rn;
```

---

# 🏆 Top 2 Orders per Product — Result

| product | order_id | sales_amount | rn |
|---|---:|---:|---:|
| Laptop | 112 | 6,295 | 1 |
| Laptop | 86 | 6,245 | 2 |
| Phone | 60 | 4,485 | 1 |
| Phone | 138 | 4,480 | 2 |
| Tablet | 50 | 1,930 | 1 |
| Tablet | 56 | 1,568 | 2 |
| Watch | 127 | 1,415 | 1 |
| Watch | 59 | 1,325 | 2 |

---

# 💡 DuckDB Shortcut: `QUALIFY`

`QUALIFY` filters a window result directly — no CTE needed
(same 8 rows as the CTE version):

```sql
SELECT product, order_id, sales_amount
FROM sales
QUALIFY ROW_NUMBER() OVER (PARTITION BY product
                           ORDER BY sales_amount DESC, order_id) <= 2;
```

---

# ⚠️ `WHERE` Cannot See a Rank

```sql
SELECT store, revenue,
       RANK() OVER (ORDER BY revenue DESC) AS rnk
FROM store_sales
WHERE rnk <= 3;
```

```console
Binder Error: WHERE clause cannot contain window functions!
```

👉 `WHERE` runs **before** window functions are computed. Rank in a
CTE (or use `QUALIFY`), then filter.

---

<style scoped>section { font-size: 24px; } pre { font-size: 19px; } table { font-size: 20px; }</style>

# 🏆 Top 2 per Region — Keep the Ties with `RANK`

```sql
WITH ranked AS (
    SELECT store, region, revenue,
           RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS rnk
    FROM store_sales
)
SELECT region, store, revenue, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY region, rnk, store;
```

---

# 🏆 Top 2 per Region — Result

| region | store | revenue | rnk |
|---|---|---:|---:|
| North | S1 | 900 | 1 |
| North | S2 | 750 | 2 |
| North | S3 | 750 | 2 |
| South | S5 | 980 | 1 |
| South | S6 | 750 | 2 |

👉 **5 rows**: North keeps **both** stores tied at 750. `ROW_NUMBER`
would return exactly 4 and drop one of them.

---

<style scoped>section { font-size: 24px; } pre { font-size: 19px; } table { font-size: 20px; }</style>

# 🥈 The Nth-Highest **Value** — `DENSE_RANK`

*"Which store has the 4th-highest revenue?"*

```sql
WITH ranked AS (
    SELECT store, revenue,
           DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_level
    FROM store_sales
)
SELECT store, revenue
FROM ranked
WHERE revenue_level = 4
ORDER BY store;
```

| store | revenue |
|---|---:|
| S4 | 600 |

With `RANK()` instead, `= 4` returns **no rows** — the ranks jump from
3 to 6 after the three-way tie.

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
