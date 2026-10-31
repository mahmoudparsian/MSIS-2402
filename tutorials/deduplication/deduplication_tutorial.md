## Comprehensive Guide: Deduplicating Data in DuckDB

```
This document covers two distinct ways 
to handle duplicates: 

  1. removing "exact" duplicates 
     (where every column is the same) 
     
  2. versus removing "business" duplicates 
     (where specific identifying columns match).

```
------------------------------

## 1. The Dataset (`raw_data.csv`)

```
Imagine a system log where some entries 
were double-saved, and some were updated.
```

```text
department,employee,salary
Sales,Alice,5000
Sales,Alice,5000
Sales,Alice,8000
HR,Bob,6000
HR,Bob,6000
IT,Charlie,7000
IT,Charlie,7000
IT,Eve,4000
IT,Eve,4000
HR,David,4500
```
------------------------------

## 2. Setup in DuckDB

```sql
-- Create table and load the "messy" data
CREATE TABLE staff 
AS 
SELECT * FROM read_csv_auto('raw_data.csv');
```

------------------------------

## 3. Example 1: Deduplicate the "Entire Record"

```
Use this when you want to remove 
identical twins. If every single 
column matches another row, you 
only want one.

The Logic: Partition by every column.
```

The Query:

```sql
SELECT 
    department, 
    employee, 
    salary
FROM staff
QUALIFY ROW_NUMBER() OVER (
    -- partition by ALL columns
    PARTITION BY department, employee, salary
) = 1;
```

The Result:

```
Alice appears twice because her $5,000 
and $8,000 rows are technically unique records.
```

| department | employee | salary | Note |
|---|---|---|---|
| Sales | Alice | 5000 | Kept 1 of 2 identical rows |
| Sales | Alice | 8000 | Unique (salary differs), so it stays |
| HR | Bob | 6000 | Kept 1 of 2 identical rows |
| IT | Charlie | 7000 | Kept 1 of 2 identical rows |
| IT | Eve | 4000 | Kept 1 of 2 identical rows |
| HR | David | 4500 | Original record |

------------------------------

## 4. Example 2: Deduplicate by "Employee" (Keeping Highest Salary)

```
Use this when you have multiple 
entries for one person but only 
want their latest or highest record.

The Logic: Partition by employee, 
           order by salary DESC.
```

The Query:

```sql
SELECT 
    department, 
    employee, 
    salary
FROM staff
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY employee 
    ORDER BY salary DESC
) = 1;
```

The Result:

```
Alice is now reduced to a single 
row—the one with the highest pay.
```

| department | employee | salary | Why? |
|---|---|---|---|
| Sales | Alice | 8000 | Winner of {5000, 5000, 8000} |
| HR | Bob | 6000 | Winner of {6000, 6000} |
| IT | Charlie | 7000 | Winner of {7000, 7000} |
| IT | Eve | 4000 | Winner of {4000, 4000} |
| HR | David | 4500 | Only one entry |

------------------------------
## 5. Summary Checklist

| Goal | Partition By... | Order By... |
|---|---|---|
| Remove exact clones | All columns | Not required (or any) |
| Keep newest record | Unique ID (e.g., employee) | timestamp DESC |
| Keep most expensive | Unique ID (e.g., employee) | salary DESC |
| Keep oldest record | Unique ID (e.g., employee) | timestamp ASC |
