# 🚲 Citi Bike — One Million Rides

**MSIS-2402 · Week 3, Part 1 — Operational Database Analysis** *(→ Week 3, Part 2 for the CTE section)*

**One million New York City bike-share rides**, with timestamps *and* coordinates.
The largest single-table story in this folder, and the only one that ends in maps.

---

## Run it — three notebooks, in order

```bash
marimo edit notebook1_build_database_marimo.py    # build citibike.duckdb — run first
marimo edit notebook2_analyze_data_marimo.py      # 30 SQL queries
marimo edit notebook3_maps_marimo.py              # geographic analysis
```

| File | Role |
|---|---|
| `notebook1_build_database_marimo.py` | Loads the CSV, renames columns, adds derived columns |
| `notebook2_analyze_data_marimo.py` | **The main analysis** — 30 queries in four parts |
| `notebook3_maps_marimo.py` | Interactive maps of the station network |
| `plot_helpers.py` | Chart functions |
| `map_helpers.py` | Map functions (uses **folium**) |
| `citibike_tutorial.csv` | **1,001,031 rides** |
| `citibike.duckdb` | Built by notebook 1 |
| `BUILD_PROMPT.md`, `using_LAT_LON_columns.md` | Build notes (provenance) |

**Notebook 1 must run first.** Notebooks 2 and 3 both expect the database to exist.

---

## The data

One table, `rides`, with 22 columns:

| Group | Columns |
|---|---|
| **Time** | `start_time`, `stop_time`, `trip_duration`, `trip_duration_min`, `start_hour`, `start_day_of_week`, `start_month`, `start_year` |
| **Start station** | `start_station_id`, `start_station_name`, `start_station_latitude`, `start_station_longitude` |
| **End station** | `end_station_id`, `end_station_name`, `end_station_latitude`, `end_station_longitude` |
| **Rider** | `user_type`, `birth_year`, `gender`, `rider_age` |
| **Derived** | `distance_km`, `bike_id` |

Seven columns are **computed at load time** in notebook 1 — duration in minutes, the
time parts, rider age, and straight-line distance between stations. Doing that once
keeps the 30 analysis queries readable.

---

## What it covers

| Part | Queries | Techniques |
|---|---|---|
| 1 — Basic | 5 | `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `DISTINCT` |
| 2 — Basic+ | 10 | `GROUP BY`, aggregates, `HAVING`, `BETWEEN`, `LIKE`, `CASE` |
| 3 — Intermediate | 10 | Subqueries, joins, window functions, time analytics |
| 4 — Ranking with CTEs | 5 | `WITH`, `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK` |

Part 4 is **Week 3, Part 2 material** (CTEs and window functions). Parts 1–3 stand on their
own for Week 3, Part 1.

---

## The third notebook: maps

Because every ride carries start and end coordinates, the station network can be drawn
rather than described. `notebook3_maps_marimo.py` produces:

- An interactive map of **all stations**, sized by ride count
- The **top 10 busiest** start stations
- A static scatter plot on lat/lon axes, for when an interactive map is not practical

Needs **folium** (`pip install folium`) and an internet connection for the map tiles.

**Why it is worth the extra notebook:** a `GROUP BY start_station_name` result is a
list of names. The same result on a map is a picture of where New York actually rides
— and students see immediately that the busiest stations cluster around transit hubs.

---

## Questions this data answers well

- **When do people ride?** Group by `start_hour` — the commuter peaks are stark.
- **Do subscribers behave differently from casual riders?** Group by `user_type`;
  the difference in trip duration is large and easy to explain.
- **Which stations are busiest, and where are they?** The bridge from SQL to the map.
- **Does ride length vary by age?** `rider_age` is derived from `birth_year`, so this
  is one `GROUP BY` away.

---

## ⚠️ Notes on the data

- **`birth_year` is unreliable.** Some riders report implausible years, which makes
  `rider_age` occasionally absurd. Worth filtering, and worth discussing.
- **`gender` is coded**, not spelled out — check the values before grouping on it.
- **One million rows is enough to feel slow** in a bad query. That is a feature: it is
  the only story here where an inefficient query is noticeably inefficient.

---

## Teaching notes

- **Run notebook 1 in front of the class.** The derived-column step is the clearest
  example in the course of preparing data once so that everything afterwards is
  simple.
- Save notebook 3 for the end of a session. It is the reward, and it makes the point
  that analysis ends in communication, not in a result set.
- `taxi_210K_trips/` asks the same kind of time-based questions with a fifth of the
  data and no maps — a good lighter-weight alternative.
