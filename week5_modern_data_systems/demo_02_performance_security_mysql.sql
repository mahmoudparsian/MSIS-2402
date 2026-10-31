-- =====================================================================
-- MSIS-2402 · Week 5 · Session 10 — Live demo: performance, security, backup
-- Goes with: lecture_slides_02_performance_security_governance.md
-- =====================================================================
--
-- Setup: the isba_shop database from Week 4 (reload it any time, from the
-- course repository's root folder):
--   macOS:    mysql -u root < datasets/oltp_database/mysql/isba_shop_mysql.sql
--   Windows:  cmd /c "mysql -u root -p < datasets\oltp_database\mysql\isba_shop_mysql.sql"
--
-- Terminal A (root):      mysql -u root isba_shop        (Windows: add -p)
-- Terminal B (from Part 2, as the application's account — see below)
--
-- Expected output is in the comments (verified on MySQL 26.7.0; timings are
-- from the verification machine and will differ on yours). The demo uses
-- the SHIPMENTS table and an APPLICATION account, so it doesn't repeat
-- Lab 2a (orders.order_date) or Lab 2b (the analyst account). It puts
-- isba_shop back exactly as it found it.
--
-- ⚠  Run it statement by statement — NEVER as a whole script. Part 3
--    deliberately tries DELETE / UPDATE / DROP TABLE as an account that is
--    NOT allowed to; run as root, those statements would really do it.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Part 1 · Terminal A — query plans and an index
-- ---------------------------------------------------------------------
-- How many shipments were delivered on 30 June 2024?
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';   -- 71

EXPLAIN FORMAT=TREE
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';
-- -> Aggregate: count(0)
--     -> Filter: (shipments.delivery_date = DATE'2024-06-30')
--         -> Table scan on shipments  (rows≈100000 — an estimate)

EXPLAIN ANALYZE
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';
-- -> Aggregate: count(0)  (actual time=7.42..7.42 rows=1)
--     -> Filter: ...  (actual ... rows=71)
--         -> Table scan on shipments  (actual ... rows=100000)
-- Read 100,000 rows to find 71.

CREATE INDEX idx_shipments_delivery_date ON shipments(delivery_date);

EXPLAIN ANALYZE
SELECT COUNT(*) FROM shipments WHERE delivery_date = '2024-06-30';
-- -> Aggregate: count(0)  (actual time=0.0132..0.0133 rows=1)
--     -> Covering index lookup on shipments using idx_shipments_delivery_date
--        (delivery_date = DATE'2024-06-30')  (actual ... rows=71)
-- Read 71 index entries. Same answer.

-- Selectivity: the optimizer uses the index only when it pays off.
-- (Selecting whole rows, so the index alone can't answer the query.)
EXPLAIN FORMAT=TREE
SELECT shipment_id, carrier FROM shipments WHERE delivery_date = '2024-06-30';
-- -> Index lookup on shipments using idx_shipments_delivery_date   (rows=71)

EXPLAIN FORMAT=TREE
SELECT shipment_id, carrier FROM shipments WHERE delivery_date >= '2024-12-01';
-- -> Index range scan on shipments using idx_shipments_delivery_date ...  (rows=2293)

EXPLAIN FORMAT=TREE
SELECT shipment_id, carrier FROM shipments WHERE delivery_date >= '2021-01-01';
-- -> Filter: (shipments.delivery_date >= DATE'2021-01-01')
--     -> Table scan on shipments  (rows≈100000 — an estimate)
-- Every row matches (deliveries run 2021-01-02 .. 2025-01-05): the index is ignored.

-- Clean up
DROP INDEX idx_shipments_delivery_date ON shipments;


-- ---------------------------------------------------------------------
-- Part 2 · Terminal A (root) — an account for the web application
-- ---------------------------------------------------------------------
CREATE USER 'shop_app'@'localhost' IDENTIFIED BY 'ShopApp#2402';
GRANT SELECT         ON isba_shop.products    TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.orders      TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.order_items TO 'shop_app'@'localhost';
GRANT SELECT, INSERT ON isba_shop.payments    TO 'shop_app'@'localhost';
GRANT SELECT (customer_id, country) ON isba_shop.customers TO 'shop_app'@'localhost';

SHOW GRANTS FOR 'shop_app'@'localhost';
-- GRANT USAGE ON *.* TO `shop_app`@`localhost`
-- GRANT SELECT (`country`, `customer_id`) ON `isba_shop`.`customers` TO `shop_app`@`localhost`
-- GRANT SELECT, INSERT ON `isba_shop`.`order_items` TO `shop_app`@`localhost`
-- GRANT SELECT, INSERT ON `isba_shop`.`orders` TO `shop_app`@`localhost`
-- GRANT SELECT, INSERT ON `isba_shop`.`payments` TO `shop_app`@`localhost`
-- GRANT SELECT ON `isba_shop`.`products` TO `shop_app`@`localhost`


-- ---------------------------------------------------------------------
-- Part 3 · Terminal B — log in AS the application (over TCP)
--   mysql -u shop_app -p -h 127.0.0.1 isba_shop        (password: ShopApp#2402)
-- ⚠  Check the next line says shop_app@localhost BEFORE going on: as root,
--    the "denied" statements below would really delete, update, and drop.
-- ---------------------------------------------------------------------
SELECT CURRENT_USER();                                       -- shop_app@localhost
SHOW TABLES;            -- customers, order_items, orders, payments, products
                        -- (no shipments, no stores: not granted, not even visible)

-- What the app needs — allowed:
SELECT product_id, category, price FROM products WHERE product_id = 1;  -- 1 | Office | 347.31
INSERT INTO orders VALUES (100001, 42, 7, '2026-10-04');                -- Query OK, 1 row affected
SELECT customer_id, country FROM customers WHERE customer_id = 42;      -- 42 | UK

-- What it doesn't need — denied:
SELECT customer_id, gender FROM customers WHERE customer_id = 42;
-- ERROR 1143 (42000): SELECT command denied to user 'shop_app'@'localhost'
--                     for column 'gender' in table 'customers'
DELETE FROM orders WHERE order_id = 100001;
-- ERROR 1142 (42000): DELETE command denied to user 'shop_app'@'localhost' for table 'orders'
UPDATE products SET price = 0.01 WHERE product_id = 1;
-- ERROR 1142 (42000): UPDATE command denied ... for table 'products'
DROP TABLE orders;
-- ERROR 1142 (42000): DROP command denied ... for table 'orders'

-- Is this connection encrypted?
SHOW SESSION STATUS LIKE 'Ssl_cipher';                       -- TLS_AES_128_GCM_SHA256

-- Terminal B: exit


-- ---------------------------------------------------------------------
-- Part 4 · Terminal A (root) — clean up
-- ---------------------------------------------------------------------
DELETE FROM orders WHERE order_id = 100001;
DROP USER 'shop_app'@'localhost';
SELECT COUNT(*) FROM orders;                                          -- 100000


-- ---------------------------------------------------------------------
-- Part 5 · In a SHELL (not at the mysql> prompt) — back up, then PROVE it restores
-- ---------------------------------------------------------------------
-- 1. Back up the database to a file:
--      mysqldump -u root --single-transaction --set-gtid-purged=OFF isba_shop > isba_shop_backup.sql
--    (about 25.5 MB, 7 CREATE TABLEs; 0.2 s on the verification machine)
--
--    Without those two flags this MySQL version prints warnings — and the
--    dump then FAILS to restore on the same server:
--      ERROR 3546 (HY000) at line 24: @@GLOBAL.GTID_PURGED cannot be changed:
--      the added gtid set must not overlap with @@GLOBAL.GTID_EXECUTED
--    (--single-transaction = a consistent snapshot while the shop keeps writing)
--
-- 2. Restore into a NEW database (never test over the real one):
--      mysql -u root -e "CREATE DATABASE isba_shop_restore"
--      mysql -u root isba_shop_restore < isba_shop_backup.sql      (about 2.4 s)
--
-- 3. Compare (back at the mysql> prompt):
SELECT 'isba_shop' AS db,
       (SELECT COUNT(*) FROM isba_shop.orders)                  AS orders,
       (SELECT COUNT(*) FROM isba_shop.order_items)             AS order_items,
       (SELECT ROUND(SUM(sales_amount), 2) FROM isba_shop.order_items) AS revenue
UNION ALL
SELECT 'isba_shop_restore',
       (SELECT COUNT(*) FROM isba_shop_restore.orders),
       (SELECT COUNT(*) FROM isba_shop_restore.order_items),
       (SELECT ROUND(SUM(sales_amount), 2) FROM isba_shop_restore.order_items);
-- isba_shop          | 100000 | 300000 | 193700546.13
-- isba_shop_restore  | 100000 | 300000 | 193700546.13

-- 4. Clean up:
DROP DATABASE isba_shop_restore;
--      and delete isba_shop_backup.sql from your shell.

-- End of demo.
