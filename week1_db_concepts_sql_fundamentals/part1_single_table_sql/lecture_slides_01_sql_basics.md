---

marp: true

title: Week 1 — SQL Foundations

theme: default

paginate: true

---

# slide-1: MSIS-2402 <br> SQL Fundamentals

* Database Management Systems – Fundamentals of SQL  

* Instructor: Dr. Mahmoud Parsian

---

# slide-2: 📊 Week 1 — SQL Foundations

From
 
### Data → Questions → Insight

---

# slide-3: — Why This Course Matters

Organizations run on **data**.

Examples of business data:

- customers
- products
- orders
- payments
- shipments

---

# slide-4: — Why This Course Matters

Example business question:

* Which product category generated the highest sales last month?

* SQL helps us answer questions like this.

---

# slide-5: — Learning Goals for Week 1

By the end of Week 1 you should understand:

• what a **database** is  
• what a **relational database** is  
• what an **RDBMS** is  
• what **SQL** is used for  
• how to write **basic SQL queries**

---

# slide-6: 🎯 Learning Objectives

By the end of today:

* Understand tables (rows / columns)

* Write basic SQL queries

* Filter data using WHERE

* Think in business questions

---

# slide-7: 🧠 What is a Database?

A database is:

* Organized data

* Structured for querying

* Designed for decision-making

---

# slide-8: 📊 Table = Business Events

```
order_id, country, product, price, quantity
```

* 👉 Each row = one transaction
* 👉 Each row = one business event

---

# slide-9: 💼 Business Translation

```
	•	Row → sale
	•	Column → attribute
	•	Table → business process
```

---

<style scoped>section { font-size: 24px; } pre, table { font-size: 20px; }</style>

# slide-10:  — What Is a Database?

A **database** is an organized collection of data.

Example table:

| sale_id | sale_date | product_id | quantity | total_amount |
|---|---|---|---|---|
| 1 | 2023-05-03 | 143 | 3 | 608.58 |
| 2 | 2022-11-23 | 87 | 1 | 269.14 |

A database lets us:

- store data
- retrieve data
- update data
- analyze data

---

# slide-11:  Why Not Just Use Spreadsheets?

Spreadsheets are useful but limited.

Problems with spreadsheets:

- hard to manage large data
- difficult for many users
- duplication of information
- slow queries

Databases solve these problems.

---

# slide-12: What Is a Relational Database?

A **relational database** stores data in **tables** that are related.

Example:

Customers

| customer_id | country |
|---|---|
| 1 | Germany |
| 2 | Canada |

Orders

| order_id | customer_id |
|---|---|
| 101 | 1 |
| 102 | 2 |

Tables connect through keys.

---

# slide-13: Table Structure

Tables consist of:

*  **rows** (records)  

*  **columns** (attributes/fields)

Example:

| sale_id | sale_date | product_category | quantity | total_amount |
|---|---|---|---|---|
| 1 | 2023‑05‑03 | Home | 3 | 608.58 |

Each row represents one transaction.

---

# slide-14:  What Is an RDBMS?

RDBMS = **Relational Database Management System**

It is software that manages relational databases.

Examples:

- DuckDB
- MySQL
- PostgreSQL
- Oracle
- SQL Server

---

# slide-15: Database vs RDBMS

Database:

The **data itself**.

RDBMS:

The **software used to manage the data**.

Example:

* Database = tables  
* RDBMS = MySQL (as a software system)

---

# slide-16: ❓ Why SQL?

SQL answers:

### - Which country performs best?

### - What products are expensive?

### - Where is revenue coming from?

---


# slide-17:  What Is SQL?

SQL = **Structured Query Language**

SQL allows us to:

* retrieve data  
* filter data  
* sort data  
* summarize data  

---

# slide-18: 🧠 Key Idea

### * SQL is NOT programming

### * SQL is asking questions to data

---

# slide-19: SQL Query Example:

```sql
SELECT *  
FROM sales;
```

---

# slide-20: 🔍 What does this mean?

```
	•	SELECT → what you want
	
	•	FROM → where data lives
	
	•		*	→ everything
```

---

# slide-21: ⚠️ Important

`SELECT *`

 is:

```
	•	good for learning ✅
	•	bad in production ❌
```

---


# slide-22: 🎯 Selecting Columns

SELECT what is required:

```
SELECT product, 
       price,
       quantity
FROM sales;
```

---

# slide-23: 💼 Business Question

* “What products do we sell and at what price?”

* "what are top-5 selling products per country?"

* "What are the sales revenue month-by-month for year 2025?"

---

# slide-24: 🧠 Thinking Shift

From:

❌ “Write SQL”

To:

✅ “Ask a question”

---

# slide-25: Types of SQL Commands

SQL includes several categories:

* Querying → SELECT  

* Data modification → INSERT, UPDATE, DELETE  

* Table creation → CREATE TABLE  

This course focuses heavily on **querying data**.

---

# slide-26:  Our Week‑1 Dataset

From here on we switch to the **real, file-backed** `sales` table —
loaded from `data/sales.csv` (200 rows), the same table used in
`notebook_3_duckdb_marimo.py`. (This replaces the small in-class demo
table from the SELECT examples earlier — same idea, real data.) From this
deck's folder (`part1_single_table_sql/`):
`CREATE OR REPLACE TABLE sales AS SELECT * FROM read_csv_auto('data/sales.csv');`

---

# slide-26:  Our Week‑1 Dataset (cont.)

Columns:

```
sale_id  
sale_date  
product_id  
product_category  
quantity  
unit_price  
total_amount
```
---

# slide-27:  Example Rows

| sale_id | sale_date | product_category | quantity | unit_price | total_amount |
|---|---|---|---|---|---|
| 1 | 2023‑05‑03 | Home | 3 | 202.86 | 608.58 |
| 2 | 2022‑11‑23 | Sports | 1 | 269.14 | 269.14 |

Possible questions:

* Which sale has the highest value?  

* Which categories appear?

---

# slide-28:  Basic SQL Query Pattern

Typical SQL structure:

```sql
SELECT column_list  
FROM table  
WHERE condition  
ORDER BY column  
LIMIT n;
```
---

# slide-29: `SELECT` Clause

`SELECT` specifies which columns to return.

Example:

```sql
SELECT product_category, 
       quantity  
FROM sales;
```
---

# slide-30: `FROM` Clause

FROM specifies the source table.

Example:

```sql
SELECT sale_id, 
       total_amount  
FROM sales;
```
---

# slide-31:  `WHERE` Clause

`WHERE` filters rows.

Example:

```sql
SELECT *  
FROM sales  
WHERE quantity >= 3;
```

---

# slide-32: 🔍 Filtering Data

```sql
SELECT product_category, 
       unit_price,
       quantity
FROM sales
WHERE product_category = 'Electronics';
```

---

# slide-33: 🧠 `WHERE` Clause

### Filters rows **BEFORE** analysis

---

# slide-34: 💼 Business Question

### “Show me all Electronics transactions”

```sql
SELECT *
FROM sales
WHERE product_category = 'Electronics';
```

---

# slide-35: 🔢 Numeric Filtering

```sql
SELECT product_category, 
       unit_price,
       quantity
FROM sales
WHERE unit_price > 300;
```

---

# slide-36: 💼 Business Meaning

### “Show high-value transactions”

---

# slide-37: 🔗 `AND` Condition

```sql
SELECT product_category, 
       unit_price,
       quantity
FROM sales
WHERE product_category = 'Electronics'
  AND unit_price > 300;
```

---

# slide-38: 🧠 Concept Check

Which is stricter?

* `AND`

* `OR`


👉 Answer: `AND`

---

# slide-39: 🔄 `OR` Condition

```sql
SELECT product_category, 
       unit_price,
       quantity
FROM sales
WHERE product_category = 'Electronics'
   OR product_category = 'Sports';
```

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# slide-40: ⚠️ `AND` Runs Before `OR`

*Goal: Electronics **or** Sports items priced over $400.*

```sql
SELECT sale_id, product_category, unit_price
FROM sales
WHERE product_category = 'Electronics'
   OR product_category = 'Sports' AND unit_price > 400
ORDER BY unit_price
LIMIT 3;
```

| sale_id | product_category | unit_price |
|---:|---|---:|
| 8 | Electronics | 26.72 |
| 35 | Electronics | 42.83 |
| 11 | Electronics | 101.45 |

❌ Electronics for **$26.72**? SQL read it as
`Electronics` **OR** (`Sports` **AND** `> 400`) — **36 rows**, most of them wrong.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# slide-41: ✅ Use Parentheses

```sql
SELECT sale_id, product_category, unit_price
FROM sales
WHERE (product_category = 'Electronics' OR product_category = 'Sports')
  AND unit_price > 400
ORDER BY unit_price
LIMIT 3;
```

| sale_id | product_category | unit_price |
|---:|---|---:|
| 34 | Sports | 401.63 |
| 55 | Sports | 422.56 |
| 82 | Electronics | 433.45 |

✅ **15 rows**, every one over $400.

👉 **Rule:** `AND` is applied before `OR` (like × before + in math).
When a `WHERE` mixes `AND` and `OR`, **always** add parentheses.

---

# slide-42: Truth table

| A | B | A AND B | A OR B | NOT A | A XOR B |
| :---: | :---: | :---: | :---: | :---: | :---: |
| T | T | T | T | F | F |
| T | F | F | T | F | T |
| F | T | F | T | T | T |
| F | F | F | F | T | F |

---

# slide-43: `ORDER BY` Clause

#### `ORDER BY` sorts results: (`A -> Z`) (`1 -> 10`)

Example:

```sql
SELECT *  
FROM sales  
ORDER BY total_amount;
```

OR 

```sql
SELECT *  
FROM sales  
ORDER BY total_amount ASC;
```

---

# slide-44: `ORDER BY` Clause (`DESC`)

#### `ORDER BY` sorts results: (`Z -> A`)(`10 -> 1`)

Example:

```sql
SELECT *  
FROM sales  
ORDER BY total_amount DESC;
```

---

# slide-45: `LIMIT` Clause

LIMIT restricts output size.

Example:

```sql
SELECT *  
FROM sales  
ORDER BY sale_id  
LIMIT 10;
```

Without `ORDER BY`, *which* 10 rows you get isn't guaranteed.

---

# slide-46: `DISTINCT` Clause

`DISTINCT` removes duplicates.

Example:

```sql
SELECT DISTINCT product_category  
FROM sales;
```

---

# slide-47: Reading SQL in Plain English

Query:

```sql
SELECT product_category, 
       total_amount  
FROM sales  
WHERE quantity >= 2  
ORDER BY total_amount DESC  
LIMIT 5;
```

Meaning:

Show the five highest sales where `quantity ≥ 2`.

---

# slide-48: Business Questions We Can Answer

Example queries: **10 Largest Sales**

```sql
SELECT *  
FROM sales  
ORDER BY total_amount DESC  
LIMIT 10;
```

---

# slide-49: Common Beginner Mistakes

Typical mistakes:

* forgetting FROM  
* misspelling columns  
* missing quotes  
* incorrect clause order

Correct example:

```sql
SELECT *  
FROM sales  
WHERE quantity > 2;
```

---

# slide-50: Why SQL Is Powerful

SQL lets us ask questions directly to data.

Example:

```sql
SELECT *  
FROM sales  
ORDER BY total_amount DESC  
LIMIT 10;
```

This immediately reveals the largest transactions.

---

<style scoped>section { font-size: 22px; } pre, table { font-size: 18px; }</style>

# slide-51: 🧮 Derived Column

A **derived column** is computed from other columns in the same row.
Give it a clear name with `AS`:

```sql
SELECT sale_id,
       product_category,
       quantity,
       unit_price,
       quantity * unit_price AS line_value,
       total_amount
FROM sales
ORDER BY line_value DESC
LIMIT 3;
```

| sale_id | product_category | quantity | unit_price | line_value | total_amount |
|---:|---|---:|---:|---:|---:|
| 108 | Computers | 4 | 499.74 | 1998.96 | 1998.96 |
| 67 | Home | 4 | 498.36 | 1993.44 | 1993.44 |
| 69 | Electronics | 4 | 485.45 | 1941.80 | 1941.80 |

👉 `line_value` matches the stored `total_amount` — a quick sanity check.

---

# slide-52: 💼 Business Insight

`Revenue = unit_price × quantity`

---

# slide-53: 🔥 First KPI

👉 `line_value` = revenue per sale

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# slide-54: 🏷️ Derived Labels with `CASE`

`CASE` turns a value into a **label** — SQL's if / else-if / else:

```sql
SELECT sale_id,
       quantity,
       CASE
           WHEN quantity = 1  THEN 'Single item'
           WHEN quantity <= 3 THEN 'Small basket'
           ELSE 'Bulk'
       END AS basket_size
FROM sales
ORDER BY sale_id
LIMIT 5;
```

| sale_id | quantity | basket_size |
|---:|---:|---|
| 1 | 3 | Small basket |
| 2 | 1 | Single item |
| 3 | 3 | Small basket |
| 4 | 3 | Small basket |
| 5 | 4 | Bulk |

---

# slide-55: 🧠 How `CASE` Reads

* Checks each `WHEN` **top to bottom** and stops at the **first** true one
  * so `quantity = 1` never reaches `quantity <= 3`
* `ELSE` catches everything left (no `ELSE` → `NULL`)
* Always end with `END` — and name the result with `AS`

⚠️ **Boundaries matter:** is a value *exactly* on the edge in the first band or
the second? Decide (`<` vs. `<=`), then test a row right at the edge.

💼 Use it for: price tiers, customer segments, order-size buckets, pass / fail.

---

# slide-56: 📊 Quick Visualization (Concept)

### SQL → extract

### Python → visualize


👉 This is your workflow

---

# slide-57: 🧪 In-Class Exercise

Write queries for:

```
	1.	price > 800
	2.	country = Canada
	3.	total_value
	4.	total_value > 1000
```
---

# slide-58: 💬 Discussion

Ask:

* Which products are expensive?

* Which country appears most?

---

# slide-59: 🧠 What did we learn?

* `SELECT`
* `FROM`
* `WHERE`
* `ORDER BY`
* `DISTINCT`
* `LIMIT`
* boolean conditions: `AND`, `OR`, `NOT`
* Derived columns
* `CASE` labels

---

# slide-60: 🎯 Most Important Idea

SQL = asking business questions

---

# slide-61: 🚀 Next Session

We move to:

* 👉 Aggregation (SUM, COUNT, AVG)

* 👉 GROUP BY

* 👉 Business KPIs

---

# slide-62: Week‑1 Summary

Today we learned:

* database fundamentals  
* relational databases  
* RDBMS systems  
* SQL basics  
* first SQL queries

---

# slide-63: 🙌 End of Deck 1

Questions?

---

Coming up:

**Aggregation later this week (Part 2), then multiple tables and JOINs in Week 2**
