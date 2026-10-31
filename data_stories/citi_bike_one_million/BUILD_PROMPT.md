You are the duckdb and jupyter notebook expert.

My files are here:

citi_bike_one_million  % pwd
<course repo>/data_stories/citi_bike_one_million

citi_bike_one_million  % ls -l
total 34288
-rw-r--r--@ 1 user  staff  17553470 May 24 23:14 citibike_tutorial.csv

citi_bike_one_million  % wc -l citibike_tutorial.csv
 1001032 citibike_tutorial.csv

citi_bike_one_million  % head citibike_tutorial.csv
tripduration,starttime,stoptime,start_station_id,start_station_name,start_station_latitude,start_station_longitude,end_station_id,end_station_name,end_station_latitude,end_station_longitude,bikeid,usertype,birth_year,gender
730,2/9/15 8:37,2/9/15 8:49,72,W 52 St & 11 Ave,40.76727216,-73.99392888,520,W 52 St & 5 Ave,40.75992262,-73.97648516,18809,Subscriber,1975,male
704,11/20/13 20:21,11/20/13 20:33,72,W 52 St & 11 Ave,40.76727216,-73.99392888,470,W 20 St & 8 Ave,40.74345335,-74.00004031,20515,Subscriber,1981,male
425,1/6/16 17:01,1/6/16 17:08,72,W 52 St & 11 Ave,40.76727216,-73.99392888,469,Broadway & W 53 St,40.76344058,-73.98268129,17116,Subscriber,1947,male
373,11/9/15 12:50,11/9/15 12:56,72,W 52 St & 11 Ave,40.76727216,-73.99392888,469,Broadway & W 53 St,40.76344058,-73.98268129,20892,Subscriber,1947,male
1149,8/3/13 17:14,8/3/13 17:33,72,W 52 St & 11 Ave,40.76727216,-73.99392888,325,E 19 St & 3 Ave,40.73624527,-73.98473765,17711,Subscriber,1981,female
1222,7/12/14 10:13,7/12/14 10:33,72,W 52 St & 11 Ave,40.76727216,-73.99392888,531,Forsyth St & Broome St,40.71893904,-73.99266288,17277,Subscriber,1967,female
363,2/28/15 15:49,2/28/15 15:55,72,W 52 St & 11 Ave,40.76727216,-73.99392888,449,W 52 St & 9 Ave,40.76461837,-73.98789473,16845,Subscriber,1956,female
740,7/1/15 16:40,7/1/15 16:53,72,W 52 St & 11 Ave,40.76727216,-73.99392888,479,9 Ave & W 45 St,40.76019252,-73.9912551,14561,Subscriber,1982,male
1767,6/30/14 8:53,6/30/14 9:22,72,W 52 St & 11 Ave,40.76727216,-73.99392888,348,W Broadway & Spring St,40.72490985,-74.00154702,18322,Subscriber,1987,female

Everything is done in jupyter notebook:

1. a separate cell
read citibike_tutorial.csv
and create a DuckDB database call it citibike.duckdb) 

2. Rename columns 

tripduration -> trip_duration
starttime -> start_time
stoptime -> stop_time
bikeid -> bike_id
usertype -> user_type

3. ADD derived columns if necessary

4. a separate cell
4.1 then dedup it (drop full duplicate rows)
4.2 Explain how to dedup it

5. If  date columns has  different formats, then standardize it

6. Create a jupyter notebook using the citibike.duckdb :

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
	*   popular destinations 
	
	
	
for each cell: 

1. what are we doing? Explain well.
 
2. sql solution (nice formatted), 

3. result displyed

4. result in plot when possible 
(plotting code should be decoupled from main notebook).

===
claude:
