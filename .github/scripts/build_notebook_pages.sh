#!/usr/bin/env bash
# Render every Marimo notebook in LABS/ and the week folders as a read-only
# HTML page (text, SQL and results), for the "👁️ View" links in the READMEs.
# Plain .py scripts in the week folders get a syntax-colored code page.
#
#   bash .github/scripts/build_notebook_pages.sh [OUT_DIR]      (default: _site)
#
# Run from the repository root. Each notebook is run from its own folder (its
# data paths are relative), and its page keeps the repository path:
#   LABS/week1/session01/x_marimo.py  ->  OUT_DIR/LABS/week1/session01/x_marimo.html
# Only files already in the repository are rendered, so lab solutions appear
# only after release_lab.py has published them. A notebook that fails to run
# is reported and skipped; the others are still published.
# Used by .github/workflows/notebook-pages.yml (GitHub Pages).
set -u
out="${1:-_site}"
root="$(pwd)"
py="${PYTHON:-python3}"
mkdir -p "$out"
case "$out" in /*) dest="$out" ;; *) dest="$root/$out" ;; esac

# The diabetic notebook reads a database that build_database.py creates.
diab="week3_sql_for_analytics/session06_ctes_advanced_analytics/notebook_diabetic"
if [ -d "$diab" ] && [ ! -f "$diab/diabetic_hospitals.duckdb" ]; then
  (cd "$diab" && "$py" build_database.py > /dev/null) || echo "::warning::build_database.py failed in $diab"
fi

ok=0; failed=0
for nb in $(grep -rl --include='*.py' 'marimo.App' LABS week[0-9]_* 2>/dev/null | sort); do
  dir="$(dirname "$nb")"; base="$(basename "$nb" .py)"
  mkdir -p "$dest/$dir"
  had_m=0; [ -d "$dir/__marimo__" ] && had_m=1
  had_p=0; [ -d "$dir/__pycache__" ] && had_p=1
  if (cd "$dir" && "$py" -m marimo export html "$base.py" -o "$dest/$dir/$base.html" > "$dest/.log" 2>&1); then
    echo "ok      $nb"; ok=$((ok + 1))
  else
    echo "::warning::could not render $nb"; sed -n '1,8p' "$dest/.log"; failed=$((failed + 1))
    rm -f "$dest/$dir/$base.html"
  fi
  [ $had_m = 0 ] && rm -rf "$dir/__marimo__"
  [ $had_p = 0 ] && rm -rf "$dir/__pycache__"
done
rm -f "$dest/.log"

# Plain Python scripts in the week folders (not notebooks): a read-only code
# page with syntax colors and line numbers (Pygments).
"$py" - "$dest" <<'EOF'
import html, subprocess, sys
from pathlib import Path
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
site = Path(sys.argv[1])
files = subprocess.run(["git", "ls-files", "week[0-9]_*/*.py", "week[0-9]_*/**/*.py"],
                       capture_output=True, text=True).stdout.split()
fmt = HtmlFormatter(linenos="table", style="friendly")
n = 0
for f in sorted(set(files)):
    src = Path(f).read_text(encoding="utf-8")
    if "marimo.App" in src:
        continue                      # notebooks are rendered by marimo above
    out = site / (f[:-3] + ".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    name = html.escape(Path(f).name)
    out.write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{name} — MSIS-2402</title>
<style>body{{font-family:system-ui,sans-serif;margin:0}}
header{{background:#eef6fb;border-bottom:1px solid #cde3f0;padding:.6rem 1rem;font-size:.9rem}}
main{{padding:1rem;overflow-x:auto}}h1{{font-size:1.2rem;margin:.2rem 0 .8rem}}
.highlight pre,.linenos pre{{margin:0;font-size:.85rem;line-height:1.45}}td.linenos{{color:#999;padding-right:.8rem;user-select:none}}
{fmt.get_style_defs('.highlight')}</style></head><body>
<header>Read-only view of a <b>Python script</b> (not a notebook) · <code>{html.escape(f)}</code> ·
<a href="https://github.com/mahmoudparsian/MSIS-2402/blob/main/{html.escape(f)}">open on GitHub</a></header>
<main><h1>{name}</h1>{highlight(src, PythonLexer(), fmt)}</main></body></html>
""", encoding="utf-8")
    print(f"code    {f}")
    n += 1
print(f"{n} Python scripts shown as code pages")
EOF

# index.html: a list of every page, by folder.
"$py" - "$dest" <<'EOF'
import html, sys
from pathlib import Path
site = Path(sys.argv[1])
pages = sorted(p.relative_to(site).as_posix() for p in site.rglob("*.html") if p.name != "index.html")
groups = {}
for p in pages:
    groups.setdefault(p.rsplit("/", 1)[0], []).append(p)
rows = []
for folder, items in groups.items():
    rows.append(f"<h2>{html.escape(folder)}/</h2><ul>")
    rows += [f'<li><a href="{html.escape(p)}">{html.escape(p.rsplit("/", 1)[1][:-5])}.py</a></li>' for p in items]
    rows.append("</ul>")
(site / "index.html").write_text(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>MSIS-2402 notebooks</title>
<style>body{{font-family:system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;line-height:1.5}}
h2{{font-size:1rem;margin-top:1.5rem}}code{{font-size:.95em}}</style></head><body>
<h1>MSIS-2402 — Marimo notebooks (read-only view)</h1>
<p>Each page shows a notebook with its text, SQL and results. To run or edit a notebook, download it from the
<a href="https://github.com/mahmoudparsian/MSIS-2402">course repository</a> and open it with
<code>marimo edit</code> from its own folder.</p>
{''.join(rows)}
</body></html>
""", encoding="utf-8")
EOF

echo "$ok notebooks rendered, $failed failed -> $out"
