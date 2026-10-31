# The course dataset in MySQL

[← Course home](../../../README.md) · [Datasets](../../README.md) · **MySQL loader**

`isba_shop_mysql.sql` loads the same 7-table dataset as the CSVs in the parent
folder (`customers`, `products`, `stores`, `orders`, `order_items`, `payments`,
`shipments`) into a MySQL database called **`isba_shop`**, with primary and
foreign keys. Used by the Week 4 and Week 5 MySQL labs.

From the course repository's root folder:

```
# macOS (Terminal)
mysql -u root < datasets/oltp_database/mysql/isba_shop_mysql.sql

# Windows (PowerShell)
cmd /c "mysql -u root -p < datasets\oltp_database\mysql\isba_shop_mysql.sql"
```

It takes a few seconds and ends by printing each table's row count (1,000 /
2,000 / 50 / 100,000 / 300,000 / 100,000 / 100,000). Running it again drops and
rebuilds `isba_shop` from scratch, which is also the way to reset after a lab.

Use the redirect (`<`) shown above rather than `SOURCE`. `SOURCE` works at
the interactive `mysql>` prompt, but recent MySQL clients turn it off when
commands are piped in, so the redirect is the one method that always works.

---

*MSIS-2402 — Database Management Systems - Fundamentals of SQL — Winter 2027*
