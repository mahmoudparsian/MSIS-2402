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
    # Data Engineering with DuckDB: <br> CSV/Parquet Ingestion 101

    This notebook is designed to guide students through the nuances of CSV ingestion in DuckDB. It covers the transition from basic auto-detection to fine-grained schema control.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One of DuckDB's most powerful features is its ability to treat CSV files as first-class citizens, often querying them faster than other databases can even import them.

    ## 1. Setup and Environment

    First, we need to install the DuckDB Python client and create a connection. We will use an **in-memory** database for this lab.
    """)
    return


@app.cell
def _():
    import duckdb
    import pandas as pd
    import os

    # Create an in-memory DuckDB connection
    con = duckdb.connect(database=':memory:')

    # Helper function to create sample CSVs for the demo
    def setup_sample_data():
        os.makedirs('./data', exist_ok=True)

        # 1. Standard CSV with headers
        with open('./data/users_header.csv', 'w') as f:
            f.write("user_id,username,join_date\n100,alice,2023-01-15\n200,bob,2023-02-20\n300,charlie,2023-03-05")

        # 2. CSV without headers
        with open('./data/logs_no_header.csv', 'w') as f:
            f.write("101,2023-01-15 10:00:00,LOGIN\n102,2023-01-15 10:05:00,LOGOUT")

    setup_sample_data()
    print("Sample files './data/users_header.csv' and './data/logs_no_header.csv' created.")

    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 2. Basic Ingestion: The `read_csv` Function

    DuckDB uses a sophisticated "Sniffing" algorithm to detect headers, delimiters, and data types automatically.

    ### A. Direct Querying (No Table Creation)

    You don't always need to "import" data to query it. This is great for quick exploration.
    """)
    return


@app.cell
def _(con):
    # Querying a file directly using the read_csv function
    res = con.sql("SELECT * FROM read_csv('./data/users_header.csv')")
    res.show()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B. Creating a Persistent Table

    To create a formal table, we wrap the read function in a `CREATE TABLE` statement.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE users AS
        SELECT *
        FROM read_csv('./data/users_header.csv')
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        DESCRIBE users
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo, users):
    _df = mo.sql(
        f"""
        SELECT *
        from users
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 3. Handling Files Without Headers

    When a CSV lacks a header row, DuckDB's sniffer might misinterpret the first row of data as column names. We use the `header=False` parameter and provide custom names.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        CREATE OR REPLACE TABLE access_logs AS
        SELECT *
        FROM read_csv('./data/logs_no_header.csv', header=False, names=[ 'event_id', 'event_timestamp', 'event_type' ])
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        DESCRIBE users
        """,
        engine=con
    )
    return


@app.cell
def _(access_logs, con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM access_logs
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 4. Advanced Configuration: Explicit Typing

    Relying on "sniffing" can be risky. DuckDB guesses each column's type from a **sample of rows — 20,480 by default** (the `sample_size` option). If a value that doesn't fit the guess appears only later — say the code `ABC` in row 30,000 of a column that was all numbers until then — reading the file fails with a `Conversion Error`. To be safe, give the types yourself with the `columns` parameter (below), or let the sniffer read the whole file with `sample_size=-1`.
    """)
    return


@app.cell
def _(con):
    # Defining explicit types (using a struct-like syntax for columns)
    con.sql("""
        CREATE OR REPLACE TABLE strict_users AS 
        SELECT * FROM read_csv(
            './data/users_header.csv',
            columns={
                'user_id': 'INTEGER',
                'username': 'VARCHAR',
                'join_date': 'DATE'
            }
        )
    """)

    con.sql("DESCRIBE strict_users").show()

    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 5. Pro-Tip: The "Auto" Replacement

    DuckDB provides a shorthand for table creation that is even more concise. If you don't need to transform the data during import, you can use the `read_csv_auto` function or simply refer to the file string.
    """)
    return


@app.cell
def _(con):
    # The 'Magic' way: DuckDB infers everything from the file extension
    con.sql("""
    CREATE OR REPLACE TABLE auto_users 
    AS 
    SELECT * FROM './data/users_header.csv'
    """)

    # View the result
    con.table("auto_users").fetchall()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Reading Parquet Files
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ```
        Parquet is the "gold standard" for analytical data storage 
        because it is columnar and compressed. Since DuckDB is a 
        columnar engine, reading Parquet files is even more efficient 
        than reading CSVs: the column types are stored in the file,
        and DuckDB reads only the columns your query needs.
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 1. Direct Querying (The "No-Install" Way)
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM 'data/users4.parquet';
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        SELECT *
        FROM 'data/users4.parquet'
        WHERE age > 27;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 2. Creating a Persistent Table
    """)
    return


@app.cell
def _(con):
    # If you want to move the data from the Parquet file 
    # into the DuckDB database (either in-memory or on-disk), 
    # use the `CREATE TABLE` syntax.

    ### A. Automatic Schema Inference
    ### DuckDB will automatically adopt the column names and 
    ### data types defined inside the Parquet metadata.

    con.sql("""
    CREATE TABLE users4
    AS 
    SELECT * FROM 'data/users4.parquet';
    """)

    con.sql("SELECT * FROM users4;").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### B. Creating a View (The Efficient Alternative)

    ### If you don't want to duplicate the data (which saves disk space), 
    ### you can create a **VIEW**. This makes the Parquet file look like 
    ### a table, but the data stays in the original file.

    ```sql
    CREATE VIEW my_view 
    AS 
    SELECT * FROM 'data/users4.parquet';
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 3. Reading Multiple Files (Globbing)

    ```
    If you have a folder full of Parquet files (e.g., 
    partitioned by date), DuckDB can read them all 
    at once using "glob" patterns.
    ```

    These are **patterns to adapt** — this tutorial's `data/` folder holds a single
    Parquet file, so there is nothing here for them to read.

    ```sql
    -- Read all parquet files in the 'uploads' folder
    CREATE TABLE all_data AS SELECT * FROM 'uploads/*.parquet';

    -- Read files from a nested hive-partitioned directory
    SELECT * FROM read_parquet('data/**/*.parquet', hive_partitioning = true);
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 4. Reading from Remote Sources (S3/HTTP)

    One of DuckDB's "superpowers" is reading Parquet
    files directly from the cloud without downloading
    the whole file first. (An example to adapt — the URL below is a placeholder.)

    ```sql
    -- First, load the httpfs extension
    INSTALL httpfs;
    LOAD httpfs;

    -- Query a file from a public URL or S3 bucket
    SELECT * FROM 'https://data.example.com/transactions.parquet' LIMIT 10;

    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # Summary Table: CSV vs. Parquet Ingestion

    | Feature | CSV Ingestion | Parquet Ingestion |
    | --- | --- | --- |
    | **Schema** | Must be "sniffed" or defined | Metadata is built-in |
    | **Speed** | Moderate (Parsing required) | Extremely Fast (Native format) |
    | **Storage** | Larger (Plain text) | Smaller (Compressed) |
    | **Projection** | Reads all columns | Only reads requested columns |

    > **Pro-Tip:** If you are dealing with very large datasets, prefer **`CREATE VIEW`** over **`CREATE TABLE`**. This allows you to leverage DuckDB's speed while keeping your database file size small.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Summary for Students

    * **`read_csv()`**: The primary function for reading CSVs.
    * **Sniffing**: DuckDB automatically detects delimiters (`,` vs `;`) and types.
    * **`header=False`**: Crucial for legacy data files.
    * **Performance**: DuckDB reads CSVs in parallel. For massive datasets, it is significantly faster than standard `pd.read_csv()`.

    ### Exercises for the Lab

    1. **Mismatch**: Try importing `users_header.csv` but set `header=False`. Observe how the header row becomes the first row of data.
    2. **Globbing**: create `data/users_more.csv` with the **same three columns** as `users_header.csv` (for example the rows `400,dana,2023-04-10` and `500,erin,2023-05-12`), then run `SELECT * FROM read_csv('data/users*.csv') ORDER BY user_id`. DuckDB reads both files as one table — 5 rows. (`read_csv('data/*.csv')` would fail with `Schema mismatch between globbed files`: `logs_no_header.csv` has different columns.)

    ---

    **Note:** Always remember to close your connection when working with file-based databases (though not strictly required for `:memory:`).
    """)
    return


@app.cell
def _():
    # con.close()

    return


if __name__ == "__main__":
    app.run()

