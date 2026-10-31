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
    # DuckDB User-Defined Functions: A Comprehensive Tutorial

    ```
    DuckDB allows you to extend its built-in function 
    library by creating your own functions. 

    This tutorial covers **every type** of user-created 
    function available in DuckDB:
    ```

    | Function Type | Mechanism | Returns |
    |---|---|---|
    | **Scalar Macro** | `CREATE MACRO` | A single value per row |
    | **Table Macro** | `CREATE MACRO ... AS TABLE` | A table (set of rows) |
    | **Python Scalar UDF** | `duckdb.create_function()` | A single value per row (Python logic) |

    We'll use an **e-commerce** schema throughout to keep examples realistic and interconnected.

    **Important API note:** Throughout this tutorial we use two different methods:
    - `con.execute()` — for DDL statements (CREATE, INSERT, DROP) that don't return rows. Returns a connection object.
    - `con.sql()` — for SELECT queries where we want to display results. Returns a `DuckDBPyRelation` object that supports `.show()`, `.df()`, etc.

    ---
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Setup and Installation
    """)
    return


@app.cell
def _():
    # Install duckdb if needed
    # !pip install duckdb

    import duckdb

    # Create an in-memory database connection
    con = duckdb.connect(database=':memory:')

    print(f"DuckDB version: {duckdb.__version__}")
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 2. Building the E-Commerce Schema

    We create four tables that model a simple e-commerce system:

    - **customers** — who is buying
    - **products** — what is for sale (with cost and price)
    - **orders** — each purchase event
    - **order_items** — line items linking orders to products

    This gives us numeric, text, date, and relational data to work with across all function types.
    """)
    return


@app.cell
def _(con):
    # Customers table
    con.execute("""
    CREATE TABLE customers (
        customer_id   INTEGER PRIMARY KEY,
        first_name    VARCHAR,
        last_name     VARCHAR,
        email         VARCHAR,
        country       VARCHAR,
        joined_date   DATE
    );
    """)

    con.execute("""
    INSERT INTO customers VALUES
        (1, 'Alice',   'Johnson',  'alice@example.com',   'US', '2023-01-15'),
        (2, 'Bob',     'Smith',    'bob@example.com',     'UK', '2023-03-22'),
        (3, 'Carlos',  'Garcia',   'carlos@example.com',  'MX', '2023-06-01'),
        (4, 'Diana',   'Chen',     'diana@example.com',   'US', '2024-01-10'),
        (5, 'Emiko',   'Tanaka',   'emiko@example.com',   'JP', '2024-02-28');
    """)

    # Products table (cost = what we pay, price = what we charge)
    con.execute("""
    CREATE TABLE products (
        product_id    INTEGER PRIMARY KEY,
        product_name  VARCHAR,
        category      VARCHAR,
        cost          DECIMAL(10,2),
        price         DECIMAL(10,2),
        weight_kg     DOUBLE
    );
    """)

    con.execute("""
    INSERT INTO products VALUES
        (101, 'Wireless Mouse',      'Electronics', 8.50,  24.99, 0.15),
        (102, 'USB-C Hub',           'Electronics', 15.00, 49.99, 0.25),
        (103, 'Notebook Journal',    'Stationery',  2.00,  12.99, 0.30),
        (104, 'Mechanical Keyboard', 'Electronics', 35.00, 89.99, 0.85),
        (105, 'Desk Lamp',          'Home',         12.00, 34.99, 1.20),
        (106, 'Coffee Mug',         'Home',         3.00,   9.99, 0.40);
    """)

    # Orders table
    con.execute("""
    CREATE TABLE orders (
        order_id      INTEGER PRIMARY KEY,
        customer_id   INTEGER REFERENCES customers(customer_id),
        order_date    DATE,
        status        VARCHAR
    );
    """)

    con.execute("""
    INSERT INTO orders VALUES
        (1001, 1, '2024-03-01', 'delivered'),
        (1002, 2, '2024-03-05', 'delivered'),
        (1003, 1, '2024-03-15', 'shipped'),
        (1004, 3, '2024-04-02', 'delivered'),
        (1005, 4, '2024-04-10', 'pending'),
        (1006, 5, '2024-04-12', 'returned'),
        (1007, 2, '2024-05-01', 'shipped'),
        (1008, 3, '2024-05-15', 'delivered');
    """)

    # Order items (line items)
    con.execute("""
    CREATE TABLE order_items (
        item_id       INTEGER PRIMARY KEY,
        order_id      INTEGER REFERENCES orders(order_id),
        product_id    INTEGER REFERENCES products(product_id),
        quantity      INTEGER,
        unit_price    DECIMAL(10,2)
    );
    """)

    con.execute("""
    INSERT INTO order_items VALUES
        (1, 1001, 101, 2, 24.99),
        (2, 1001, 103, 1, 12.99),
        (3, 1002, 102, 1, 49.99),
        (4, 1002, 106, 3,  9.99),
        (5, 1003, 104, 1, 89.99),
        (6, 1004, 101, 1, 24.99),
        (7, 1004, 105, 2, 34.99),
        (8, 1005, 102, 1, 49.99),
        (9, 1005, 103, 4, 12.99),
        (10, 1006, 104, 1, 89.99),
        (11, 1007, 106, 5,  9.99),
        (12, 1007, 105, 1, 34.99),
        (13, 1008, 101, 3, 24.99),
        (14, 1008, 103, 2, 12.99);
    """)

    print("Schema created successfully!")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Let's verify our data:
    """)
    return


@app.cell
def _(con):
    # Quick look at all tables
    for table in ['customers', 'products', 'orders', 'order_items']:
        print(f"\n{'='*60}")
        print(f"  {table.upper()}")
        print(f"{'='*60}")
        con.sql(f"SELECT * FROM {table}").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 3. SQL Scalar Macros (`CREATE MACRO`)

    A **scalar macro** is the simplest user-defined function in DuckDB. It takes one or more inputs and returns a single value per row — just like built-in functions such as `UPPER()` or `ROUND()`.

    **Syntax:**
    ```sql
    CREATE [OR REPLACE] [TEMP] MACRO function_name(param1, param2, ...) AS expression;
    ```

    Key points:
    - Macros are **expression-based** — the body is a single SQL expression (no `BEGIN...END` blocks).
    - They are **inlined** at query time, so there is zero function-call overhead.
    - Use `OR REPLACE` to overwrite an existing macro.
    - Use `TEMP` if you only need the macro for the current session.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.1 Simple Scalar Macro — Profit Margin

    Our products table has `cost` and `price`. Let's create a function that computes the profit margin as a percentage.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO profit_margin(cost, price) AS
        ROUND(((price - cost) / price) * 100, 2)
    """)

    # Use it
    con.sql("""
    SELECT product_name,
           cost,
           price,
           profit_margin(cost, price) AS margin_pct
    FROM products
    ORDER BY margin_pct DESC
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **What happened?** DuckDB replaced `profit_margin(cost, price)` with the inline expression `ROUND(((price - cost) / price) * 100, 2)` at query planning time. There's no function call overhead — it's pure syntactic sugar that makes your SQL cleaner and reusable.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.2 Scalar Macro with Conditional Logic (CASE)

    Macros can contain any valid SQL expression, including `CASE WHEN`. Let's create a function that categorizes profit margins into tiers.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO margin_tier(cost, price) AS
        CASE
            WHEN ((price - cost) / price) * 100 >= 70 THEN 'Premium'
            WHEN ((price - cost) / price) * 100 >= 50 THEN 'Healthy'
            WHEN ((price - cost) / price) * 100 >= 30 THEN 'Standard'
            ELSE 'Low'
        END
    """)

    con.sql("""
    SELECT product_name,
           profit_margin(cost, price) AS margin_pct,
           margin_tier(cost, price)   AS tier
    FROM products
    ORDER BY margin_pct DESC
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Notice how we can use **one macro inside the same query as another** — `profit_margin` and `margin_tier` side by side. Each is independently inlined.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.3 Scalar Macro with Default Parameters

    DuckDB macros support **default parameter values** using the `:=` operator. This is great for functions where a common case exists but you want flexibility.

    Let's create a shipping cost estimator where the rate per kg defaults to 5.00 but can be overridden.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO shipping_cost(weight_kg, quantity, rate_per_kg := 5.00) AS
        ROUND(weight_kg * quantity * rate_per_kg, 2)
    """)

    # Use with default rate, then with custom express rate
    con.sql("""
    SELECT product_name,
           weight_kg,
           shipping_cost(weight_kg, 1)           AS ship_1_default,
           shipping_cost(weight_kg, 1, 8.50)     AS ship_1_express,
           shipping_cost(weight_kg, 3)           AS ship_3_default
    FROM products
    ORDER BY weight_kg
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Key detail:** Default parameters use `:=` (not `=`) in the macro definition. When calling the function, you can either pass the argument positionally or skip it to use the default.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.4 Scalar Macro Calling Other Macros

    Macros can reference other macros — DuckDB resolves them recursively. Let's build a `total_line_cost` macro that uses our `shipping_cost` macro to compute the full cost of a line item (product price × quantity + shipping).
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO total_line_cost(unit_price, quantity, weight_kg) AS
        ROUND((unit_price * quantity) + shipping_cost(weight_kg, quantity), 2)
    """)

    con.sql("""
    SELECT oi.item_id,
           p.product_name,
           oi.unit_price,
           oi.quantity,
           p.weight_kg,
           shipping_cost(p.weight_kg, oi.quantity) AS shipping,
           total_line_cost(oi.unit_price, oi.quantity, p.weight_kg) AS total
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    ORDER BY total DESC
    LIMIT 8
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.5 Scalar Macro with String Operations

    Macros work with any SQL expression — including string functions. Here we build a `full_name` formatter and a `mask_email` privacy helper.
    """)
    return


@app.cell
def _(con):
    # full_name: "LastName, FirstName"
    con.execute("""
    CREATE OR REPLACE MACRO full_name(first_name, last_name) AS
        last_name || ', ' || first_name
    """)

    # mask_email: show first 2 chars, then ***, then domain
    con.execute("""
    CREATE OR REPLACE MACRO mask_email(email) AS
        LEFT(email, 2) || '***' || SUBSTRING(email FROM POSITION('@' IN email))
    """)

    con.sql("""
    SELECT full_name(first_name, last_name) AS name,
           mask_email(email) AS masked_email,
           country
    FROM customers
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 3.6 Using Macros in WHERE, GROUP BY, and ORDER BY

    Macros aren't limited to the `SELECT` list — you can use them anywhere an expression is valid.
    """)
    return


@app.cell
def _(con):
    # Find only "Premium" margin products
    print("Products with Premium margins:")
    con.sql("""
    SELECT product_name,
           profit_margin(cost, price) AS margin_pct
    FROM products
    WHERE margin_tier(cost, price) = 'Premium'
    ORDER BY profit_margin(cost, price) DESC
    """).show()

    # Group by margin tier
    print("\nProducts grouped by margin tier:")
    con.sql("""
    SELECT margin_tier(cost, price) AS tier,
           COUNT(*)                 AS product_count,
           ROUND(AVG(profit_margin(cost, price)), 2) AS avg_margin
    FROM products
    GROUP BY margin_tier(cost, price)
    ORDER BY avg_margin DESC
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 4. SQL Table Macros (`CREATE MACRO ... AS TABLE`)

    A **table macro** returns an entire result set — think of it as a parameterized view or an inline table-valued function. You call it in the `FROM` clause.

    **Syntax:**
    ```sql
    CREATE [OR REPLACE] [TEMP] MACRO function_name(params) AS TABLE
        SELECT ...;
    ```

    **When to use table macros vs. scalar macros:**
    - Use a **scalar macro** when you need a computed column (one value per row).
    - Use a **table macro** when you need a reusable, parameterized query that returns rows.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.1 Basic Table Macro — Customer Orders

    A macro that returns all orders for a given customer ID, with the total amount per order.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO customer_orders(cid) AS TABLE
        SELECT o.order_id,
               o.order_date,
               o.status,
               SUM(oi.unit_price * oi.quantity) AS order_total
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.customer_id = cid
        GROUP BY o.order_id, o.order_date, o.status
        ORDER BY o.order_date;
    """)

    # Get Alice's orders (customer_id = 1)
    print("Alice's orders:")
    con.sql("SELECT * FROM customer_orders(1)").show()

    # Get Bob's orders (customer_id = 2)
    print("\nBob's orders:")
    con.sql("SELECT * FROM customer_orders(2)").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Notice the call syntax:** `FROM customer_orders(1)` — table macros appear in the `FROM` clause, just like a table or subquery.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.2 Table Macro with Multiple Parameters and Defaults

    Let's build a product search macro that filters by category and a minimum price, with the category defaulting to all.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO search_products(min_price := 0, cat := NULL) AS TABLE
        SELECT product_id,
               product_name,
               category,
               price,
               profit_margin(cost, price) AS margin_pct
        FROM products
        WHERE price >= min_price
          AND (cat IS NULL OR category = cat)
        ORDER BY price DESC;
    """)

    print("All products over $30:")
    con.sql("SELECT * FROM search_products(min_price := 30)").show()

    print("\nElectronics only:")
    con.sql("SELECT * FROM search_products(cat := 'Electronics')").show()

    print("\nHome products over $10:")
    con.sql("SELECT * FROM search_products(min_price := 10, cat := 'Home')").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Key feature:** When calling with named parameters, you use `:=` syntax: `search_products(cat := 'Electronics')`. This is especially useful when you want to skip earlier defaults.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.3 Table Macro — Order Summary Report

    A more complex table macro that generates a date-filtered sales summary with aggregations.
    """)
    return


@app.cell
def _(con):
    con.execute("""
    CREATE OR REPLACE MACRO sales_report(start_date, end_date) AS TABLE
        SELECT c.first_name || ' ' || c.last_name AS customer,
               COUNT(DISTINCT o.order_id)          AS num_orders,
               SUM(oi.quantity)                     AS items_bought,
               ROUND(SUM(oi.unit_price * oi.quantity), 2) AS revenue,
               ROUND(AVG(oi.unit_price * oi.quantity), 2) AS avg_line_value
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN customers c   ON o.customer_id = c.customer_id
        WHERE o.order_date BETWEEN start_date AND end_date
          AND o.status != 'returned'
        GROUP BY c.customer_id, c.first_name, c.last_name
        ORDER BY revenue DESC;
    """)

    print("Sales report for March 2024:")
    con.sql("SELECT * FROM sales_report('2024-03-01', '2024-03-31')").show()

    print("\nSales report for Q2 2024 (Apr-Jun):")
    con.sql("SELECT * FROM sales_report('2024-04-01', '2024-06-30')").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 4.4 Using a Table Macro Inside Another Query

    Since table macros return a result set, you can use them as subqueries, join them, or wrap them in CTEs.
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        WITH alice_orders AS (SELECT * FROM customer_orders(1))
        SELECT
            order_id,
            order_date,
            order_total
        FROM alice_orders
        WHERE order_total = (SELECT MAX(order_total) FROM alice_orders)
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 5. Listing and Managing Macros

    DuckDB stores macro metadata in its catalog. You can inspect what you've created using `duckdb_functions()`.
    """)
    return


@app.cell
def _(con):
    # List all user-defined scalar macros
    print("=== Scalar Macros ===")
    con.sql("""
    SELECT function_name, parameters, macro_definition
    FROM duckdb_functions()
    WHERE function_type = 'macro'
      AND schema_name = 'main'
    ORDER BY function_name
    """).show()

    # List all user-defined table macros
    print("\n=== Table Macros ===")
    con.sql("""
    SELECT function_name, parameters
    FROM duckdb_functions()
    WHERE function_type = 'table_macro'
      AND schema_name = 'main'
    ORDER BY function_name
    """).show()
    return


@app.cell
def _(con):
    # Dropping a macro (we'll recreate it to demonstrate the workflow)
    con.execute("DROP MACRO IF EXISTS full_name")
    print("Dropped 'full_name' macro.")

    # Recreate it
    con.execute("""
    CREATE MACRO full_name(first_name, last_name) AS
        last_name || ', ' || first_name
    """)
    print("Recreated 'full_name' macro.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 6. Python Scalar UDFs (`create_function`)

    When SQL expressions aren't enough — maybe you need complex string parsing, external libraries, or algorithmic logic — DuckDB lets you register **Python functions** directly.

    **Syntax:**
    ```python
    con.create_function(
        name,            # function name in SQL
        function,        # Python callable
        parameters,      # list of input DuckDB types
        return_type,     # DuckDB return type
        null_handling='default'  # 'default' or 'special'
    )
    ```

    **Key differences from SQL macros:**
    - Python UDFs execute Python code at runtime (not inlined into the query plan).
    - They can use any Python library (regex, math, custom modules, etc.).
    - They have a performance cost due to Python-DuckDB data marshalling.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.1 Simple Python Scalar UDF — Slugify Product Names

    Let's create a function that converts product names to URL-friendly slugs (lowercase, hyphens instead of spaces). This is hard to do cleanly in pure SQL but trivial in Python.
    """)
    return


@app.cell
def _(con):
    import re

    def slugify(text):
        """Convert text to a URL-friendly slug."""
        if text is None:
            return None
        slug = text.lower().strip()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)  # replace non-alphanumeric with hyphens
        slug = slug.strip('-')                     # remove leading/trailing hyphens
        return slug

    # Register with DuckDB
    con.create_function('slugify', slugify, ['VARCHAR'], 'VARCHAR')

    con.sql("""
    SELECT product_name,
           slugify(product_name) AS slug
    FROM products
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.2 Python UDF with Multiple Parameters — Discount Calculator

    A function that applies tiered quantity discounts: 10% off for 3+ items, 20% off for 5+ items.
    """)
    return


@app.cell
def _(con):
    def calc_discount(unit_price, quantity):
        """Apply tiered quantity discount."""
        if unit_price is None or quantity is None:
            return None
        subtotal = float(unit_price) * int(quantity)
        if quantity >= 5:
            return round(subtotal * 0.20, 2)  # 20% discount
        elif quantity >= 3:
            return round(subtotal * 0.10, 2)  # 10% discount
        else:
            return 0.0  # no discount

    con.create_function('calc_discount', calc_discount, ['DECIMAL', 'INTEGER'], 'DOUBLE')

    con.sql("""
    SELECT oi.item_id,
           p.product_name,
           oi.unit_price,
           oi.quantity,
           (oi.unit_price * oi.quantity) AS subtotal,
           calc_discount(oi.unit_price, oi.quantity) AS discount,
           ROUND((oi.unit_price * oi.quantity) - calc_discount(oi.unit_price, oi.quantity), 2) AS final_price
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    ORDER BY discount DESC
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.3 Python UDF with Null Handling

    By default, DuckDB will **not** call your function if any input is NULL — it returns NULL immediately. If you need to handle NULLs yourself (e.g., to provide a fallback), set `null_handling='special'`.
    """)
    return


@app.cell
def _(con):
    def safe_country_label(country):
        """Return a display label for the country, with fallback for NULL."""
        country_map = {
            'US': 'United States',
            'UK': 'United Kingdom',
            'MX': 'Mexico',
            'JP': 'Japan',
        }
        if country is None:
            return 'Unknown Region'
        return country_map.get(country, f'Other ({country})')

    con.create_function(
        'country_label',
        safe_country_label,
        ['VARCHAR'],
        'VARCHAR',
        null_handling='special'  # our function handles NULLs itself
    )

    con.sql("""
    SELECT first_name,
           country,
           country_label(country) AS region
    FROM customers
    """).show()

    # Test with a NULL value
    print("Testing NULL handling:")
    con.sql("SELECT country_label(NULL) AS fallback").show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.4 Python UDF Using External Libraries

    One of the biggest advantages of Python UDFs is access to the full Python ecosystem. Here's a function that uses `hashlib` to generate a SHA-256 hash of customer emails (useful for anonymization or ID generation).
    """)
    return


@app.cell
def _(con):
    import hashlib

    def hash_email(email):
        """Generate a short SHA-256 hash of an email address."""
        if email is None:
            return None
        return hashlib.sha256(email.encode()).hexdigest()[:16]

    con.create_function('hash_email', hash_email, ['VARCHAR'], 'VARCHAR')

    con.sql("""
    SELECT first_name,
           email,
           hash_email(email) AS email_hash
    FROM customers
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.5 Python UDF with Type Annotations (Simplified Registration)

    DuckDB can infer parameter and return types from Python type annotations, so you can skip the explicit type lists. This makes registration more concise.
    """)
    return


@app.cell
def _(con):
    def days_since_joined(joined_date: str) -> int:
        """Calculate days since a customer joined (from their join date to today)."""
        from datetime import date, datetime
        if joined_date is None:
            return None
        # DuckDB passes dates as strings in ISO format
        join_dt = datetime.strptime(str(joined_date), '%Y-%m-%d').date()
        return (date.today() - join_dt).days

    # No need to specify types — DuckDB reads the annotations!
    con.create_function('days_since_joined', days_since_joined)

    con.sql("""
    SELECT first_name,
           joined_date,
           days_since_joined(joined_date::VARCHAR) AS days_active
    FROM customers
    ORDER BY days_active DESC
    """).show()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### 6.6 Combining SQL Macros and Python UDFs in One Query

    The real power comes from mixing both approaches. SQL macros handle the relational logic efficiently, while Python UDFs handle complex transformations. DuckDB resolves each function type at its own layer.
    """)
    return


@app.cell
def _(con, customers, mo, order_items, orders):
    _df = mo.sql(
        f"""
        SELECT
            full_name(c.first_name, c.last_name) AS customer,
            country_label(c.country) AS region,
            hash_email(c.email) AS anon_id,
            o.order_id,
            o.status,
            SUM(oi.unit_price * oi.quantity) AS subtotal,
            SUM(calc_discount(oi.unit_price, oi.quantity)) AS total_discount
        FROM customers c
        JOIN orders o
        ON c.customer_id = o.customer_id
        JOIN order_items oi
        ON o.order_id = oi.order_id
        GROUP BY
            c.first_name,
            c.last_name,
            c.country,
            c.email,
            o.order_id,
            o.status
        ORDER BY subtotal DESC
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    In that single query:
    - `full_name()` is a **SQL scalar macro** (inlined, zero overhead)
    - `country_label()` is a **Python UDF** with `null_handling='special'`
    - `hash_email()` is a **Python UDF** using `hashlib`
    - `calc_discount()` is a **Python UDF** with business logic

    DuckDB seamlessly handles the interplay between inlined macros and Python function calls.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 7. Removing Functions

    DuckDB provides `DROP` statements for each function type. Note the different syntax for each:
    """)
    return


@app.cell
def _(con):
    # Drop a scalar macro

    con.execute("DROP MACRO IF EXISTS mask_email")

    print("Dropped scalar macro 'mask_email'")

    # Drop a table macro

    con.execute("DROP MACRO TABLE IF EXISTS search_products")

    print("Dropped table macro 'search_products'")

    # Drop a Python UDF

    con.remove_function("slugify")

    print("Dropped Python UDF 'slugify'")

    print("\nSyntax summary:")

    print("  Scalar macros:  DROP MACRO [IF EXISTS] name")

    print("  Table macros:   DROP MACRO TABLE [IF EXISTS] name")

    print("  Python UDFs:    con.remove_function(name)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 8. Summary and Best Practices

    ### Function Type Comparison

    | Feature | SQL Scalar Macro | SQL Table Macro | Python UDF |
    |---|---|---|---|
    | **Defined with** | `CREATE MACRO` | `CREATE MACRO ... AS TABLE` | `con.create_function()` |
    | **Returns** | Single value | Table (set of rows) | Single value |
    | **Used in** | SELECT, WHERE, ORDER BY, etc. | FROM clause | SELECT, WHERE, ORDER BY, etc. |
    | **Execution** | Inlined (zero overhead) | Inlined | Python runtime (some overhead) |
    | **Default params** | Yes (`:=`) | Yes (`:=`) | Via Python defaults |
    | **Can call other functions** | Yes | Yes | Yes |
    | **NULL handling** | Automatic | Automatic | Configurable |
    | **External libraries** | No | No | Yes (any Python lib) |
    | **Drop syntax** | `DROP MACRO` | `DROP MACRO TABLE` | `DROP FUNCTION` |
    | **Best for** | Reusable calculations | Parameterized queries | Complex logic, regex, hashing |

    ### Best Practices

    1. **Prefer SQL macros when possible.** They are inlined at planning time with zero runtime overhead. Use them for calculations, formatting, and conditional logic that SQL can express.

    2. **Use Python UDFs for what SQL can't do.** Regular expressions, hashing, calling external APIs, complex string manipulation — these are where Python UDFs shine.

    3. **Handle NULLs explicitly in Python UDFs.** Either check for `None` in your function body, or set `null_handling='special'` if you need custom NULL behavior.

    4. **Use `OR REPLACE` during development.** It saves you from having to drop and recreate macros every time you iterate on the definition.

    5. **Use default parameters for flexibility.** The `:=` syntax lets you create functions that work for the common case but can be customized when needed.

    6. **Compose functions.** SQL macros can call other macros, and queries can mix SQL macros with Python UDFs. Build small, focused functions and combine them.

    7. **Use table macros instead of views when you need parameters.** Views are fixed queries; table macros accept arguments, making them far more flexible for reporting and exploration.
    """)
    return


@app.cell
def _(con):
    # Clean up
    con.close()
    print("Connection closed. Tutorial complete!")
    return


if __name__ == "__main__":
    app.run()

