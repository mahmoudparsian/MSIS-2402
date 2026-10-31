## Mastering SQL Joins: Connecting the Dots

A hands-on tour of `INNER JOIN`, `LEFT JOIN` and `RIGHT JOIN` in DuckDB, using two
small CSV files: 12 employees and 4 departments.

```
In relational databases, data is split into 
multiple tables to avoid redundancy. Joins 
are the tools we use to stitch that data back 
together to answer business questions.
```

------------------------------

## 1. The Data Setup

```
We will create two files: 

employees.csv (the "Left" table) and 
departments.csv (the "Right" table).
```

## File : `employees.csv`

```
Note: Employees John and Sarah have 
dept_id 99, which doesn't exist in our 
department list. They are "unassigned" 
or "orphaned" records.
```

```
emp_id,name,dept_id
1,Alice,10
2,Bob,10
3,Charlie,10
4,David,20
5,Eve,20
6,Frank,20
7,Grace,30
8,Heidi,30
9,Ivan,30
10,Judy,30
11,John,99
12,Sarah,99
```

## File : `departments.csv`

```
Note: The Marketing department (ID 40) 
currently has no employees assigned to it.
```

```
dept_id,dept_name
10,Sales
20,IT
30,HR
40,Marketing
```
------------------------------

## 2. DuckDB Setup

Run these commands to load your tables.

```sql
CREATE TABLE employees 
AS 
SELECT * FROM read_csv_auto('employees.csv');

SELECT * FROM employees;
┌────────┬─────────┬─────────┐
│ emp_id │  name   │ dept_id │
│ int64  │ varchar │  int64  │
├────────┼─────────┼─────────┤
│      1 │ Alice   │      10 │
│      2 │ Bob     │      10 │
│      3 │ Charlie │      10 │
│      4 │ David   │      20 │
│      5 │ Eve     │      20 │
│      6 │ Frank   │      20 │
│      7 │ Grace   │      30 │
│      8 │ Heidi   │      30 │
│      9 │ Ivan    │      30 │
│     10 │ Judy    │      30 │
│     11 │ John    │      99 │
│     12 │ Sarah   │      99 │
└────────┴─────────┴─────────┘
  12 rows          3 columns

CREATE TABLE departments 
AS 
SELECT * FROM read_csv_auto('departments.csv');

SELECT * FROM departments;
┌─────────┬───────────┐
│ dept_id │ dept_name │
│  int64  │  varchar  │
├─────────┼───────────┤
│      10 │ Sales     │
│      20 │ IT        │
│      30 │ HR        │
│      40 │ Marketing │
└─────────┴───────────┘
```
------------------------------

## 3. INNER JOIN: The "Perfect Match"

```
The INNER JOIN only returns rows where 
there is a match in both tables. 

If an employee doesn't have a valid department, 
or a department has no employees, they are excluded.

The Business Question: "Give me a list of all 
employees and their department names."
```

```sql
SELECT e.name, 
       d.dept_name
FROM employees e
INNER JOIN departments d ON e.dept_id = d.dept_id;

┌─────────┬───────────┐
│  name   │ dept_name │
│ varchar │  varchar  │
├─────────┼───────────┤
│ Alice   │ Sales     │
│ Bob     │ Sales     │
│ Charlie │ Sales     │
│ David   │ IT        │
│ Eve     │ IT        │
│ Frank   │ IT        │
│ Grace   │ HR        │
│ Heidi   │ HR        │
│ Ivan    │ HR        │
│ Judy    │ HR        │
└─────────┴───────────┘
  10 rows   2 columns
```

Why?

``` 
Why? John and Sarah (dept 99) are 
hidden because dept 99 isn't in the 
department table. 

Marketing (dept 40) is hidden because 
no one works there.
```

------------------------------

## 4. LEFT JOIN: "Prioritize the People"

```
The LEFT JOIN returns all rows from the 
left table (employees), plus matches from 
the right table. If there is no match, the 
right side will show NULL.

The Business Question: "I need a list of 
every single employee. If they belong to 
a department, show it; if not, show them 
anyway so we can fix their record."
```

```sql
SELECT e.name, 
       d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;

┌─────────┬───────────┐
│  name   │ dept_name │
│ varchar │  varchar  │
├─────────┼───────────┤
│ Alice   │ Sales     │
│ Bob     │ Sales     │
│ Charlie │ Sales     │
│ David   │ IT        │
│ Eve     │ IT        │
│ Frank   │ IT        │
│ Grace   │ HR        │
│ Heidi   │ HR        │
│ Ivan    │ HR        │
│ Judy    │ HR        │
│ John    │ NULL      │ <--- 🛑
│ Sarah   │ NULL      │ <--- 🛑
└─────────┴───────────┘
12 rows   2 columns
```

* Insight: 

```
Insight: John and Sarah appear, but their 
dept_name is NULL. This tells a manager: 
"These two people are on payroll but aren't 
assigned to a valid department!"
```

------------------------------

## 5. RIGHT JOIN: "Prioritize the Departments"

```
The RIGHT JOIN returns all rows from 
the right table (departments), plus 
matching employees. If a department 
has no employees, the employee side 
shows NULL.

The Business Question: 

    "Show me all departments and 
    who works in them. I also want 
    to see departments that are 
    currently empty."
```


```sql
SELECT e.name, 
       d.dept_name
FROM employees e
RIGHT JOIN departments d ON e.dept_id = d.dept_id;

┌─────────┬───────────┐
│  name   │ dept_name │
│ varchar │  varchar  │
├─────────┼───────────┤
│ Alice   │ Sales     │
│ Bob     │ Sales     │
│ Charlie │ Sales     │
│ David   │ IT        │
│ Eve     │ IT        │
│ Frank   │ IT        │
│ Grace   │ HR        │
│ Heidi   │ HR        │
│ Ivan    │ HR        │
│ Judy    │ HR        │
│ NULL    │ Marketing │ <--- 🛑
└─────────┴───────────┘
  11 rows   2 columns
```

The Result: 

```
     11 rows returned:
        10 matched employees 
        + 1 empty department.
```

* Insight:

```
* Insight: Marketing appears with a 
NULL employee name. This tells a 
recruiter: "We have a Marketing department, 
but we haven't hired anyone for it yet!"
```

------------------------------

## 6. Visual Summary for Students

| Join Type | Left Table (Employees) | Right Table (Depts) | When to use? |
|---|---|---|---|
| INNER | Only the matched | Only the matched | To see only complete relationships. |
| LEFT | Everything | Only the matched | To find "orphaned" records on the left (NULLs on right). |
| RIGHT | Only the matched | Everything | To find "empty" categories on the right (NULLs on left). |
| FULL | Everything | Everything | To see every record from both sides, matched or not. |

------------------------------

## 7. The "Master Stroke" Business Insight Query

```
Let's combine Joins with Aggregation 
to get a high-level view.

Question: 
          "Show me each department, 
          how many people work there, 
          and the list of names."

SELECT 
    d.dept_name, 
    COUNT(e.emp_id) AS head_count,
    LISTAGG(e.name, ', ') AS staff_list
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_name;
```

The Result:

```
┌───────────┬────────────┬──────────────────────────┐
│ dept_name │ head_count │        staff_list        │
│  varchar  │   int64    │         varchar          │
├───────────┼────────────┼──────────────────────────┤
│ IT        │          3 │ David, Eve, Frank        │
│ HR        │          4 │ Grace, Heidi, Ivan, Judy │
│ Sales     │          3 │ Alice, Bob, Charlie      │
│ Marketing │          0 │ NULL                     │
└───────────┴────────────┴──────────────────────────┘
```

## Crucial Lesson: 

		Notice we used a LEFT JOIN starting 
		from departments. If we had used an 
		INNER JOIN, the Marketing department 
		would have vanished from the report entirely, 
		giving the false impression it doesn't exist!


# Final Exercise for Students:

	How would you write a query to find 
	only the employees who are not assigned 
	to a valid department? 
	
	(Hint: Use LEFT JOIN and WHERE d.dept_id IS NULL).



