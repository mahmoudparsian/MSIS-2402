# DuckDB Window Functions Tutorial
# `ROW_NUMBER`, `RANK`, and `DENSE_RANK`

```
This tutorial demonstrates the differences 
between the three primary ranking functions 
in SQL using DuckDB.
```
---

## 1. The Data (employees.csv)

```
Save the following 10 rows into a 
file named employees.csv. Notice that 
some employees have the same salary (ties) 
to highlight how the functions differ.
```

```text
country,gender,employee,salary
USA,M,John,5000
USA,F,Sarah,5000
USA,M,Mike,4000
UK,F,Emma,6000
UK,M,Liam,6000
UK,F,Olivia,5500
CAN,M,Alex,7000
CAN,F,Zoe,7000
CAN,M,Ryan,5000
CAN,F,Maya,4500
```

---

## 2. DuckDB Setup

```
Run these commands to create
your table and load the data.
```

```sql
-- Create table and import data
CREATE TABLE staff 
AS 
SELECT * FROM read_csv_auto('employees.csv');
```

---

## 3. Example 1: Without PARTITION BY (Global Ranking)

```
When used without a partition, the 
window functions look at the entire 
dataset as one single group.
```

The Query:

```sql
SELECT 
    employee,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK()       OVER (ORDER BY salary DESC) as rnk,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rnk
FROM staff;
```

The Result:

| employee | salary | row_num | rnk | dense_rnk | Logic Explanation |
|---|---|---|---|---|---|
| Alex | 7000 | 1 | 1 | 1 | Tie for 1st |
| Zoe | 7000 | 2 | 1 | 1 | Tie for 1st |
| Emma | 6000 | 3 | 3 | 2 | RANK skips 2; DENSE does not |
| Liam | 6000 | 4 | 3 | 2 | Tie for 3rd |
| Olivia | 5500 | 5 | 5 | 3 | RANK skips 4 |
| John | 5000 | 6 | 6 | 4 | Three-way tie for 6th |
| Sarah | 5000 | 7 | 6 | 4 | ... |
| Ryan | 5000 | 8 | 6 | 4 | ... |
| Maya | 4500 | 9 | 9 | 5 | RANK skips 7 and 8 |
| Mike | 4000 | 10 | 10 | 6 | ... |

---

## 4. Example 2: With PARTITION BY (Ranking within Country)

```
This tells DuckDB to restart the 
calculations every time the country 
value changes.
```

The Query:

```sql
SELECT 
    country,
    employee,
    salary,
    ROW_NUMBER() OVER (PARTITION BY country ORDER BY salary DESC) as row_num,
    RANK()       OVER (PARTITION BY country ORDER BY salary DESC) as rnk,
    DENSE_RANK() OVER (PARTITION BY country ORDER BY salary DESC) as dense_rnk
FROM staff;
```

The Result:

| country | employee | salary | row_num | rnk | dense_rnk |
|---|---|---|---|---|---|
| CAN | Alex | 7000 | 1 | 1 | 1 |
| CAN | Zoe | 7000 | 2 | 1 | 1 |
| CAN | Ryan | 5000 | 3 | 3 | 2 |
| CAN | Maya | 4500 | 4 | 4 | 3 |
| UK | Emma | 6000 | 1 | 1 | 1 |
| UK | Liam | 6000 | 2 | 1 | 1 |
| UK | Olivia | 5500 | 3 | 3 | 2 |
| USA | John | 5000 | 1 | 1 | 1 |
| USA | Sarah | 5000 | 2 | 1 | 1 |
| USA | Mike | 4000 | 3 | 3 | 2 |

---

## Summary Table: Which one should I use?

| Function | Handle Ties? | Sequential? | Typical Use Case |
|---|---|---|---|
| ROW_NUMBER | No (Unique IDs) | Yes (1, 2, 3, 4) | Pagination or picking exactly one row. |
| RANK | Yes (Same value = Same rank) | No (1, 1, 3, 4) | Standard "Top 10" lists where ties skip places. |
| DENSE_RANK | Yes (Same value = Same rank) | Yes (1, 1, 2, 3) | Grouped rankings where you don't want gaps. |



## Tutorial: Using Multiple Partitions in DuckDB

```
Partitioning by multiple columns 
(e.g., country and gender) creates 
smaller, highly specific subgroups. 
DuckDB will reset the counter only 
when the combination of those columns 
changes.
```

## 1. The Data (`employees.csv`)

We will use the same 10 rows from the previous example.

```
country,gender,employee,salary
USA,M,John,5000
USA,F,Sarah,5000
USA,M,Mike,4000
UK,F,Emma,6000
UK,M,Liam,6000
UK,F,Olivia,5500
CAN,M,Alex,7000
CAN,F,Zoe,7000
CAN,M,Ryan,5000
CAN,F,Maya,4500
```

---

## 2. The SQL Query (Multi-Column Partition)

```
In this query, we partition by both 
country and gender. This allows us to 
see who the top earner is for Males 
in Canada, Females in Canada, Males 
in the USA, etc.
```

```sql
SELECT 
    country,
    gender,
    employee,
    salary,
    ROW_NUMBER() OVER (
        PARTITION BY country, gender 
        ORDER BY salary DESC
    ) as row_num,
    RANK() OVER (
        PARTITION BY country, gender 
        ORDER BY salary DESC
    ) as rnk
FROM staff
ORDER BY country, gender, row_num;
```

---

## 3. The Result

| country | gender | employee | salary | row_num | rnk | Notes |
|---|---|---|---|---|---|---|
| CAN | F | Zoe | 7000 | 1 | 1 | Top Female in CAN |
| CAN | F | Maya | 4500 | 2 | 2 | |
| CAN | M | Alex | 7000 | 1 | 1 | Top Male in CAN |
| CAN | M | Ryan | 5000 | 2 | 2 | |
| UK | F | Emma | 6000 | 1 | 1 | Top Female in UK |
| UK | F | Olivia | 5500 | 2 | 2 | |
| UK | M | Liam | 6000 | 1 | 1 | Top Male in UK |
| USA | F | Sarah | 5000 | 1 | 1 | Top Female in USA |
| USA | M | John | 5000 | 1 | 1 | Top Male in USA |
| USA | M | Mike | 4000 | 2 | 2 | |

---

## Key Takeaways for Multi-Partitioning

```
   1. Granularity: Adding more columns to 
      PARTITION BY makes your groups more 
      "granular." Instead of ranking against 
      everyone in the country, you are only 
      ranking against people of the same gender 
      within that country.
      
   2. Resetting: The ROW_NUMBER resets to 1 
      every time a new combination of 
      country + gender appears.
   
   3. Use Case: This is extremely useful for 
      identifying "Best in Class" across 
      multiple categories—for example, finding 
      the most expensive product in every Category 
      and Sub-Category.
```

#  DuckDB and QUALIFY clause

```
DuckDB has a special shortcut that 
lets you filter window functions 
without using a subquery.

The QUALIFY clause is one of DuckDB's 
best "power features." In standard SQL, 
you cannot use window functions in a 
WHERE clause because window functions 
are calculated after filtering. 

Normally, you have to use a CTE or 
Subquery.

QUALIFY allows you to filter the results 
of window functions directly in your main 
query, making your code much cleaner.
```

## 1. The Goal

```
Find only the highest-paid employee 
for each gender within each country.
```

----

## 2. The DuckDB SQL (The "Old" Way vs. The DuckDB Way)

## The "Old" Standard SQL (Using a CTE)

```sql
WITH ranked_staff AS (
    SELECT 
        country, gender, employee, salary,
        ROW_NUMBER() OVER (
           PARTITION BY country, gender 
           ORDER BY salary DESC
        ) as rn
    FROM staff
)
SELECT * 
FROM ranked_staff 
WHERE rn = 1;
```

## The DuckDB Way (Using QUALIFY)

```
Notice how we don't even need to 
include the ROW_NUMBER in the 
SELECT list if we don't want to.
```

```sql
SELECT 
    country, 
    gender, 
    employee, 
    salary
FROM staff
QUALIFY ROW_NUMBER() OVER (
   PARTITION BY country, gender 
   ORDER BY salary DESC
) = 1;
```
---

## 3. The Result

| country | gender | employee | salary |
|---|---|---|---|
| CAN | F | Zoe | 7000 |
| CAN | M | Alex | 7000 |
| UK | F | Emma | 6000 |
| UK | M | Liam | 6000 |
| USA | F | Sarah | 5000 |
| USA | M | John | 5000 |

---

## 4. Why this is powerful

```
   1. Cleaner Code: You avoid nesting your queries.
   
   2. Logic Separation: You use WHERE to filter 
      raw rows (e.g., WHERE salary > 0) and 
      QUALIFY to filter the results of your 
      window calculations.
      
   3. Flexibility: You can use any ranking function 
      (RANK, DENSE_RANK, ROW_NUMBER) or even moving 
      averages inside the QUALIFY clause.
```

## Pro Tip: Using it for Duplicates

```
If you have a table with duplicate entries 
and only want to see one unique row per employee:
```

```sql
SELECT * 
FROM staff
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY employee ORDER BY salary DESC
) = 1;
```


