#!/usr/bin/env bash
#
# build_books_db.sh — build books.duckdb from the raw Book-Crossing CSVs.
#
# Runs the whole pipeline in the required order:
#
#     inject_duplicates.py  ->  inject_unrated.py  ->  build_database.py
#
# Order matters. inject_duplicates.py samples rows at random from whatever is in
# the file, so running it after inject_unrated.py could duplicate a synthetic row.
#
# Usage:
#     ./build_books_db.sh              build (safe to re-run; injectors self-guard)
#     ./build_books_db.sh --clean      restore pristine CSVs first, then build
#     ./build_books_db.sh --verify     build, then run integrity checks
#     ./build_books_db.sh --clean --verify
#     ./build_books_db.sh --help
#
# Exits non-zero on the first failure, so it is safe to chain or use in CI.

set -euo pipefail

# Always operate on this script's own directory, whatever the caller's cwd is.
cd "$(dirname "${BASH_SOURCE[0]}")"

SOURCE_DIR="../../datasets/books_dataset"
CSVS=(books.csv users.csv ratings.csv)
DB="books.duckdb"

CLEAN=0
VERIFY=0

for arg in "$@"; do
    case "$arg" in
        --clean)  CLEAN=1 ;;
        --verify) VERIFY=1 ;;
        -h|--help)
            sed -n '3,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *)
            echo "Unknown option: $arg" >&2
            echo "Try: $0 --help" >&2
            exit 2 ;;
    esac
done

step() { printf '\n\033[1m==> %s\033[0m\n' "$1"; }
fail() { printf '\033[31mERROR:\033[0m %s\n' "$1" >&2; exit 1; }

# ── Prerequisites ────────────────────────────────────────────────────────────

command -v python3 >/dev/null || fail "python3 not found on PATH."

python3 - <<'PY' || fail "Missing Python packages. Run: pip install \"duckdb>=2.0\" marimo pandas matplotlib"
import importlib.util, sys
missing = [m for m in ("duckdb", "marimo", "pandas", "matplotlib")
           if importlib.util.find_spec(m) is None]
if missing:
    print("missing:", ", ".join(missing), file=sys.stderr)
    sys.exit(1)
PY

# ── Optional clean slate ─────────────────────────────────────────────────────

if [[ $CLEAN -eq 1 ]]; then
    step "Restoring pristine CSVs from $SOURCE_DIR"

    for f in "${CSVS[@]}"; do
        [[ -f "$SOURCE_DIR/$f" ]] || fail "Source file not found: $SOURCE_DIR/$f"
    done

    # data/*.csv also removes the generated *.utf8.csv copies — they end in .csv
    # too, and build_database.py regenerates them.
    rm -f data/*.csv ./*_injected.json "$DB"
    for f in "${CSVS[@]}"; do
        cp "$SOURCE_DIR/$f" data/
    done
    echo "Restored ${#CSVS[@]} files; removed manifests and $DB."
fi

# ── Check the inputs exist ───────────────────────────────────────────────────

for f in "${CSVS[@]}"; do
    [[ -f "data/$f" ]] || fail "data/$f not found.
Re-run with --clean to copy the three CSVs from $SOURCE_DIR,
or copy them into data/ yourself."
done

# ── Pipeline ─────────────────────────────────────────────────────────────────

step "1/3  Injecting duplicate rows (20 users, 30 books, 50 ratings)"
python3 inject_duplicates.py

step "2/3  Injecting unrated records (5 users, 10 books)"
python3 inject_unrated.py

step "3/3  Building $DB"
python3 build_database.py

# ── Optional verification ────────────────────────────────────────────────────

if [[ $VERIFY -eq 1 ]]; then
    step "Verifying database integrity"
    python3 - <<'PY' || fail "Integrity checks did not pass."
import duckdb, sys

con = duckdb.connect("books.duckdb", read_only=True)
checks = [
    ("books PK unique",
     "SELECT COUNT(*) = COUNT(DISTINCT isbn) FROM books"),
    ("users PK unique",
     "SELECT COUNT(*) = COUNT(DISTINCT user_id) FROM users"),
    ("ratings PK unique",
     "SELECT COUNT(*) = COUNT(DISTINCT (user_id, isbn)) FROM ratings"),
    ("no orphan books in ratings",
     "SELECT COUNT(*) = 0 FROM ratings r "
     "WHERE NOT EXISTS (SELECT 1 FROM books b WHERE b.isbn = r.isbn)"),
    ("no orphan users in ratings",
     "SELECT COUNT(*) = 0 FROM ratings r "
     "WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = r.user_id)"),
    ("is_explicit agrees with rating",
     "SELECT COUNT(*) = 0 FROM ratings WHERE is_explicit <> (rating > 0)"),
    ("5 synthetic users present, unrated",
     "SELECT (SELECT COUNT(*) FROM users WHERE user_id >= 900001) = 5 "
     "AND (SELECT COUNT(*) FROM ratings WHERE user_id >= 900001) = 0"),
    ("10 synthetic books present, unrated",
     "SELECT (SELECT COUNT(*) FROM books WHERE isbn LIKE 'ISBA2402%') = 10 "
     "AND (SELECT COUNT(*) FROM ratings WHERE isbn LIKE 'ISBA2402%') = 0"),
]

failed = 0
for label, sql in checks:
    ok = con.execute(sql).fetchall()[0][0]
    print(f"  {'PASS' if ok else 'FAIL'}  {label}")
    failed += not ok

counts = con.execute("""
    SELECT (SELECT COUNT(*) FROM books)            AS books,
           (SELECT COUNT(*) FROM users)            AS users,
           (SELECT COUNT(*) FROM ratings)          AS ratings,
           (SELECT COUNT(*) FROM ratings_orphaned) AS orphaned
""").fetchall()[0]
print(f"\n  books {counts[0]:>10,}\n  users {counts[1]:>10,}"
      f"\n  ratings {counts[2]:>8,}\n  orphaned {counts[3]:>7,}")

sys.exit(1 if failed else 0)
PY
fi

step "Done"
echo "Next:  marimo edit analyze_data.py     (or: marimo run analyze_data.py)"
