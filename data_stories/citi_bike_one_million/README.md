# 🚲 Citi Bike — 10,889 Rides in a One-Million-Line File

**MSIS-2402 · Week 3, Part 1 — Operational Database Analysis** *(→ Week 3, Part 2 for the CTE section)*

**New York City bike-share rides**, with timestamps *and* coordinates — the only story
that ends in maps.

**The data-quality lesson comes first:** `citibike_tutorial.csv` has 1,001,032 rows, but
only **10,889** are rides. The other **990,143** lines are completely empty (nothing but
commas). Notebook 1 finds them, shows why they must not be counted, and builds the
`rides` table from the 10,889 real rides only. (The folder keeps its original name.)

---

## Run it — three notebooks, in order

```bash
cd data_stories/citi_bike_one_million                 # from the course repository folder
marimo edit notebook1_build_database_marimo.py    # build citibike.duckdb — run first
marimo edit notebook2_analyze_data_marimo.py      # 30 questions
pip install folium                                # once — notebook 3 needs it
marimo edit notebook3_maps_marimo.py              # geographic analysis (internet needed for map tiles)
```

| File | Role |
|---|---|
| `notebook1_build_database_marimo.py` | Loads the CSV, removes the 990,143 empty rows, renames columns, adds derived columns |
| `notebook2_analyze_data_marimo.py` | **The main analysis** — 30 questions in four parts |
| `notebook3_maps_marimo.py` | Interactive maps of the station network |
| `plot_helpers.py` | Chart functions |
| `map_helpers.py` | Map functions (uses **folium**) |
| `citibike_tutorial.csv` | **1,001,032 rows: 10,889 rides + 990,143 empty lines** |
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
- The **busiest start stations** (the data has only 5 distinct start stations)
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
- **Most of the file is empty lines.** Before trusting any `COUNT(*)` on a new file,
  check what the rows actually contain — here, 990,143 of 1,001,032 rows are blank.

---

## Teaching notes

- **Run notebook 1 in front of the class.** The derived-column step is the clearest
  example in the course of preparing data once so that everything afterwards is
  simple.
- Save notebook 3 for the end of a session. It is the reward, and it makes the point
  that analysis ends in communication, not in a result set.
- `taxi_210K_trips/` asks the same kind of time-based questions with a fifth of the
  data and no maps — a good lighter-weight alternative.
