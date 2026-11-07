---
marp: true
title: MSIS-2402 — Case Study: From SQL to Decision
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

# 📊 Case Study: From SQL to Decision

From SQL → Insight → Decision

---

# 🎯 Learning Objectives

By the end of today:

* Apply all SQL concepts together
* Translate data into business insights
* Communicate findings clearly
* Make data-driven recommendations

---

# 🎯 Learning Objectives (cont.)

Dataset for this walkthrough: the same 7-table `oltp_database` used since
Week 1 (`customers`, `orders`, `order_items`, `products`, `payments`,
`shipments`, `stores`), loaded from this deck's folder with
`read_csv_auto('../../datasets/oltp_database/<table>.csv')`. Today's demo runs company-wide, across all six
countries; in the "Try It Yourself" exercise at the end, you repeat it for one
country of your choice.

---

# 🧠 The Big Transition

Weeks 1–3:

👉 Learn SQL

Today:

👉 Use SQL to think and decide

---

# 💼 Real-World Expectation

Employers don't want:

❌ "Someone who writes SQL"

They want:

✅ "Someone who explains what the data means"

---

# 📊 Case Study Scenario

You are the newest data analyst at **Nova Retail**, a mid-size e-commerce
company operating in six countries. The VP of Sales wants a briefing
ahead of next quarter's planning meeting.

---

# 🎯 Your Mission

Answer:

* Where is revenue coming from?
* Which customer segments matter most?
* How is the business evolving?
* What should we do next?

---

# 🔁 Analytical Workflow

1. Explore data
2. Aggregate metrics
3. Join across tables (customers → orders → order_items, and beyond)
4. Apply window functions
5. Visualize
6. Interpret

---

# 🧾 Step 1 — Explore

```sql
SELECT * FROM customers ORDER BY customer_id LIMIT 10;
```

💼 Goal — understand:

* structure
* patterns
* anomalies

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# 📊 Step 2 — Revenue by Country

```sql
SELECT c.country, ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.country
ORDER BY revenue DESC;
```

| country | revenue |
|---|---:|
| Germany | 38,242,802.95 |
| Australia | 34,225,578.67 |
| USA | 32,966,179.60 |
| France | 31,497,062.18 |
| UK | 30,655,319.39 |
| Canada | 26,113,603.34 |

🧠 Insight: 👉 Germany leads every market — but notice the spread is not
huge (Germany to Canada is less than 1.5x). No single market dominates the
way "top product" questions often do.

---

# 📦 Step 3 — Segment Performance

```sql
SELECT c.segment, SUM(oi.sales_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY c.segment
ORDER BY revenue DESC;
```

💼 Question: which customer segments drive revenue — and by how much?

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# 🏆 Step 4 — Ranking Within Groups

```sql
WITH seg AS (
    SELECT c.country, c.segment, SUM(oi.sales_amount) AS revenue
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.country, c.segment
)
SELECT country, segment, revenue,
       RANK() OVER (PARTITION BY country ORDER BY revenue DESC) AS rnk
FROM seg
ORDER BY country, rnk;
```

🧠 Insight: 👉 `Consumer` ranks #1 in **every** country — a genuinely
consistent pattern. But the #2 spot isn't always the same segment
everywhere. `PARTITION BY` is how you check "does the overall winner also
win in every subgroup," instead of assuming a company-wide number applies
uniformly.

---

# 📈 Step 5 — Trend Analysis

```sql
SELECT EXTRACT(YEAR FROM o.order_date) AS yr, SUM(oi.sales_amount) AS revenue
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY yr
ORDER BY yr;
```

💼 Question: are we growing? (Real answer: revenue is flat year over
year, within ~2%. A flat trend is a legitimate finding — don't force a
"growth story" that isn't in the data.)

---

<style scoped>section { font-size: 21px; } pre, table { font-size: 17px; }</style>

# 🧩 Step 6 — Segmentation (CASE WHEN)

```sql
WITH customer_revenue AS (
    SELECT c.customer_id, SUM(oi.sales_amount) AS total_revenue
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
    JOIN order_items oi ON oi.order_id = o.order_id
    GROUP BY c.customer_id
)
SELECT
    CASE WHEN total_revenue >= 220000 THEN 'High'
         WHEN total_revenue >= 180000 THEN 'Medium'
         ELSE 'Low' END AS value_tier,
    COUNT(*) AS customer_count
FROM customer_revenue
GROUP BY value_tier;
```

🧠 Insight: 👉 thresholds should come from *your* data's actual
percentiles, not round numbers picked in advance — every country's
revenue scale is different.

---

# 📊 Step 7 — Visualization

* Bar chart → compare markets or segments
* Line chart → trend over time

---

# 🧠 The Most Important Step

👉 Interpretation

A correct query is not the finish line — what it *means* for the
business is.

---

# 💬 Example Insights

* Consumer is the leading segment in every one of the 6 countries — a
  pattern worth building strategy around, unlike a single combined number
* Revenue is roughly flat year over year — no growth or decline story to
  tell, and that's an honest finding, not a weak one
* No single country dominates the way you might expect — Germany to
  Canada is under a 1.5x spread

---

# ⚠️ Common Student Mistake

Stopping at:

❌ "Here's my SQL query and the result table."

---

# ✅ What We Want

* SQL
* Result
* Insight
* Recommendation

---

# 💼 Executive Thinking

Translate:

Data → Action

---

# 🎯 Example Recommendation

* Invest further in the Consumer segment — the one pattern that holds in
  every market, not just on average
* Investigate why the #2 segment differs in some countries before
  copy-pasting a single company-wide segment strategy
* Since revenue is flat, look for growth levers outside of "wait for the
  trend to turn" — e.g., moving Low-tier customers to Medium

---

# 🧪 Try It Yourself

Pick **one country** as your regional market and repeat today's workflow
for it:

* Explore → aggregate → rank → trend → segment, scoped to your market
* Analyze results across customers, products, and operations
* Write a short insight under each query
* Close with a 3–4 sentence recommendation for a manager

---

# 🔥 Advanced Thinking

Ask, about the country you picked:

* What surprised you?
* What would you investigate next?
* What data is missing that would change your recommendation?

---

# 🧠 What Did We Learn?

* SQL as a tool
* Analytics mindset
* Business storytelling

---

# 🎯 Final Takeaway

SQL is not the goal.

**Insight is the goal.**

---

# 🚀 The SQL Journey

* Week 1 → Query & summarize
* Week 2 → Join & combine
* Week 3 → Analyze
* Case study → Decide

---

# 🙌 Congratulations

You can now:

✅ Analyze real data

✅ Generate insights

✅ Think like a data analyst

---

# 💬 Final Question

What would YOU do with your market's data?

---

# 🙌 Questions?

Thank You
