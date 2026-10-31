# 🛍️ Shopify Sales

**MSIS-2402 · Week 3, Part 1 — Operational Database Analysis**

60,000 e-commerce orders with a genuinely wide set of dimensions — category, country,
traffic source, payment method — plus **profit**, which lets students ask questions
that revenue alone cannot answer.

It is also the only story here that ships a **quarantine table** for bad rows.

---

## Run it

```bash
marimo edit 01_data_setup_marimo.py    # build shopify_sales.duckdb — run first
marimo edit 02_queries_marimo.py       # the analysis
```

| File | Role |
|---|---|
| `01_data_setup_marimo.py` | Loads the CSV, separates bad rows, builds the database |
| `02_queries_marimo.py` | The analysis — 30 queries in four sections |
| `plot_utils.py` | Chart functions, kept out of the notebooks |
| `shopify_sales_dataset_ml_eda.csv` | **60,020 rows** as delivered |
| `shopify_sales.duckdb` | Built by the first notebook |

**Run the setup notebook first.**

---

## The data

Two tables:

| Table | Rows | What it holds |
|---|---|---|
| `sales` | **60,000** | Clean orders |
| `investigate_records` | **6** | Rows with a missing `order_id` — quarantined |

`sales` has 17 columns:

| Group | Columns |
|---|---|
| **Identity** | `order_id`, `customer_id`, `product_id` |
| **Time** | `order_date` |
| **Product** | `product_category`, `product_price` |
| **Order** | `quantity`, `discount_percent`, `discounted_price` |
| **Customer** | `customer_country` |
| **Channel** | `traffic_source`, `payment_method` |
| **Outcome** | `shipping_cost`, `rating`, `is_returned`, `revenue`, `profit` |

---

## The quarantine table is the interesting part

Six rows arrived with a **`NULL` order_id**. Rather than silently dropping them or
letting them poison the analysis, the setup notebook moves them into
`investigate_records`.

Three reasons that is the right call, and all three are worth saying to a class:

- **An order without an ID cannot be counted reliably.** It has no identity, so
  `COUNT(DISTINCT order_id)` would miss it and a join would lose it.
- **Deleting them destroys evidence.** Six missing IDs might be a bug in an upstream
  export, and somebody may want to know.
- **Keeping them in `sales` would be worse.** Every total would include rows that
  cannot be traced back to anything.

Have students query `investigate_records` and decide for themselves what should happen
to those six orders. There is no single right answer, which is what makes it a good
question.

---

## What it covers

| Section | Queries | Techniques |
|---|---|---|
| 1 — Basic | 5 | `SELECT`, `WHERE`, `ORDER BY`, `COUNT` |
| 2 — Basic+ | 10 | `GROUP BY`, `SUM`, `AVG`, `HAVING` |
| 3 — Intermediate | 10 | Subqueries, `CASE`, multi-column grouping |
| 4 — Ranking | 5 | `ROW_NUMBER`, `RANK`, `NTILE`, CTEs |

Section 4 uses window functions and CTEs — **Week 3, Part 2 material**. Sections 1–3 stand
alone for Week 3, Part 1.

---

## Questions this data answers well

- **Which category earns the most profit — and is it the one with the most revenue?**
  Having both columns makes the difference visible in a single query.
- **Does a bigger discount actually increase profit?** Group by `discount_percent`
  and watch margin move.
- **Which traffic source brings the most valuable customers?** Not the same as the one
  that brings the most orders.
- **Which countries return the most?** `is_returned` grouped by `customer_country`.

---

## Teaching notes

- **Open with the quarantine table**, before any analysis. Starting a story with "six
  rows were set aside, and here is why" frames the whole session as *analysis you can
  trust* rather than *queries that ran*.
- The revenue-versus-profit question is the strongest one here. Ask for the "best"
  category before defining what "best" means.
- Pairs with `coffee_shop_149K_records/`: both are sales data, but this one has profit
  and a returns flag, so the questions can go further.
