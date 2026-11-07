# 🏅 120 Years of Olympic History

**MSIS-2402 · Week 1, Part 2 — Aggregation & KPIs**

Every athlete in every event from **Athens 1896 to Rio 2016** — 271,116 rows. One
wide table, and a dataset students can sanity-check against things they already know,
which is exactly what makes a good teaching set.

---

## Run it

```bash
cd data_stories/olympic_120_years                 # from the course repository folder
marimo edit olympics_analysis_marimo.py    # interactive
marimo run  olympics_analysis_marimo.py    # read-only, for students
```

| File | Role |
|---|---|
| `olympics_analysis_marimo.py` | The notebook — 25 queries in three parts |
| `plotting_utils.py` | Chart functions, kept out of the notebook |
| `data/athlete_events.csv` | **271,116 athlete-events** |
| `olympics_120_years.duckdb` | The database |

---

## The data

One table, `athlete_events`. **Each row is one athlete competing in one event** — so
a swimmer entering five events appears five times.

| Column | Meaning |
|---|---|
| `id` | Unique number per athlete |
| `name` | Athlete's name |
| `sex` | M or F |
| `age`, `height`, `weight` | Age in years, height in cm, weight in kg |
| `team` | Team name |
| `noc` | National Olympic Committee — 3-letter code |
| `games`, `year`, `season` | e.g. "1992 Summer", 1992, Summer |
| `city` | Host city |
| `sport`, `event` | e.g. Swimming / "Swimming Men's 100 metres Freestyle" |
| `medal` | Gold, Silver, Bronze — or `NA` |

**Source:** [120 Years of Olympic History on Kaggle](https://www.kaggle.com/datasets/heesoo37/120-years-of-olympic-history-athletes-and-results/data)

---

## What it covers

| Part | Queries | Techniques |
|---|---|---|
| 1 — Basic | 5 | `COUNT`, `DISTINCT`, `GROUP BY`, `ORDER BY`, `LIMIT` |
| 2 — Basic+ | 10 | `AVG`, `HAVING`, `CASE`, filtering on `NULL` |
| 3 — Intermediate | 10 | Subqueries, multi-column grouping, CTEs |

---

## ⚠️ Two traps built into this dataset

**1 · One row is not one athlete.** Because each row is an athlete-*event*,
`COUNT(*)` counts entries, not people. To count athletes you need
`COUNT(DISTINCT id)`. Getting this wrong inflates every number, and the result still
looks plausible.

**2 · `medal` is `NA` for most rows, and `NA` may be a string.** The vast majority of
entries won a nothing. Depending on how the CSV was read, "no medal" may be the
**text** `'NA'` rather than a true `NULL` — which means `WHERE medal IS NULL` returns
zero rows and `COUNT(medal)` counts the non-medallists too.

The notebook contains a **deliberately broken query** demonstrating exactly this: a
column inferred as `VARCHAR` because of literal `'NA'` strings, so `AVG()`, `MIN()`
and `MAX()` refuse to run on it. The fix is shown alongside.

That second trap is the most valuable thing in this story. **Type inference is a
decision the loader makes on your behalf, and it can quietly make columns unusable.**

---

## Questions this data answers well

- Which country has won the most golds? (`GROUP BY noc` + filter on medal)
- How has the share of female athletes changed over time? (`GROUP BY year, sex`)
- Which sports have the tallest athletes? (`GROUP BY sport` + `AVG(height)`)
- How many athletes have competed in both Summer and Winter Games?

Every one of these is checkable against general knowledge, which is why students trust
their results here faster than on abstract data.

---

## Teaching notes

- **Open with the `COUNT(*)` vs `COUNT(DISTINCT id)` question.** Ask "how many
  athletes are in this dataset?" and let two different answers appear.
- The broken query in Part 2 is best run *live*. Seeing `AVG()` fail on a column that
  looks numeric is more memorable than being warned about it.
- If you also use `coffee_shop_149K_records/`, note the contrast: there the derived
  columns were prepared carefully at load time; here the loader guessed, and guessed
  badly.
