# 🚕 NYC Taxi Trips

**MSIS-2402 · Week 3, Part 1 — Operational Database Analysis**

210,035 New York City taxi rides from January 2015, with **real timestamps** — which
makes this one of only two stories here that can teach time-based analysis.

---

## Run it

```bash
marimo edit taxi_rides_queries_marimo.py    # interactive
marimo run  taxi_rides_queries_marimo.py    # read-only, for students
```

| File | Role |
|---|---|
| `taxi_rides_queries_marimo.py` | The notebook — 31 queries |
| `plot_helpers.py` | Chart functions, kept out of the notebook |
| `taxi.csv` | **210,034 trips** |
| `taxi_rides.duckdb` | The database |
| `build_notebook.py` | Generator script (produces `.ipynb`) — not the notebook |
| `BUILD_PROMPT.md` | The original build specification (provenance) |

---

## The data

One table, `rides`, with 21 columns:

| Group | Columns |
|---|---|
| **Time** | `pickup_datetime`, `dropoff_datetime`, `hour_of_day`, `day_of_week` |
| **Place** | `pickup_location_id`, `drop_location_id` |
| **Trip** | `passenger_count`, `trip_distance`, `trip_duration_minutes`, `rate_code_id` |
| **Money** | `fare_amount`, `extra`, `mta_tax`, `tip_amount`, `tolls_amount`, `improvement_surcharge`, `total_amount`, `tip_percentage` |
| **Other** | `vendor_id`, `payment_type`, `store_and_fwd_flag` |

Four columns are **derived at load time** — `trip_duration_minutes`,
`tip_percentage`, `hour_of_day` and `day_of_week`. Computing them once keeps every
downstream query readable.

---

## What it covers

| § | Section | Techniques |
|---|---|---|
| 0–1 | Setup, load the CSV | `read_csv`, column renaming |
| 2 | Basic queries | `SELECT`, `WHERE`, `ORDER BY`, `COUNT` |
| 3 | Aggregation | `GROUP BY`, `HAVING` |
| 4 | Intermediate | **Window functions, subqueries, time analysis** |
| 5 | Ranking | **CTEs + window rankings**, percentile ranking |

---

## Why this one is good for Week 3, Part 1

**It has real timestamps.** Most stories here can group by category; this one can
group by *hour*, and that unlocks a different class of question:

- When is demand highest? Group by `hour_of_day` — the rush-hour shape is unmistakable.
- Does the weekend look different from a weekday? Group by `day_of_week`.
- Is a long trip a profitable trip? Compare `trip_distance` against `total_amount`.
- Do people tip more at night? `tip_percentage` grouped by `hour_of_day`.

**It is operational data.** These are individual business events — a real dispatch
system's output — rather than a tidy summary table. That is what "operational
database analysis" means, and it is what Week 3, Part 1 is about.

---

## ⚠️ Data-quality notes worth raising in class

Real operational data contains impossible records, and this dataset is no exception:

- **Zero-distance trips** that still carry a fare
- **Zero or negative durations** where the dropoff precedes the pickup
- **Passenger counts of 0**
- **Negative fares**, which are refunds recorded as trips

None of these are bugs in the notebook. They are what a live meter records when
something goes wrong, and deciding whether to exclude them is the analyst's call — a
judgement students should be asked to make and defend rather than have made for them.

---

## Teaching notes

- **Plot rides per hour early.** The twin commuter peaks appear immediately and prove
  the data is real, which buys attention for the harder questions.
- Ask for average trip duration *before* filtering out the zero-duration rows, then
  after. The gap makes the case for data cleaning better than any lecture slide.
- `citi_bike_one_million/` is the natural companion — same shape of question, five
  times the rows, and it adds maps.
