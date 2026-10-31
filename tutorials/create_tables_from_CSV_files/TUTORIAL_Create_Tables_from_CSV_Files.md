# Data Engineering with DuckDB: CSV Ingestion 101

This tutorial is designed to guide students through the nuances of CSV ingestion in DuckDB. It covers the transition from basic auto-detection to fine-grained schema control.

---


One of DuckDB's most powerful features is its ability to treat CSV files as first-class citizens, often querying them faster than other databases can even import them.

## 1. Setup and Environment

First, we need to install the DuckDB Python client and create a connection. We will use an **in-memory** database for this lab.

```python
import duckdb
import pandas as pd
import os

# Create an in-memory DuckDB connection
con = duckdb.connect(database=':memory:')

# Helper function to create sample CSVs for the demo
def setup_sample_data():
    # 1. Standard CSV with headers
    with open('users_header.csv', 'w') as f:
        f.write("user_id,username,join_date\n1,alice,2023-01-15\n2,bob,2023-02-20\n3,charlie,2023-03-05")
    
    # 2. CSV without headers
    with open('logs_no_header.csv', 'w') as f:
        f.write("101,2023-01-15 10:00:00,LOGIN\n102,2023-01-15 10:05:00,LOGOUT")

setup_sample_data()
print("Sample files 'users_header.csv' and 'logs_no_header.csv' created.")

```

---

## 2. Basic Ingestion: The `read_csv` Function

DuckDB uses a sophisticated "Sniffing" algorithm to detect headers, delimiters, and data types automatically.

### A. Direct Querying (No Table Creation)

You don't always need to "import" data to query it. This is great for quick exploration.

```python
# Querying a file directly using the read_csv function
res = con.sql("SELECT * FROM read_csv('users_header.csv')")
res.show()

```

### B. Creating a Persistent Table

To create a formal table, we wrap the read function in a `CREATE TABLE` statement.

```python
# Create table from CSV
con.sql("CREATE TABLE users AS SELECT * FROM read_csv('users_header.csv')")

# Verify schema
con.sql("DESCRIBE users").show()

```

---

## 3. Handling Files Without Headers

When a CSV lacks a header row, DuckDB's sniffer might misinterpret the first row of data as column names. We use the `header=False` parameter and provide custom names.

```python
# Ingesting logs without headers
# We use the names parameter to define our schema on the fly
con.sql("""
    CREATE TABLE access_logs AS 
    SELECT * FROM read_csv(
        'logs_no_header.csv', 
        header=False, 
        names=['event_id', 'event_timestamp', 'event_type']
    )
""")

con.sql("SELECT * FROM access_logs").show()

```

---

## 4. Advanced Configuration: Explicit Typing

In production environments, relying on "sniffing" can be risky. If a column is empty in the first 100 rows, DuckDB might guess the wrong type. We can enforce types using the `columns` parameter.

```python
# Defining explicit types (using a struct-like syntax for columns)
con.sql("""
    CREATE TABLE strict_users AS 
    SELECT * FROM read_csv(
        'users_header.csv',
        columns={
            'user_id': 'INTEGER',
            'username': 'VARCHAR',
            'join_date': 'DATE'
        }
    )
""")

con.sql("DESCRIBE strict_users").show()

```

---

## 5. Pro-Tip: The "Auto" Replacement

DuckDB provides a shorthand for table creation that is even more concise. If you don't need to transform the data during import, you can use the `read_csv_auto` function or simply refer to the file string.

```python
# The 'Magic' way: DuckDB infers everything from the file extension
con.sql("CREATE TABLE auto_users AS SELECT * FROM 'users_header.csv'")

# View the result
print(con.table("auto_users").fetchall())

```

---

## Summary for Students

* **`read_csv()`**: The primary function for reading CSVs.
* **Sniffing**: DuckDB automatically detects delimiters (`,` vs `;`) and types.
* **`header=False`**: Crucial for legacy data files.
* **Performance**: DuckDB reads CSVs in parallel. For massive datasets, it is significantly faster than standard `pd.read_csv()`.

### Exercises for the Lab

1. **Mismatch**: Try importing `users_header.csv` but set `header=False`. Observe how the header row becomes the first row of data.
2. **Globbing**: Create a third CSV and try `SELECT * FROM read_csv('*.csv')`. DuckDB will union them automatically!

---

**Note:** Always remember to close your connection when working with file-based databases (though not strictly required for `:memory:`).

```python
con.close()

```
