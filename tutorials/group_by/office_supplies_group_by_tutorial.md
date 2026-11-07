# `GROUP BY` with Office Supplies

[← Tutorials](../README.md) · **`GROUP BY` with office supplies** · [`GROUP BY` tutorial 101](Group_By_Tutorial.md)

Grouping, aggregate functions, `WHERE` vs. `HAVING`, and the two most common
`GROUP BY` errors — on 12 orders from an office-supply store.

---

## 1. The Data

[`office_supplies.csv`](office_supplies.csv), in this folder — 12 orders, with
a mix of departments, products, and prices:

```
department,product,quantity,unit_price
Sales,Pens,10,2.00
Sales,Pens,5,2.00
Sales,Paper,20,5.00
Sales,Laptops,1,1200.00
IT,Laptops,2,1200.00
IT,Monitors,5,300.00
IT,Pens,2,2.50
IT,Laptops,1,1300.00
HR,Paper,10,5.00
HR,Pens,3,2.00
HR,Monitors,1,350.00
HR,Paper,5,5.00
```

---

## 2. Setup

Start DuckDB **from this folder**. From the course repository folder
(`MSIS-2402-main` if you downloaded the ZIP):

```
cd tutorials/group_by
duckdb
```

(or create a Marimo notebook in this folder and run the SQL in SQL cells). Then:

```sql
CREATE OR REPLACE TABLE orders AS
SELECT * FROM read_csv_auto('office_supplies.csv');

SELECT COUNT(*) AS n_orders FROM orders;
```

Result:

| n_orders |
|---:|
| 12 |

*1 row*

---

## 3. The Mental Model

Think of the table as a deck of cards. `GROUP BY` sorts the deck into **piles**
by a column (for example `department`). Once the cards are in piles you can no
longer look at single cards — you can only ask questions about each pile: *how
many cards? what is the total?*

### Looking inside the piles with `STRING_AGG`

`STRING_AGG(column, ', ' ORDER BY ...)` glues a pile's values into one text
value, so you can see what went into each total. (MySQL calls it `GROUP_CONCAT`;
DuckDB also accepts the name `LISTAGG`.) The `ORDER BY` inside it fixes the
order of the values — without it, the order is not guaranteed.

```sql
SELECT department,
       SUM(quantity)                                                       AS total_qty,
       STRING_AGG(product || ' (' || quantity || ')', ', ' ORDER BY product, quantity) AS products_with_qty
FROM orders
GROUP BY department
ORDER BY department;
```

Result:

| department | total_qty | products_with_qty |
|---|---:|---|
| HR | 19 | Monitors (1), Paper (5), Paper (10), Pens (3) |
| IT | 10 | Laptops (1), Laptops (2), Monitors (5), Pens (2) |
| Sales | 36 | Laptops (1), Paper (20), Pens (5), Pens (10) |

*3 rows*

Each department's `total_qty` is the sum of the numbers in brackets next to it.

---

## 4. Grouping by Two Columns

Grouping by two columns makes smaller piles: one per **combination** of
department and product.

```sql
SELECT department,
       product,
       SUM(quantity) AS total_sold
FROM orders
GROUP BY department, product
ORDER BY department, product;
```

Result:

| department | product | total_sold |
|---|---|---:|
| HR | Monitors | 1 |
| HR | Paper | 15 |
| HR | Pens | 3 |
| IT | Laptops | 3 |
| IT | Monitors | 5 |
| IT | Pens | 2 |
| Sales | Laptops | 1 |
| Sales | Paper | 20 |
| Sales | Pens | 15 |

*9 rows*

---

## 5. `WHERE` vs. `HAVING`

The rule:

1. **`WHERE`** filters **rows**, *before* the piles are made.
2. **`HAVING`** filters **piles**, *after* the totals are computed.

### Example A — `WHERE`

*"Total items sold per department — ignoring laptops."* The laptop cards are
thrown away **before** grouping:

```sql
SELECT department,
       SUM(quantity) AS total_qty
FROM orders
WHERE product <> 'Laptops'
GROUP BY department
ORDER BY department;
```

Result:

| department | total_qty |
|---|---:|
| HR | 19 |
| IT | 7 |
| Sales | 35 |

*3 rows*

### Example B — `HAVING`

*"Total items sold per department — only departments that sold more than 15
items."* First all the totals:

```sql
SELECT department,
       SUM(quantity) AS total_qty
FROM orders
GROUP BY department
ORDER BY department;
```

Result:

| department | total_qty |
|---|---:|
| HR | 19 |
| IT | 10 |
| Sales | 36 |

*3 rows*

Then the same query with `HAVING` hides the piles that are too small (IT, with 10):

```sql
SELECT department,
       SUM(quantity) AS total_qty
FROM orders
GROUP BY department
HAVING SUM(quantity) > 15
ORDER BY department;
```

Result:

| department | total_qty |
|---|---:|
| HR | 19 |
| Sales | 36 |

*2 rows*

(DuckDB also accepts the alias, `HAVING total_qty > 15`; MySQL does too. Writing
the aggregate itself works everywhere.)

---

## 6. Everything Together

The full life of a query: **filter rows → group → aggregate → filter groups → sort.**

```sql
SELECT department,
       STRING_AGG(product, ', ' ORDER BY product) AS contents,
       COUNT(*)                                   AS number_of_orders,
       SUM(quantity * unit_price)                 AS total_revenue
FROM orders
WHERE unit_price < 1000              -- 1. drop the expensive items (laptops) first
GROUP BY department                  -- 2. make one pile per department
HAVING SUM(quantity * unit_price) > 100   -- 3. keep only piles above $100
ORDER BY total_revenue DESC;         -- 4. sort
```

Result:

| department | contents | number_of_orders | total_revenue |
|---|---|---:|---:|
| IT | Monitors, Pens | 2 | 1505.0 |
| HR | Monitors, Paper, Paper, Pens | 4 | 431.0 |
| Sales | Paper, Pens, Pens | 3 | 130.0 |

*3 rows*

The revenues are lower than the departments' real totals because `WHERE` removed
the laptops before grouping.

| Clause | When it runs | What it does | Can it use `SUM`, `AVG`, …? |
|---|---|---|---|
| `WHERE` | before grouping | filters rows | **no** |
| `GROUP BY` | grouping | makes the piles | — |
| `HAVING` | after grouping | filters groups | **yes** |

---

## 7. Two Common Errors

### Error 1 — a column that is neither grouped nor aggregated

*The mistake:* show the total quantity per department — but also list `product`
in `SELECT`:

```sql
SELECT department,
       product,
       SUM(quantity)
FROM orders
GROUP BY department;
```

Result — an error:

```console
Binder Error: column "product" must appear in the GROUP BY clause or must be part of an aggregate function.
```

**Why it fails:** the Sales pile holds Pens, Paper, and Laptops. SQL can give
you one `SUM(quantity)` for the pile (36) — but which **one** `product` should it
show on that one row?

**The fix — three choices:**

1. group by it as well: `GROUP BY department, product` (more piles);
2. aggregate it: `STRING_AGG(product, ', ' ORDER BY product)` (all values in
   one text);
3. leave it out of `SELECT` if your question doesn't need it.

### Error 2 — an aggregate in `WHERE`

*The mistake:* filter on a total in `WHERE`:

```sql
SELECT department,
       SUM(quantity) AS total_qty
FROM orders
WHERE SUM(quantity) > 10
GROUP BY department;
```

Result — an error:

```console
Binder Error: WHERE clause cannot contain aggregates!
```

**Why it fails:** `WHERE` runs **before** the piles exist, so there is no
`SUM(quantity)` yet. **The fix:** `HAVING`, which runs after grouping:

```sql
SELECT department,
       SUM(quantity) AS total_qty
FROM orders
GROUP BY department
HAVING SUM(quantity) > 10
ORDER BY department;
```

Result:

| department | total_qty |
|---|---:|
| HR | 19 |
| Sales | 36 |

*2 rows*

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
