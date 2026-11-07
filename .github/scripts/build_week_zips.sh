#!/usr/bin/env bash
# Build the ZIP downloads for students who do not use git.
#
#   Week ZIPs — one per week folder:
#     week1_db_concepts_sql_fundamentals.zip
#     └── MSIS-2402-week1_db_concepts_sql_fundamentals/
#         ├── week1_db_concepts_sql_fundamentals/   ← the week folder
#         └── datasets/oltp_database/               ← the shared data the notebooks read
#
#   Lab ZIPs — one per session already released into LABS/ (none before the term):
#     session01-labs.zip
#     └── MSIS-2402-session01-labs/
#         ├── LABS/week1_lab1/                      ← exactly what is in LABS/week1_lab1/ now
#         └── datasets/oltp_database/
#
# Both keep the repository's own folder layout, so every relative data path
# (../../datasets/oltp_database/..., ../part1_single_table_sql/data/...) works unchanged.
#
# Run from the repo root. GitHub Actions runs it on a fresh checkout, so only
# tracked files go into the ZIPs — gitignored files (CLAUDE.md, *.duckdb) never do.
#
# Usage: .github/scripts/build_week_zips.sh [output_dir]   (default: dist)
set -euo pipefail

out="${1:-dist}"
mkdir -p "$out"
out="$(cd "$out" && pwd)"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT

DATA="datasets/oltp_database"

# pack <top_folder_name> <zip_name> <path>...   (paths are repo-relative)
pack() {
  local top="$1" name="$2"; shift 2
  rm -rf "${stage:?}/$top"
  mkdir -p "$stage/$top"
  for p in "$@" "$DATA"; do
    mkdir -p "$stage/$top/$(dirname "$p")"
    cp -R "$p" "$stage/$top/$p"
  done
  rm -f "$out/$name.zip"
  (cd "$stage" && zip -rqX "$out/$name.zip" "$top" \
      -x '*/.DS_Store' '*/__pycache__/*' '*/__marimo__/*' '*.duckdb' '*.duckdb.wal' '*/CLAUDE.md')
  echo "built $name.zip"
}

for wk in week[1-5]_*/; do
  wk="${wk%/}"
  pack "MSIS-2402-$wk" "$wk" "$wk"
done

# Session number: weekW_labL -> 2*(W-1)+L  (week1_lab1 = Session 1 … week5_lab2 = Session 10)
for lab in LABS/week[1-5]_lab[12]/; do
  [ -d "$lab" ] || continue
  lab="${lab%/}"
  b="$(basename "$lab")"
  w="${b:4:1}"; l="${b:9:1}"
  n=$(printf '%02d' $(( 2 * (w - 1) + l )))
  pack "MSIS-2402-session$n-labs" "session$n-labs" "$lab"
done
