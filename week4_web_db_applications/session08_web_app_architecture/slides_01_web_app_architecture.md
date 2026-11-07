---
marp: true
title: Week 4 — Web Application Architecture
theme: default
paginate: true
style: |
  h2 {
    background: linear-gradient(90deg, #2c3e50, #4ca1af);
    color: white;
    padding: 10px 18px;
    border-radius: 6px;
    width: fit-content;
  }
  h3 {
    background: #ecf0f1;
    padding: 6px 10px;
    border-radius: 4px;
  }
  pre code {
    font-size: 20px;
  }
  table {
    font-size: 22px;
  }
---

# 🌐 Week 4 — Web Application Architecture

Session 8 · How a click in a browser becomes a SQL query — and back

MSIS-2402 — Database Management Systems: Fundamentals of SQL

---

# 🎯 Learning Objectives

By the end of today you can:

* Name the **three layers** of a web application and what each one owns
* Read a **URL**, an HTTP **request**, and an HTTP **response**
* Explain how an HTML **form** turns into request data (`GET` vs. `POST`)
* Follow application code from **route** → **SQL** → **HTML**
* Explain why SQL values are sent as **parameters** (`?`), not pasted in
* Decide which work belongs in the **database** and which in the app

---

# 🔁 Where We Are

Session 7: a **server** owns the data; **clients** connect and send SQL.

```
  you ──> mysql client ──SQL──> MySQL server
```

Today: the client is **a program** — a web application — and the person
using it never writes SQL at all.

```
  shopper ──> browser ──HTTP──> web application ──SQL──> database
```

---

## The Three Layers

```
  1. USER INTERFACE           2. APPLICATION LOGIC          3. DATABASE
  (browser: HTML page)        (Python on a server)          (MySQL, DuckDB, ...)

            ── HTTP request ──>             ──── SQL ────>
            <── HTTP response ──            <─── rows ────
```

* **User interface** — what people see and click
* **Application logic** — decides what to do, checks input, runs SQL
* **Database** — stores the data and enforces its rules

---

# 🧩 Who Owns What

| | User interface | Application logic | Database |
|---|---|---|---|
| Runs on | the user's device | a server | a server |
| Holds the data? | only what's on screen | only during one request | **yes — permanently** |
| Speaks | HTML, clicks, forms | Python (or Java, JS, …) | SQL |
| Can the user change it? | **yes, completely** | no | no |

👉 Anything the browser "checks" can be bypassed — the user controls it.
Real rules live in the **application** and the **database**.

---

# 🖱️ One Click, Start to Finish

A shopper searches the Store Finder for **Retail** stores in the **USA**:

1. The **browser** turns the form into a URL and sends an HTTP **request**
2. The **web server** receives it and calls the function for that **path**
3. The **application** reads `country` and `store_type` from the request
4. It sends **SQL + parameters** to the **database**
5. The database returns **rows** (5 stores)
6. The application turns the rows into **HTML**
7. The **response** goes back; the browser draws the page

👉 Every click repeats all seven steps. HTTP itself remembers nothing between requests.

---

## Anatomy of a URL

```
http://localhost:8001/find?country=USA&store_type=Retail
└─┬┘   └───┬───┘ └┬─┘└─┬─┘ └──────────────┬──────────────┘
scheme   host    port path           query string
```

| Part | Meaning |
|---|---|
| `http` | the protocol (`https` = encrypted) |
| `localhost` | which machine — here, your own |
| `8001` | which program on that machine |
| `/find` | which page — the app maps it to a function |
| `?country=USA&store_type=Retail` | the inputs: `name=value` pairs joined by `&` |

---

## An HTTP Request (real, captured with `curl -v`)

```
GET /find?country=USA&store_type=Retail HTTP/1.1
Host: 127.0.0.1:8001
User-Agent: curl/8.7.1
Accept: */*
```

* **Method** `GET` — "give me this page"
* **Path + query string** — what page, with which inputs
* **Headers** — `Name: value` lines describing the request
* It is just **text** sent over the network

---

## An HTTP Response

```
HTTP/1.0 200 OK
Server: BaseHTTP/0.6 Python/3.13.2
Content-Type: text/html; charset=utf-8

<!doctype html>
<html><head><meta charset="utf-8"><title>Find stores</title>
...
<p>5 store(s)</p><table><tr><th>store_id</th><th>store_type</th> ...
```

* **Status line** — `200 OK` means it worked
* **`Content-Type`** — what kind of body follows (HTML here)
* **Body** — the page itself; the browser draws it

---

# 🚦 Status Codes You'll Meet

| Code | Meaning | In the Store Finder demo |
|---|---|---|
| **200** OK | it worked | `/store?id=7` |
| **400** Bad Request | the input is invalid | `/store?id=abc` |
| **404** Not Found | no such page or thing | `/store?id=999`, `/nope` |
| **500** Internal Server Error | the app crashed | — (not in the demo: an unhandled bug) |
| **501** Not Implemented | method not supported | a `POST` to this GET-only app |

👉 **4xx** = the request's fault. **5xx** = the server's fault.

---

## HTML Forms → Request Data

```html
<form method="get" action="/find">
  Country: <select name="country"> <option>USA</option> ... </select>
  Type:    <select name="store_type"> <option>Retail</option> ... </select>
  <button>Search</button>
</form>
```

Clicking **Search** sends:

```
GET /find?country=USA&store_type=Retail
```

* `action` → the **path**
* each field's `name` → a **`name=value`** pair
* `method` → **`GET`** (fields go in the URL) or **`POST`**

---

# 📮 `GET` vs. `POST`

| | `GET` | `POST` |
|---|---|---|
| Used for | **reading**: search, view a page | **changing data**: add, update, buy |
| Fields travel in | the URL's query string | the request **body** |
| Bookmarkable / shareable | yes | no |
| Safe to repeat? | yes — nothing changes | no — may add a second row |

A `POST` request (captured with `curl -v`; the body is the last line):

```
POST /add_product HTTP/1.1
Content-Length: 25
Content-Type: application/x-www-form-urlencoded

category=Toys&price=24.99
```

---

# 🔣 Special Characters in URLs

A value like **`Côte d'Ivoire`** can't go in a URL as-is. The browser
**encodes** it:

```
country=C%C3%B4te+d%27Ivoire
```

| Character | Sent as |
|---|---|
| space | `+` (or `%20`) |
| `'` apostrophe | `%27` |
| `ô` | `%C3%B4` |

The application **decodes** it back to `Côte d'Ivoire` before using it —
apostrophe and all. Remember that apostrophe.

---

## The Server Side: Routing

Every web framework has a table from **path** to **function**:

```python
ROUTES = {                      # URL path → function
    "/":           handle_home,
    "/find":       handle_find,
    "/store":      handle_store,
    "/api/stores": handle_api_stores,
}
```

* A request for `/find?...` calls `handle_find(query)`
* A path that isn't in the table → **404**
* Adding a page = write a function + add one line here

---

# 📥 Reading the Request: Everything Is Text

```python
from urllib.parse import parse_qs

parse_qs("country=USA&store_type=Retail")
# {'country': ['USA'], 'store_type': ['Retail']}

parse_qs("id=7")        # {'id': ['7']}          ← the TEXT '7'
parse_qs("price=24.99") # {'price': ['24.99']}   ← the TEXT '24.99'
```

👉 The app must **convert** (`int(...)`, `float(...)`) and **check** values.
Compared as text, `'499.93' <= '50'` is *true* — Class Discussion 2 found
1,804 "cheap" products instead of 154.

---

# ✅ Validate Before You Query

```python
def handle_store(query):
    raw_id = query.get("id", [""])[0]
    if not raw_id.isdigit():                      # check first
        raise ValueError(f"Store id must be a whole number, got {raw_id!r}")
    store_id = int(raw_id)
    _, rows = run_sql("SELECT store_type, country FROM stores WHERE store_id = ?",
                      [store_id])
    if not rows:
        raise NotFound(f"There is no store {store_id}")
    ...
```

The server's log for `/store?id=abc`:

```
GET /store?id=abc
  -> 400                  ← no SQL was run at all
```

---

## Talking to the Database: SQL + Parameters

```python
sql = "SELECT store_id, store_type, country FROM stores WHERE 1 = 1"
params = []
if country:
    sql += " AND country = ?"
    params.append(country)
if store_type:
    sql += " AND store_type = ?"
    params.append(store_type)
run_sql(sql, params)
```

What the database receives (from the app's log):

```
[SQL]    SELECT store_id, store_type, country FROM stores
         WHERE 1 = 1 AND country = ? AND store_type = ? ORDER BY store_id
[params] ['USA', 'Retail']
```

👉 The **query** and the **values** travel **separately**.

---

# ⚠️ Why Not Just Paste the Text In?

```python
sql = f"SELECT store_id, store_type, country FROM stores WHERE country = '{country}'"
```

With `country = "Côte d'Ivoire"` the database receives:

```sql
SELECT store_id, store_type, country FROM stores WHERE country = 'Côte d'Ivoire'
```

```
Parser Error: unterminated string literal
```

* The apostrophe in the **data** ended the string in the **SQL**
* With a parameter (`country = ?`) the same search runs fine — and finds 0 stores
* If one character can break the query, what could a **whole sentence** do?
  → Session 8 Lab B

---

# 📤 Rows → HTML

```python
def html_table(columns, rows):
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in r) + "</tr>"
        for r in rows)
    return f"<table><tr>{head}</tr>{body}</table>"
```

* The database returns **rows**; the app writes **HTML** around them
* `html.escape(...)` turns `<` `>` `&` `'` `"` into safe codes, so data is
  shown **as text**, never run as part of the page:
  `<b>Tom & Jerry's</b>` → `&lt;b&gt;Tom &amp; Jerry&#x27;s&lt;/b&gt;`

---

## Same Data, Different Interface: a JSON API

`GET /api/stores?country=Germany` → `Content-Type: application/json`

```json
[
  { "store_id": 4,  "store_type": "Online",    "country": "Germany" },
  { "store_id": 22, "store_type": "Retail",    "country": "Germany" },
  { "store_id": 25, "store_type": "Warehouse", "country": "Germany" },
  ...
]
```

* Same function, same SQL as the HTML page — only the **output** differs
* Mobile apps, other websites, and dashboards read JSON, not HTML
* One application layer can serve **many** user interfaces

---

# 🏋️ Where Should the Work Happen?

Revenue by category for a dashboard:

| Approach | Rows sent from database to app |
|---|---:|
| `SELECT *` from `order_items`, add up in Python | 300,000 |
| `SUM(...) ... GROUP BY category` in SQL | 8 |

Order counts for 1,000 customers:

| Approach | Queries per page view |
|---|---:|
| one query for the list + one per customer | 1,001 |
| one `LEFT JOIN ... GROUP BY` | 1 |

👉 Let the **database** do set work. Every round trip costs time once the
database is on another machine.

---

# 🏗️ From Demo to Production

| Our demo | A real web application |
|---|---|
| Python's built-in `http.server` | a **framework**: Flask, Django, FastAPI, Node.js, … |
| DuckDB inside the app | **MySQL / PostgreSQL** on its own server |
| one connection | a **pool** of reusable connections |
| `http://localhost` | **`https://`** — encrypted |
| one process on a laptop | many app servers behind a load balancer |

👉 The three layers, the request → SQL → response cycle, and parameters
are **exactly the same**.

---

# 🧪 The Live Demo: Store Finder

From the course repository's root folder:

```
cd week4_web_db_applications/session08_web_app_architecture
python3 demo_01_store_finder.py          (Windows: python demo_01_store_finder.py)
```

Open **http://localhost:8001** and watch the terminal:

* `/find` — choose a country and type → see the `[SQL]` and `[params]`
* `/store?id=7` → 1,905 orders with line items, $3,794,230.77 revenue
* `/store?id=abc` → **400**, no SQL run · `/store?id=999` → **404**
* `/api/stores?country=Germany` → the same data as **JSON**

---

# 🔁 Recap

* Three layers: **user interface**, **application logic**, **database**
* HTTP is text: a **request** (method, path, query, headers) and a
  **response** (status, headers, body)
* Forms become `name=value` pairs — in the URL (`GET`) or the body (`POST`)
* Everything from the browser is **text**: convert and **validate** it
* Send values as **parameters**, never pasted into SQL
* Push set work into **SQL**; keep round trips few

---

# 🧪 Today's Labs

**Session 8 Lab A — Inside a database-backed web application**
Run the ISBA Shop app, follow one request from browser to SQL, map the code to
the three layers, then add a feature and a new page yourself.

**Session 8 Lab B — Attacking and fixing a web app** *(challenge)*
See what pasted-in SQL really allows, fix it, and add a form that **writes**
to the database safely.

Next week: **transactions** — what happens when many users write at once.
