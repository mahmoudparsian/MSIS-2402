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
#         ├── LABS/week1/session01/                 ← exactly what is in LABS/week1/session01/ now
#         └── datasets/oltp_database/
#
# Both keep the repository's own folder layout, so every relative data path
# (../../datasets/oltp_database/..., ../session01_single_table_sql/data/...) works unchanged.
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

# One ZIP per released session folder: LABS/week1/session01/ -> session01-labs.zip
for lab in LABS/week[1-5]/session[01][0-9]/; do
  [ -d "$lab" ] || continue
  lab="${lab%/}"
  n="$(basename "$lab")"          # session01 … session10
  pack "MSIS-2402-$n-labs" "$n-labs" "$lab"
done
