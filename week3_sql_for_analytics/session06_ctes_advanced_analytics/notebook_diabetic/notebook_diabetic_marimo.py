import marimo


__generated_with = "0.23.10"

app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Diabetes 130-US Hospitals — Advanced SQL with DuckDB

    Week 3 (SQL for Data Analytics) · MSIS-2402

    This notebook queries `diabetic_hospitals.duckdb`, a persistent (on-disk)
    DuckDB database built from the UCI **Diabetes 130-US Hospitals
    (1999-2008)** dataset by `build_database.py`. See `database_schema.md` in
    this folder for the full schema explanation, entity-relationship diagram,
    and data-cleaning decisions before running this notebook.

    **13 business questions, in three parts:**

    - **Part A — Simple (3):** `SELECT` / `WHERE` / `ORDER BY` / `LIMIT`,
      `GROUP BY` with aggregates, a single lookup-table `JOIN`.
    - **Part B — Intermediate (5):** `CASE` bucketing, `HAVING`, multi-table
      joins, a scalar subquery, `STRING_AGG`.
    - **Part C — Intermediate+ (5):** window functions (`ROW_NUMBER`, `LAG`,
      `RANK`, `NTILE`), `QUALIFY`, a CTE feeding a window function, and
      DuckDB's native `PIVOT`.

    **4 charts** (pie, bar, horizontal bar, line) visualize a few of the
    results — the matplotlib code itself lives in the sibling `plot_helpers.py`
    module, not in this notebook; each chart cell here is a one-line call
    like `plot_bar(df, ...)`, keeping SQL/results and plotting code cleanly
    separated.

    Every query below was run against the real database while writing this
    notebook — the results shown are real, not illustrative.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup — Connect to the Database

    The database is opened **read-only** — this notebook only ever queries
    it, it never modifies it. Rebuilding the database (if you've changed the
    source CSVs) is `build_database.py`'s job, not this notebook's.
    """)
    return


@app.cell
def _():
    import sys
    import os
    import duckdb
    import pandas as pd

    # make sure plot_helpers.py (same folder as this notebook) is importable
    sys.path.insert(0, os.path.dirname(os.path.abspath("__file__")))
    from plot_helpers import plot_bar, plot_hbar, plot_pie, plot_line

    con = duckdb.connect("diabetic_hospitals.duckdb", read_only=True)
    print("Connected to diabetic_hospitals.duckdb (read-only)")
    print("Tables:", con.execute("SHOW TABLES").fetchdf()["name"].tolist())
    return con, plot_bar, plot_hbar, plot_line, plot_pie


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Quick Check — Row Counts for All Tables

    Before writing any business queries, confirm the size of every table —
    this is the same shape check `build_database.py` runs itself after
    loading, just re-run here so the notebook is self-verifying too.
    """)
    return


@app.cell
def _(con, mo):
    df_counts = mo.sql(
        f"""
        SELECT 'admission_type' AS table_name, COUNT(*) AS num_rows FROM admission_type
        UNION ALL
        SELECT 'discharge_disposition', COUNT(*) FROM discharge_disposition
        UNION ALL
        SELECT 'admission_source', COUNT(*) FROM admission_source
        UNION ALL
        SELECT 'medications', COUNT(*) FROM medications
        UNION ALL
        SELECT 'encounters', COUNT(*) FROM encounters
        UNION ALL
        SELECT 'encounter_medications', COUNT(*) FROM encounter_medications
        """,
        engine=con
    )
    return (df_counts,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Overview — Readmission Outcomes Across All Encounters

    A quick pie chart of the notebook's eventual target variable, before
    digging into individual questions: of all 101,766 encounters, what
    fraction were readmitted within 30 days, after 30 days, or not at all?
    """)
    return


@app.cell
def _(con, mo):
    df_overview = mo.sql(
        f"""
        SELECT
            readmitted,
            COUNT(*) AS num_encounters
        FROM encounters
        GROUP BY
            readmitted
        ORDER BY
            num_encounters DESC
        """,
        engine=con
    )
    return (df_overview,)


@app.cell
def _(df_overview, plot_pie):
    plot_pie(
        df_overview, "readmitted", "num_encounters",
        title="Readmission Outcomes — All Encounters"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part A — Simple Queries (3)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q1 — The 10 Longest Hospital Stays
    **Concept:** `SELECT` / `ORDER BY` / `LIMIT`
    **Business question:** Which encounters kept a patient in the hospital
    the longest, and how did those encounters turn out?
    """)
    return


@app.cell
def _(con, mo):
    df_q1 = mo.sql(
        f"""
        SELECT
            encounter_id,
            patient_nbr,
            age,
            gender,
            time_in_hospital,
            readmitted
        FROM encounters
        ORDER BY
            time_in_hospital DESC,
            num_medications DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_q1,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** `time_in_hospital` tops out at 14 days in this dataset (a
    known cap in how the source study collected it) — plenty of encounters
    tie at the maximum, which is why the `ORDER BY` uses `num_medications` as
    a tiebreaker.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q2 — Average Length of Stay by Age Bracket
    **Concept:** `GROUP BY` with `COUNT` / `AVG`
    **Business question:** Does length of stay increase with patient age?
    """)
    return


@app.cell
def _(con, mo):
    df_q2 = mo.sql(
        f"""
        SELECT
            age,
            COUNT(*) AS num_encounters,
            ROUND(AVG(time_in_hospital), 2) AS avg_stay_days
        FROM encounters
        GROUP BY
            age
        ORDER BY
            age
        """,
        engine=con
    )
    return (df_q2,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Q2
    """)
    return


@app.cell
def _(df_q2, plot_bar):
    plot_bar(
        df_q2, "age", "avg_stay_days",
        title="Average Length of Stay by Age Bracket",
        xlabel="Age bracket", ylabel="Avg. days in hospital"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** average stay climbs steadily from 2.55 days in the
    youngest bracket to 4.59 days in the oldest — a small but consistent
    trend, not a dramatic jump, which is itself worth noting to students who
    might expect a bigger effect.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q3 — Top 5 Admission Sources by Volume
    **Concept:** `JOIN` a fact table to a lookup table, then `GROUP BY` / `ORDER BY` / `LIMIT`
    **Business question:** Where do most encounters originate — the ER,
    physician referral, or somewhere else?
    """)
    return


@app.cell
def _(con, mo):
    df_q3 = mo.sql(
        f"""
        SELECT
            src.description AS admission_source,
            COUNT(*) AS num_encounters
        FROM encounters e
        JOIN admission_source src
            USING (admission_source_id)
        GROUP BY
            src.description
        ORDER BY
            num_encounters DESC
        LIMIT 5
        """,
        engine=con
    )
    return (df_q3,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** the Emergency Room accounts for well over half of all
    encounters (57,494 of 101,766) — a useful number to keep in mind for any
    later query that slices by admission source.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part B — Intermediate Queries (5)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q4 — Readmission Rate by Length-of-Stay Bucket
    **Concept:** `CASE` expression for bucketing + conditional aggregation
    (`SUM(CASE WHEN ...)`)
    **Business question:** Are longer hospital stays associated with a
    higher chance of a within-30-day readmission?
    """)
    return


@app.cell
def _(con, mo):
    df_q4 = mo.sql(
        f"""
        SELECT
            CASE
                WHEN time_in_hospital <= 3 THEN 'short (1-3 days)'
                WHEN time_in_hospital <= 7 THEN 'medium (4-7 days)'
                ELSE 'long (8+ days)'
            END AS stay_bucket,
            COUNT(*) AS num_encounters,
            ROUND(100.0 * SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_readmitted_lt30
        FROM encounters
        GROUP BY
            stay_bucket
        ORDER BY
            pct_readmitted_lt30 DESC
        """,
        engine=con
    )
    return (df_q4,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** the relationship is real but modest — 13.4% for long stays
    vs. 9.7% for short stays. Worth flagging to students that "longer stay ->
    sicker patient -> more likely to come back" is a plausible story, but this
    single-table aggregate can't establish causation.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q5 — Medical Specialties with the Heaviest Medication Load
    **Concept:** `GROUP BY` + `HAVING` (filtering on an aggregate, not a raw column)
    **Business question:** Among specialties that see a meaningful volume of
    encounters (>= 500), which ones prescribe the most medications per
    encounter on average?
    """)
    return


@app.cell
def _(con, mo):
    df_q5 = mo.sql(
        f"""
        SELECT
            medical_specialty,
            COUNT(*) AS num_encounters,
            ROUND(AVG(num_medications), 2) AS avg_num_medications
        FROM encounters
        WHERE
            medical_specialty IS NOT NULL
        GROUP BY
            medical_specialty
        HAVING
            COUNT(*) >= 500
        ORDER BY
            avg_num_medications DESC
        """,
        engine=con
    )
    return (df_q5,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** `HAVING` is doing real work here — without the `>= 500`
    filter, several one-off specialties with 1-2 unusually high-medication
    encounters would dominate the top of the list. `HAVING` filters *after*
    grouping, which is exactly why it can reference `COUNT(*)` when `WHERE`
    can't.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q6 — Where Hospice-Bound Patients Were Admitted From
    **Concept:** `JOIN` two lookup tables onto the fact table in one query
    **Business question:** For encounters that ended in a discharge to
    hospice care, where did those patients originally come from?
    """)
    return


@app.cell
def _(con, mo):
    df_q6 = mo.sql(
        f"""
        SELECT
            src.description AS admission_source,
            COUNT(*) AS num_encounters
        FROM encounters e
        JOIN discharge_disposition dd
            USING (discharge_disposition_id)
        JOIN admission_source src
            USING (admission_source_id)
        WHERE
            dd.description ILIKE 'Hospice%'
        GROUP BY
            src.description
        ORDER BY
            num_encounters DESC
        """,
        engine=con
    )
    return (df_q6,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** this is the payoff for normalizing `IDS_mapping.csv` into
    three real lookup tables in `database_schema.sql` instead of leaving
    everything as raw integer codes — the query reads like the business
    question it answers.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q7 — Patients With an Above-Average Number of Encounters
    **Concept:** scalar subquery (a query inside `HAVING`, built on a derived table)
    **Business question:** Which patients have been readmitted far more often
    than a typical patient in this dataset?
    """)
    return


@app.cell
def _(con, mo):
    df_q7 = mo.sql(
        f"""
        SELECT
            patient_nbr,
            COUNT(*) AS num_encounters
        FROM encounters
        GROUP BY
            patient_nbr
        HAVING
            COUNT(*) > (
                SELECT AVG(cnt)
                FROM (
                    SELECT COUNT(*) AS cnt
                    FROM encounters
                    GROUP BY patient_nbr
                )
            )
        ORDER BY
            num_encounters DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_q7,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** the average patient in this dataset has only ~1.4
    encounters (101,766 encounters / 71,518 patients), so "above average"
    here just means "more than one" for most patients — the top of this list
    (one patient with 40 encounters) is the real outlier worth a closer look.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q8 — Encounters on 3+ Active Diabetes Medications
    **Concept:** `STRING_AGG` over the normalized `encounter_medications` table
    **Business question:** For the most medication-intensive encounters,
    which specific drugs (and dose changes) were involved?
    """)
    return


@app.cell
def _(con, mo):
    df_q8 = mo.sql(
        f"""
        SELECT
            em.encounter_id,
            COUNT(*) AS num_active_meds,
            STRING_AGG(em.medication_name || ' (' || em.status || ')', ', ' ORDER BY em.medication_name) AS medications
        FROM encounter_medications em
        GROUP BY
            em.encounter_id
        HAVING
            COUNT(*) > 2
        ORDER BY
            num_active_meds DESC
        LIMIT 10
        """,
        engine=con
    )
    return (df_q8,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** this query only works cleanly because `encounter_medications`
    is long/normalized rather than 23 wide columns — try writing this same
    question directly against the raw wide CSV shape and it turns into an
    unreadable pile of `CASE WHEN metformin <> 'No' THEN ... `.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part C — Intermediate+ Queries (5)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q9 — Each Repeat Patient's Visit Sequence
    **Concept:** `ROW_NUMBER()` / `COUNT()` as window functions, `QUALIFY`
    to filter on a window result without a wrapping subquery
    **Business question:** For patients with more than one encounter, what
    does their sequence of visits look like?
    """)
    return


@app.cell
def _(con, mo):
    df_q9 = mo.sql(
        f"""
        SELECT
            patient_nbr,
            encounter_id,
            ROW_NUMBER() OVER (PARTITION BY patient_nbr ORDER BY encounter_id) AS visit_number,
            COUNT(*) OVER (PARTITION BY patient_nbr) AS total_visits,
            time_in_hospital,
            readmitted
        FROM encounters
        QUALIFY
            total_visits > 1
        ORDER BY
            patient_nbr,
            visit_number
        LIMIT 12
        """,
        engine=con
    )
    return (df_q9,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** `QUALIFY` is DuckDB's (and a few other engines')
    answer to "I want to filter on a window function result" — without it,
    the same filter needs the whole query wrapped in a subquery just to reach
    `WHERE total_visits > 1`. `encounter_id` is used to order each patient's
    visits since the dataset has no visit date, only an encounter sequence
    number that increases over time.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q10 — Did Medication Count Rise on Follow-Up Visits?
    **Concept:** `LAG()` window function inside a CTE, to compare each visit
    to the *same patient's* previous visit
    **Business question:** Across every follow-up visit, does the medication
    count tend to go up, down, or stay the same compared to the patient's
    prior visit?
    """)
    return


@app.cell
def _(con, mo):
    df_q10 = mo.sql(
        f"""
        WITH med_seq AS (
            SELECT
                patient_nbr,
                encounter_id,
                num_medications,
                LAG(num_medications) OVER (PARTITION BY patient_nbr ORDER BY encounter_id) AS prev_num_medications,
                ROW_NUMBER() OVER (PARTITION BY patient_nbr ORDER BY encounter_id) AS visit_number
            FROM encounters
        )
        SELECT
            COUNT(*) AS num_followup_visits,
            SUM(CASE WHEN num_medications > prev_num_medications THEN 1 ELSE 0 END) AS meds_increased,
            SUM(CASE WHEN num_medications < prev_num_medications THEN 1 ELSE 0 END) AS meds_decreased,
            SUM(CASE WHEN num_medications = prev_num_medications THEN 1 ELSE 0 END) AS meds_unchanged
        FROM med_seq
        WHERE
            visit_number > 1
        """,
        engine=con
    )
    return (df_q10,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** of 30,248 follow-up visits, medication counts went up
    slightly more often (14,949) than down (13,567) — the CTE (`med_seq`)
    computes the window function once, cleanly, so the final `SELECT` is
    plain conditional aggregation over an already-shaped result.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q11 — Ranking Specialties by 30-Day Readmission Rate
    **Concept:** `RANK()` window function applied on top of a CTE's aggregated results
    **Business question:** Among specialties with meaningful volume (>= 200
    encounters), which have the highest 30-day readmission rates?
    """)
    return


@app.cell
def _(con, mo):
    df_q11 = mo.sql(
        f"""
        WITH specialty_rates AS (
            SELECT
                medical_specialty,
                COUNT(*) AS num_encounters,
                ROUND(100.0 * SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_lt30_pct
            FROM encounters
            WHERE
                medical_specialty IS NOT NULL
            GROUP BY
                medical_specialty
            HAVING
                COUNT(*) >= 200
        )
        SELECT
            RANK() OVER (ORDER BY readmit_lt30_pct DESC) AS rank_by_readmit_rate,
            medical_specialty,
            num_encounters,
            readmit_lt30_pct
        FROM specialty_rates
        ORDER BY
            rank_by_readmit_rate
        LIMIT 10
        """,
        engine=con
    )
    return (df_q11,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Q11
    """)
    return


@app.cell
def _(df_q11, plot_hbar):
    plot_hbar(
        df_q11, "medical_specialty", "readmit_lt30_pct",
        title="Top 10 Specialties by 30-Day Readmission Rate",
        xlabel="% readmitted within 30 days", ylabel="Medical specialty"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** Hematology/Oncology and Oncology top the list at ~19% —
    plausible given how those patient populations look clinically, and a good
    discussion prompt on the difference between `RANK()` (ties share a rank
    and the next rank is skipped) and `DENSE_RANK()` (ties share a rank, next
    rank is not skipped).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q12 — Medication Status Counts, Wide Format
    **Concept:** DuckDB's native `PIVOT` — the mirror image of the `UNPIVOT`
    used in `build_database.py` to build `encounter_medications` in the
    first place
    **Business question:** For each medication, how many encounters had its
    dose held steady vs. increased vs. decreased?
    """)
    return


@app.cell
def _(con, mo):
    df_q12 = mo.sql(
        f"""
        PIVOT encounter_medications
        ON status
        USING COUNT(*)
        GROUP BY medication_name
        ORDER BY medication_name
        """,
        engine=con
    )
    return (df_q12,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** this comes full circle with `database_schema.md` §3 —
    `build_database.py` reshaped the raw CSV's 23 wide medication columns
    into the long `encounter_medications` table with `UNPIVOT` so it could be
    stored and queried cleanly (Q8, Q12 are both proof of that), and `PIVOT`
    reshapes it back to wide for whichever queries actually want that shape.
    Neither direction is "more correct" — pick whichever shape the question
    needs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Q13 — Readmission Rate by Lab-Procedure Intensity Quartile
    **Concept:** `NTILE()` window function inside a CTE, to bucket encounters
    into equal-sized groups by a continuous measure
    **Business question:** Do encounters with more lab procedures performed
    (a rough proxy for how intensively a patient was worked up) show a
    different 30-day readmission rate?
    """)
    return


@app.cell
def _(con, mo):
    df_q13 = mo.sql(
        f"""
        WITH quartiled AS (
            SELECT
                encounter_id,
                num_lab_procedures,
                readmitted,
                NTILE(4) OVER (ORDER BY num_lab_procedures) AS lab_procedure_quartile
            FROM encounters
        )
        SELECT
            lab_procedure_quartile,
            MIN(num_lab_procedures) AS min_procs,
            MAX(num_lab_procedures) AS max_procs,
            COUNT(*) AS num_encounters,
            ROUND(100.0 * SUM(CASE WHEN readmitted = '<30' THEN 1 ELSE 0 END) / COUNT(*), 2) AS readmit_lt30_pct
        FROM quartiled
        GROUP BY
            lab_procedure_quartile
        ORDER BY
            lab_procedure_quartile
        """,
        engine=con
    )
    return (df_q13,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Visualization — Q13
    """)
    return


@app.cell
def _(df_q13, plot_line):
    plot_line(
        df_q13, "lab_procedure_quartile", "readmit_lt30_pct",
        title="30-Day Readmission Rate by Lab-Procedure Quartile",
        xlabel="Lab-procedure quartile (1 = fewest procedures)",
        ylabel="% readmitted within 30 days"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Takeaway:** the trend is mild but monotonic — 10.15% in the lowest
    quartile up to 11.85% in the highest. `NTILE(4)` guarantees four
    (nearly) equal-sized buckets regardless of how `num_lab_procedures` is
    distributed, which is different from — and often more useful for
    cohort comparisons than — fixed-width buckets like the `CASE` bucketing
    used back in Q4.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Summary

    | Part | Queries | Concepts covered |
    |---|---|---|
    | A — Simple | Q1-Q3 | `SELECT`/`WHERE`/`ORDER BY`/`LIMIT`, `GROUP BY` aggregates, single `JOIN` |
    | B — Intermediate | Q4-Q8 | `CASE` bucketing, `HAVING`, multi-table `JOIN`, scalar subquery, `STRING_AGG` |
    | C — Intermediate+ | Q9-Q13 | `ROW_NUMBER`, `QUALIFY`, `LAG` in a CTE, `RANK`, `PIVOT`, `NTILE` |

    Every query in this notebook runs against `diabetic_hospitals.duckdb`
    exactly as built by `build_database.py` — see `database_schema.md` for
    the schema these queries depend on, and its §8 for known caveats
    (`weight` is 96.9% `NULL`, `gender` includes a small `'Unknown/Invalid'`
    category) worth surfacing to students before they draw conclusions from
    this data.
    """)
    return


if __name__ == "__main__":
    app.run()
