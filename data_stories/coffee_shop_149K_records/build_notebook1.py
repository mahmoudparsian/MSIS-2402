import json, uuid

def uid():
    return uuid.uuid4().hex[:8]

def md(src):
    lines = src.strip().split('\n')
    lines = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    return {'cell_type':'markdown','metadata':{},'source':lines,'id':uid()}

def code(src):
    lines = src.strip().split('\n')
    lines = [l + '\n' for l in lines[:-1]] + [lines[-1]]
    return {'cell_type':'code','metadata':{},'source':lines,'outputs':[],'execution_count':None,'id':uid()}

nb = {
    'nbformat': 4, 'nbformat_minor': 5,
    'metadata': {
        'kernelspec': {'display_name': 'Python 3 (ipykernel)', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.11.0'}
    },
    'cells': []
}
c = nb['cells']

# ── Title ──
c.append(md("""# Coffee Shop Sales — Build DuckDB Database

This notebook reads the raw Excel file **coffee_shop_sales.xlsx**, cleans the data,
and stores it in a persistent **DuckDB** database file (`coffee_shop_sales.duckdb`).

### Steps
1. Import libraries
2. Load the Excel file into a Pandas DataFrame
3. Inspect the raw data
4. Check for and remove duplicate rows
5. Standardize the `transaction_date` column
6. Extract useful time features (hour, day-of-week, month, etc.)
7. Compute derived measures (`sales_amount`)
8. Write the cleaned table into a DuckDB database file

> **Prerequisite:** place `coffee_shop_sales.xlsx` in the same folder as this notebook."""))

# ── Cell 1 — Imports ──
c.append(md("""## Cell 1 — Import libraries

### What are we doing?
We import the Python libraries needed for file loading, data cleaning, and DuckDB database creation.

### Why?
Setting up all dependencies at the top keeps the notebook clean and ensures
any missing packages are caught early."""))

c.append(code("""import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import duckdb
import datetime
from pathlib import Path

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 160)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

print("Libraries loaded successfully.")"""))

# ── Cell 2 — Load xlsx ──
c.append(md("""## Cell 2 — Load the Excel file

### What are we doing?
We read `coffee_shop_sales.xlsx` into a Pandas DataFrame. If the Excel file
is not found, we fall back to a CSV version (`coffee_shop_sales.csv`).

### Why?
Some students may not have the `openpyxl` dependency installed.
Supporting both formats avoids unnecessary setup friction."""))

c.append(code("""xlsx_path = Path("coffee_shop_sales.xlsx")
csv_path  = Path("coffee_shop_sales.csv")

if xlsx_path.exists():
    try:
        df = pd.read_excel(xlsx_path)
        source_used = str(xlsx_path)
    except Exception as e:
        print("Excel read failed:", e)
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            source_used = str(csv_path)
        else:
            raise FileNotFoundError("Could not read .xlsx and .csv was not found.")
elif csv_path.exists():
    df = pd.read_csv(csv_path)
    source_used = str(csv_path)
else:
    raise FileNotFoundError("Neither .xlsx nor .csv found in the current folder.")

# A CSV stores times as text ("07:06:11"); turn them back into time
# values, as read_excel does.
if source_used.endswith(".csv"):
    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"], format="%H:%M:%S"
    ).dt.time

print(f"Loaded source : {source_used}")
print(f"Shape          : {df.shape}")
df.head()"""))

# ── Cell 3 — Inspect raw structure ──
c.append(md("""## Cell 3 — Inspect the raw data

### What are we doing?
We examine column names, data types, and non-null counts.

### Why?
Understanding the raw structure tells us which columns need type
conversion, which may have nulls, and what cleaning is required."""))

c.append(code("""df.info()"""))

# ── Cell 4 — Check for duplicates ──
c.append(md("""## Cell 4 — Check for duplicate rows

### What are we doing?
We count **exact** duplicate rows — rows where every column value is identical.

### Why?
Duplicate transaction lines inflate counts, quantities, and revenue.
In transactional data this is a critical data-quality check.

### How deduplication works
`df.duplicated()` returns `True` for every row that has already appeared
earlier with identical values in **all** columns. We count those rows,
then drop them with `drop_duplicates()`."""))

c.append(code("""dup_count = df.duplicated().sum()
print(f"Exact duplicate rows found: {dup_count:,}")

if dup_count > 0:
    print(f"Dropping {dup_count:,} duplicates ...")
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"Shape after dedup: {df.shape}")
else:
    print("No duplicates — the dataset is already clean.")"""))

# ── Cell 5 — Standardize transaction_date ──
c.append(md("""## Cell 5 — Standardize `transaction_date`

### What are we doing?
We convert `transaction_date` to a proper `datetime64` type. The raw column
may come in as `dd-mm-yy`, `yyyy-mm-dd`, or an Excel serial date —
so we try multiple formats and let Pandas pick the best one.

### Why?
A consistent date type is essential for:
- date arithmetic (e.g., date ranges, differences)
- SQL `WHERE` / `GROUP BY` on dates
- extracting year, month, day, and day-of-week"""))

c.append(code("""# Attempt 1 — let Pandas auto-detect
df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")

# If everything came back NaT, try dd-mm-yy explicitly
if df["transaction_date"].isna().all():
    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], format="%d-%m-%y", errors="coerce"
    )

valid_dates = df["transaction_date"].notna().sum()
print(f"Valid dates : {valid_dates:,} / {len(df):,}")
print(f"Date range  : {df['transaction_date'].min()} → {df['transaction_date'].max()}")
df[["transaction_id", "transaction_date"]].head()"""))

# ── Cell 6 — Extract time features ──
c.append(md("""## Cell 6 — Extract hour from `transaction_time`

### What are we doing?
Excel may store `transaction_time` as a `datetime.time` object or as a
string like `"07:06:11"`. We robustly extract the **hour** regardless
of the underlying type.

### Why?
The hour column enables time-of-day analysis (peak hours, morning vs.
afternoon) — one of the most valuable business insights in retail data."""))

c.append(code("""def extract_hour(x):
    \"\"\"Return the integer hour from various time representations.\"\"\"
    if pd.isna(x):
        return None
    if isinstance(x, datetime.time):
        return x.hour
    try:
        return pd.to_datetime(str(x)).hour
    except Exception:
        return None

df["hour"] = df["transaction_time"].apply(extract_hour)

valid_hours = df["hour"].notna().sum()
print(f"Valid hours: {valid_hours:,} / {len(df):,}")
print(f"Hour range : {int(df['hour'].min())} – {int(df['hour'].max())}")"""))

# ── Cell 7 — Derived columns ──
c.append(md("""## Cell 7 — Create derived columns

### What are we doing?
We add several columns that make analysis much easier:

| Column | Formula / Source |
|---|---|
| `sales_amount` | `transaction_qty × unit_price` |
| `year` | extracted from `transaction_date` |
| `month` | month number (1–12) |
| `month_name` | e.g., January, February |
| `day` | day of month |
| `day_name` | e.g., Monday, Tuesday |

### Why?
Pre-computing these in Python means the DuckDB table is immediately
ready for `GROUP BY year`, `GROUP BY month_name`, etc., without having
to write date-extraction functions in every SQL query."""))

c.append(code("""# Ensure numerics
for col in ["transaction_qty", "unit_price"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["sales_amount"] = df["transaction_qty"] * df["unit_price"]

df["year"]       = df["transaction_date"].dt.year
df["month"]      = df["transaction_date"].dt.month
df["month_name"] = df["transaction_date"].dt.month_name()
df["day"]        = df["transaction_date"].dt.day
df["day_name"]   = df["transaction_date"].dt.day_name()

print(f"Total revenue: ${df['sales_amount'].sum():,.2f}")
df[["transaction_id", "transaction_date", "hour", "sales_amount",
    "year", "month_name", "day_name"]].head(10)"""))

# ── Cell 8 — Quick validation ──
c.append(md("""## Cell 8 — Validate the cleaned DataFrame

### What are we doing?
A final sanity check before writing to DuckDB:
- Row count
- Null summary
- Basic statistics

### Why?
Writing bad data to a database propagates problems downstream.
It is good practice to validate before persisting."""))

c.append(code("""print("Shape:", df.shape)
print()
print("Null counts:")
print(df.isna().sum())
print()
df.describe(include="all")"""))

# ── Cell 9 — Write to DuckDB ──
c.append(md("""## Cell 9 — Create the DuckDB database file

### What are we doing?
We open a **persistent** DuckDB connection pointing to `coffee_shop_sales.duckdb`.
Then we write the cleaned DataFrame as a table called `sales`.

### Why?
A persistent `.duckdb` file means:
- the data survives after the notebook is closed
- the second notebook can simply open the same file and start querying
- no need to re-run the cleaning pipeline every time"""))

c.append(code("""db_path = "coffee_shop_sales.duckdb"

# Remove old database if it exists so we get a clean build
if Path(db_path).exists():
    Path(db_path).unlink()

con = duckdb.connect(db_path)

# Register the DataFrame and write it as a permanent table
con.register("df_temp", df)

con.execute(\"\"\"
    CREATE TABLE sales AS
    SELECT * FROM df_temp
    WHERE transaction_date IS NOT NULL
      AND transaction_qty IS NOT NULL
      AND unit_price      IS NOT NULL
      AND sales_amount    IS NOT NULL
      AND hour            IS NOT NULL
\"\"\")

row_count = con.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
print(f"Rows written to '{db_path}': {row_count:,}")"""))

# ── Cell 10 — Verify the database ──
c.append(md("""## Cell 10 — Verify the database

### What are we doing?
We query the freshly created DuckDB table to confirm the data is
accessible and looks correct.

### Why?
Always verify a write operation. A quick `SELECT` confirms the
table exists, the schema is correct, and the data is readable."""))

c.append(code("""# Show schema
print("Table schema:")
print(con.execute("DESCRIBE sales").df().to_string(index=False))
print()

# Sample rows
print("Sample rows:")
con.execute("SELECT * FROM sales LIMIT 5").df()"""))

# ── Cell 11 — Summary stats via SQL ──
c.append(md("""## Cell 11 — Quick summary statistics via SQL

### What are we doing?
We run a single summary query to produce a high-level profile:
total rows, total units, total revenue, distinct stores, distinct products,
and the date range.

### Why?
This gives us (and any student opening the second notebook) a fast
executive-style overview of what is inside the database."""))

c.append(code("""con.execute(\"\"\"
    SELECT
        COUNT(*)                     AS total_rows,
        SUM(transaction_qty)         AS total_units_sold,
        ROUND(SUM(sales_amount), 2)  AS total_revenue,
        COUNT(DISTINCT store_id)     AS distinct_stores,
        COUNT(DISTINCT product_id)   AS distinct_products,
        MIN(transaction_date)        AS first_date,
        MAX(transaction_date)        AS last_date
    FROM sales
\"\"\").df()"""))

# ── Cell 12 — Close and done ──
c.append(md("""## Cell 12 — Close the connection

### What are we doing?
We close the DuckDB connection to flush all data to disk.

### Why?
Closing ensures the file is fully written and safe to open
from the second notebook."""))

c.append(code("""con.close()
print(f"Database '{db_path}' is ready.")
print("You can now open Notebook 2 to start querying.")"""))

# Write the notebook
with open('/sessions/happy-laughing-dijkstra/mnt/coffee_shop/coffee_shop_build_db.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Notebook 1 written successfully.")
