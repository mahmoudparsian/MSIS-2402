---

marp: true
title: MSIS-2402 — Course Roadmap
theme: default
paginate: true
style: |
  pre code {
    font-size: 22px;
  }

---

## Course Roadmap
### MSIS-2402 — Database Management Systems: Fundamentals of SQL

* Santa Clara University · Leavey School of Business

* 2 units · 5 weeks · 10 sessions of 95 minutes · Winter 2027

* Instructor: Dr. Mahmoud Parsian

---

# 🌍 Course Vision

Transform students from:

❌ spreadsheet users

➡️

✅ data thinkers who can query and explore data

---

# 🎯 Learning Outcomes

Students will be able to:

* Explain how relational data is organized (tables, keys, relationships)
* Create, retrieve, filter, summarize, and modify data with SQL
* Combine related tables and break complex questions into smaller queries
* Use SQL for data analysis, including window functions and CTEs
* Describe how databases fit into web and other modern applications
* Recognize the main types of modern data systems and the operational,
  security, performance, and governance issues in managing data

---

# 🧠 Learning Progression

```
Data 

→ Query & Summarize          (Week 1)

→ Combine & Decompose        (Week 2)

→ Analyze                    (Week 3)

→ Build Applications         (Week 4)

→ Manage Data at Scale       (Week 5)
```

---

# 📊 Course Structure — 5 Weeks

| Week | Theme                                            | Skill                        |
|------|--------------------------------------------------|------------------------------|
| 1    | Database Concepts and SQL Fundamentals           | Querying & summarizing       |
| 2    | Working with Multiple Tables and Complex Queries | Combining & decomposing      |
| 3    | SQL for Data Analytics                           | Insight discovery            |
| 4    | Introduction to Web Database Applications        | Application architecture     |
| 5    | Modern Data Systems and Database Management      | The data landscape           |

---

### MSIS-2402 — Course Roadmap

```
          ┌───────────────────────────────┐
          │ WEEK 1: DATABASE CONCEPTS &   │
          │         SQL FUNDAMENTALS      │
          │  SELECT, WHERE, ORDER BY      │
          │  GROUP BY, HAVING, KPIs       │
          └──────────────┬────────────────┘
                         ▼
          ┌───────────────────────────────┐
          │ WEEK 2: MULTIPLE TABLES &     │
          │         COMPLEX QUERIES       │
          │  Primary/Foreign Keys, JOINs  │
          │  orders → order_items         │
          └──────────────┬────────────────┘
                         ▼
          ┌───────────────────────────────┐
          │ WEEK 3: SQL FOR DATA ANALYTICS│
          │  Full operational database    │
          │  Window functions, CTEs       │
          └──────────────┬────────────────┘
                         ▼
          ┌───────────────────────────────┐
          │ WEEK 4: WEB DATABASE          │
          │         APPLICATIONS          │
          │  UI → app logic → database    │
          └──────────────┬────────────────┘
                         ▼
          ┌───────────────────────────────┐
          │ WEEK 5: MODERN DATA SYSTEMS & │
          │         DATABASE MANAGEMENT   │
          │  NoSQL, warehouses, cloud     │
          │  security, performance        │
          └───────────────────────────────┘
```

---

## Slide — Overall Course Progression


* Week 1 → Database Concepts and SQL Fundamentals

* Week 2 → Working with Multiple Tables and Complex Queries

* Week 3 → SQL for Data Analytics

* Week 4 → Introduction to Web Database Applications

* Week 5 → Modern Data Systems and Database Management


### Goal of the course:

Learn how to **analyze real business data using SQL**, and understand
how databases power applications and organizations.

---

# 📘 Week 1 — Database Concepts and SQL Fundamentals

How relational data is organized, and the core skills for creating,
retrieving, filtering, summarizing, and modifying data.

Topics

* What is a database / a relational database / an RDBMS  
* What is SQL  
* Tables, rows, columns  

---

## 📘 Week 1 — Retrieving & Filtering Data

Students learn:

* SELECT ... FROM 
* WHERE, AND / OR / NOT  
* ORDER BY  
* LIMIT  
* DISTINCT  

Dataset:

Single **sales** table.

---

# SQL for Business Analytics

### Data
→
### 1. Transform Data  
→
### 2. Insight 
→ 
### 3. Decisions

---

## Week 1 — Example Query

Largest sales in the dataset.

```sql
SELECT *
FROM sales
ORDER BY total_amount DESC
LIMIT 10;
```

Learning outcome:

Students learn to **retrieve and filter data**.

---

## SQL Mindset

> SQL is NOT code  

> SQL is a **question language**

---

# 📘 Week 1 — Summarizing Data

* `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
* `GROUP BY`, `HAVING`
* basic business metrics (KPIs)

```sql
SELECT product_category,
       SUM(total_amount) AS total_sales
FROM sales
GROUP BY product_category
ORDER BY total_sales DESC;
```

---

## Business Insight

- Which product category leads?

- Where to invest?

- What drives growth?

---

## Week 2 — Multiple Tables and Complex Queries

Students move from **one table → multiple tables**.

**Tables introduced:**

- `customers`  
- `orders`  
- `products`  
- `order_items`  

**Topics**

• primary keys and foreign keys  
• relational modeling and normalization  
• INNER JOIN and LEFT JOIN  
• multi‑table joins (and why a wrong `ON` condition silently mismatches rows)  
• reasoning carefully about query results

---

## Week 2 — Example Query

Orders by country.

```sql
SELECT c.country, 
       COUNT(o.order_id) AS num_of_orders
FROM customers c
JOIN orders o
ON c.customer_id = o.customer_id
GROUP BY c.country;
```

Learning outcome:

Students learn to **combine tables to answer questions**.

---

## Week 2 — Example Query

Revenue by product category.

```sql
SELECT p.category,
       SUM(oi.sales_amount) AS total_revenue
FROM order_items oi
JOIN products p
  ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;
```

Learning outcome:

Students perform their **first multi-table business analytics queries**.

---


## Week 3 — SQL for Data Analytics

Students explore a **real business schema**.

Tables

```
customers  
orders  
order_items  
products  
stores  
payments  
shipments  
```

Topics

• operational analytics and data quality checks  
• Window functions and ranking queries  
• Common Table Expressions (CTE)  
• Running totals and trends

---

## Week 3 — Example Query

Revenue by store type.

```sql
SELECT s.store_type, 
       SUM(oi.sales_amount) AS total_revenue
FROM stores s
JOIN orders o ON s.store_id = o.store_id
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY s.store_type;
```

Learning outcome:

Students analyze a **complete business database**.

---

## Week 3 — Example Query

Top customers by revenue.

```sql
SELECT customer_id,
       SUM(sales_amount) AS revenue,
       RANK() OVER (
          ORDER BY SUM(sales_amount) DESC
       ) AS rnk
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY customer_id;
```

Learning outcome:

Students perform **real analytics workflows in SQL**.

---

## Week 4 — Introduction to Web Database Applications

The role of databases in web and other modern applications.

Topics

• Application architecture: user interface → application logic → database  
• Client–server databases  
• Basic web technologies  
• A simple database-backed application: how data moves through a real application

---

## Week 5 — Modern Data Systems and Database Management

Beyond SQL and relational databases.

Topics

• Types of data systems and database technologies  
• Data platforms (warehouses, lakes, cloud)  
• Operations: transactions and concurrency  
• Security, performance, and governance of organizational data

---

## What You Will Be Able To Do

By the end of the course students can:

* explore unfamiliar databases  
* write complex SQL queries  
* join multiple tables  
* perform data analytics using SQL  
* answer real business questions
* explain how applications and organizations use and manage databases

SQL becomes a **data analysis tool**, not just a query language.

---


# 🧪 Tools & Technologies

* SQL
* Python
* **DuckDB** — the main SQL engine (Weeks 1–3)
* **MySQL** — a client–server database (Weeks 4–5)
* **Marimo** — reactive Python notebooks with SQL cells
* **qStudio** — a desktop SQL editor
* CSV datasets

---

# 🗓 How Each Session Works

| Time | What happens |
|---|---|
| First ~55 minutes | Lecture and live demo |
| Last ~40 minutes | Start the session's **lab** in class |
| By **11:00 pm Pacific Time** | Finish and submit labs a and b on Camino |

Every session has an **a** lab (core, 40 points), a **b** lab (a step more
challenging, 30 points), and an optional, ungraded **c** lab — published in
the course repository's `LABS/` folder during class.

---

# 📦 Assessments

| Component | Points |
|---|---:|
| 🧪 10 Labs — one per session, 70 points each (a 40 + b 30) | 700 |
| ✏️ Final Exam — 2 hours, closed book, lock-down browser, after Session 10 | 300 |
| **Total** | **1,000** |

Details: `course_information/ASSIGNMENTS_and_GRADING.md`

---

# 💼 Teaching Philosophy

* Learn by doing

* Focus on intuition over theory

* Emphasize business questions

---

# 🎯 Final Outcome

Students will:

* confidently query data

* understand datasets

* be ready for **MSIS-2407** — DBMS - Design, Development & Administration

---

# 🚀 Career Relevance

Prepares students for:

* Data Analyst 

* Business Analyst

* Analytics roles

---

# 🙌 End of Roadmap

---


## Let’s Begin

Week 1 starts with a simple question:

**What can we learn from sales data?**

Let’s start querying.
