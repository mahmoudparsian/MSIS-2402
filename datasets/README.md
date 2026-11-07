# Datasets

[← Course home](../README.md) · **Datasets**

Shared data used across the course. The main one is
[`oltp_database/`](oltp_database/) — the 7-table retail database behind Weeks
1–3, the MySQL labs in Weeks 4–5, and the Final Exam. The others are smaller
copies, samples, or raw sources for the data stories.

> **You rarely need to open these directly.** Course notebooks already read the
> files they need by relative path — so keep the repository's folders as
> downloaded.

---

## At a Glance

| Folder | What it is | Size | Used by |
|---|---|---:|---|
| [`oltp_database/`](oltp_database/) | **The course database** — a retail business in 7 related tables | 22 MB | Weeks 1–5, the labs, and the Final Exam |
| [`oltp_database/mysql/`](oltp_database/mysql/README.md) | The same 7 tables as one MySQL load script | 25 MB | Weeks 4–5 (MySQL) |
| [`samples/`](samples/) | 50-row samples of three course tables | 12 KB | Previewing columns |
| [`books_dataset/`](books_dataset/) | Book-Crossing books, users, and ratings (raw) | 115 MB | The [`books_users_ratings`](../data_stories/books_users_ratings/README.md) data story |
| [`diabetes_130_hospitals/`](diabetes_130_hospitals/) | UCI Diabetes 130-US Hospitals (zipped original) | 3 MB | Source of Week 3's [`notebook_diabetic`](../week3_sql_for_analytics/session06_ctes_advanced_analytics/notebook_diabetic/README.md) |

---

## `oltp_database/` — the Course Database

An online-and-in-store retail business: customers place orders at stores; orders
have line items (one per product bought), and each order has exactly one payment
and one shipment.

| Table | Rows | Columns |
|---|---:|---|
| `customers` | 1,000 | `customer_id`, `gender`, `country`, `segment`, `signup_date` |
| `products` | 2,000 | `product_id`, `category`, `price` |
| `stores` | 50 | `store_id`, `store_type`, `country` |
| `orders` | 100,000 | `order_id`, `customer_id`, `store_id`, `order_date` |
| `order_items` | 300,000 | `order_item_id`, `order_id`, `product_id`, `quantity`, `category`, `price`, `sales_amount` |
| `payments` | 100,000 | `payment_id`, `order_id`, `payment_method`, `payment_date`, `payment_amount` |
| `shipments` | 100,000 | `shipment_id`, `order_id`, `carrier`, `shipment_date`, `delivery_date` |

**How the tables connect:**

```
customers ──< orders >── stores
                │
                ├──< order_items >── products
                ├─── payments
                └─── shipments
```

`──<` means **one-to-many** (one customer has many orders; one order has many
line items). `───` means **one-to-one** (one payment and one shipment per order).
Every foreign key in the data points to an existing row.

**In DuckDB**, query a file directly or load it as a table (path shown from the
repository's root folder):

```sql
CREATE OR REPLACE TABLE orders AS
SELECT * FROM read_csv_auto('datasets/oltp_database/orders.csv');
```

**In MySQL**, load all seven tables into a database called `isba_shop` with one
command — see [`oltp_database/mysql/README.md`](oltp_database/mysql/README.md).

---

## The Smaller Sets

- **`samples/`** — 50 rows each from `customers`, `orders`, and `order_items`,
  for a quick look at the columns.

  > ⚠️ The three samples were drawn **independently**, so they barely match
  > each other — joining them returns almost nothing. For joins, use
  > `oltp_database/`.

---

## Raw Sources for Other Materials

- **`books_dataset/`** — the original
  [Book-Crossing dataset](https://www.kaggle.com/datasets/saurabhbagchi/books-dataset)
  (CC0 public domain): `books.csv`, `users.csv`, `ratings.csv`. The files are
  separated by `;` and partly Latin-1 encoded, so they don't load cleanly on
  their own — use the
  [`books_users_ratings`](../data_stories/books_users_ratings/README.md) data
  story, whose build cleans them.
- **`diabetes_130_hospitals/`** — the original
  [UCI Diabetes 130-US Hospitals](https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008)
  download (1999–2008), zipped. Week 3's `notebook_diabetic` already includes the
  unzipped CSVs it needs.

---

*MSIS-2402 — Database Management Systems - Fundamentals of SQL — Winter 2027*
