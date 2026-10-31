
import argparse, os, random, datetime
import pandas as pd
import numpy as np

def generate(seed, size, out_dir):
    random.seed(seed)
    np.random.seed(seed)

    profiles = {
        "small":  {"customers":200, "products":500,  "orders":10000},
        "medium": {"customers":1000,"products":2000, "orders":100000},
        "large":  {"customers":10000,"products":5000,"orders":1000000}
    }

    profile = profiles[size]
    n_customers = profile["customers"]
    n_products = profile["products"]
    n_orders = profile["orders"]
    n_items = int(n_orders*3)

    start = datetime.date(2021,1,1)
    end = datetime.date(2024,12,31)
    def rand_date():
        delta = (end-start).days
        return start + datetime.timedelta(days=random.randint(0,delta))

    # customers
    countries = ["USA","Canada","UK","Germany","France","Australia"]
    genders = ["Male","Female","Other"]
    segments = ["Consumer","Small Business","Corporate","VIP"]

    customers = pd.DataFrame({
        "customer_id": range(1,n_customers+1),
        "gender": np.random.choice(genders,n_customers),
        "country": np.random.choice(countries,n_customers),
        "customer_segment": np.random.choice(segments,n_customers,p=[0.7,0.15,0.1,0.05]),
        "signup_date":[rand_date() for _ in range(n_customers)]
    })

    # products
    categories = ["Electronics","Computers","Home","Office","Sports","Clothing","Beauty","Toys"]
    products = pd.DataFrame({
        "product_id": range(1,n_products+1),
        "category": np.random.choice(categories,n_products),
        "price": np.round(np.random.uniform(10,500,n_products),2)
    })

    # orders
    orders = pd.DataFrame({
        "order_id": range(1,n_orders+1),
        "customer_id": np.random.randint(1,n_customers+1,n_orders),
        "order_date":[rand_date() for _ in range(n_orders)]
    })

    # order items
    items = pd.DataFrame({
        "order_item_id": range(1,n_items+1),
        "order_id": np.random.randint(1,n_orders+1,n_items),
        "product_id": np.random.randint(1,n_products+1,n_items),
        "quantity": np.random.randint(1,5,n_items)
    })

    items = items.merge(products,on="product_id")
    items["sales_amount"] = items["quantity"] * items["price"]

    # save CSV
    os.makedirs(out_dir,exist_ok=True)
    customers.to_csv(os.path.join(out_dir,"customers.csv"),index=False)
    products.to_csv(os.path.join(out_dir,"products.csv"),index=False)
    orders.to_csv(os.path.join(out_dir,"orders.csv"),index=False)
    items.to_csv(os.path.join(out_dir,"order_items.csv"),index=False)

    # schema
    schema = """
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
"""
    with open(os.path.join(out_dir,"schema.sql"),"w") as f:
        f.write(schema)

    # SQL inserts from CSV
    def csv_to_sql(csv_file,table):
        df=pd.read_csv(csv_file)
        lines=[]
        for _,r in df.iterrows():
            vals=",".join([repr(x) for x in r])
            lines.append(f"INSERT INTO {table} VALUES ({vals});")
        return "\n".join(lines)

    data_sql = ""
    for t in ["customers","products","orders","order_items"]:
        data_sql += csv_to_sql(os.path.join(out_dir,f"{t}.csv"),t) + "\n"

    with open(os.path.join(out_dir,"data.sql"),"w") as f:
        f.write(data_sql)

    # reset script
    reset = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

.read schema.sql
.read data.sql
"""
    with open(os.path.join(out_dir,"reset_duckdb.sql"),"w") as f:
        f.write(reset)

    verify = """
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;
"""
    with open(os.path.join(out_dir,"verify_dataset.sql"),"w") as f:
        f.write(verify)

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--size",default="medium")
    parser.add_argument("--seed",default=2026,type=int)
    parser.add_argument("--out",default="nova_dataset")
    args=parser.parse_args()
    generate(args.seed,args.size,args.out)
