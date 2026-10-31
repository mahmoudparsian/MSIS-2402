You are the duckdb and jupyter notebook expert.

My files are here:

% pwd
<course repo>/data_stories/taxi_trips

% ls -l taxi.csv
-rw-r--r--@ 1 user  staff  14869249 May 24 23:04 taxi.csv

ponder-datasets (main) % wc -l taxi.csv
  210035 taxi.csv
  
% head taxi.csv
VENDORID,TPEP_PICKUP_DATETIME,TPEP_DROPOFF_DATETIME,PASSENGER_COUNT,TRIP_DISTANCE,RATECODEID,STORE_AND_FWD_FLAG,PULOCATIONID,DOLOCATIONID,PAYMENT_TYPE,FARE_AMOUNT,EXTRA,MTA_TAX,TIP_AMOUNT,TOLLS_AMOUNT,IMPROVEMENT_SURCHARGE,TOTAL_AMOUNT
1,1/1/15 0:11,1/1/15 0:16,1,1,1,N,41,166,1,5.7,0.5,0.5,1.4,0,0,8.4
1,1/1/15 0:18,1/1/15 0:24,1,0.9,1,N,166,238,3,6,0.5,0.5,0,0,0,7.3
1,1/1/15 0:26,1/1/15 0:41,1,3.5,1,N,238,162,1,13.2,0.5,0.5,2.9,0,0,17.4
1,1/1/15 0:45,1/1/15 0:53,1,2.1,1,N,162,263,1,8.2,0.5,0.5,2.37,0,0,11.87
1,1/1/15 0:59,1/1/15 1:05,1,1,1,N,236,141,3,6,0.5,0.5,0,0,0,7.3
1,1/1/15 0:07,1/1/15 0:11,1,0.8,1,N,239,238,2,5,0.5,0.5,0,0,0,6.3
1,1/1/15 0:47,1/1/15 0:54,1,1.1,1,N,238,239,2,7,0.5,0.5,0,0,0,8.3
1,1/1/15 0:58,1/1/15 1:11,1,2.9,1,N,238,42,1,12.2,0.5,0.5,2.7,0,0,16.2
1,1/1/15 0:29,1/1/15 0:37,2,1.3,1,N,90,125,2,7,0.5,0.5,0,0,0,8.3


Everything is done in jupyter notebook:

1. a separate cell to read taxi.csv
and create a DuckDB database call it taxi_rides.duckdb) 

2. Rename columns (please check my renaming to make sure we are good)

VENDORID -> vendor_id
TPEP_PICKUP_DATETIME -> pickup_datetime
TPEP_DROPOFF_DATETIME -> dropoff_datetime
PASSENGER_COUNT -> passenger_count
TRIP_DISTANCE -> trip_distance
RATECODEID -> rate_code_id
STORE_AND_FWD_FLAG -> store_and_fwd_flag
PULOCATIONID -> pickup_location_id
DOLOCATIONID -> drop_location_id
PAYMENT_TYPE -> payment_type
FARE_AMOUNT -> fare_amount
EXTRA -> extra
MTA_TAX -> mta_tax
TIP_AMOUNT -> tip_amount
TOLLS_AMOUNT -> tolls_amount
IMPROVEMENT_SURCHARGE -> improvement_surcharge
TOTAL_AMOUNT -> total_amount

3. ADD derived columns if necessary


4. If  date columns has  different formats, 
  then standardize it or partition it to date and time

5. Create a jupyter notebook using the taxi_rides.duckdb :

5 basic queries
10 basic+ queries
10 intermediate queries
5  Ranking functions queries (using "WITH" subqueries and ranking functions)

Enables key SQL concepts

You can cover:
	•	GROUP BY (core)
	•	WHERE vs HAVING
	•	Window functions 
	•	Top-N queries
	•	Time-based analytics
	*   popular queries
	
	
	
for each cell: 

1. what are we doing? Explain well.
 
2. sql solution (nice formatted), 

3. result displyed

4. result in plot when possible 

5. plotting code should be decoupled from main notebook.

===
