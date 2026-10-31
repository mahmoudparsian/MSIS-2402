"""
inject_unrated.py — Append users who never rate and books nobody rates.

WHY THIS EXISTS
---------------
Anti-join queries ("find the rows in A with no match in B") are a core SQL skill,
and they are much easier to teach when you can point at specific rows and say
"these five, exactly these, should come back".

The Book-Crossing data already contains plenty of unrated records — 186,750 users
with no ratings and 1,209 books with none. So the anti-join queries in the analysis
notebook would return results with or without this script. What this script adds is
**traceability**: 5 users and 10 books with recognisable synthetic keys that a
student can verify by eye.

    5 users   user_id 900001-900005      (max real user_id is 278,858)
    10 books  isbn ISBA2402001-...010    ('ISBA' prefix has zero collisions)

No rows are added to ratings.csv, so these records are unrated by construction.

RUN ORDER
---------
    python inject_duplicates.py     # first
    python inject_unrated.py        # second
    python build_database.py

Duplicates first, because `inject_duplicates.py` samples rows at random from
whatever is in the file; running it afterwards could pick one of these synthetic
rows and duplicate it, which would be confusing rather than wrong.

Both scripts are individually idempotent and refuse to double-apply.

USAGE
-----
    python inject_unrated.py           # append the records
    python inject_unrated.py --verify  # report presence, write nothing
"""

import argparse
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MANIFEST = Path(__file__).parent / "unrated_injected.json"

# Deliberately far above the real maximum (278,858) so they are unmistakable.
USERS = [
    (900001, "santa clara, california, usa", 21),
    (900002, "lisbon, lisboa, portugal", 34),
    (900003, "kyoto, kansai, japan", None),      # missing age, like 40% of real users
    (900004, "cork, munster, ireland", 58),
    (900005, "valparaiso, valparaiso, chile", None),
]

# 'ISBA' prefix: zero collisions with the 271,379 real ISBNs.
# Years stay inside 1376-2004 so the CHECK constraint on books accepts them.
BOOKS = [
    ("ISBA2402001", "Field Notes on Relational Algebra",       "M. Parsian",        1998, "Broncos Press"),
    ("ISBA2402002", "The Quiet Shelf: Essays on Reading",      "H. Aldridge",       2001, "Mission Street Books"),
    ("ISBA2402003", "Cartography of Small Rivers",             "P. Nakamura",       1994, "Coastal Editions"),
    ("ISBA2402004", "An Index of Forgotten Trades",            "R. Okonkwo",        1987, "Lantern House"),
    ("ISBA2402005", "Winter Term",                             "S. Vasquez",        2003, "Alameda Books"),
    ("ISBA2402006", "Notes Toward a Theory of Catalogues",     "T. Lindqvist",      1979, "Northgate Academic"),
    ("ISBA2402007", "The Unread Library",                      "A. Ferrante",       2000, "Palo Alto Review Press"),
    ("ISBA2402008", "Grammars of Silence",                     "K. Osei",           1992, "Meridian & Co"),
    ("ISBA2402009", "Sixteen Ways to Leave a Dataset",         "J. Whitfield",      2004, "Broncos Press"),
    ("ISBA2402010", "Marginalia",                              "E. Sorensen",       1968, "Old Quarry Books"),
]

IMG = "http://images.amazon.com/images/P/{isbn}.01.{size}ZZZZZZZ.jpg"


def read_lines(path):
    raw = path.read_bytes()
    lines = raw.split(b"\r\n")
    if lines and lines[-1] == b"":
        lines.pop()
    return lines


def q(value):
    """Quote a field the way the source files do; bare NULL for missing values."""
    return "NULL" if value is None else f'"{value}"'


def user_row(user_id, location, age):
    return ";".join([q(user_id), q(location), q(age)])


def book_row(isbn, title, author, year, publisher):
    return ";".join([
        q(isbn), q(title), q(author), q(year), q(publisher),
        q(IMG.format(isbn=isbn, size="THUMB")),
        q(IMG.format(isbn=isbn, size="M")),
        q(IMG.format(isbn=isbn, size="L")),
    ])


def present(path, keys, col=0):
    """How many of `keys` already appear in column `col` of the file."""
    found = set()
    for line in read_lines(path)[1:]:
        fields = [f.strip(b'"').decode("latin-1") for f in line.split(b";")]
        if len(fields) > col and fields[col] in keys:
            found.add(fields[col])
    return found


def append(path, rows):
    lines = read_lines(path)
    out = b"\r\n".join(lines + [r.encode("latin-1") for r in rows]) + b"\r\n"
    path.write_bytes(out)
    return len(lines) - 1, len(rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true",
                    help="report whether the records are present; write nothing")
    args = ap.parse_args()

    user_keys = {str(u[0]) for u in USERS}
    book_keys = {b[0] for b in BOOKS}

    found_users = present(DATA_DIR / "users.csv", user_keys)
    found_books = present(DATA_DIR / "books.csv", book_keys)

    if args.verify:
        print(f"{'file':<12} {'expected':>9} {'present':>8}")
        print("-" * 32)
        print(f"{'users.csv':<12} {len(USERS):>9} {len(found_users):>8}")
        print(f"{'books.csv':<12} {len(BOOKS):>9} {len(found_books):>8}")
        return

    # Guard 1 — the manifest.
    if MANIFEST.exists():
        print(f"{MANIFEST.name} already exists — records were injected previously.")
        print("Nothing was changed. To start over, restore the CSVs from source:")
        print("  rm -f data/*.csv *_injected.json books.duckdb")
        print("  cp ../../datasets/books_dataset/{books,ratings,users}.csv data/")
        return

    # Guard 2 — the data. Catches a deleted manifest with modified CSVs still
    # in place, which would otherwise append a second copy and break the primary
    # keys the build notebook is about to declare.
    if found_users or found_books:
        print("These synthetic keys are already in the CSVs:")
        if found_users:
            print(f"  users.csv  {len(found_users)} of {len(USERS)} user_ids")
        if found_books:
            print(f"  books.csv  {len(found_books)} of {len(BOOKS)} isbns")
        print("\nNothing was changed — appending again would duplicate them.")
        print("Restore the CSVs from source first (see above).")
        return

    u_before, u_added = append(DATA_DIR / "users.csv",
                               [user_row(*u) for u in USERS])
    b_before, b_added = append(DATA_DIR / "books.csv",
                               [book_row(*b) for b in BOOKS])

    MANIFEST.write_text(json.dumps({
        "users": [{"user_id": u[0], "location": u[1], "age": u[2]} for u in USERS],
        "books": [{"isbn": b[0], "title": b[1], "author": b[2],
                   "year": b[3], "publisher": b[4]} for b in BOOKS],
    }, indent=2))

    print(f"{'file':<12} {'before':>10} {'added':>7} {'after':>10}")
    print("-" * 42)
    print(f"{'users.csv':<12} {u_before:>10,} {u_added:>7} {u_before + u_added:>10,}")
    print(f"{'books.csv':<12} {b_before:>10,} {b_added:>7} {b_before + b_added:>10,}")
    print(f"\nNo ratings added — these records are unrated by construction.")
    print(f"Manifest written to {MANIFEST.name}")


if __name__ == "__main__":
    main()
