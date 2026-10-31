import marimo


__generated_with = "0.23.10"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    # Jupyter's IPython.display.display() shim, since these
    # notebooks call display() directly for mid-cell output.
    try:
        from IPython.display import display
    except ImportError:
        def display(x):
            print(x)
    return (display,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Shopify Sales Data - Setup Notebook

    This notebook performs the following steps:

    1. Load the CSV file into a DuckDB database

    2. Deduplicate the data (remove full duplicate rows)

    3. Move records with missing/NULL order_id to an investigation table


    **Dataset:** shopify_sales_dataset_ml_eda.csv (60,020 records)

    **Output:** shopify_sales.duckdb
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 0: Import Libraries
    """)
    return


@app.cell
def _():
    import duckdb
    import pandas as pd
    import os

    print("Libraries loaded successfully!")
    return duckdb, os


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 1: Load CSV and Create DuckDB Database

    We read the CSV file  and load it into a 
    persistent DuckDB database file called .

    DuckDB is an in-process analytical database that excels at:
    - Fast analytical queries on columnar data
    - SQL-based analysis without needing a server
    - Direct CSV/Parquet ingestion

    We use  which automatically detects column types, delimiters, and headers.
    """)
    return


@app.cell
def _(duckdb, os):
    # Remove existing database file if it exists (fresh start)
    db_path = "shopify_sales.duckdb"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing {db_path}")

    # Create a persistent DuckDB database
    con = duckdb.connect(db_path)

    # Load CSV into a table called "sales"
    con.execute("""
        CREATE TABLE sales AS
        SELECT * FROM read_csv_auto('shopify_sales_dataset_ml_eda.csv')
    """)

    # Verify the load
    row_count = con.execute("SELECT COUNT(*) AS total_rows FROM sales").fetchdf()
    print(f"Total rows loaded: {row_count['total_rows'][0]:,}")
    print()

    # Show table schema
    print("Table Schema:")
    print("=" * 50)
    schema = con.execute("DESCRIBE sales").fetchdf()
    print(schema.to_string(index=False))
    print()

    # Preview first 5 rows
    print("First 5 rows:")
    con.execute("SELECT * FROM sales LIMIT 5").fetchdf()
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 2: Deduplicate the Data

    ### What is Deduplication?

    Deduplication means removing **full duplicate rows** — rows where every single 
    column has the same value as another row. This can happen due to:
    - ETL pipeline errors (data loaded more than once)
    - Application bugs that insert the same record multiple times
    - Data export/import issues

    ### How We Dedup in DuckDB

    We use a **window function** approach with :

    1. **Partition** rows by ALL columns — identical rows land in the same partition
    2. **Number** them within each partition using 
    3. **Keep only** the first occurrence (row_number = 1), effectively dropping duplicates

    This is equivalent to  but gives us the ability to count 
    how many duplicates were removed.



    An alternative simpler approach is:

    Both produce the same result. We use  for simplicity below.
    """)
    return


@app.cell
def _(con):
    # Count duplicates before dedup
    total_before = con.execute("SELECT COUNT(*) AS cnt FROM sales").fetchall()[0][0]
    distinct_count = con.execute("SELECT COUNT(*) AS cnt FROM (SELECT DISTINCT * FROM sales)").fetchall()[0][0]
    duplicates = total_before - distinct_count

    print(f"Total rows BEFORE dedup: {total_before:,}")
    print(f"Distinct rows:           {distinct_count:,}")
    print(f"Duplicate rows found:    {duplicates:,}")
    print()

    # Perform deduplication: replace the table with distinct rows
    con.execute("""    
        CREATE OR REPLACE TABLE sales AS
        SELECT DISTINCT * FROM sales
    """)

    # Verify
    total_after = con.execute("SELECT COUNT(*) AS cnt FROM sales").fetchall()[0][0]
    print(f"Total rows AFTER dedup:  {total_after:,}")
    print(f"Rows removed:            {total_before - total_after:,}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Step 3: Handle Missing/NULL order_id Records

    Records without an  cannot be reliably linked to a transaction.
    Rather than deleting them, we move them to a separate  
    table for further review. This preserves data integrity while keeping the 
    main  table clean for analysis.
    """)
    return


@app.cell
def _(con, display):
    # Check how many records have NULL or missing order_id
    null_count = con.execute("""
        SELECT COUNT(*) AS cnt
        FROM sales
        WHERE order_id IS NULL
    """).fetchall()[0][0]

    print(f"Records with NULL order_id: {null_count:,}")
    print()

    # Create the investigate_records table with those rows
    con.execute("""
        CREATE OR REPLACE TABLE investigate_records AS
        SELECT *
        FROM sales
        WHERE order_id IS NULL
    """)

    # Remove them from the main sales table
    con.execute("""
        DELETE FROM sales
        WHERE order_id IS NULL
    """)

    # Verify
    sales_count = con.execute("SELECT COUNT(*) FROM sales").fetchall()[0][0]
    invest_count = con.execute("SELECT COUNT(*) FROM investigate_records").fetchall()[0][0]

    print(f"Records in sales table:             {sales_count:,}")
    print(f"Records in investigate_records:      {invest_count:,}")
    print(f"Total accounted for:                 {sales_count + invest_count:,}")

    if invest_count > 0:
        print("Sample of investigate_records:")
        display(con.execute("SELECT * FROM investigate_records LIMIT 5").fetchdf())
    else:
        print("No NULL order_id records found - all records are clean!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Summary
    """)
    return


@app.cell
def _(con):
    # Final summary of all tables in the database
    print("===========")
    print("DATABASE SUMMARY: shopify_sales.duckdb")
    print("===========")

    tables = con.execute("SHOW TABLES").fetchdf()
    print(f"Tables in database: {list(tables['name'])}")
    print()

    for table in tables['name']:
        count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchall()[0][0]
        print(f"  {table}: {count:,} rows")

    print("===========")
    print("Setup complete! The database is ready for querying.")
    print("Open the queries notebook to begin analysis.")
    print("===========")

    # Close the connection
    con.close()
    return


if __name__ == "__main__":
    app.run()

