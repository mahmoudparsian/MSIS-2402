-- =====================================================================
-- MSIS-2402 · Week 5 · Session 9 — Live demo: transactions and isolation
-- Goes with: lecture_slides_01_transactions_modern_data.md
-- =====================================================================
--
-- Setup: the isba_shop database from Week 4 (reload it any time, from the
-- course repository's root folder):
--   macOS:    mysql -u root < datasets/oltp_database/mysql/isba_shop_mysql.sql
--   Windows:  cmd /c "mysql -u root -p < datasets\oltp_database\mysql\isba_shop_mysql.sql"
--
-- Open TWO terminal windows and connect in both:
--   mysql -u root isba_shop          (Windows: mysql -u root -p isba_shop)
--
-- Run each block in the terminal named in its header, one statement at a
-- time. Expected output is in the comments (verified on MySQL 26.7.0 with
-- two live sessions). Nothing here makes a session WAIT for a lock — that
-- is Lab 1b's job. The demo puts isba_shop back exactly as it found it.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Part 1 · Terminal A — autocommit is on
-- ---------------------------------------------------------------------
SELECT @@autocommit;                                                  -- 1
-- Every statement is its own transaction and is saved the moment it succeeds.


-- ---------------------------------------------------------------------
-- Part 2 · Isolation: nobody sees your work until you COMMIT
-- ---------------------------------------------------------------------

-- Terminal A
START TRANSACTION;
UPDATE customers SET segment = 'VIP' WHERE customer_id = 42;
SELECT customer_id, segment FROM customers WHERE customer_id = 42;   -- 42 | VIP

-- Terminal B — answers immediately (readers don't wait), and sees the OLD value
SELECT customer_id, segment FROM customers WHERE customer_id = 42;   -- 42 | Consumer

-- Terminal A — change of mind
ROLLBACK;
SELECT customer_id, segment FROM customers WHERE customer_id = 42;   -- 42 | Consumer

-- Terminal A — this time keep it
START TRANSACTION;
UPDATE customers SET segment = 'VIP' WHERE customer_id = 42;
COMMIT;

-- Terminal B — now everyone sees it
SELECT customer_id, segment FROM customers WHERE customer_id = 42;   -- 42 | VIP

-- Terminal A — put it back (autocommit)
UPDATE customers SET segment = 'Consumer' WHERE customer_id = 42;


-- ---------------------------------------------------------------------
-- Part 3 · A consistent snapshot for a reader (REPEATABLE READ, the default)
-- ---------------------------------------------------------------------

-- Terminal B — an analyst starts a "report"
START TRANSACTION;
SELECT COUNT(*) AS orders_seen_by_B FROM orders;                      -- 100000

-- Terminal A — a new order arrives (autocommit: saved immediately)
INSERT INTO orders VALUES (100001, 42, 7, '2026-10-04');
SELECT COUNT(*) AS orders_seen_by_A FROM orders;                      -- 100001

-- Terminal B — still inside its transaction: the report's numbers don't shift
SELECT COUNT(*) AS orders_seen_by_B FROM orders;                      -- 100000
COMMIT;
SELECT COUNT(*) AS orders_seen_by_B FROM orders;                      -- 100001

-- Terminal A — clean up
DELETE FROM orders WHERE order_id = 100001;


-- ---------------------------------------------------------------------
-- Part 4 · A checkout as one unit of work — and a failure in the middle
-- ---------------------------------------------------------------------

-- Terminal A — order, line item, payment ... but the payment is invalid
START TRANSACTION;
INSERT INTO orders      VALUES (100001, 42, 7, '2026-10-04');                  -- OK
INSERT INTO order_items VALUES (300001, 100001, 1, 2, 'Office', 347.31, 694.62); -- OK
INSERT INTO payments    VALUES (100001, 100001, NULL, '2026-10-04', 694.62);
-- ERROR 1048 (23000): Column 'payment_method' cannot be null

-- Terminal A — MySQL undid ONLY the failed statement; the rest is still pending
SELECT (SELECT COUNT(*) FROM orders      WHERE order_id = 100001) AS order_row,
       (SELECT COUNT(*) FROM order_items WHERE order_id = 100001) AS item_rows,
       (SELECT COUNT(*) FROM payments    WHERE order_id = 100001) AS payment_rows;
-- 1 | 1 | 0      ← an order with no payment, if we COMMITted now

-- Terminal B — none of it is visible outside A's transaction
SELECT COUNT(*) AS order_100001_seen_by_B FROM orders WHERE order_id = 100001;  -- 0

-- Terminal A — so the application must ROLLBACK on any error
ROLLBACK;
SELECT (SELECT COUNT(*) FROM orders      WHERE order_id = 100001) AS order_row,
       (SELECT COUNT(*) FROM order_items WHERE order_id = 100001) AS item_rows,
       (SELECT COUNT(*) FROM payments    WHERE order_id = 100001) AS payment_rows;
-- 0 | 0 | 0

-- Terminal A — the complete, valid checkout
START TRANSACTION;
INSERT INTO orders      VALUES (100001, 42, 7, '2026-10-04');
INSERT INTO order_items VALUES (300001, 100001, 1, 2, 'Office', 347.31, 694.62);
INSERT INTO payments    VALUES (100001, 100001, 'Credit Card', '2026-10-04', 694.62);
COMMIT;

-- Terminal B — all three rows appear together
SELECT o.order_id, oi.sales_amount, p.payment_method, p.payment_amount
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
JOIN payments p     ON p.order_id  = o.order_id
WHERE o.order_id = 100001;
-- 100001 | 694.62 | Credit Card | 694.62


-- ---------------------------------------------------------------------
-- Cleanup · Terminal A — children first (foreign keys), as one unit
-- ---------------------------------------------------------------------
START TRANSACTION;
DELETE FROM payments    WHERE order_id = 100001;
DELETE FROM order_items WHERE order_id = 100001;
DELETE FROM orders      WHERE order_id = 100001;
COMMIT;

SELECT (SELECT COUNT(*) FROM orders)      AS orders,
       (SELECT COUNT(*) FROM order_items) AS order_items,
       (SELECT COUNT(*) FROM payments)    AS payments;
-- 100000 | 300000 | 100000

-- End of demo. Close both terminals with: exit
