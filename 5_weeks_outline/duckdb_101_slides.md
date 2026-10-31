---

marp: true

title: DuckDB 101

paginate: true

---

### Slide 1 — DuckDB 101

**MSIS-2402 — Database Management Systems: Fundamentals of SQL**

DuckDB Basics for Analytics

Topics:

- What is DuckDB
- Installation
- Reading CSV files
- Creating tables
- Running SQL queries
- DuckDB + Pandas
- Multiple CSV files
- DuckDB vs Spark / BigQuery

---

### Slide 2 — What is DuckDB?

DuckDB is an **in-process (embedded) analytical database**.

Key idea:

It runs **inside your application** (Python, R, a Marimo notebook) — there is
no separate database server to install, configure, or connect to.

Characteristics:

- open-source
- columnar, vector-execution engine
- optimized for analytics (OLAP), not high-volume transaction processing
- no server required — `import duckdb; con = duckdb.connect()` and you're
  querying
- very fast on datasets from a few MB up to tens of GB, on a single laptop

Think of DuckDB as: **"SQLite for analytics"**

---

### Slide 3 — Why Use DuckDB for Teaching?

Advantages for students:

- No database server setup (no install, no admin password, no port conflicts)
- Works directly with CSV files — no separate load step required
- Fast analytics queries, even on a laptop
- Runs inside **Marimo notebooks** — the notebooks used throughout this course
- Supports (most of) standard SQL, so the skills transfer to Postgres/MySQL/Snowflake

Typical workflow:

CSV → DuckDB → SQL → Pandas / Visualization

---

### Slide 4 — DuckDB vs Traditional Databases

| Feature                 | DuckDB       | MySQL / PostgreSQL |
|--------------------------|--------------|---------------------|
| Server required          | ❌ No        | ✔ Yes               |
| Installation complexity  | Very easy (`pip install duckdb`) | Medium (server install + config) |
| Analytics (OLAP) performance | Excellent | Good |
| Transactional (OLTP) performance | Not the design target | Excellent |
| Runs embedded inside Python | ✔ Yes | ❌ No — connects to an external server process |

DuckDB is designed for:

**analytics, data science, and exploration** — not for high-concurrency
transactional apps (that's what MySQL/Postgres are for).

---

### Slide 5 — Installing DuckDB

Install using pip:

```bash
python3 -m pip install "duckdb>=2.0"
```

Verify installation:

```python
import duckdb
print(duckdb.__version__)   # 2.x.x
```

Works on Mac, Windows, and Linux.

Full step-by-step setup: the course's **`software_installation/`** guide.

---

### Slide 6 — Using DuckDB in Python

Example:

```python
import duckdb

con = duckdb.connect()   # in-memory database — nothing written to disk

con.execute("SELECT 1 + 1").fetchall()
```

Output:

```
[(2,)]
```

DuckDB executes **standard SQL queries**, right inside your Python process.

---

### Slide 7 — Reading a CSV File

DuckDB can read CSV files directly — no `CREATE TABLE` or import step needed.
First, let's create a small sample file so this example is fully
**self-contained and runnable, top to bottom**:

```python
import pandas as pd

# A tiny sample with the same shape as the Week 1 "sales" dataset
sample_sales = pd.DataFrame({
    "sale_id":          [1, 2, 3, 4, 5, 6],
    "sale_date":        ["2024-01-05", "2024-01-06", "2024-01-06",
                          "2024-01-07", "2024-01-08", "2024-01-08"],
    "product_id":       [101, 102, 101, 103, 102, 104],
    "product_category": ["Electronics", "Home", "Electronics",
                          "Office", "Home", "Electronics"],
    "quantity":         [2, 1, 3, 5, 2, 1],
    "unit_price":       [199.99, 49.50, 199.99, 12.75, 49.50, 899.00],
    "total_amount":     [399.98, 49.50, 599.97, 63.75, 99.00, 899.00],
})
sample_sales.to_csv("sales.csv", index=False)
```

Now query the file directly with SQL:

```sql
SELECT *
FROM read_csv_auto('sales.csv')
LIMIT 5;
```

DuckDB automatically:

- detects column names (from the CSV header)
- infers data types (dates, integers, decimals, text)

---

### Slide 8 — Creating a Table from CSV

Convert CSV → table:

```sql
CREATE OR REPLACE TABLE sales AS
SELECT * FROM read_csv_auto('sales.csv');
```

Now the table **sales** exists in this DuckDB connection — later queries
can reference `sales` directly, without repeating `read_csv_auto(...)`.

```sql
DESCRIBE sales;
```

---

### Slide 9 — Query Example

```sql
SELECT product_category,
       SUM(total_amount) AS revenue
FROM sales
GROUP BY product_category
ORDER BY revenue DESC;
```

Business question:

Which product category generates the most revenue?

---

### Slide 10 — DuckDB + Pandas

```python
# reuse the same `con` from Slide 8 — the `sales` table already exists there
df = con.execute("""
    SELECT *
    FROM sales
    ORDER BY total_amount DESC
    LIMIT 10
""").df()

df
```

DuckDB returns a **Pandas DataFrame** via `.df()` — Marimo shows it as a
table, ready for `matplotlib` or anything else in the Python data stack.

---

### Slide 11 — Visualization Example

```python
import matplotlib.pyplot as plt

# same `con`, same `sales` table as Slides 8–10
df = con.execute("""
    SELECT product_category,
           SUM(total_amount) AS revenue
    FROM sales
    GROUP BY product_category
    ORDER BY revenue DESC
""").df()

df.plot(kind="bar", x="product_category", y="revenue", legend=False)
plt.ylabel("Revenue ($)")
plt.title("Revenue by Product Category")
plt.tight_layout()
plt.show()
```

Workflow:

SQL → Pandas → Visualization

---

### Slide 12 — Reading Multiple CSV Files

If your data is split across several files (e.g. `sales_jan.csv`,
`sales_feb.csv`, `sales_mar.csv`), DuckDB can read them all at once with a
glob pattern:

```sql
SELECT *
FROM read_csv_auto('data/sales_*.csv');
```

DuckDB automatically loads and stacks all matching files into one result.

Useful for:

- partitioned datasets (one file per day/month)
- large data collections split across many files

---

### Slide 13 — DuckDB vs Spark vs BigQuery

| System    | Best Use Case                        |
|-----------|----------------------------------------|
| DuckDB    | Local analytics (single machine)       |
| Spark     | Distributed big data processing (cluster) |
| BigQuery  | Cloud data warehouse analytics         |
| Snowflake | Cloud data warehouse analytics         |

Rule of thumb:

```
DuckDB   → laptop
Spark    → cluster
BigQuery / Snowflake → cloud
```

---

### Slide 14 — DuckDB in 30 Seconds

Complete workflow example — CSV to chart, in one script:

```python
import duckdb
import matplotlib.pyplot as plt

con = duckdb.connect()

df = con.execute("""
    SELECT product_category,
           SUM(total_amount) AS revenue
    FROM read_csv_auto('sales.csv')
    GROUP BY product_category
    ORDER BY revenue DESC
""").df()

df.plot(kind="bar", x="product_category", y="revenue", legend=False)
plt.show()
```

Pipeline:

CSV → DuckDB → SQL → Pandas → Visualization

---

### Slide 15 — Summary-1

DuckDB is:

- lightweight
- fast
- easy to install (`pip install duckdb`, no server)
- ideal for analytics on CSV/Parquet data

Typical workflow:

CSV → DuckDB → SQL → Python Visualization

---

### Slide 16 — Summary-2

We will use DuckDB throughout this course to:

- explore datasets
- run SQL analytics
- visualize results
