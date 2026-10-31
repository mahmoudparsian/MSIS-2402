# `ROW_NUMBER()` Example

```
   In DuckDB, you can run window functions 
   directly on in-memory data. This example 
   ranks laptops by price within each brand.
```

## 1. The SQL Script

```
    You can copy and paste this directly 
    into a DuckDB CLI or a SQL notebook.

    -- Create a temporary table with sample data

    CREATE TABLE laptops AS 
    SELECT * FROM 
    (VALUES 
        ('Apple', 'MacBook Air', 999),
        ('Apple', 'MacBook Pro', 2499),
        ('Dell', 'XPS 13', 1100),
        ('Dell', 'Inspiron', 600),
        ('Dell', 'Alienware', 2100)
    ) AS t(brand, model, price);
 
    -- Apply ROW_NUMBER() with PARTITION BY

    SELECT 
        brand,
        model,
        price,
        ROW_NUMBER() OVER (
             PARTITION BY brand 
             ORDER BY price DESC
        ) AS price_rank
    FROM laptops;
```

## 2. The Result

```
The ROW_NUMBER() starts over 
at 1 for every new brand group.
```

| brand | model | price | price_rank |
|---|---|---|---|
| Apple | MacBook Pro | 2499 | 1 |
| Apple | MacBook Air | 999 | 2 |
| Dell | Alienware | 2100 | 1 |
| Dell | XPS 13 | 1100 | 2 |
| Dell | Inspiron | 600 | 3 |


## Why use this in DuckDB?

```
    DuckDB is highly optimized for analytical 
    queries like this. A common pattern is using 
    this query as a Subquery or CTE to filter 
    for only the top item per group:
```

```sql
    -- Returns only the most expensive 
    -- laptop for each brand
    WITH ranked_laptops AS (
        SELECT *, 
            ROW_NUMBER() OVER (
                PARTITION BY brand 
                ORDER BY price DESC
            ) as rnk
        FROM laptops
    )
    SELECT * FROM ranked_laptops 
    WHERE rnk = 1; 
```

---

# Example-2: Query The CSV File Directly

Save this content as a file named `employees.csv`

```
department,employee,salary
Sales,Alice,5000
Sales,Bob,6000
HR,Charlie,4500
HR,David,4500
IT,Eve,7000
```

## 2. The DuckDB SQL Commands

```
    DuckDB can query CSV files directly 
    using the read_csv_auto function.
```

* Example 1: `ROW_NUMBER()` without `PARTITION BY`

```sql
-- This treats the whole file as one group 
-- and numbers everything 1-5:

SELECT 
       *,
       ROW_NUMBER() OVER (ORDER BY salary DESC) 
       as global_rank
FROM read_csv_auto('employees.csv');
```


## 3. The Result (Without Partition (Global Ranking))

| department | employee | salary | global_rank |
|---|---|---|---|
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 2 |
| Sales | Alice | 5000 | 3 |
| HR | Charlie | 4500 | 4 |
| HR | David | 4500 | 5 |

* Example 2: `ROW_NUMBER()` with `PARTITION BY`

```sql
        -- This restarts the numbering 
        -- for each department.
        SELECT 
               *,
               ROW_NUMBER() OVER (
                   PARTITION BY department 
                   ORDER BY salary DESC
               ) as dept_rank
        FROM read_csv_auto('employees.csv');
```

## Result 2: With Partition (Ranking per Department)

| department | employee | salary | dept_rank |
|---|---|---|---|
| HR | Charlie | 4500 | 1 |
| HR | David | 4500 | 2 |
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 1 |
| Sales | Alice | 5000 | 2 |


---


# Create Table from CSV Then Query


## 1. The CSV Content (employees.csv)

```
department,employee,salary
Sales,Alice,5000
Sales,Bob,6000
HR,Charlie,4500
HR,David,4500
IT,Eve,7000
```

## 2. DuckDB SQL Setup and Queries

```sql

-- ---------------------------------------------
-- Step 1: Create the table by importing the CSV
-- ----------------------------------------------
CREATE TABLE staff 
AS 
SELECT * FROM read_csv_auto('employees.csv');


-- --------------------------------------------
-- Step 2: ROW_NUMBER() without PARTITION BY
-- Numbers every row in the table based on 
-- salary (highest to lowest)
-- ----------------------------------------------
SELECT 
    department, 
    employee, 
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as global_rank
FROM staff;

-- ----------------------------------------
-- Step 3: ROW_NUMBER() with PARTITION BY
-- Restarts the count at 1 for every 
-- unique department
-- ------------------------------------------
SELECT 
    department, 
    employee, 
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY department 
        ORDER BY salary DESC
    ) as dept_rankFROM staff;
```

## 3. The Results## Global Ranking (No Partition)

| department | employee | salary | global_rank |
|---|---|---|---|
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 2 |
| Sales | Alice | 5000 | 3 |
| HR | Charlie | 4500 | 4 |
| HR | David | 4500 | 5 |

## Department Ranking (With Partition)

| department | employee | salary | dept_rank |
|---|---|---|---|
| HR | Charlie | 4500 | 1 |
| HR | David | 4500 | 2 |
| IT | Eve | 7000 | 1 |
| Sales | Bob | 6000 | 1 |
| Sales | Alice | 5000 | 2 |



