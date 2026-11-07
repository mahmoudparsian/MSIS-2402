---
marp: true
title: MSIS-2402 - Session 2 - Text and Date Functions
theme: default
paginate: true
---

# Slide 1 — MSIS-2402: SQL Fundamentals
## Session 2 — Text and Date Functions

Clean the text → Use the dates → Trust the numbers

---

# Slide 2 — Why Functions Matter for Analytics

Two problems you will meet in almost every real dataset:

1. **Messy text** — `'San Jose'`, `'san jose'`, `' San Jose '` look the
   same to you, but SQL counts them as **three different cities**
2. **Dates** — most business questions are about time:
   *per year? per month? how many days since…? the last 90 days?*

👉 Today: a **small set** of functions that solve both.

👉 SQL has hundreds more. When you need one, **look it up** (last slide).

---

# Slide 3 — Learning Objectives

By the end of today you can:

* Clean text with `TRIM`, `LOWER`, `UPPER`
* Join text together with `||`
* Write a date the right way: `DATE '2024-12-31'`
* Group by time with `YEAR`, `MONTH`, `DATE_TRUNC`
* Show a month as `'2024-01'` with `strftime`
* Measure time with `date_diff` and `INTERVAL`

---

<style scoped>section { font-size: 25px; } pre { font-size: 20px; }</style>

# Slide 4 — Setup: Two Tables

Run from `week1_db_concepts_sql_fundamentals/session02_aggregation_kpis/`:

```sql
-- 1) Six sign-ups, typed by hand (messy on purpose)
CREATE OR REPLACE TABLE signups AS
SELECT * FROM (VALUES
    (1, '  Maria ', 'Garcia', 'San Jose'),
    (2, 'JAMES',    'lee',    'san jose'),
    (3, 'Aisha',    'Khan ',  ' San Jose '),
    (4, 'tom',      'NGUYEN', 'SAN JOSE'),
    (5, 'Li',       'Wei',    'Austin'),
    (6, 'Sara',     'Cohen',  'austin ')
) AS t(signup_id, first_name, last_name, city);

-- 2) The 200 dated sales from Session 1 (2021-01-03 to 2024-12-28)
CREATE OR REPLACE TABLE sales_history AS
SELECT * FROM read_csv_auto('../session01_single_table_sql/data/sales.csv');
```

---

<style scoped>section { font-size: 26px; }</style>

# Slide 5 — 🧹 The Problem: Messy Text Splits Your Groups

*How many sign-ups per city?*

```sql
SELECT city, COUNT(*) AS signups
FROM signups
GROUP BY city
ORDER BY signups DESC, city;
```

---

# Slide 6 — 🧹 The Problem: Messy Text Splits Your Groups (cont.)

| city | signups |
|---|---:|
| `' San Jose '` | 1 |
| `'Austin'` | 1 |
| `'SAN JOSE'` | 1 |
| `'San Jose'` | 1 |
| `'austin '` | 1 |
| `'san jose'` | 1 |

⚠️ **6 groups**, but there are only **2 cities**. Every count is wrong.

---

<style scoped>section { font-size: 25px; } table { font-size: 22px; }</style>

# Slide 7 — `TRIM`, `LOWER`, `UPPER`

| Function | What it does | Example | Result |
|---|---|---|---|
| `TRIM(x)` | removes outer spaces | `TRIM(' San Jose ')` | `'San Jose'` |
| `LOWER(x)` | all lowercase | `LOWER('SAN JOSE')` | `'san jose'` |
| `UPPER(x)` | all uppercase | `UPPER('san jose')` | `'SAN JOSE'` |

👉 `TRIM` does **not** touch spaces in the middle: `'San Jose'` keeps its space.

👉 Functions can be **nested**: `LOWER(TRIM(city))` runs `TRIM` first, then `LOWER`.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 8 — See Each Step

```sql
SELECT signup_id,
       city,
       TRIM(city)        AS trimmed,
       LOWER(TRIM(city)) AS clean_city
FROM signups
ORDER BY signup_id;
```

| signup_id | city | trimmed | clean_city |
|---:|---|---|---|
| 1 | `'San Jose'` | `'San Jose'` | `'san jose'` |
| 2 | `'san jose'` | `'san jose'` | `'san jose'` |
| 3 | `' San Jose '` | `'San Jose'` | `'san jose'` |
| 4 | `'SAN JOSE'` | `'SAN JOSE'` | `'san jose'` |
| 5 | `'Austin'` | `'Austin'` | `'austin'` |
| 6 | `'austin '` | `'austin'` | `'austin'` |

---

# Slide 9 — ✅ The Fix: Group by the Clean Value

```sql
SELECT LOWER(TRIM(city)) AS clean_city,
       COUNT(*)          AS signups
FROM signups
GROUP BY clean_city
ORDER BY signups DESC, clean_city;
```

| clean_city | signups |
|---|---:|
| san jose | 4 |
| austin | 2 |

👉 **Rule:** clean text **before** you `GROUP BY`, `COUNT`, or compare it.

💼 Customer cities, product names, survey answers, sales regions — always check.

---

<style scoped>section { font-size: 26px; }</style>

# Slide 10 — `||`: Join Text Together

`||` glues pieces of text into one value:

```sql
SELECT signup_id,
       TRIM(first_name) || ' ' || UPPER(TRIM(last_name)) AS full_name
FROM signups
ORDER BY signup_id;
```

---

# Slide 11 — `||`: Join Text Together (cont.)

| signup_id | full_name |
|---:|---|
| 1 | Maria GARCIA |
| 2 | JAMES LEE |
| 3 | Aisha KHAN |
| 4 | tom NGUYEN |
| 5 | Li WEI |
| 6 | Sara COHEN |

👉 `' '` is a text value with one space — it goes **between** the names.

---

# Slide 12 — 📅 Dates: The `DATE` Type

* `sale_date` in `sales_history` is a real **`DATE`**:
  `read_csv_auto` saw `2023-05-03` and chose `DATE` for you
* A date **you type** in a query is just **text** — until you say it is a date:

| You write | SQL sees |
|---|---|
| `'2024-12-31'` | text |
| `DATE '2024-12-31'` | a date ✅ |

👉 Always write dates as `DATE 'YYYY-MM-DD'` — year, month, day, with dashes.

---

<style scoped>section { font-size: 26px; }</style>

# Slide 13 — `YEAR` and `MONTH`

Pull one part out of a date — the result is a **number**:

```sql
SELECT sale_id,
       sale_date,
       YEAR(sale_date)  AS sale_year,
       MONTH(sale_date) AS sale_month
FROM sales_history
ORDER BY sale_id
LIMIT 3;
```

| sale_id | sale_date | sale_year | sale_month |
|---:|---|---:|---:|
| 1 | 2023-05-03 | 2023 | 5 |
| 2 | 2022-11-23 | 2022 | 11 |
| 3 | 2022-04-26 | 2022 | 4 |

---

<style scoped>section { font-size: 26px; }</style>

# Slide 14 — 📊 KPI: Revenue per Year

```sql
SELECT YEAR(sale_date)             AS sale_year,
       COUNT(*)                    AS sales,
       ROUND(SUM(total_amount), 2) AS revenue
FROM sales_history
GROUP BY sale_year
ORDER BY sale_year;
```

| sale_year | sales | revenue |
|---:|---:|---:|
| 2021 | 47 | 33,211.39 |
| 2022 | 47 | 35,361.13 |
| 2023 | 47 | 30,654.61 |
| 2024 | 59 | 32,155.98 |

💼 2024 had the **most sales** (59) but **not the most revenue** — smaller baskets?

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 15 — `DATE_TRUNC`: Group by Month

`DATE_TRUNC('month', d)` moves every date to the **first day of its month**:

```sql
SELECT DATE_TRUNC('month', sale_date) AS sale_month,
       COUNT(*)                       AS sales,
       ROUND(SUM(total_amount), 2)    AS revenue
FROM sales_history
WHERE sale_date >= DATE '2024-01-01'
  AND sale_date <  DATE '2024-07-01'
GROUP BY sale_month
ORDER BY sale_month;
```

---

# Slide 16 — `DATE_TRUNC`: Group by Month (cont.)

| sale_month | sales | revenue |
|---|---:|---:|
| 2024-01-01 | 6 | 2,656.67 |
| 2024-02-01 | 1 | 42.83 |
| 2024-03-01 | 4 | 2,884.91 |
| 2024-04-01 | 7 | 3,610.92 |
| 2024-05-01 | 4 | 3,036.58 |
| 2024-06-01 | 4 | 2,955.15 |

---

# Slide 17 — Why `DATE_TRUNC` and Not `MONTH`?

* `MONTH(sale_date)` gives `1` for January **of every year** —
  January 2023 and January 2024 would be **added together**
* `DATE_TRUNC('month', sale_date)` keeps the year: `2024-01-01`
  → one group per **real month**, already in time order

👉 For a **trend over time**, use `DATE_TRUNC`.
👉 For **seasonality** ("are Decembers always strong?"), use `MONTH`.

ℹ️ `DATE_TRUNC` returns a timestamp, so some tools show
`2024-01-01 00:00:00`. Same month — the time part is always `00:00:00`.

---

<style scoped>section { font-size: 25px; } pre { font-size: 21px; }</style>

# Slide 18 — `strftime`: Show a Month as `'2024-01'`

`strftime(d, '%Y-%m')` turns a date into **text** in the pattern you give:

```sql
SELECT strftime(DATE_TRUNC('month', sale_date), '%Y-%m') AS sale_month,
       COUNT(*)                    AS sales,
       ROUND(SUM(total_amount), 2) AS revenue
FROM sales_history
WHERE sale_date >= DATE '2024-01-01'
  AND sale_date <  DATE '2024-07-01'
GROUP BY sale_month
ORDER BY sale_month;
```

---

# Slide 19 — `strftime`: Show a Month as `'2024-01'` (cont.)

| sale_month | sales | revenue |
|---|---:|---:|
| 2024-01 | 6 | 2,656.67 |
| 2024-02 | 1 | 42.83 |
| 2024-03 | 4 | 2,884.91 |
| 2024-04 | 7 | 3,610.92 |
| 2024-05 | 4 | 3,036.58 |
| 2024-06 | 4 | 2,955.15 |

`%Y` = 4-digit year · `%m` = 2-digit month → `'2024-01'` still sorts in time order.

---

<style scoped>section { font-size: 26px; }</style>

# Slide 20 — `date_diff`: How Many Days Between?

`date_diff('day', start, end)` = days from `start` to `end`:

```sql
SELECT sale_id,
       sale_date,
       date_diff('day', sale_date, DATE '2024-12-31') AS days_ago
FROM sales_history
ORDER BY sale_date DESC, sale_id
LIMIT 5;
```

---

# Slide 21 — `date_diff`: How Many Days Between? (cont.)

| sale_id | sale_date | days_ago |
|---:|---|---:|
| 56 | 2024-12-28 | 3 |
| 81 | 2024-12-28 | 3 |
| 133 | 2024-12-12 | 19 |
| 112 | 2024-12-05 | 26 |
| 15 | 2024-12-04 | 27 |

💼 "Days since last purchase" (recency), delivery time, days to pay an invoice.

---

# Slide 22 — `INTERVAL`: The Last 90 Days

*How did we do in the last 90 days of 2024?*

```sql
SELECT COUNT(*)                    AS sales,
       ROUND(SUM(total_amount), 2) AS revenue
FROM sales_history
WHERE sale_date > DATE '2024-12-31' - INTERVAL 90 DAY;
```

| sales | revenue |
|---:|---:|
| 14 | 6,810.70 |

👉 `DATE '2024-12-31' - INTERVAL 90 DAY` = 90 days before Dec 31, 2024.
👉 Also: `INTERVAL 1 MONTH`, `INTERVAL 1 YEAR`.

💼 Rolling windows: last 7 days, last 30 days, last quarter.

---

<style scoped>section { font-size: 24px; } pre { font-size: 20px; }</style>

# Slide 23 — ⚠️ Two Common Mistakes

**1. A date without `DATE` is text:**

```sql
SELECT YEAR('2024-03-15');        -- ❌ Binder Error
SELECT YEAR(DATE '2024-03-15');   -- ✅ 2024
```

The error: *Could not choose a best candidate function for the function
call "year(STRING_LITERAL)"* → it means "I got text, I need a date."

**2. `date_diff` order is `start, end`:**

```sql
SELECT date_diff('day', DATE '2024-12-31', DATE '2024-12-01');  -- -30 ❌
SELECT date_diff('day', DATE '2024-12-01', DATE '2024-12-31');  --  30 ✅
```

👉 A **negative** number of days usually means the dates are swapped.

---

<style scoped>section { font-size: 24px; }</style>

# Slide 24 — 🧾 Cheat Sheet

| You want to… | Write |
|---|---|
| remove spaces at start and end | `TRIM(x)` |
| lowercase / uppercase | `LOWER(x)` / `UPPER(x)` |
| clean text before grouping | `LOWER(TRIM(x))` |
| join text | `a \|\| ' ' \|\| b` |
| write a date | `DATE '2024-12-31'` |
| year / month number | `YEAR(d)` / `MONTH(d)` |
| group by real month | `DATE_TRUNC('month', d)` |
| show a month as `'2024-01'` | `strftime(d, '%Y-%m')` |
| days between two dates | `date_diff('day', start, end)` |
| a date N days earlier | `d - INTERVAL 90 DAY` |

---

<style scoped>section { font-size: 25px; }</style>

# Slide 25 — 🧪 Try It

**1.** Monthly revenue for **2023**: columns `sale_month` (`'YYYY-MM'`),
`sales`, `revenue` (`ROUND(..., 2)`); sort by `sale_month`.

* Self-check: **11 rows**. One month of 2023 is missing — which one, and why?

**2.** Every sale in the **last 30 days of 2024**
(`sale_date > DATE '2024-12-31' - INTERVAL 30 DAY`): columns `sale_id`,
`sale_date`, `days_ago` (days from `sale_date` to `DATE '2024-12-31'`);
sort by `days_ago`, then `sale_id`.

* Self-check: **6 rows**.

---

# Slide 26 — 🔎 Need Another Function? Look It Up

We learned a **small** set on purpose. When a task needs more
(replace a word, cut out part of a code, a weekday name…), search:

* Text functions — <https://duckdb.org/docs/stable/sql/functions/text>
* Date functions — <https://duckdb.org/docs/stable/sql/functions/date>
* `strftime` patterns — <https://duckdb.org/docs/stable/sql/functions/dateformat>

👉 Every database (MySQL, PostgreSQL, SQL Server…) has the same ideas —
names and argument order can differ, so **check the docs** for yours.

---

# Slide 27 — What Did We Learn?

* Messy text splits groups → `LOWER(TRIM(x))` **before** grouping
* `||` joins text
* Write dates as `DATE '…'`
* `YEAR` / `MONTH` for parts, `DATE_TRUNC` for trends, `strftime` for labels
* `date_diff` and `INTERVAL` measure and filter time

🎯 **Clean data + the right time grain = numbers you can trust.**
