import marimo


__generated_with = "0.23.10"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Coffee Shop Sales — Build DuckDB Database

    This notebook 

    * reads the raw Excel file **coffee_shop_sales.xlsx**, 
    * cleans the data, and
    * stores it in a persistent **DuckDB** database file (`coffee_shop_sales.duckdb`).

    ### Steps
    1. Import libraries
    2. Load the Excel file into a Pandas DataFrame
    3. Inspect the raw data
    4. Check for and remove duplicate rows
    5. Standardize the `transaction_date` column
    6. Extract useful time features (hour, day-of-week, month, etc.)
    7. Compute derived measures (`sales_amount`)
    8. Write the cleaned table into a DuckDB database file

    > **Prerequisite:** place `coffee_shop_sales.xlsx` in the same folder as this notebook.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 1 — Import libraries

    ### What are we doing?
    We import the Python libraries needed for file loading, data cleaning, and DuckDB database creation.

    ### Why?
    Setting up all dependencies at the top keeps the notebook clean and ensures
    any missing packages are caught early.
    """)
    return


@app.cell
def _():
    import warnings
    warnings.filterwarnings("ignore")

    import pandas as pd
    import numpy as np
    import duckdb
    import datetime
    from pathlib import Path

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

    print("Libraries loaded successfully.")
    return Path, datetime, duckdb, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 2 — Load the Excel file

    ### What are we doing?
    We read `coffee_shop_sales.xlsx` into a Pandas DataFrame. If the Excel file
    is not found, we fall back to a CSV version (`coffee_shop_sales.csv`).

    ### Why?
    Some students may not have the `openpyxl` dependency installed.
    Supporting both formats avoids unnecessary setup friction.
    """)
    return


@app.cell
def _(Path, pd):
    xlsx_path = Path("coffee_shop_sales.xlsx")
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
    df.head()
    return (df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 3 — Inspect the raw data

    ### What are we doing?
    We examine column names, data types, and non-null counts.

    ### Why?
    Understanding the raw structure tells us which columns need type
    conversion, which may have nulls, and what cleaning is required.
    """)
    return


@app.cell
def _(df):
    df.info()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 4 — Check for duplicate rows

    ### What are we doing?
    We count **exact** duplicate rows — rows where every column value is identical.

    ### Why?
    Duplicate transaction lines inflate counts, quantities, and revenue.
    In transactional data this is a critical data-quality check.

    ### How deduplication works
    `df.duplicated()` returns `True` for every row that has already appeared
    earlier with identical values in **all** columns. We count those rows,
    then drop them with `drop_duplicates()`.
    """)
    return


@app.cell
def _(df):
    dup_count = df.duplicated().sum()
    print(f"Exact duplicate rows found: {dup_count:,}")

    if dup_count > 0:
        print(f"Dropping {dup_count:,} duplicates ...")
        df_2 = df.drop_duplicates().reset_index(drop=True)
        print(f"Shape after dedup: {df_2.shape}")
    else:
        df_2 = df
        print("No duplicates — the dataset is already clean.")
    return (df_2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 5 — Standardize `transaction_date`

    ### What are we doing?
    We convert `transaction_date` to a proper `datetime64` type. The raw column
    may come in as `dd-mm-yy`, `yyyy-mm-dd`, or an Excel serial date —
    so we try multiple formats and let Pandas pick the best one.

    ### Why?
    A consistent date type is essential for:
    - date arithmetic (e.g., date ranges, differences)
    - SQL `WHERE` / `GROUP BY` on dates
    - extracting year, month, day, and day-of-week
    """)
    return


@app.cell
def _(df_2, pd):
    # Attempt 1 — let Pandas auto-detect
    df_2["transaction_date"] = pd.to_datetime(df_2["transaction_date"], errors="coerce")

    # If everything came back NaT, try dd-mm-yy explicitly
    if df_2["transaction_date"].isna().all():
        df_2["transaction_date"] = pd.to_datetime(
            df_2["transaction_date"], format="%d-%m-%y", errors="coerce"
        )

    valid_dates = df_2["transaction_date"].notna().sum()
    print(f"Valid dates : {valid_dates:,} / {len(df_2):,}")
    print(f"Date range  : {df_2['transaction_date'].min()} → {df_2['transaction_date'].max()}")
    df_2[["transaction_id", "transaction_date"]].head()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 6 — Extract hour from `transaction_time`

    ### What are we doing?
    Excel may store `transaction_time` as a `datetime.time` object or as a
    string like `"07:06:11"`. We robustly extract the **hour** regardless
    of the underlying type.

    ### Why?
    The hour column enables time-of-day analysis (peak hours, morning vs.
    afternoon) — one of the most valuable business insights in retail data.
    """)
    return


@app.cell
def _(datetime, df_2, pd):
    def extract_hour(x):
        """Return the integer hour from various time representations."""
        if pd.isna(x):
            return None
        if isinstance(x, datetime.time):
            return x.hour
        try:
            return pd.to_datetime(str(x)).hour
        except Exception:
            return None

    df_2["hour"] = df_2["transaction_time"].apply(extract_hour)

    valid_hours = df_2["hour"].notna().sum()
    print(f"Valid hours: {valid_hours:,} / {len(df_2):,}")
    print(f"Hour range : {int(df_2['hour'].min())} – {int(df_2['hour'].max())}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 7 — Create derived columns

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
    to write date-extraction functions in every SQL query.
    """)
    return


@app.cell
def _(df_2, pd):
    # Ensure numerics
    for col in ["transaction_qty", "unit_price"]:
        df_2[col] = pd.to_numeric(df_2[col], errors="coerce")

    df_2["sales_amount"] = df_2["transaction_qty"] * df_2["unit_price"]

    df_2["year"]       = df_2["transaction_date"].dt.year
    df_2["month"]      = df_2["transaction_date"].dt.month
    df_2["month_name"] = df_2["transaction_date"].dt.month_name()
    df_2["day"]        = df_2["transaction_date"].dt.day
    df_2["day_name"]   = df_2["transaction_date"].dt.day_name()

    print(f"Total revenue: ${df_2['sales_amount'].sum():,.2f}")
    df_2[["transaction_id", "transaction_date", "hour", "sales_amount",
        "year", "month_name", "day_name"]].head(10)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 8 — Validate the cleaned DataFrame

    ### What are we doing?
    A final sanity check before writing to DuckDB:
    - Row count
    - Null summary
    - Basic statistics

    ### Why?
    Writing bad data to a database propagates problems downstream.
    It is good practice to validate before persisting.
    """)
    return


@app.cell
def _(df_2):
    print("Shape:", df_2.shape)
    print()
    print("Null counts:")
    print(df_2.isna().sum())
    print()
    df_2.describe(include="all")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 9 — Create the DuckDB database file

    ### What are we doing?
    We open a **persistent** DuckDB connection pointing to `coffee_shop_sales.duckdb`.
    Then we write the cleaned DataFrame as a table called `sales`.

    ### Why?
    A persistent `.duckdb` file means:
    - the data survives after the notebook is closed
    - the second notebook can simply open the same file and start querying
    - no need to re-run the cleaning pipeline every time
    """)
    return


@app.cell
def _(Path, df_2, duckdb):
    db_path = "coffee_shop_sales.duckdb"

    # Remove old database if it exists so we get a clean build
    if Path(db_path).exists():
        Path(db_path).unlink()

    con = duckdb.connect(db_path)

    # Register the DataFrame and write it as a permanent table
    con.register("df_temp", df_2)

    con.execute("""
        CREATE TABLE sales AS
        SELECT * FROM df_temp
        WHERE transaction_date IS NOT NULL
          AND transaction_qty IS NOT NULL
          AND unit_price      IS NOT NULL
          AND sales_amount    IS NOT NULL
          AND hour            IS NOT NULL
    """)

    row_count = con.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
    print(f"Rows written to '{db_path}': {row_count:,}")
    return con, db_path


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 10 — Verify the database

    ### What are we doing?
    We query the freshly created DuckDB table to confirm the data is
    accessible and looks correct.

    ### Why?
    Always verify a write operation. A quick `SELECT` confirms the
    table exists, the schema is correct, and the data is readable.
    """)
    return


@app.cell
def _(con):
    # Show schema
    print("Table schema:")
    print(con.execute("DESCRIBE sales").df().to_string(index=False))
    print()

    # Sample rows
    print("Sample rows:")
    con.execute("SELECT * FROM sales LIMIT 5").df()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 11 — Quick summary statistics via SQL

    ### What are we doing?
    We run a single summary query to produce a high-level profile:
    total rows, total units, total revenue, distinct stores, distinct products,
    and the date range.

    ### Why?
    This gives us (and any student opening the second notebook) a fast
    executive-style overview of what is inside the database.
    """)
    return


@app.cell
def _(con, mo, sales):
    _df = mo.sql(
        f"""
        SELECT
            COUNT(*) AS total_rows,
            SUM(transaction_qty) AS total_units_sold,
            ROUND(SUM(sales_amount), 2) AS total_revenue,
            COUNT(DISTINCT store_id) AS distinct_stores,
            COUNT(DISTINCT product_id) AS distinct_products,
            MIN(transaction_date) AS first_date,
            MAX(transaction_date) AS last_date
        FROM sales
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cell 12 — Close the connection

    ### What are we doing?
    We close the DuckDB connection to flush all data to disk.

    ### Why?
    Closing ensures the file is fully written and safe to open
    from the second notebook.
    """)
    return


@app.cell
def _(con, db_path):
    con.close()
    print(f"Database '{db_path}' is ready.")
    print("You can now open Notebook 2 to start querying.")
    return


if __name__ == "__main__":
    app.run()

