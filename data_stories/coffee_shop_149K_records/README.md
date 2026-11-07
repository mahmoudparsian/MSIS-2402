# ☕ Coffee Shop Sales

**MSIS-2402 · Week 1, Part 2 — Aggregation & KPIs**

149,116 transactions from three coffee shop locations. One wide table with a rich set
of grouping columns — store, product category, hour, day, month — which makes it a
natural fit for the week where `GROUP BY` is the point.

---

## Run it

```bash
cd data_stories/coffee_shop_149K_records                 # from the course repository folder
marimo edit coffee_shop_build_db_marimo.py     # build the database — run first
marimo edit coffee_shop_sql_analysis_marimo.py # the analysis
```

| File | Role |
|---|---|
| `coffee_shop_build_db_marimo.py` | Reads the Excel file (or the CSV copy), builds `coffee_shop_sales.duckdb` |
| `coffee_shop_sql_analysis_marimo.py` | The analysis notebook — 30 queries in four parts |
| `plot_helpers.py` | Chart functions, kept out of the notebooks |
| `coffee_shop_sales.xlsx` | The source data |
| `coffee_shop_sales.csv` | The same data as CSV — used when the `openpyxl` package (needed to read Excel) isn't installed, which is the case with the course's standard setup |
| `coffee_shop_sales.duckdb` | Built by the first notebook |
| `build_notebook1.py`, `build_notebook2.py` | Generator scripts (produce `.ipynb`) — not the notebooks |
| `BUILD_PROMPT.md` | The original build specification (provenance) |

**Run the build notebook first.** The analysis notebook expects the database to exist.

---

## The data

One table, `sales`, with **149,116 rows** and 18 columns:

| Group | Columns |
|---|---|
| **Identity** | `transaction_id`, `product_id`, `store_id` |
| **Time** | `transaction_date`, `transaction_time`, `hour`, `year`, `month`, `month_name`, `day`, `day_name` |
| **Place** | `store_location` |
| **Product** | `product_category`, `product_type`, `product_detail` |
| **Money** | `unit_price`, `transaction_qty`, `sales_amount` |

The time columns are **pre-derived** — `hour`, `day_name` and `month_name` were
computed during the build rather than being extracted in every query. That is a
deliberate choice worth pointing out: doing the work once at load time keeps the
analysis queries readable.

---

## What it covers

| Part | Queries | Techniques |
|---|---|---|
| A — Basic | 5 | `SELECT`, `WHERE`, `COUNT`, `DISTINCT` |
| B — Basic+ | 10 | `GROUP BY`, `SUM`, `AVG`, `ORDER BY` |
| C — Intermediate | 10 | `HAVING`, `CASE`, subqueries, multi-column grouping |
| D — Ranking & Window | 5 | `ROW_NUMBER`, `RANK`, CTEs |

---

## Questions this data answers well

- **Which hour of the day is busiest?** Group by `hour` — the morning peak is obvious
  and satisfying, because everyone already knows the answer and the query confirms it.
- **Does the busiest hour differ by store?** Two-column `GROUP BY`, and the answer is
  less obvious.
- **Which product category earns the most, and is it the one that sells the most
  units?** Revenue and volume are different measures — a recurring lesson.
- **What does the week look like?** Group by `day_name` and watch the weekday/weekend
  shape appear.

---

## A note on scope

Part D uses **window functions and CTEs**, which MSIS-2402 covers in Week 3. Parts A–C
are solid Week 1 (Part 2) material and can be assigned on their own; treat Part D as a preview
or save it for later in the term.

---

## Teaching notes

- **Start with the busiest-hour query.** Students can predict the answer before
  running it, which builds confidence that the tool works before it is asked anything
  hard.
- Ask what would change if `hour` had *not* been pre-computed. The answer —
  `EXTRACT(hour FROM transaction_time)` in every single query — makes the case for
  doing derivation once at load time.
- Pairs well with `sales_table_200_rows/`: same shape of question, three orders of
  magnitude more data, so students see when eyeballing stops working.
