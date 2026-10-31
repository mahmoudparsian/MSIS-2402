"""MSIS-2402 — Week 4 · Session 8 — Live demo: a database-backed web app.

Goes with: lecture_slides_02_web_app_architecture.md

Run it from this folder:   python3 demo_02_store_finder.py      (Windows: python ...)
Then open:                 http://localhost:8001                (Ctrl+C to stop)

A "Store Finder" with the three layers every web application has:

  1. USER INTERFACE    — HTML pages (and one JSON endpoint) sent to the browser
  2. APPLICATION LOGIC — Python functions that read the request, check it,
                         run SQL, and build the response (the `handle_*` functions)
  3. DATABASE          — DuckDB holding the course's stores / orders / order_items

Pages:
  /                     home
  /find?country=..&store_type=..   search form (GET) — parameterized SQL
  /store?id=7           one store: details + order count + revenue
                        (try id=abc → 400 Bad Request, id=999 → 404 Not Found)
  /api/stores?country=USA          the same data as JSON, for other programs

The terminal shows every request (method, path, status) and every SQL
statement with its parameters, so you can watch a click become a query.
Only Python's standard library and DuckDB are used.
"""
import html
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import duckdb

# ---------------------------------------------------------------------------
# 3. DATABASE — one connection, opened once when the server starts
# ---------------------------------------------------------------------------
DATA_DIR = (Path(__file__).resolve().parent / "../datasets/oltp_database").resolve()

con = duckdb.connect()
for table in ["stores", "orders", "order_items"]:
    con.execute(f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto('{DATA_DIR / (table + '.csv')}')")


def run_sql(sql, params=None):
    """Run one SQL statement with its parameters, log both, return (columns, rows)."""
    print(f"  [SQL]    {' '.join(sql.split())}\n  [params] {params}", flush=True)
    cur = con.execute(sql, params or [])
    return [d[0] for d in cur.description], cur.fetchall()


class NotFound(Exception):
    """Raised by a handler when the thing asked for doesn't exist (→ HTTP 404)."""


# ---------------------------------------------------------------------------
# 1. USER INTERFACE — HTML building blocks
# ---------------------------------------------------------------------------
def page(title, body):
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<style>
  body {{ font-family: sans-serif; margin: 2rem; max-width: 50rem; }}
  table {{ border-collapse: collapse; margin-top: 1rem; }}
  th, td {{ border: 1px solid #ccc; padding: .3rem .6rem; text-align: left; }}
  nav a {{ margin-right: 1rem; }}
</style></head>
<body>
<nav><a href="/">Home</a><a href="/find">Find stores</a></nav>
<h1>{html.escape(title)}</h1>
{body}
</body></html>"""


def html_table(columns, rows, link_first_column=False):
    if not rows:
        return "<p><em>No stores match.</em></p>"
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in columns)
    lines = []
    for r in rows:
        cells = [html.escape(str(v)) for v in r]
        if link_first_column:
            cells[0] = f'<a href="/store?id={cells[0]}">{cells[0]}</a>'
        lines.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    return f"<p>{len(rows)} store(s)</p><table><tr>{head}</tr>{''.join(lines)}</table>"


OPTION_QUERIES = {   # fixed SQL for each drop-down — never built from user input
    "country":    "SELECT DISTINCT country FROM stores ORDER BY country",
    "store_type": "SELECT DISTINCT store_type FROM stores ORDER BY store_type",
}


def html_options(column, selected):
    """<option>s for a drop-down, filled from the distinct values in the database."""
    _, rows = run_sql(OPTION_QUERIES[column])
    opts = ['<option value="">(any)</option>']
    for (value,) in rows:
        sel = " selected" if value == selected else ""
        opts.append(f"<option{sel}>{html.escape(value)}</option>")
    return "".join(opts)


# ---------------------------------------------------------------------------
# 2. APPLICATION LOGIC — one function per page
# ---------------------------------------------------------------------------
def handle_home(query):
    return page("Store Finder", """
<p>A tiny web application backed by a database.</p>
<ul>
  <li><a href="/find">Find stores</a> by country and type</li>
  <li><a href="/store?id=7">One store's details</a></li>
  <li><a href="/api/stores?country=USA">The same data as JSON</a></li>
</ul>""")


def find_stores(country, store_type):
    """Shared by the HTML page and the JSON API: build and run the search."""
    sql = "SELECT store_id, store_type, country FROM stores WHERE 1 = 1"
    params = []
    if country:
        sql += " AND country = ?"
        params.append(country)
    if store_type:
        sql += " AND store_type = ?"
        params.append(store_type)
    sql += " ORDER BY store_id"
    return run_sql(sql, params)


def handle_find(query):
    country = query.get("country", [""])[0]
    store_type = query.get("store_type", [""])[0]
    columns, rows = find_stores(country, store_type)
    form = f"""
<form method="get" action="/find">
  Country: <select name="country">{html_options("country", country)}</select>
  Type: <select name="store_type">{html_options("store_type", store_type)}</select>
  <button>Search</button>
</form>"""
    return page("Find stores", form + html_table(columns, rows, link_first_column=True))


def handle_store(query):
    raw_id = query.get("id", [""])[0]
    if not raw_id.isdigit():                       # validate BEFORE touching the database
        raise ValueError(f"Store id must be a whole number, got {raw_id!r}")
    store_id = int(raw_id)

    _, rows = run_sql("SELECT store_type, country FROM stores WHERE store_id = ?", [store_id])
    if not rows:
        raise NotFound(f"There is no store {store_id}")
    store_type, country = rows[0]

    _, stats = run_sql("""
        SELECT COUNT(DISTINCT o.order_id)       AS orders,
               ROUND(SUM(oi.sales_amount), 2)   AS revenue
        FROM orders o
        JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.store_id = ?""", [store_id])
    n_orders, revenue = stats[0]
    return page(f"Store {store_id}", f"""
<table>
  <tr><th>Type</th><td>{html.escape(store_type)}</td></tr>
  <tr><th>Country</th><td>{html.escape(country)}</td></tr>
  <tr><th>Orders with line items</th><td>{n_orders:,}</td></tr>
  <tr><th>Revenue</th><td>${revenue:,.2f}</td></tr>
</table>""")


def handle_api_stores(query):
    """Same search as /find, but the 'user interface' is JSON for another program."""
    columns, rows = find_stores(query.get("country", [""])[0], query.get("store_type", [""])[0])
    return [dict(zip(columns, r)) for r in rows]


ROUTES = {                                        # URL path → function
    "/": handle_home,
    "/find": handle_find,
    "/store": handle_store,
    "/api/stores": handle_api_stores,
}


# ---------------------------------------------------------------------------
# The web server: turns each HTTP request into a call to one function above
# ---------------------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        print(f"\n{self.command} {self.path}", flush=True)
        handler = ROUTES.get(url.path)
        try:
            if handler is None:
                raise NotFound(f"No page at {url.path}")
            result = handler(parse_qs(url.query))
            status = 200
        except ValueError as e:
            result, status = page("Bad request", f"<p>{html.escape(str(e))}</p>"), 400
        except NotFound as e:
            result, status = page("Not found", f"<p>{html.escape(str(e))}</p>"), 404

        if isinstance(result, str):
            body, content_type = result, "text/html; charset=utf-8"
        else:
            body, content_type = json.dumps(result, indent=2), "application/json"
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, fmt, *args):            # print the status line our own way
        print(f"  -> {args[1]}", flush=True)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    print(f"Store Finder running on http://localhost:{port}  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
