# `GROUP BY` Tutorial 101

[← Tutorials](../README.md) · **`GROUP BY` tutorial 101** · [Notebook version](Group_By_Notebook.py) · [`GROUP BY` with office supplies →](office_supplies_group_by_tutorial.md)

## What `GROUP BY` Does

1. `GROUP BY` gathers rows with the same value(s) in the listed column(s) into
   one **summary row** per group — it *reduces* many rows to a few.
2. It is almost always used with **aggregate functions** — `COUNT()`, `SUM()`,
   `AVG()`, `MIN()`, `MAX()` — which compute one value per group.

```
SELECT column_name(s),
       AGGREGATE_FUNCTION(column_name)
FROM   table_name
WHERE  condition
GROUP BY column_name(s);
```

---

## Setup

Everything below runs in the **DuckDB command line** (start it with `duckdb`
in a terminal — it prints its version, `v2.…`, and a `D` prompt) or in a
Marimo notebook's SQL cells. No files are needed: the table is typed in.

### A table with two columns

```sql
CREATE OR REPLACE TABLE scores (player VARCHAR, score INT);
```

### Four rows for Alex, four for Jane — some scores missing (`NULL`)

```sql
INSERT INTO scores (player, score) VALUES ('Alex', 10);
INSERT INTO scores (player, score) VALUES ('Alex', 20);
INSERT INTO scores (player, score) VALUES ('Alex', 30);
INSERT INTO scores (player, score) VALUES ('Alex', NULL);
INSERT INTO scores (player, score) VALUES ('Jane', 70);
INSERT INTO scores (player, score) VALUES ('Jane', 90);
INSERT INTO scores (player, score) VALUES ('Jane', NULL);
INSERT INTO scores (player, score) VALUES ('Jane', NULL);
```

```sql
SELECT *
FROM scores
ORDER BY player, score NULLS LAST;
```

Result:

| player | score |
|---|---:|
| Alex | 10 |
| Alex | 20 |
| Alex | 30 |
| Alex | NULL |
| Jane | 70 |
| Jane | 90 |
| Jane | NULL |
| Jane | NULL |

*8 rows*

---

## Average Score per Player

```sql
SELECT player,
       AVG(score) AS avg_score
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | avg_score |
|---|---:|
| Alex | 20.0 |
| Jane | 80.0 |

*2 rows*

**Note:** `AVG()` ignores `NULL`s. Alex's scores are 10, 20, 30, `NULL`, so his
average is (10 + 20 + 30) / 3 = 20.0 — not (10 + 20 + 30 + 0) / 4.

## Lowest and Highest Score per Player

```sql
SELECT player,
       MIN(score) AS min_score,
       MAX(score) AS max_score
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | min_score | max_score |
|---|---:|---:|
| Alex | 10 | 30 |
| Jane | 70 | 90 |

*2 rows*

## `COUNT(*)` vs. `COUNT(column)`

`COUNT(*)` counts every row in the group, `NULL`s included. `COUNT(score)`
counts only the rows where `score` is not `NULL`.

```sql
SELECT player,
       COUNT(*)     AS total_rows,
       COUNT(score) AS non_null_scores
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | total_rows | non_null_scores |
|---|---:|---:|
| Alex | 4 | 3 |
| Jane | 4 | 2 |

*2 rows*

Alex has 4 rows but 3 scores; Jane has 4 rows but 2 scores.

## Total Score per Player

```sql
SELECT player,
       SUM(score) AS total_score
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | total_score |
|---|---:|
| Alex | 60 |
| Jane | 160 |

*2 rows*

Like `AVG()`, `SUM()` ignores `NULL`s.

## Several Aggregates in One Query

```sql
SELECT player,
       COUNT(*)     AS total_rows,
       COUNT(score) AS non_null_scores,
       SUM(score)   AS total_score,
       AVG(score)   AS avg_score,
       MIN(score)   AS min_score,
       MAX(score)   AS max_score
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | total_rows | non_null_scores | total_score | avg_score | min_score | max_score |
|---|---:|---:|---:|---:|---:|---:|
| Alex | 4 | 3 | 60 | 20.0 | 10 | 30 |
| Jane | 4 | 2 | 160 | 80.0 | 70 | 90 |

*2 rows*

---

## `HAVING`: Filter Groups After Aggregation

`WHERE` filters **rows** before grouping; `HAVING` filters **groups** after the
aggregates are computed.

Players whose average score is greater than 50:

```sql
SELECT player,
       AVG(score) AS avg_score
FROM scores
GROUP BY player
HAVING AVG(score) > 50
ORDER BY player;
```

Result:

| player | avg_score |
|---|---:|
| Jane | 80.0 |

*1 row*

Players with more than 2 non-`NULL` scores:

```sql
SELECT player,
       COUNT(score) AS non_null_scores
FROM scores
GROUP BY player
HAVING COUNT(score) > 2
ORDER BY player;
```

Result:

| player | non_null_scores |
|---|---:|
| Alex | 3 |

*1 row*

---

## `STRING_AGG` and `LIST`: See the Values in Each Group

`STRING_AGG()` joins a group's values into one text value; `LIST()` collects
them into a DuckDB list. The `ORDER BY` inside each fixes the order of the
values — without it, the order is not guaranteed.

```sql
SELECT player,
       STRING_AGG(score::VARCHAR, ', ' ORDER BY score) AS scores_text,
       LIST(score ORDER BY score)                      AS scores_list
FROM scores
GROUP BY player
ORDER BY player;
```

Result:

| player | scores_text | scores_list |
|---|---|---|
| Alex | 10, 20, 30 | [10, 20, 30, NULL] |
| Jane | 70, 90 | [70, 90, NULL, NULL] |

*2 rows*

**`NULL`s are treated differently:** `STRING_AGG()` skips them (`10, 20, 30`),
but `LIST()` **keeps** them (`[10, 20, 30, NULL]`). To leave them out of the
list, filter them: `LIST(score ORDER BY score) FILTER (WHERE score IS NOT NULL)`.

---

## Grouping by Two Columns

First, add a `team` column and fill it in:

```sql
ALTER TABLE scores ADD COLUMN team VARCHAR;
UPDATE scores SET team = 'Red'  WHERE player = 'Alex';
UPDATE scores SET team = 'Blue' WHERE player = 'Jane';
```

Now each player also plays one game for the other team:

```sql
INSERT INTO scores (player, score, team) VALUES ('Alex', 50, 'Blue');
INSERT INTO scores (player, score, team) VALUES ('Jane', 40, 'Red');
```

```sql
SELECT *
FROM scores
ORDER BY team, player, score NULLS LAST;
```

Result:

| player | score | team |
|---|---:|---|
| Alex | 50 | Blue |
| Jane | 70 | Blue |
| Jane | 90 | Blue |
| Jane | NULL | Blue |
| Jane | NULL | Blue |
| Alex | 10 | Red |
| Alex | 20 | Red |
| Alex | 30 | Red |
| Alex | NULL | Red |
| Jane | 40 | Red |

*10 rows*

One group per **team and player**:

```sql
SELECT team,
       player,
       COUNT(score) AS games,
       SUM(score)   AS total_score,
       AVG(score)   AS avg_score
FROM scores
GROUP BY team, player
ORDER BY team, player;
```

Result:

| team | player | games | total_score | avg_score |
|---|---|---:|---:|---:|
| Blue | Alex | 1 | 50 | 50.0 |
| Blue | Jane | 2 | 160 | 80.0 |
| Red | Alex | 3 | 60 | 20.0 |
| Red | Jane | 1 | 40 | 40.0 |

*4 rows*

One group per **team**:

```sql
SELECT team,
       COUNT(score) AS games,
       SUM(score)   AS total_score,
       AVG(score)   AS avg_score
FROM scores
GROUP BY team
ORDER BY team;
```

Result:

| team | games | total_score | avg_score |
|---|---:|---:|---:|
| Blue | 3 | 210 | 70.0 |
| Red | 4 | 100 | 25.0 |

*2 rows*

---

## `WHERE` + `GROUP BY` + `HAVING` Together

The order of work: `WHERE` filters rows, then `GROUP BY` groups them, then
`HAVING` filters the groups. *Using only scores above 15, which teams average
more than 40?*

```sql
SELECT team,
       AVG(score)   AS avg_score,
       COUNT(score) AS num_scores
FROM scores
WHERE score > 15
GROUP BY team
HAVING AVG(score) > 40
ORDER BY avg_score DESC;
```

Result:

| team | avg_score | num_scores |
|---|---:|---:|
| Blue | 70.0 | 3 |

*1 row*

## Sorting by an Aggregate

Teams by total score, highest first:

```sql
SELECT team,
       SUM(score) AS total_score
FROM scores
GROUP BY team
ORDER BY total_score DESC;
```

Result:

| team | total_score |
|---|---:|
| Blue | 210 |
| Red | 100 |

*2 rows*

---

## Beyond `GROUP BY`: Ranking Rows

`GROUP BY` collapses rows; a **window function** such as `RANK()` keeps every
row and adds a value computed over other rows (see the
[window functions tutorial](../window_functions/ranking_tutorial.md)).

All scores ranked from highest to lowest (`NULL` scores sort last and are
ranked last):

```sql
SELECT player,
       score,
       RANK() OVER (ORDER BY score DESC) AS rnk
FROM scores
ORDER BY rnk, player;
```

Result:

| player | score | rnk |
|---|---:|---:|
| Jane | 90 | 1 |
| Jane | 70 | 2 |
| Alex | 50 | 3 |
| Jane | 40 | 4 |
| Alex | 30 | 5 |
| Alex | 20 | 6 |
| Alex | 10 | 7 |
| Alex | NULL | 8 |
| Jane | NULL | 8 |
| Jane | NULL | 8 |

*10 rows*

A separate ranking for each player (`PARTITION BY player`):

```sql
SELECT player,
       score,
       RANK() OVER (PARTITION BY player ORDER BY score DESC) AS rnk
FROM scores
ORDER BY player, rnk;
```

Result:

| player | score | rnk |
|---|---:|---:|
| Alex | 50 | 1 |
| Alex | 30 | 2 |
| Alex | 20 | 3 |
| Alex | 10 | 4 |
| Alex | NULL | 5 |
| Jane | 90 | 1 |
| Jane | 70 | 2 |
| Jane | 40 | 3 |
| Jane | NULL | 4 |
| Jane | NULL | 4 |

*10 rows*

Each player's top 2 scores — rank inside a CTE, then filter on the rank:

```sql
WITH ranked AS (
    SELECT player,
           score,
           RANK() OVER (PARTITION BY player ORDER BY score DESC) AS rnk
    FROM scores
)
SELECT player,
       score,
       rnk
FROM ranked
WHERE rnk <= 2
ORDER BY player, rnk;
```

Result:

| player | score | rnk |
|---|---:|---:|
| Alex | 50 | 1 |
| Alex | 30 | 2 |
| Jane | 90 | 1 |
| Jane | 70 | 2 |

*4 rows*

---

*MSIS-2402 — Database Management Systems: Fundamentals of SQL — Winter 2027*
