import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium", sql_output="pandas")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Welcome to Marimo and DuckDB!

    * **Course:** MSIS-2402
    * **Instructor:** Dr. Mahmoud Parsian
    * **Tool:** Marimo — an interactive notebook for SQL and Python
    * **Database:** DuckDB — it runs inside the notebook, no server needed

    ---

    ## What Is a Notebook?

    A **notebook** is a document made of **cells**. <br>
    Each cell can contain:

    - **Text** (like what you're reading right now) — for explanations
    - **SQL** — to ask questions of a database
    - **Python** — to run code, make charts, etc.

    You read the text cells, then **run** the SQL/code cells to see results.
    Think of it like a lab workbook where the experiments run themselves.

    ## How to Use This Notebook

    1. **Read** the text cells (like this one)
    2. **Look at** the SQL cells below each explanation — they show both the query and the result
    3. **Try editing** a SQL cell and pressing **Cmd+Enter** (Mac) or **Ctrl+Enter** (Windows) to re-run it
    4. Notice how **downstream cells update automatically** — that's Marimo's superpower!
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## Your First Database

    * A **database** is an organized collection of data stored in **tables**.
    * A **table** looks like a spreadsheet — it has **rows** (records) and **columns** (fields).

    Below, we first connect to DuckDB (a **Python cell**), then create a tiny
    table of students and their favorite foods (a **SQL cell**).

    ![](https://media.geeksforgeeks.org/wp-content/uploads/20260124113248518106/rdbms_4.webp)

    ![](https://www.pragimtech.com/blog/contribute/article_images/2220211210231003/what-is-a-relational-database.jpg)
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    # Create a Connection to DuckDB
    """)
    return


@app.cell
def _():
    # Python Cell

    import duckdb
    con = duckdb.connect(database=":memory:")
    print("DuckDB version: ", duckdb.__version__)
    print("DuckDB Connection Object: ", con)
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Create a database table called "students"
    """)
    return


@app.cell
def _(con, mo):
    _df = mo.sql(
        f"""
        -- SQL Cell
        CREATE OR REPLACE TABLE students (
            student_id   INTEGER,
            name         VARCHAR,
            major        VARCHAR,
            favorite_food VARCHAR
        );
        """,
        engine=con
    )
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        -- SQL cell
        -- Describe the structure of students table
        DESC students;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    We just told the database: *"Create a table called `students` with four columns."*

    But the table is empty!

    ---

    # Let's add some data:
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        -- SQL cell
        INSERT INTO students (student_id, name, major, favorite_food) 
        VALUES
            (1, 'Alice',   'Marketing',  'Pizza'),
            (2, 'Bob',     'Finance',    'Sushi'),
            (3, 'Carol',   'Accounting', 'Tacos'),
            (4, 'David',   'Marketing',  'Pasta'),
            (5, 'Eva',     'Finance',    'Pizza'),
            (6, 'Frank',   'Accounting', 'Sushi'),
            (7, 'Rafa',    'Sports',     'Pizza');
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Now let's **look** at our data. The SQL command `SELECT * FROM students`
    means *"show me everything in the students table."*
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        SELECT * 
        FROM students
        ORDER BY student_id
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## Asking Questions with SQL

    SQL stands for **Structured Query Language**. It's how you ask a database
    to answer business questions. You don't need to be a programmer — SQL reads
    almost like English.

    ---

    **Question 1:** *"Who are the Marketing majors?"*
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        SELECT name, 
               major
        FROM   students
        WHERE  major = 'Marketing'
        ORDER BY name
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    Read that SQL out loud: *"Select the name and major from students where the major is Marketing."*
    It's almost plain English!

    ---

    **Question 2:** *"Who likes Pizza?"*
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        SELECT name, 
               favorite_food
        FROM   students
        WHERE  favorite_food = 'Pizza'
        ORDER BY name
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---

    **Question 3:** *"How many students are in each major?"*

    The `GROUP BY` command groups rows together, and `COUNT(*)` counts them.
    Three majors tie with 2 students, so `ORDER BY` adds `major` as a tie-breaker (A → Z):
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        SELECT major,
               COUNT(*) AS num_students
        FROM   students
        GROUP BY major
        ORDER BY num_students DESC, major
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## Try It Yourself!

    Here's the fun part. **Edit the SQL cell below** and press **Cmd+Enter** (Mac) or **Ctrl+Enter** (Windows) to run it.

    Some ideas to try:

    - Change `'Pizza'` to `'Sushi'` and see who likes Sushi
    - Change `favorite_food = 'Pizza'` to `major = 'Finance'` to list the Finance majors
    - Remove the `WHERE` line to see every student
    - Add yourself! Replace the whole query with
      `INSERT INTO students VALUES (8, 'YourName', 'MSIS', 'Ramen')`,
      run it, then put the `SELECT` back and re-run the Question 3 cell to see the new count
    """)
    return


@app.cell
def _(con, mo, students):
    _df = mo.sql(
        f"""
        -- Edit this query! Try different foods, different columns, or add yourself.
        SELECT name, 
               favorite_food
        FROM   students
        WHERE  favorite_food = 'Pizza'
        ORDER BY name
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ---
    ## What Makes Marimo Special?

    Marimo is **reactive** — when you change one cell,   <br>
    every cell that depends on it updates automatically. <br>
    You never have to worry about running cells in the   <br>
    right order or getting stale results.

    This is different from regular scripts where you run      <br>
    everything top-to-bottom and hope nothing is out of date. <br>
    In Marimo, the notebook always shows you the truth.

    ---
    ## What You'll Learn in These 5 Weeks

    | Week | Topic | What You'll Be Able to Do |
    |------|-------|---------------------------|
    | 1 | Database Concepts and SQL Fundamentals | Retrieve, filter, summarize, and modify data with `SELECT`, `WHERE`, `GROUP BY`, `INSERT` / `UPDATE` / `DELETE` |
    | 2 | Multiple Tables and Complex Queries | Combine tables with keys and joins; break big questions into subqueries and CTEs |
    | 3 | SQL for Data Analytics | Rank, compare, and find trends with window functions and CTEs |
    | 4 | Web Database Applications | Work with a client–server database (MySQL) and see how a small web application uses a database |
    | 5 | Modern Data Systems and Database Management | Understand transactions, performance, security, and the modern data landscape |

    Weeks 1–3 use Marimo notebooks like this one; Weeks 4–5 add the MySQL
    command-line client and a small web application. You'll write SQL,
    see results instantly, and build up your skills week by week.

    ---
    *MSIS-2402*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Practice, Be Hands-On, and Learn!
    """)
    return


if __name__ == "__main__":
    app.run()
