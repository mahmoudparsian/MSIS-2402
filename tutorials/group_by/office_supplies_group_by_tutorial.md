## Mastering SQL Aggregation: The GROUP BY Tutorial 

## 1. The Dataset (`office_supplies.csv`)

```
This dataset represents orders at an 
office supply store. It includes intentional 
variety in departments, products, and prices 
to demonstrate how grouping works.
``` 

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
------------------------------

## 2. DuckDB Setup

Run this to create your table and load the data.

```sql
CREATE TABLE orders 
AS 
SELECT * FROM read_csv_auto('office_supplies.csv');

SELECT * FROM orders;
┌────────────┬──────────┬──────────┬────────────┐
│ department │ product  │ quantity │ unit_price │
│  varchar   │ varchar  │  int64   │   double   │
├────────────┼──────────┼──────────┼────────────┤
│ Sales      │ Pens     │       10 │        2.0 │
│ Sales      │ Pens     │        5 │        2.0 │
│ Sales      │ Paper    │       20 │        5.0 │
│ Sales      │ Laptops  │        1 │     1200.0 │
│ IT         │ Laptops  │        2 │     1200.0 │
│ IT         │ Monitors │        5 │      300.0 │
│ IT         │ Pens     │        2 │        2.5 │
│ IT         │ Laptops  │        1 │     1300.0 │
│ HR         │ Paper    │       10 │        5.0 │
│ HR         │ Pens     │        3 │        2.0 │
│ HR         │ Monitors │        1 │      350.0 │
│ HR         │ Paper    │        5 │        5.0 │
└────────────┴──────────┴──────────┴────────────┘
  12 rows                             4 columns
------------------------------

## 3. The Mental Model: What is GROUP BY?

```
Imagine your table is a deck of 
cards. GROUP BY takes that deck 
and sorts it into piles based on 
a column (e.g., Department). 

Once the cards are in piles, you 
can no longer see individual cards; 
you can only ask questions about the 
pile (e.g., "How many cards are here?" 
or "What is the total cost?"). 
```

## Visualizing the Aggregation with LISTAGG (GROUP_CONCAT)

```
In DuckDB, LISTAGG (similar to GROUP_CONCAT 
in MySQL) is the best way for students to see 
"inside" the group pile.
```

The Query:

```sql
memory D SELECT
             department,
             SUM(quantity) AS total_qty,
             LISTAGG(quantity, ', ') AS quantities,
             LISTAGG(product, ', ')  AS  ptoducts
         FROM orders
         GROUP BY department;
┌────────────┬───────────┬──────────────┬──────────────────────────────────┐
│ department │ total_qty │  quantities  │             ptoducts             │
│  varchar   │  int128   │   varchar    │             varchar              │
├────────────┼───────────┼──────────────┼──────────────────────────────────┤
│ HR         │        19 │ 10, 3, 1, 5  │ Paper, Pens, Monitors, Paper     │
│ IT         │        10 │ 2, 5, 2, 1   │ Laptops, Monitors, Pens, Laptops │
│ Sales      │        36 │ 10, 5, 20, 1 │ Pens, Pens, Paper, Laptops       │
└────────────┴───────────┴──────────────┴──────────────────────────────────┘
```

memory D SELECT
             department,
             SUM(quantity) AS total_qty,
             -- Combine product and quantity into 
             -- one string before aggregating
             LISTAGG(product || ' (' || quantity || ')', ', ') 
               AS products_with_qty
         FROM orders
         GROUP BY department;
┌────────────┬───────────┬──────────────────────────────────────────────────┐
│ department │ total_qty │                products_with_qty                 │
│  varchar   │  int128   │                     varchar                      │
├────────────┼───────────┼──────────────────────────────────────────────────┤
│ Sales      │        36 │ Pens (10), Pens (5), Paper (20), Laptops (1)     │
│ IT         │        10 │ Laptops (2), Monitors (5), Pens (2), Laptops (1) │
│ HR         │        19 │ Paper (10), Pens (3), Monitors (1), Paper (5)    │
└────────────┴───────────┴──────────────────────────────────────────────────┘
```



------------------------------

## 4. Grouping by Multiple Columns

```
You can create more specific piles by 
grouping by two columns/attributes. 
The "pile" now represents a unique combination.
```

The Query:

```
SELECT 
    department, 
    product,
    SUM(quantity) AS total_sold
FROM orders
GROUP BY department, product
ORDER BY department;
```

The Result:

```
┌────────────┬──────────┬────────────┐
│ department │ product  │ total_sold │
│  varchar   │ varchar  │   int128   │
├────────────┼──────────┼────────────┤
│ HR         │ Paper    │         15 │
│ HR         │ Monitors │          1 │
│ HR         │ Pens     │          3 │
│ IT         │ Monitors │          5 │
│ IT         │ Pens     │          2 │
│ IT         │ Laptops  │          3 │
│ Sales      │ Laptops  │          1 │
│ Sales      │ Pens     │         15 │
│ Sales      │ Paper    │         20 │
└────────────┴──────────┴────────────┘
```

------------------------------

## 5. The Great Filter Debate: WHERE vs. HAVING

```
This is the most confusing part for students. 
Here is the rule:

   1. WHERE: Filters rows BEFORE the piles are made.
   
   2. HAVING: Filters piles AFTER the calculation is done.  
```

## Example A: Using `WHERE`

```
"Show me the total items sold per department, 
but ignore all Laptops." (The "Laptop" cards 
are thrown in the trash before we start grouping).
```

```sql
SELECT department, 
       SUM(quantity) as total_qty
FROM orders
WHERE product != 'Laptops'
GROUP BY department
ORDER by department;

┌────────────┬───────────┐
│ department │ total_qty │
│  varchar   │  int128   │
├────────────┼───────────┤
│ HR         │        19 │
│ IT         │         7 │
│ Sales      │        35 │
└────────────┴───────────┘
```

## Example B: Using `HAVING`

```
"Show me the total items sold per department, 
but only show me departments that sold more 
than 15 items in total."

(We make all the piles first, calculate 
the totals, and then hide the piles that 
are too small).
```

```sql
SELECT department, 
       SUM(quantity) as total_qty
FROM orders
GROUP BY department
ORDER BY department;

┌────────────┬───────────┐
│ department │ total_qty │
│  varchar   │  int128   │
├────────────┼───────────┤
│ HR         │        19 │
│ IT         │        10 │
│ Sales      │        36 │
└────────────┴───────────┘
```

Filter aggregated result set:

```
SELECT department, 
       SUM(quantity) as total_qty
FROM orders
GROUP BY department
HAVING total_qty > 15
ORDER BY department;

┌────────────┬───────────┐
│ department │ total_qty │
│  varchar   │  int128   │
├────────────┼───────────┤
│ HR         │        19 │
│ Sales      │        36 │
└────────────┴───────────┘
```
------------------------------

## 6. Combining Everything (The "Flagship" Query)

```
This query shows the full lifecycle of a 
SQL statement: 

Filter rows → Group → Aggregate → Filter Groups → Sort. 
```

```sql
SELECT 
    department,
    LISTAGG(product, '|') AS contents,
    COUNT(*) AS number_of_orders,
    SUM(quantity * unit_price) AS total_revenue
FROM orders
WHERE unit_price < 1000      -- 1. Ignore expensive items first
GROUP BY department          -- 2. Create piles by department
HAVING total_revenue > 100   -- 3. Only keep high-revenue departments
ORDER BY total_revenue DESC; -- 4. Final Sort
```

The Result:


| department | contents | number_of_orders | total_revenue |
|---|---|---|---|
| IT | Monitors, Pens | 2 | 1505.00 |
| Sales | Pens, Pens, Paper | 3 | 130.00 |
| HR | Paper, Pens, Monitors, Paper | 4 | 431.00 |

```
(Note: Revenue looks different here 
because Laptops were filtered out 
by the WHERE clause!)
```

------------------------------

## 7. Summary Table for Students

| Clause  | Timing | Purpose | Can use Aggregates (SUM/AVG)? |
|---|---|---|---|
| WHERE | Pre-Grouping | Filter raw data | No |
| GROUP BY | Processing | Create categories | N/A |
| HAVING | Post-Grouping | Filter result sets | Yes |

------------------------------
## 1. The Illegal Column Error

```
The Mistake:

A student wants to see the total quantity 
sold per department, but they also include 
the product column in the SELECT list without 
grouping by it or aggregating it.

-- THIS WILL FAIL in most SQL databases

SELECT department, product, 
       SUM(quantity)
FROM orders
GROUP BY department;

Why it fails (The Logic):

If the "Sales" department pile contains 
Pens, Paper, and Laptops, and you ask for 
SUM(quantity), SQL can easily give you 36. 
But if you ask for product, SQL gets confused: 
"Should I show you 'Pens'? 'Paper'? Or 'Laptops'? 
I have three different values but only one row 
to show them in!"

The Fix:

You have three choices:

   1. Group by that column too: 
      GROUP BY department, product (Creates more piles).
      
   2. Aggregate that column: LISTAGG(product, ', ') 
      (Shows all values in one string).
      
   3. Remove the column: If it's not part of 
      your question, don't include it in the SELECT.
```

------------------------------

## 2. The "Filtering Aggregates in WHERE" Error

```
The Mistake:

A student tries to filter the result of 
a SUM() inside the WHERE clause.

-- THIS WILL FAIL
SELECT department, 
       SUM(quantity) as total_qty
FROM orders
WHERE total_qty > 10
GROUP BY department;

Why it fails:

The WHERE clause is the very first thing 
that happens. At that moment, SQL hasn't 
even created the piles yet, so it doesn't 
know what the SUM(quantity) is.

The Fix:
Use HAVING.

SELECT department, 
       SUM(quantity) AS total_qty
FROM orders
GROUP BY department
HAVING total_qty > 10; -- This works because it happens AFTER grouping.
```

------------------------------

## 3. The Alias Reference Error

```
The Mistake:
Using a name you created (an Alias) 
inside the WHERE or GROUP BY clause.

-- THIS WILL FAIL in many traditional SQL 
-- engines (though DuckDB is smarter)

SELECT department, 
       SUM(quantity) AS total_qty
FROM orders
WHERE total_qty > 10
GROUP BY department;

Why it fails:
Technically, the WHERE clause is executed 
before the SELECT clause. Therefore, the 
database engine hasn't "read" the name 
total_qty yet.

The Fix:
Repeat the calculation in the HAVING clause, 
or use the raw column name in the WHERE clause.

* Note: DuckDB is modern and actually allows 
  you to use aliases in many places where older 
  databases (like Oracle or SQL Server) do not.
```
------------------------------

## 4. Summary of the SQL Execution Order (The "Why")

```
To help students remember, teach them 
the Logical Query Processing Order. This 
is the order in which the computer actually 
"thinks" about your query:

   1. FROM / JOIN: Get the raw data.
   2. WHERE: Filter the individual rows.
   3. GROUP BY: Put the remaining rows into piles.
   4. AGGREGATIONS: Calculate the SUM, COUNT, AVG for each pile.
   5. HAVING: Filter the piles based on those calculations.
   6. SELECT: Choose which columns/results to show.
   7. ORDER BY: Sort the final result.
```

------------------------------

## Final Pro-Tip for the Classroom

```
If a student is ever stuck, ask them: 

"Is the column you are selecting either 
in a pile (GROUP BY) or a calculation 
(SUM/COUNT/AVG)?"

If the answer is "Neither," the query is 
logically broken and will throw an error.
```


