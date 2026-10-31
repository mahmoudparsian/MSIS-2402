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
    # Notebook 2: Analysing the Book-Crossing Database

    **18 SQL queries** against `books.duckdb`, the database built in
    `build_database.py`.

    | Part | Queries | Concepts |
    |---|---|---|
    | 1 — Simple | 3 | `SELECT`, `LIMIT`, `COUNT`, `GROUP BY`, `ORDER BY` |
    | 2 — Intermediate | 9 | `JOIN`, `LEFT JOIN`, anti-joins, `HAVING`, `CASE`, `COUNT(DISTINCT)` |
    | 3 — Intermediate+ | 6 | CTEs, window functions, `QUALIFY`, `NTILE`, self-joins, `FILTER` |

    Every query cell is **pure SQL**. Where a chart helps, it is drawn in a
    separate cell by a function imported from `plot_helpers.py` — no plotting code
    appears in this notebook. Six queries are plotted: **Q3, Q4, Q7, Q8, Q12, Q13**.

    ## The database

    | Table | Rows | What it holds |
    |---|---|---|
    | `books` | 271,389 | One row per ISBN |
    | `users` | 278,862 | One row per user, location split into city/state/country |
    | `ratings` | 1,031,175 | One row per (user, book). Both FKs enforced |
    | `ratings_orphaned` | 118,589 | Ratings whose ISBN is missing from `books` |

    ## Two things to remember before you start

    1. **`rating = 0` does not mean "zero out of ten".** It means the user
       interacted with the book without scoring it. 62% of rows are like this.
       Filter with `WHERE is_explicit` whenever you average. Q18 shows exactly how
       much damage forgetting this does.
    2. **`ratings` excludes 118,589 orphaned rows.** They live in
       `ratings_orphaned`. Any total you compute from `ratings` is a total over
       books the catalogue actually knows about.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Setup
    """)
    return


@app.cell
def _():
    import duckdb

    from plot_helpers import (
        plot_books_per_decade,
        plot_rating_distribution,
        plot_ratings_by_country,
        plot_reader_activity,
        plot_top_books,
        plot_user_segments,
    )

    con = duckdb.connect("books.duckdb", read_only=True)

    _n = con.execute("SELECT COUNT(*) FROM ratings").fetchall()[0][0]
    print(f"Connected to books.duckdb — {_n:,} ratings available")
    return (
        con,
        plot_books_per_decade,
        plot_rating_distribution,
        plot_ratings_by_country,
        plot_reader_activity,
        plot_top_books,
        plot_user_segments,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # Part 1 — Simple Queries (3)

    Getting a feel for the tables: what is in them, how big they are, and how the
    single most important column is distributed.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q1. What does a book record look like?

    **What are we doing?**
    Reading a handful of rows to see the shape of the data. This should always be
    the first query you run against an unfamiliar table.

    Note that `publication_year` is `NULL` for some books — the build notebook set
    it to `NULL` wherever the source value was not a usable year.

    **SQL concepts:** `SELECT`, `LIMIT`
    """)
    return


@app.cell
def _(books, con, mo):
    q1_preview = mo.sql(
        f"""
        SELECT isbn, title, author, publication_year, publisher
        FROM books
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q2. How big is each table?

    **What are we doing?**
    Counting the rows in all four tables at once. `UNION ALL` stacks the results
    of several queries into a single result set — each `SELECT` must return the
    same number of columns, with compatible types.

    We use `UNION ALL` rather than `UNION` because we do not want the database to
    spend time looking for duplicate rows to remove. `UNION` deduplicates;
    `UNION ALL` does not, and is faster.

    **SQL concepts:** `COUNT(*)`, `UNION ALL`, `ORDER BY`
    """)
    return


@app.cell
def _(books, con, mo, ratings, ratings_orphaned, users):
    q2_table_sizes = mo.sql(
        f"""
        SELECT 'books'            AS table_name, COUNT(*) AS row_count FROM books
        UNION ALL
        SELECT 'users',            COUNT(*) FROM users
        UNION ALL
        SELECT 'ratings',          COUNT(*) FROM ratings
        UNION ALL
        SELECT 'ratings_orphaned', COUNT(*) FROM ratings_orphaned
        ORDER BY row_count DESC;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q3. How are the 1–10 ratings distributed?  📊

    **What are we doing?**
    Counting how often each score was given, and expressing each as a percentage
    of the total.

    The percentage uses a **window function**: `SUM(COUNT(*)) OVER ()` computes
    the grand total across all groups *after* the `GROUP BY` has run. The empty
    `OVER ()` means "over every row in the result", which is exactly the
    denominator we want. Without it you would need a second query or a subquery.

    Note the `WHERE is_explicit` filter — without it, 647,323 implicit zeros would
    swamp the chart.

    **SQL concepts:** `GROUP BY`, `COUNT`, `ROUND`, window function `OVER ()`
    """)
    return


@app.cell
def _(con, mo, ratings):
    q3_rating_distribution = mo.sql(
        f"""
        SELECT
            rating,
            COUNT(*)                                            AS n_ratings,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)  AS pct_of_explicit
        FROM ratings
        WHERE is_explicit
        GROUP BY rating
        ORDER BY rating;
        """,
        engine=con
    )
    return (q3_rating_distribution,)


@app.cell
def _(plot_rating_distribution, q3_rating_distribution):
    plot_rating_distribution(q3_rating_distribution)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Readers are generous. **8 is the most common score**, and 7–10 together account
    for roughly three quarters of all explicit ratings. Scores of 1–4 are rare.

    This matters for anything you build later: on this scale, "average" is about
    7.6, not 5.5. A book rated 6 is below average here, not mediocre.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # Part 2 — Intermediate Queries (9)

    Joining tables. Every query in this section combines two or three tables, and
    most of them filter groups with `HAVING` after aggregating.

    The last three (Q10–Q12) are **anti-joins** and `LEFT JOIN`s — finding rows that
    have *no* match on the other side, which is a different habit of mind from the
    inner joins that come before them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q4. Which books have the most ratings?  📊

    **What are we doing?**
    Joining `ratings` to `books` to turn ISBNs into titles, then counting ratings
    per title.

    We group by `title` rather than `isbn` on purpose: the same book is often in
    the catalogue several times under different ISBNs (different editions,
    hardback vs paperback). Grouping by title merges those editions. Grouping by
    ISBN would split one popular book across several rows.

    **SQL concepts:** `INNER JOIN`, `GROUP BY`, `AVG`, `ORDER BY`, `LIMIT`
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q4_top_books = mo.sql(
        f"""
        SELECT
            b.title,
            b.author,
            COUNT(*)                AS n_ratings,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM ratings r
        JOIN books b ON b.isbn = r.isbn
        WHERE r.is_explicit
        GROUP BY b.title, b.author
        ORDER BY n_ratings DESC
        LIMIT 12;
        """,
        engine=con
    )
    return (q4_top_books,)


@app.cell
def _(plot_top_books, q4_top_books):
    plot_top_books(q4_top_books)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Look at the second row. **`Wild Animus` has 581 ratings and an average of
    4.39** — every other book in this top 12 averages above 7.

    That is not an accident of taste. *Wild Animus* was a self-published novel
    whose author gave away enormous numbers of free copies in the early 2000s.
    People received it without choosing it, read it, and disliked it. Popularity
    and quality are different measurements, and this row is the proof.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q5. Which books are rated *highest*?

    **What are we doing?**
    Sorting by average rating instead of by count — but only among books with at
    least 100 ratings.

    That threshold is the entire point of this query. Without it the top of the
    list is books with a single 10/10 rating, which tells you nothing. `HAVING`
    applies the filter **after** grouping, which is what makes it different from
    `WHERE`:

    | Clause | Runs | Can see |
    |---|---|---|
    | `WHERE` | before grouping | individual rows |
    | `HAVING` | after grouping | aggregates like `COUNT(*)` |

    Try changing `100` to `20` and watch the list fill with obscure titles.

    **SQL concepts:** `HAVING`, `AVG`, `JOIN`
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q5_highest_rated = mo.sql(
        f"""
        SELECT
            b.title,
            b.author,
            COUNT(*)                AS n_ratings,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM ratings r
        JOIN books b ON b.isbn = r.isbn
        WHERE r.is_explicit
        GROUP BY b.title, b.author
        HAVING COUNT(*) >= 100
        ORDER BY avg_rating DESC
        LIMIT 12;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A completely different list from Q4 — **Harry Potter takes five of the top
    six places**, alongside *To Kill a Mockingbird* and *Ender's Game*.

    Q4 answered "what did people read?"; Q5 answers "what did people love?".
    Neither is more correct. Choosing which one a business question actually needs
    is the skill.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q6. Which authors dominate the collection?

    **What are we doing?**
    Aggregating by author instead of by book, counting both how many distinct
    titles they have in the catalogue and how many ratings they attracted.

    `COUNT(DISTINCT b.isbn)` is essential here. A plain `COUNT(*)` would count one
    row per *rating*, so an author with one wildly popular book would appear to
    have thousands of books. `DISTINCT` counts each ISBN once no matter how many
    ratings it received.

    **SQL concepts:** `COUNT(DISTINCT ...)`, `HAVING`, `JOIN`
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q6_top_authors = mo.sql(
        f"""
        SELECT
            b.author,
            COUNT(DISTINCT b.isbn)  AS n_books,
            COUNT(*)                AS n_ratings,
            ROUND(AVG(r.rating), 2) AS avg_rating
        FROM ratings r
        JOIN books b ON b.isbn = r.isbn
        WHERE r.is_explicit AND b.author IS NOT NULL
        GROUP BY b.author
        HAVING COUNT(DISTINCT b.isbn) >= 20
        ORDER BY n_ratings DESC
        LIMIT 12;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Stephen King leads on volume** with hundreds of catalogue entries and the
    most ratings of any author — but his average sits around 7.8, in the same
    band as everyone else on the list. **J. K. Rowling has far fewer titles and
    the highest average by a clear margin.**

    Volume and acclaim are, again, separate axes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q7. Where in the world are the raters?  📊

    **What are we doing?**
    A **three-table join**: `ratings` → `users` (who rated) → filtered to explicit
    ratings, grouped by the `country` that the build notebook parsed out of the
    free-text location field.

    `HAVING COUNT(*) >= 1500` drops the long tail of countries with too few
    ratings for the average to mean anything.

    **SQL concepts:** multi-table `JOIN`, `GROUP BY`, `HAVING`, `IS NOT NULL`
    """)
    return


@app.cell
def _(con, mo, ratings, users):
    q7_by_country = mo.sql(
        f"""
        SELECT
            u.country,
            COUNT(DISTINCT u.user_id) AS n_users,
            COUNT(*)                  AS n_ratings,
            ROUND(AVG(r.rating), 2)   AS avg_rating
        FROM ratings r
        JOIN users u ON u.user_id = r.user_id
        WHERE r.is_explicit
          AND u.country IS NOT NULL
        GROUP BY u.country
        HAVING COUNT(*) >= 1500
        ORDER BY n_ratings DESC
        LIMIT 12;
        """,
        engine=con
    )
    return (q7_by_country,)


@app.cell
def _(plot_ratings_by_country, q7_by_country):
    plot_ratings_by_country(q7_by_country)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The USA contributes more ratings than every other country combined** — about
    seven times the next largest, Canada.

    Notice how little the `avg_rating` column varies: every country sits between
    roughly 7.3 and 7.8. Rating *generosity* is nearly universal; rating *volume*
    is extremely concentrated. Any "global" conclusion drawn from this dataset is
    really a conclusion about American readers.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q8. When were these books published?  📊

    **What are we doing?**
    Bucketing publication years into decades with integer division.

    `publication_year // 10 * 10` turns 1997 into 199 and then back into 1990.
    The `//` operator is **integer division** — it discards the remainder.
    Ordinary `/` in DuckDB produces a decimal, which would give you `199.7` and
    ruin the grouping. This is a very common bug.

    `WHERE publication_year IS NOT NULL` excludes the 4,720 books whose year was
    unusable in the source.

    **SQL concepts:** integer division `//`, `GROUP BY` on a computed column
    """)
    return


@app.cell
def _(books, con, mo):
    q8_by_decade = mo.sql(
        f"""
        SELECT
            (publication_year // 10) * 10 AS decade,
            COUNT(*)                      AS n_books,
            COUNT(DISTINCT publisher)     AS n_publishers
        FROM books
        WHERE publication_year IS NOT NULL
          AND publication_year >= 1940
        GROUP BY decade
        ORDER BY decade;
        """,
        engine=con
    )
    return (q8_by_decade,)


@app.cell
def _(plot_books_per_decade, q8_by_decade):
    plot_books_per_decade(q8_by_decade)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The catalogue is a snapshot, not a library.** Nearly half of all books were
    published in the 1990s, and the 2000s bar covers only 2000–2004 because the
    data was collected in 2004.

    The steep drop before 1980 is not evidence that fewer books existed — it
    reflects what was in print and being traded online in 2004. Always ask what a
    dataset's shape says about *how it was collected* before treating it as a
    description of the world.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q9. Do older readers rate differently from younger ones?

    **What are we doing?**
    Bucketing users into age bands with a `CASE` expression, then comparing
    average ratings across bands.

    The band labels are prefixed `1.`, `2.`, `3.` … so that `ORDER BY age_group`
    sorts them correctly. Without the prefixes SQL would sort alphabetically and
    put `'18-24'` before `'under 18'`. This is a small trick worth remembering
    whenever you build categories by hand.

    **SQL concepts:** `CASE WHEN`, `GROUP BY` on a computed label, `COUNT(DISTINCT)`
    """)
    return


@app.cell
def _(con, mo, ratings, users):
    q9_by_age = mo.sql(
        f"""
        SELECT
            CASE
                WHEN u.age < 18 THEN '1. under 18'
                WHEN u.age < 25 THEN '2. 18-24'
                WHEN u.age < 35 THEN '3. 25-34'
                WHEN u.age < 50 THEN '4. 35-49'
                WHEN u.age < 65 THEN '5. 50-64'
                ELSE                 '6. 65+'
            END                       AS age_group,
            COUNT(DISTINCT u.user_id) AS n_readers,
            COUNT(*)                  AS n_ratings,
            ROUND(AVG(r.rating), 2)   AS avg_rating
        FROM ratings r
        JOIN users u ON u.user_id = r.user_id
        WHERE r.is_explicit
          AND u.age IS NOT NULL
        GROUP BY age_group
        ORDER BY age_group;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Age barely matters.** Every band averages between 7.6 and 7.9 — a spread of
    about a quarter of a point on a ten-point scale.

    This is a genuinely useful negative result, and worth sitting with. A great
    many analyses set out expecting demographics to explain behaviour; here the
    honest finding is that they do not. Reporting "we checked, and it does not
    vary" is a real answer.

    Remember also that 40% of users left age blank, and they are excluded here.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q10. Which users have never rated a book?

    **What are we doing?**
    Finding rows in one table that have **no** match in another. This is called an
    **anti-join**, and it answers a whole family of business questions: customers
    who never ordered, products never sold, accounts never logged into.

    SQL gives you three ways to write it. Two are good, one is a trap.

    | Pattern | Verdict |
    |---|---|
    | `NOT EXISTS (SELECT 1 FROM ...)` | ✅ what we use — clear, fast, NULL-safe |
    | `LEFT JOIN ... WHERE b.key IS NULL` | ✅ equivalent; the classic phrasing |
    | `NOT IN (SELECT key FROM ...)` | ⚠️ **breaks silently if the subquery returns any NULL** |

    The `NOT IN` trap is worth understanding because it is completely silent. If the
    subquery returns even one `NULL`, then `x NOT IN (1, 2, NULL)` evaluates to
    `UNKNOWN` rather than `TRUE` for every `x` — so the query returns **zero rows**
    and looks like a legitimate "no results" answer. `NOT EXISTS` has no such
    problem. Prefer it by default.

    ### One question, two meanings

    "Never rated a book" is ambiguous here, and the gap is 13,174 users:

    | Definition | Count |
    |---|---|
    | No rows in `ratings` | 186,755 |
    | No rows in `ratings` **and** none in `ratings_orphaned` | 173,581 |

    The difference is users who only ever rated books that are missing from our
    catalogue. They *did* rate things; we just cannot say what. The query below
    reports both so the ambiguity is visible rather than assumed away.

    **SQL concepts:** `NOT EXISTS`, anti-join, `COUNT(*) FILTER`
    """)
    return


@app.cell
def _(con, mo):
    q10_users_never_rated = mo.sql(
        f"""
        SELECT
            COUNT(*)                                    AS users_total,
            COUNT(*) FILTER (
                WHERE NOT EXISTS (
                    SELECT 1 FROM ratings r WHERE r.user_id = u.user_id
                )
            )                                           AS no_catalogued_ratings,
            COUNT(*) FILTER (
                WHERE NOT EXISTS (
                    SELECT 1 FROM ratings r WHERE r.user_id = u.user_id
                )
                AND NOT EXISTS (
                    SELECT 1 FROM ratings_orphaned o WHERE o.user_id = u.user_id
                )
            )                                           AS no_activity_at_all
        FROM users u;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now the same anti-join returning the actual rows rather than a count. The five
    users with IDs above 900000 were added by `inject_unrated.py` specifically so
    that this query has a small, checkable answer at the end of it — they are
    guaranteed to have no ratings at all.
    """)
    return


@app.cell
def _(con, mo):
    q10b_never_rated_sample = mo.sql(
        f"""
        SELECT
            u.user_id,
            u.city,
            u.country,
            u.age
        FROM users u
        WHERE NOT EXISTS (
            SELECT 1 FROM ratings r WHERE r.user_id = u.user_id
        )
        AND u.country IS NOT NULL
        ORDER BY u.user_id DESC
        LIMIT 10;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Two thirds of registered users never rated a single catalogued book.** That is
    not a defect — it is what voluntary participation looks like. People sign up,
    look around, and never contribute.

    It does mean you should be careful about the phrase "our users". A statement
    like "our users rate books 7.6 on average" is really about the 24% who rated
    anything at all.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q11. Which books have never been rated?

    **What are we doing?**
    The same anti-join in the other direction — books with no matching row in
    `ratings`.

    This one has a wrinkle the users version does not. A book can be missing from
    `ratings` for two very different reasons:

    1. **Nobody rated it.** Genuinely unread.
    2. **It was rated, but under an ISBN we quarantined.** No — this cannot happen.
       `ratings_orphaned` holds ratings whose ISBN is *absent* from `books`, so an
       ISBN that exists in `books` can never appear there.

    Reasoning through that second case is the useful part. It is exactly the kind of
    check that separates a correct anti-join from a plausible one, and the schema
    design guarantees the answer.

    **SQL concepts:** `NOT EXISTS`, anti-join, `LEFT JOIN` alternative
    """)
    return


@app.cell
def _(con, mo):
    q11_books_never_rated = mo.sql(
        f"""
        SELECT
            b.isbn,
            b.title,
            b.author,
            b.publication_year,
            b.isbn LIKE 'ISBA2402%' AS is_synthetic
        FROM books b
        WHERE NOT EXISTS (
            SELECT 1 FROM ratings r WHERE r.isbn = b.isbn
        )
        ORDER BY is_synthetic DESC, b.publication_year DESC NULLS LAST, b.title
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **1,219 of 271,389 books (0.4%) have never been rated** — a far smaller share
    than the 67% of users who never rated.

    Ten of those 1,219 are the synthetic titles added by `inject_unrated.py`. The
    `is_synthetic` column tests `isbn LIKE 'ISBA2402%'` and the `ORDER BY` puts them
    first, so you can confirm all ten come back before the real never-rated books
    begin. Sorting by publication year alone would **not** have surfaced them —
    hundreds of genuine 2004 titles are also unrated, and they sort first
    alphabetically. Worth remembering when you want specific rows in a result: sort
    on the thing that identifies them, not on something correlated with it.

    The asymmetry is worth a moment. Almost every book has at least one rating,
    while most users have none, because a book only needs **one** person to rate it
    to leave the unrated set — and the handful of extremely active readers from
    Q13 cover an enormous amount of the catalogue between them.

    Here is the same query written as a `LEFT JOIN`, which you will meet often:

    ```sql
    SELECT b.isbn, b.title
    FROM books b
    LEFT JOIN ratings r ON r.isbn = b.isbn
    WHERE r.isbn IS NULL;
    ```

    The `LEFT JOIN` keeps every book and fills unmatched rows with `NULL`; testing
    the joined key for `NULL` then isolates exactly the non-matches. Same answer,
    same speed in DuckDB — pick whichever reads better to you.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q12. How does the user base split by engagement?  📊

    **What are we doing?**
    Putting every user into exactly one of three buckets, then showing the split as
    a pie chart.

    The `LEFT JOIN` is doing the important work. An `INNER JOIN` would drop users
    with no ratings entirely — which is precisely the group we most want to count.
    `LEFT JOIN` keeps every user and produces `NULL`s for the missing side, so
    `COUNT(r.rating)` returns 0 for them.

    Note that `COUNT(r.rating)` and `COUNT(*)` are **not** interchangeable here:
    `COUNT(*)` counts rows, and a user with no ratings still produces one row after
    the `LEFT JOIN`. `COUNT(r.rating)` counts non-NULL values, which is 0. Getting
    this backwards is one of the most common `LEFT JOIN` mistakes.

    **On pie charts:** they deserve their bad reputation — people compare angles
    poorly, so a pie with eight similar slices is unreadable. This one is defensible
    because there are only **three** slices, they are very different sizes, and every
    user falls into exactly one, so the whole is real. Beyond about five categories,
    or when the parts do not sum to a meaningful whole, use a bar chart.

    **SQL concepts:** `LEFT JOIN`, `COUNT(column)` vs `COUNT(*)`, `CASE`, `FILTER`
    """)
    return


@app.cell
def _(con, mo):
    q12_user_segments = mo.sql(
        f"""
        WITH user_activity AS (
            SELECT
                u.user_id,
                COUNT(r.rating)                       AS n_ratings,
                COUNT(*) FILTER (WHERE r.is_explicit) AS n_explicit
            FROM users u
            LEFT JOIN ratings r ON r.user_id = u.user_id
            GROUP BY u.user_id
        )
        SELECT
            CASE
                WHEN n_ratings  = 0 THEN 'Never rated anything'
                WHEN n_explicit = 0 THEN 'Implicit activity only'
                ELSE                     'Gave explicit ratings'
            END                                                AS segment,
            COUNT(*)                                           AS n_users,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_users
        FROM user_activity
        GROUP BY segment
        ORDER BY n_users DESC;
        """,
        engine=con
    )
    return (q12_user_segments,)


@app.cell
def _(plot_user_segments, q12_user_segments):
    plot_user_segments(q12_user_segments)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The middle slice is the interesting one. **24,015 users (8.6%) appear in
    `ratings` but never gave a single explicit score** — every one of their rows is
    an implicit zero.

    If you had forgotten the `is_explicit` filter, these users would silently drag
    every per-user average toward zero while looking like ordinary raters. They are
    the human face of the trap that Q18 measures.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    # Part 3 — Intermediate+ Queries (6)

    Common Table Expressions and window functions. A window function computes a
    value across a set of rows *related to the current row* without collapsing
    them the way `GROUP BY` does — which is what makes ranking, running totals and
    per-group top-N possible in a single query.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q13. How concentrated is rating activity?  📊

    **What are we doing?**
    First a **CTE** (`WITH per_user AS ...`) counts each user's ratings. Then the
    outer query buckets users by how active they were and reports each band's
    share of the total.

    A CTE is a named temporary result you can refer to like a table. It exists
    only for the duration of the query. Use them whenever a query needs a
    two-stage calculation — they read far better than nested subqueries, and the
    name documents the intent.

    **SQL concepts:** `WITH` (CTE), `CASE`, `SUM(SUM(...)) OVER ()`
    """)
    return


@app.cell
def _(con, mo, ratings):
    q13_reader_activity = mo.sql(
        f"""
        WITH per_user AS (
            SELECT user_id, COUNT(*) AS n_ratings
            FROM ratings
            GROUP BY user_id
        )
        SELECT
            CASE
                WHEN n_ratings = 1   THEN 'a. exactly 1'
                WHEN n_ratings <= 5  THEN 'b. 2-5'
                WHEN n_ratings <= 20 THEN 'c. 6-20'
                WHEN n_ratings <= 100 THEN 'd. 21-100'
                WHEN n_ratings <= 500 THEN 'e. 101-500'
                ELSE                      'f. 500+'
            END                    AS activity_band,
            COUNT(*)               AS n_users,
            SUM(n_ratings)         AS total_ratings,
            ROUND(100.0 * SUM(n_ratings) / SUM(SUM(n_ratings)) OVER (), 1)
                                   AS pct_of_all_ratings
        FROM per_user
        GROUP BY activity_band
        ORDER BY activity_band;
        """,
        engine=con
    )
    return (q13_reader_activity,)


@app.cell
def _(plot_reader_activity, q13_reader_activity):
    plot_reader_activity(q13_reader_activity)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This is the most important structural fact about the dataset.

    | Band | Readers | Share of readers | Share of ratings |
    |---|---|---|---|
    | exactly 1 | 51,270 | 55.7% | **5.0%** |
    | 500+ | 261 | 0.3% | **29.8%** |

    **261 people — three tenths of one percent of readers — produced almost 30% of
    all ratings.** Meanwhile the majority of readers rated exactly one book.

    This shape is called a *power law*, and it appears in almost every dataset
    built from voluntary online participation. The practical consequence: an
    "average reader" does not exist here. Any per-user average is dominated by a
    few hundred extremely active accounts, and a recommendation system trained on
    this data would mostly learn their taste.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q14. What is the most popular book in each country?

    **What are we doing?**
    Ranking books *within* each country and keeping the top 3 — a classic
    "top-N per group" problem.

    ### Two chained CTEs

    The query needs "the top 3 books in each of the top 6 countries", which is two
    separate top-N problems stacked on top of each other. Each gets its own CTE:

    | CTE | Job |
    |---|---|
    | `top_countries` | find the 6 countries with the most explicit ratings |
    | `country_books` | count ratings per (country, book) for just those countries |

    The second CTE refers to the first through `IN (SELECT country FROM
    top_countries)`. **Nothing is hardcoded** — if the data changes, or if you
    rebuild after filtering differently, the country list follows automatically.

    Writing the six country names as string literals would have been shorter, and
    it is what you will see in a lot of code. It is also a small time bomb: the
    literals silently stop reflecting the data the moment the data moves, and
    nothing errors. Deriving the list keeps the query honest. Change `LIMIT 6` to
    `LIMIT 10` and the whole thing still works.

    ### Ranking within each group

    | Piece | Job |
    |---|---|
    | `PARTITION BY country` | restart the numbering for each country |
    | `ORDER BY n_ratings DESC` | decide the ranking inside each country |
    | `QUALIFY rank_in_country <= 3` | keep only the top 3 of each |

    `QUALIFY` filters on the result of a window function. You cannot use `WHERE`
    for this — at `WHERE` time the window function has not been computed yet.
    `QUALIFY` is to window functions what `HAVING` is to aggregates.

    We use `ROW_NUMBER()` rather than `RANK()` here. `RANK()` gives tied rows the
    same number, so a three-way tie for 2nd place would return five rows for that
    country. `ROW_NUMBER()` always returns exactly three, breaking ties by title.

    **SQL concepts:** chained CTEs, subquery in `IN`, `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`, `QUALIFY`
    """)
    return


@app.cell
def _(books, con, mo, ratings, users):
    q14_top_per_country = mo.sql(
        f"""
        WITH top_countries AS (
            SELECT u.country
            FROM ratings r
            JOIN users u ON u.user_id = r.user_id
            WHERE r.is_explicit
              AND u.country IS NOT NULL
            GROUP BY u.country
            ORDER BY COUNT(*) DESC
            LIMIT 6
        ),
        country_books AS (
            SELECT
                u.country,
                b.title,
                COUNT(*)                AS n_ratings,
                ROUND(AVG(r.rating), 2) AS avg_rating
            FROM ratings r
            JOIN users u ON u.user_id = r.user_id
            JOIN books b ON b.isbn    = r.isbn
            WHERE r.is_explicit
              AND u.country IN (SELECT country FROM top_countries)
            GROUP BY u.country, b.title
            HAVING COUNT(*) >= 10
        )
        SELECT
            country,
            title,
            n_ratings,
            avg_rating,
            ROW_NUMBER() OVER (
                PARTITION BY country
                ORDER BY n_ratings DESC, title
            ) AS rank_in_country
        FROM country_books
        QUALIFY rank_in_country <= 3
        ORDER BY country, rank_in_country;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Reading is local.** Germany's top books are German-language titles
    (*Der Vorleser*, *Illuminati.* — the German edition of *Angels & Demons*);
    Spain's are Spanish (*El Hobbit*, *El guardián entre el centeno*).

    The English-speaking countries share the same bestsellers, and *Wild Animus*
    turns up again in Canada and Australia — the free-copy giveaway was
    international.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q15. How is attention spread across the catalogue?

    **What are we doing?**
    `NTILE(4)` sorts the books by rating count and splits them into four
    equal-sized groups (quartiles). We then measure how many of the *ratings* each
    quartile of *books* received.

    `NTILE(n)` divides rows into `n` buckets of as near to equal size as possible.
    It is the tool for "split my data into quartiles / deciles / percentiles".

    **SQL concepts:** `NTILE`, nested CTEs, window `SUM` for percentage-of-total
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q15_popularity_quartiles = mo.sql(
        f"""
        WITH book_popularity AS (
            SELECT b.isbn, COUNT(*) AS n_ratings
            FROM ratings r
            JOIN books b ON b.isbn = r.isbn
            GROUP BY b.isbn
        ),
        ranked AS (
            SELECT *, NTILE(4) OVER (ORDER BY n_ratings) AS quartile
            FROM book_popularity
        )
        SELECT
            quartile,
            COUNT(*)          AS n_books,
            MIN(n_ratings)    AS fewest_ratings,
            MAX(n_ratings)    AS most_ratings,
            SUM(n_ratings)    AS total_ratings,
            ROUND(100.0 * SUM(n_ratings) / SUM(SUM(n_ratings)) OVER (), 1)
                              AS pct_of_all_ratings
        FROM ranked
        GROUP BY quartile
        ORDER BY quartile;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The bottom half of the catalogue has exactly one rating per book.** The top
    quartile collects roughly 74% of all rating activity.

    Look at quartiles 1 and 2: both show `fewest_ratings = 1` and
    `most_ratings = 1`. So many books are tied at a single rating that `NTILE` has
    to split the tie arbitrarily to make the buckets equal. That is worth knowing
    about `NTILE` — it guarantees **equal bucket sizes**, not meaningful
    boundaries. When ties dominate, the quartile edges are an artefact.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q16. Readers who liked *The Da Vinci Code* also liked…

    **What are we doing?**
    The skeleton of a recommendation engine, in one query.

    1. The `fans` CTE finds every user who gave *The Da Vinci Code* an 8 or better.
    2. We join those users back to `ratings` to see **everything else** they rated
       highly.
    3. Group by title, count how many fans rated each, exclude the original book.

    This is a **self-join**: `ratings` is used twice in one query, once to define
    the audience and once to find what that audience read. `HAVING COUNT(*) >= 15`
    keeps out coincidences.

    **SQL concepts:** CTE, self-join, `DISTINCT`, `HAVING`
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q16_also_liked = mo.sql(
        f"""
        WITH fans AS (
            SELECT DISTINCT r.user_id
            FROM ratings r
            JOIN books b ON b.isbn = r.isbn
            WHERE b.title = 'The Da Vinci Code'
              AND r.rating >= 8
        )
        SELECT
            b.title,
            b.author,
            COUNT(*)                AS n_fans_who_liked_it,
            ROUND(AVG(r.rating), 2) AS avg_rating_from_fans
        FROM fans f
        JOIN ratings r ON r.user_id = f.user_id
        JOIN books   b ON b.isbn    = r.isbn
        WHERE r.rating >= 8
          AND b.title <> 'The Da Vinci Code'
        GROUP BY b.title, b.author
        HAVING COUNT(*) >= 15
        ORDER BY n_fans_who_liked_it DESC
        LIMIT 12;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The top recommendation is *Angels & Demons* — the same author's other
    thriller featuring the same protagonist.** The query had no idea who wrote
    anything; it only knew who rated what. That the obvious answer falls out of
    pure co-rating behaviour is a good sign the logic is sound.

    Notice what else surfaces, though: *The Lovely Bones*, *The Secret Life of
    Bees*, *Life of Pi*. These are simply the most-rated books overall from Q4.
    A naive co-occurrence count is **biased toward popularity** — it recommends
    bestsellers to everybody. Real recommenders correct for this by dividing by
    each book's overall popularity, so that a shared taste counts for more than a
    shared bestseller.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q17. How concentrated is the author market?

    **What are we doing?**
    Building a **running total** down the ranked list of authors, to see how few
    of them account for a large share of all rating activity.

    ```sql
    SUM(n_ratings) OVER (ORDER BY n_ratings DESC ROWS UNBOUNDED PRECEDING)
    ```

    The `ROWS UNBOUNDED PRECEDING` frame means "every row from the start of the
    ordering up to and including this one". As the window slides down the list the
    frame grows, which is exactly a cumulative sum. Change the frame and you get a
    different calculation — `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` would give
    a 3-row moving total.

    **SQL concepts:** window frames, running total, cumulative percentage
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q17_author_concentration = mo.sql(
        f"""
        WITH author_totals AS (
            SELECT b.author, COUNT(*) AS n_ratings
            FROM ratings r
            JOIN books b ON b.isbn = r.isbn
            WHERE r.is_explicit
              AND b.author IS NOT NULL
            GROUP BY b.author
        )
        SELECT
            author,
            n_ratings,
            ROUND(100.0 * n_ratings / SUM(n_ratings) OVER (), 3) AS pct_of_all,
            SUM(n_ratings) OVER (
                ORDER BY n_ratings DESC
                ROWS UNBOUNDED PRECEDING
            )                                                    AS running_total,
            ROUND(
                100.0 * SUM(n_ratings) OVER (
                    ORDER BY n_ratings DESC
                    ROWS UNBOUNDED PRECEDING
                ) / SUM(n_ratings) OVER (), 2
            )                                                    AS cumulative_pct
        FROM author_totals
        ORDER BY n_ratings DESC
        LIMIT 15;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Stephen King alone accounts for about 1.2% of every explicit rating in the
    database**, and the top 15 authors together reach roughly 7%.

    That may sound modest until you remember there are over 100,000 distinct
    authors here. The `cumulative_pct` column is the useful one — it is the shape
    of a market-concentration curve, and the same query pattern works unchanged
    for revenue by customer, traffic by page, or defects by component.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Q18. The implicit-zero trap — the most important query here

    **What are we doing?**
    Computing the same average two ways, side by side, to measure exactly how
    wrong you are if you forget that `rating = 0` means "not scored".

    `AVG(r.rating) FILTER (WHERE r.is_explicit)` applies a condition to **one
    aggregate only**, leaving the others untouched. It is cleaner than the
    equivalent `AVG(CASE WHEN r.is_explicit THEN r.rating END)` and it is standard
    SQL. `FILTER` is the right tool whenever one query needs several differently
    scoped aggregates.

    **SQL concepts:** `FILTER (WHERE ...)`, comparing aggregates, `HAVING`
    """)
    return


@app.cell
def _(books, con, mo, ratings):
    q18_implicit_trap = mo.sql(
        f"""
        SELECT
            b.title,
            COUNT(*)                                   AS all_rows,
            COUNT(*) FILTER (WHERE r.is_explicit)      AS explicit_rows,
            ROUND(AVG(r.rating), 2)                    AS avg_wrong,
            ROUND(AVG(r.rating) FILTER (WHERE r.is_explicit), 2)
                                                       AS avg_correct,
            ROUND(AVG(r.rating) FILTER (WHERE r.is_explicit) - AVG(r.rating), 2)
                                                       AS understated_by
        FROM ratings r
        JOIN books b ON b.isbn = r.isbn
        GROUP BY b.title
        HAVING COUNT(*) >= 300
        ORDER BY all_rows DESC
        LIMIT 12;
        """,
        engine=con
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Every book is understated by three to four full points.**

    *The Da Vinci Code* scores **4.64** if you include the implicit zeros and
    **8.44** if you do not. The first number is not merely imprecise — it is
    meaningless, because it averages a rating scale together with a flag that was
    never on that scale.

    What makes this dangerous is that **4.64 looks completely plausible.** It is a
    number in the right range, on the right side of the midpoint, that you could
    put in a report and defend. Nothing about it announces that it is wrong.

    This is the lesson worth carrying out of this notebook: the errors that survive
    are the ones that produce believable numbers. Before you average a column, know
    what every value in it means — including the ones that look like data but are
    really codes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ---
    ## What we found

    | # | Question | Answer |
    |---|---|---|
    | Q3 | How do people rate? | Generously — 8 is the mode, ~7.6 is average |
    | Q4 | Most-rated book? | *The Lovely Bones*; *Wild Animus* is popular but disliked |
    | Q5 | Best-rated book? | Harry Potter, five of the top six |
    | Q7 | Who is rating? | The USA, more than everyone else combined |
    | Q8 | What is in the catalogue? | A 1990s snapshot, truncated at 2004 |
    | Q9 | Does age predict rating? | No — every band is within a quarter point |
    | Q10 | Who never rated? | 186,755 users — two thirds of everyone registered |
    | Q11 | What was never read? | Only 1,219 books (0.4%) — far rarer than idle users |
    | Q12 | How does engagement split? | 67% never rated · 8.6% implicit only · 24% explicit |
    | Q13 | How concentrated is activity? | 0.3% of readers made 29.8% of ratings |
    | Q14 | Do countries differ? | Yes — Germany and Spain read in their own languages |
    | Q15 | How is attention spread? | Half the catalogue has exactly one rating |
    | Q16 | Can we recommend? | Yes, but naive co-occurrence just recommends bestsellers |
    | Q17 | Author concentration? | Top 15 of 100,000+ authors ≈ 7% of all ratings |
    | Q18 | Biggest trap? | Implicit zeros understate every average by 3–4 points |

    ## SQL techniques used

    | Technique | First seen | Why it mattered |
    |---|---|---|
    | `UNION ALL` | Q2 | Stack counts from several tables |
    | Window `OVER ()` | Q3 | Percentage of total without a second query |
    | `INNER JOIN` | Q4 | Turn foreign keys into readable names |
    | `HAVING` | Q5 | Filter *groups*, not rows — the minimum-votes threshold |
    | `COUNT(DISTINCT)` | Q6 | Count books, not rating rows |
    | Integer division `//` | Q8 | Bucket years into decades without decimals |
    | `CASE WHEN` | Q9 | Build categories that do not exist in the data |
    | `NOT EXISTS` (anti-join) | Q10 | Rows with no match on the other side |
    | `LEFT JOIN` + `IS NULL` | Q11 | The other way to write an anti-join |
    | `COUNT(col)` vs `COUNT(*)` | Q12 | Counting non-NULLs after a `LEFT JOIN` |
    | CTE (`WITH`) | Q13 | Two-stage calculations that stay readable |
    | Chained CTEs | Q14 | Derive the country list instead of hardcoding it |
    | `ROW_NUMBER` + `QUALIFY` | Q14 | Top-N per group |
    | `NTILE` | Q15 | Equal-sized buckets — and their limits under ties |
    | Self-join | Q16 | Use one table twice for co-occurrence |
    | Window frames | Q17 | Running totals and cumulative share |
    | `FILTER (WHERE ...)` | Q18 | Several differently scoped aggregates at once |

    ## Exercises

    1. **Q5 variant.** Change the `HAVING` threshold from 100 to 20, then to 500.
       At what point does the list stop being dominated by obscure books? What does
       that tell you about choosing thresholds?
    2. **Q7 variant.** Rank countries by *average rating* instead of volume, with a
       minimum of 1,000 ratings. Does the ordering resemble the volume ranking?
    3. **Q14 variant.** Swap `ROW_NUMBER()` for `RANK()` and then `DENSE_RANK()`.
       Explain why the number of rows returned changes.
    4. **Q16 variant.** Pick a different seed book. Try one with a strong genre
       identity (*1984*) and one bestseller (*The Lovely Bones*). Which gives more
       useful recommendations, and why?
    5. **Orphans.** `ratings_orphaned` holds 118,589 ratings whose ISBN is missing
       from `books`. Are those users different from the rest — do they rate more
       often, or more harshly? Write the query.
    6. **Q10 variant.** Rewrite the anti-join three ways — `NOT EXISTS`,
       `LEFT JOIN ... IS NULL`, and `NOT IN`. Confirm the first two agree. Then work
       out why `NOT IN` is dangerous here, and construct a case where it silently
       returns zero rows.
    7. **Q11 variant.** Of the 1,219 never-rated books, are any by authors who are
       popular elsewhere in the catalogue? Join back to the author totals from Q17.
    8. **Hard.** Correct Q16's popularity bias: divide each candidate's fan count
       by its total number of ratings across all users, so that a book which
       *everyone* rates highly scores lower than one which *only Da Vinci Code
       fans* rate highly. Does the list improve?
    """)
    return


if __name__ == "__main__":
    app.run()
