-- =====================================================================
-- MSIS-2402 · Week 4 · Session 7 — Live demo: a server and two clients
-- Goes with: lecture_slides_01_client_server_mysql.md
-- =====================================================================
--
-- Setup (once, from the course repository's root folder):
--   macOS:    mysql -u root < datasets/oltp_database/mysql/isba_shop_mysql.sql
--   Windows:  cmd /c "mysql -u root -p < datasets\oltp_database\mysql\isba_shop_mysql.sql"
--
-- Then open TWO terminal windows and connect in both:
--   mysql -u root isba_shop          (Windows: mysql -u root -p isba_shop)
--
-- Run each block in the terminal named in its header, one statement at a
-- time. The expected output is shown in comments (verified on MySQL 26.7.0;
-- connection IDs will differ). The demo cleans up after itself, so
-- isba_shop is unchanged for the labs.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Part 1 · Terminal A, then Terminal B — two clients, two sessions
-- ---------------------------------------------------------------------
SELECT CONNECTION_ID() AS my_connection,
       USER()          AS logged_in_as,
       DATABASE()      AS current_db;
-- Terminal A:  17 | root@localhost | isba_shop
-- Terminal B:  18 | root@localhost | isba_shop
-- Same user, same database, two separate connections to one server.


-- ---------------------------------------------------------------------
-- Part 2 · Terminal A — a table that was designed, not guessed
-- ---------------------------------------------------------------------
DESCRIBE customers;
-- customer_id  int          NO  PRI
-- gender       varchar(10)  NO
-- country      varchar(30)  NO
-- segment      varchar(30)  NO
-- signup_date  date         NO
-- Compare DuckDB's DESCRIBE of the CSV-loaded table: BIGINT/VARCHAR,
-- every column nullable, no key.


-- ---------------------------------------------------------------------
-- Part 3 · A writes, B reads (CRUD across two clients)
-- ---------------------------------------------------------------------

-- Terminal B
SELECT COUNT(*) AS customers FROM customers;                         -- 1000

-- Terminal A
INSERT INTO customers VALUES (1001, 'Female', 'Canada', 'Consumer', '2026-10-04');
-- Query OK, 1 row affected

-- Terminal B — visible immediately: autocommit is on
SELECT * FROM customers WHERE customer_id = 1001;
-- 1001 | Female | Canada | Consumer | 2026-10-04

-- Terminal A
UPDATE customers SET segment = 'VIP' WHERE customer_id = 1001;
-- Query OK, 1 row affected — Rows matched: 1  Changed: 1

-- Terminal B
SELECT customer_id, segment FROM customers WHERE customer_id = 1001;  -- VIP

-- Terminal A
DELETE FROM customers WHERE customer_id = 1001;
-- Query OK, 1 row affected

-- Terminal B
SELECT COUNT(*) AS customers FROM customers;                         -- 1000


-- ---------------------------------------------------------------------
-- Part 4 · Terminal A — the server refuses bad data
-- ---------------------------------------------------------------------
-- An order item for an order that does not exist:
INSERT INTO order_items VALUES (300001, 999999, 1, 1, 'Office', 347.31, 347.31);
-- ERROR 1452 (23000): Cannot add or update a child row: a foreign key
-- constraint fails (`isba_shop`.`order_items`, CONSTRAINT `order_items_ibfk_1`
-- FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`))

-- A value of the wrong type (strict mode):
INSERT INTO stores VALUES ('abc', 'Retail', 'USA');
-- ERROR 1366 (HY000): Incorrect integer value: 'abc' for column 'store_id' at row 1

SELECT COUNT(*) AS stores FROM stores;                               -- 50 (nothing saved)
-- (Lab 1b has students break the other constraints themselves.)


-- ---------------------------------------------------------------------
-- Part 5 · Terminal A — DECIMAL is exact
-- ---------------------------------------------------------------------
SELECT category, SUM(sales_amount) AS revenue
FROM order_items
GROUP BY category
ORDER BY revenue DESC
LIMIT 3;
-- Clothing | 26607217.96
-- Toys     | 25909756.51
-- Office   | 25160829.12
-- The same query in DuckDB (DOUBLE, from the CSV) prints 26607217.960000124.


-- ---------------------------------------------------------------------
-- Part 6 · Terminal A — the same SQL on another engine
-- ---------------------------------------------------------------------
SELECT s.country,
       ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM stores s
JOIN orders o       ON o.store_id  = s.store_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY s.country
ORDER BY revenue DESC;
-- USA 42738573.55 · Australia 42106400.08 · France 38831155.02 ·
-- UK 26898706.48 · Canada 23446005.44 · Germany 19679705.56
-- Identical in DuckDB. Now show a dialect difference:
SELECT EXTRACT(YEAR FROM order_date) AS yr, COUNT(*) AS n_orders
FROM orders
GROUP BY ALL
ORDER BY yr;
-- ERROR 1064 (42000): You have an error in your SQL syntax; ... near 'ALL ORDER BY yr'
-- (GROUP BY ALL is DuckDB-only; GROUP BY yr works on both.)


-- ---------------------------------------------------------------------
-- Part 7 · A creates a view, B uses it
-- ---------------------------------------------------------------------

-- Terminal A
CREATE VIEW v_country_revenue AS
SELECT s.country,
       ROUND(SUM(oi.sales_amount), 2) AS revenue
FROM stores s
JOIN orders o       ON o.store_id  = s.store_id
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY s.country;

-- Terminal B — the view lives on the server, so every client can use it
SELECT * FROM v_country_revenue ORDER BY revenue DESC LIMIT 3;
-- USA 42738573.55 · Australia 42106400.08 · France 38831155.02

-- Terminal A — clean up (Lab 1b builds its own view)
DROP VIEW v_country_revenue;


-- ---------------------------------------------------------------------
-- Part 8 · Terminal A — the server describes itself
-- ---------------------------------------------------------------------
SELECT table_name, table_rows
FROM information_schema.tables
WHERE table_schema = 'isba_shop'
ORDER BY table_name;
-- orders shows an ESTIMATE (97604 on the verification run; yours may differ)

SELECT COUNT(*) AS real_count FROM orders;                           -- 100000
-- table_rows is an estimate for InnoDB tables; COUNT(*) is the truth.

-- End of demo. Close both terminals with: exit
