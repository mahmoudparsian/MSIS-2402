# E-Commerce Analytics — CTEs and Window Functions with DuckDB

[← Week 3](../../README.md) · [Course home](../../../README.md) · **Week 3 · Session 6 · Example notebook**

Ten business questions answered with SQL on the course's retail dataset — the
same `customers` / `products` / `stores` / `orders` / `order_items` tables
used throughout Weeks 1–3 — with a focus on **CTEs (`WITH`), window
functions, ranking, and running totals**.

| | |
|---|---|
| **Notebook** | [`notebook_ecommerce.py`](notebook_ecommerce.py) |
| **Data** | 5 tables from [`datasets/oltp_database/`](../../../datasets/oltp_database/), loaded directly from CSV |
| **Each question has** | The SQL, a plain-English explanation, and — for half of them — a chart |

---

## Quick Start

From **inside this folder**:

```bash
marimo edit notebook_ecommerce.py
```

The notebook uses an **in-memory** DuckDB connection and loads the CSV files
fresh every time it runs, so there is no database file to build first. (It
reads the data by relative path, so it must be opened from this folder.)

---

## The 10 Questions

| # | Question | SQL technique |
|:---:|---|---|
| 1 | Top 10 customers by revenue | `GROUP BY`, `ORDER BY … LIMIT` |
| 2 | Rank customers by revenue | `RANK()` |
| 3 | Revenue by category | `GROUP BY` |
| 4 | Rank categories by revenue | `RANK()` |
| 5 | Top product in each category | CTE + `ROW_NUMBER() OVER (PARTITION BY …)` |
| 6 | Running daily revenue total | `SUM() OVER (ORDER BY …)` |
| 7 | Average order revenue by customer | Subquery in `FROM` + `AVG` |
| 8 | Customers above average revenue | Two CTEs — compare each customer to the overall average |
| 9 | Rank stores by revenue | `RANK()` |
| 10 | Revenue share by category | Percent of total with `SUM() OVER ()` |

## Data at a Glance

| Table | Columns | Rows |
|---|---|---:|
| `customers` | `customer_id`, `gender`, `country`, `segment`, `signup_date` | 1,000 |
| `products` | `product_id`, `category`, `price` | 2,000 |
| `stores` | `store_id`, `store_type`, `country` | 50 |
| `orders` | `order_id`, `customer_id`, `store_id`, `order_date` | 100,000 |
| `order_items` | `order_item_id`, `order_id`, `product_id`, `quantity`, `category`, `price`, `sales_amount` | 300,000 |

## Compare with the Other Example

The sibling [`notebook_diabetic/`](../notebook_diabetic/) takes the opposite
approach: it builds a **persistent, on-disk** database once with a separate
script, then queries it read-only. That suits a large dataset you query many
times. This notebook's in-memory approach suits a single, self-contained
analysis — every run reflects whatever is currently in the CSV files.

---

[← Week 3](../../README.md) · [Course home](../../../README.md)
