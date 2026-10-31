You are the duckdb and jupyter notebook expert.

My files are here:

<course repo>/data_stories/coffee_shop

Coffee Shop Transactions. 
 % xlsx2csv coffee_shop_sales.xlsx | head
transaction_id,transaction_date,transaction_time,transaction_qty,store_id,store_location,product_id,unit_price,product_category,product_type,product_detail
1,01-01-23,07:06,2,5,Lower Manhattan,32,3,Coffee,Gourmet brewed coffee,Ethiopia Rg
2,01-01-23,07:08,2,5,Lower Manhattan,57,3.1,Tea,Brewed Chai tea,Spicy Eye Opener Chai Lg
3,01-01-23,07:14,2,5,Lower Manhattan,59,4.5,Drinking Chocolate,Hot chocolate,Dark chocolate Lg
4,01-01-23,07:20,1,5,Lower Manhattan,22,2,Coffee,Drip coffee,Our Old Time Diner Blend Sm
5,01-01-23,07:22,2,5,Lower Manhattan,57,3.1,Tea,Brewed Chai tea,Spicy Eye Opener Chai Lg
6,01-01-23,07:22,1,5,Lower Manhattan,77,3,Bakery,Scone,Oatmeal Scone
7,01-01-23,07:25,1,5,Lower Manhattan,22,2,Coffee,Drip coffee,Our Old Time Diner Blend Sm
8,01-01-23,07:33,2,5,Lower Manhattan,28,2,Coffee,Gourmet brewed coffee,Columbian Medium Roast Sm
9,01-01-23,07:39,1,5,Lower Manhattan,39,4.25,Coffee,Barista Espresso,Latte Rg

% xlsx2csv coffee_shop_sales.xlsx | wc -l
  149117    
  
There are only data for 6 months.

Everything is done in jupyter notebook:

1. a separate cell
read shopify_sales_dataset_ml_eda.csv
and create a DuckDB database call it coffee_shop_sales.duckdb) 

2. a separate cell
2.1 then dedup it (drop full duplicate rows)
2.2 Explain how to dedup it

3. If transaction_date has  different formats, then standardize it

4. Create a jupyter notebook using the coffee_shop_sales.duckdb :

5 basic queries
10 basic+ queries
10 intermediate queries
5  Ranking functions queries (using "WITH" subqueries and ranking functions)

sample queries:

	•	“Which store generates most revenue?”
	•	“Top-selling product categories?”
	•	“Morning vs afternoon sales?”
	•	“Coffee vs Tea trends?”

Enables key SQL concepts

You can cover:
	•	GROUP BY (core)
	•	WHERE vs HAVING
	•	Window functions (later)
	•	Top-N queries
	•	Time-based analytics
	
	
for each cell: 

1. what are we doing? Explain well.
 
2. sql solution (nice formatted), 

3. result displyed

4. result in plot when possible 
(plotting code should be decoupled from main notebook).

===
claude:

I need access to that folder to read the files. Let me request it.Got access. Let me read the README and explore the project structure.Let me check the existing checkpoint notebooks to see if there's prior work to build on.Great, I've reviewed everything — the README specs, the data (149K coffee shop transactions across 3 NYC stores, Jan–Jun 2023), and the two existing checkpoint notebooks (EDA and star schema). The README is asking for something more focused on **SQL skill progression** rather than the EDA/warehouse approach in the checkpoints.Clear. Let me set up task tracking and get to work.Let me first install the needed packages and test the data loading in the sandbox, then build the notebooks.Good — I can build proper .ipynb files with Python's json module. Let me create all three files now. I'll build them via Python scripts in the sandbox.Now the plot helpers module:Now the big one — Notebook 2 with all 30 SQL queries. I'll build it in parts:Now let me verify the notebooks are valid and well-structured:Both notebooks validate perfectly. Let me also verify the SQL in the analysis notebook references the right column names from the data:Everything checks out — the D section count of 6 includes the section intro header plus 5 query headers, and the 32 code cells = 1 setup + 30 queries + 1 close. Let me list the final files:All three files are in your `coffee_shop` folder. Here's what was created:

**1. `coffee_shop_build_db.ipynb`** (25 cells, 12 code) — Loads the xlsx, inspects the data, deduplicates, standardizes dates, extracts hour/day/month features, computes `sales_amount`, and writes everything to `coffee_shop_sales.duckdb`.

**2. `plot_helpers.py`** — Decoupled plotting module with 7 reusable functions: `bar_chart`, `hbar_chart`, `line_chart`, `multi_line_chart`, `pie_chart`, `heatmap_chart`, and `grouped_bar_chart`. The analysis notebook imports these instead of embedding plot code inline.

**3. `coffee_shop_sql_analysis.ipynb`** (69 cells, 30 queries) — Opens the DuckDB file read-only and runs 30 progressive queries:

| Section | Queries | Concepts |
|---|---|---|
| A — Basic | 5 | `SELECT`, `COUNT`, `DISTINCT`, `SUM`, `LIMIT` |
| B — Basic+ | 10 | `GROUP BY`, `WHERE`, `HAVING`, `AVG`/`MIN`/`MAX`, Top-N |
| C — Intermediate | 10 | `CASE`, subqueries, multi-column grouping, heatmaps, time analytics |
| D — Ranking | 5 | CTEs (`WITH`), `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, running totals |

Every query cell has a Markdown explanation (what + why + SQL concept), the formatted SQL, and a plot via `plot_helpers` where applicable. Run Notebook 1 first, then Notebook 2.







