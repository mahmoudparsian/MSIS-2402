CREATE TABLE customers(
 customer_id INT,
 gender TEXT,
 country TEXT,
 customer_segment TEXT,
 signup_date DATE
);

CREATE TABLE products(
 product_id INT,
 category TEXT,
 price DOUBLE
);

CREATE TABLE orders(
 order_id INT,
 customer_id INT,
 order_date DATE
);

CREATE TABLE order_items(
 order_item_id INT,
 order_id INT,
 product_id INT,
 quantity INT,
 category TEXT,
 price DOUBLE,
 sales_amount DOUBLE
);
