"""
inject_duplicates.py — Deliberately corrupt the raw CSVs with exact duplicate rows.

WHY THIS EXISTS
---------------
The Book-Crossing CSVs arrive with clean primary keys: every ISBN in books.csv is
unique, and every User-ID in users.csv is unique. That is convenient but it means
students never have to *find* a duplicate before writing a deduplication query.

This script re-introduces the problem on purpose:

    users.csv     +20 duplicate rows
    books.csv     +30 duplicate rows
    ratings.csv   +50 duplicate rows

The duplicates are byte-for-byte copies of rows already in the file, appended at
the end. That is the hardest kind to spot by eye and the easiest to reason about
in SQL, which is exactly what we want for teaching.

HOW IT WORKS
------------
The files are read in BINARY mode and split on b'\r\n'. This matters:

  * books.csv and users.csv are Latin-1 encoded, not UTF-8. Decoding them to
    str and re-encoding risks mangling characters in author names and city
    names. Copying raw bytes cannot corrupt anything.
  * The files use Windows CRLF line endings. Binary mode preserves them exactly.

A manifest (duplicates_injected.json) records which keys were duplicated so the
build notebook can PROVE the deduplication worked, rather than just asserting it.

USAGE
-----
    python inject_duplicates.py            # inject into data/*.csv
    python inject_duplicates.py --verify   # report current duplicate counts only

Re-running is safe: the script detects rows it already appended and stops rather
than stacking a second round of duplicates on top of the first.
"""

import argparse
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MANIFEST = Path(__file__).parent / "duplicates_injected.json"

# Fixed seed: every student who runs this gets the identical set of duplicates,
# so the row counts in the build notebook and the README always agree.
SEED = 2402

# (filename, how many duplicates to append, which 0-based column is the key)
TARGETS = [
    ("users.csv", 20, 0),    # key = User-ID
    ("books.csv", 30, 0),    # key = ISBN
    ("ratings.csv", 50, [0, 1]),  # key = (User-ID, ISBN) composite
]


def read_lines(path):
    """Read a CSV as raw byte lines, dropping the trailing empty element."""
    raw = path.read_bytes()
    lines = raw.split(b"\r\n")
    if lines and lines[-1] == b"":
        lines.pop()
    return lines


def key_of(line, key_cols):
    """Extract the key from a raw byte line as a plain string."""
    fields = [f.strip(b'"').decode("latin-1") for f in line.split(b";")]
    if isinstance(key_cols, int):
        return fields[key_cols]
    return " | ".join(fields[c] for c in key_cols)


def inject(path, n_dupes, key_cols, rng):
    lines = read_lines(path)
    header, body = lines[0], lines[1:]

    chosen = rng.sample(body, n_dupes)
    keys = [key_of(line, key_cols) for line in chosen]

    # Append the duplicates verbatim, preserving CRLF endings.
    out = b"\r\n".join(lines + chosen) + b"\r\n"
    path.write_bytes(out)

    return {
        "file": path.name,
        "rows_before": len(body),
        "duplicates_added": n_dupes,
        "rows_after": len(body) + n_dupes,
        "duplicated_keys": keys,
    }


def verify(path, key_cols):
    """Count how many rows share a key with an earlier row."""
    lines = read_lines(path)
    seen, dupes = set(), 0
    for line in lines[1:]:
        k = key_of(line, key_cols)
        if k in seen:
            dupes += 1
        seen.add(k)
    return len(lines) - 1, dupes


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verify", action="store_true",
                    help="report duplicate counts without modifying anything")
    args = ap.parse_args()

    if args.verify:
        print(f"{'file':<14} {'rows':>10} {'dupe rows':>10}")
        print("-" * 36)
        for name, _, key_cols in TARGETS:
            rows, dupes = verify(DATA_DIR / name, key_cols)
            print(f"{name:<14} {rows:>10,} {dupes:>10,}")
        return

    # Guard 1 — the manifest. Catches the ordinary "ran it twice" case.
    if MANIFEST.exists():
        print(f"{MANIFEST.name} already exists — duplicates were injected previously.")
        print("Nothing was changed. To start over, restore the CSVs from source:")
        print("  rm -f data/*.csv duplicates_injected.json books.duckdb")
        print("  cp ../../datasets/books_dataset/{books,ratings,users}.csv data/")
        return

    # Guard 2 — the data itself. The manifest can be deleted while the modified
    # CSVs stay in place; without this check that combination would stack a
    # second round of duplicates on top of the first (40/60/100 instead of
    # 20/30/50) and the build's verification counts would stop matching.
    dirty = [(name, dupes)
             for name, _, key_cols in TARGETS
             for _, dupes in [verify(DATA_DIR / name, key_cols)]
             if dupes]
    if dirty:
        print("These files already contain duplicate keys:")
        for name, dupes in dirty:
            print(f"  {name:<14} {dupes:>6,} duplicate rows")
        print("\nNothing was changed — injecting again would stack them.")
        print("Restore the CSVs from source first (see above).")
        return

    rng = random.Random(SEED)
    report = [inject(DATA_DIR / name, n, key_cols, rng)
              for name, n, key_cols in TARGETS]

    MANIFEST.write_text(json.dumps({"seed": SEED, "files": report}, indent=2))

    print(f"{'file':<14} {'before':>10} {'added':>7} {'after':>10}")
    print("-" * 44)
    for r in report:
        print(f"{r['file']:<14} {r['rows_before']:>10,} "
              f"{r['duplicates_added']:>7} {r['rows_after']:>10,}")
    print(f"\nManifest written to {MANIFEST.name}")


if __name__ == "__main__":
    main()
