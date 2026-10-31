"""
repair_encoding.py — Undo the double-encoding damage in books.csv and users.csv.

THE PROBLEM
-----------
3.2% of the lines in books.csv contain text like:

    Der illustrierte Mann. ErzÃÂ¤hlungen.        (should be: Erzählungen)
    El guardiÃ¡n entre el centeno                 (should be: guardián)
    LÃ?Â¼bbe                                      (should be: Lübbe)

This is classic *mojibake*. At some point in the file's history, UTF-8 bytes
were decoded as Latin-1 and then re-encoded as UTF-8 — twice. Each round trip
expands one accented character into two or four bytes of garbage.

A second, separate injury happened afterwards: a lossy conversion replaced the
C1 control byte 0x83 with a literal '?' (0x3F). That is why some sequences read
'Ã?Â¼' rather than 'ÃÂ¼'.

THE REPAIR
----------
1. At the BYTE level, restore the destroyed control byte: b'\\xc3\\x3f' -> b'\\xc3\\x83'.
2. Decode as Latin-1 to get the mojibake text.
3. Apply `text.encode('latin-1').decode('utf-8')` repeatedly until the text
   stops changing or stops being valid. Each pass peels off one encoding layer;
   this file needs two.

Result: 8,004 of 8,669 damaged lines (92.3%) are fully recovered. The remaining
665 lines (0.24% of the file) lost bytes permanently in the lossy conversion and
cannot be recovered by any means — they are left as-is rather than guessed at.

WHY A SEPARATE FILE INSTEAD OF EDITING IN PLACE
-----------------------------------------------
The originals in data/ stay untouched so the damage remains inspectable — a
student should be able to see the "before". Repaired copies are written
alongside as *.utf8.csv and are gitignored, since they are reproducible output
rather than source data.

USAGE
-----
    python repair_encoding.py           # write data/books.utf8.csv, data/users.utf8.csv
    python repair_encoding.py --force   # rewrite even if they already exist
    python repair_encoding.py --report  # show what would change, write nothing
"""

import argparse
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# ratings.csv is pure ASCII and needs no repair.
TARGETS = ["books.csv", "users.csv"]

MOJIBAKE_MARKERS = ("Ã", "Â")


def repair_text(s, max_passes=3):
    """Peel off successive layers of UTF-8-decoded-as-Latin-1 damage."""
    for _ in range(max_passes):
        if not any(m in s for m in MOJIBAKE_MARKERS):
            break
        try:
            candidate = s.encode("latin-1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            break          # irreparable — leave the line as it stands
        if candidate == s:
            break
        s = candidate
    return s


def is_stale(src, out):
    """
    True if `out` needs rebuilding — it is missing, or `src` has changed since.

    This check matters more than it looks. The build notebook reads the *.utf8.csv
    copies, never the originals. Skipping regeneration purely because the output
    exists means that appending rows to a source CSV (inject_duplicates.py,
    inject_unrated.py) has no effect on the database, and nothing errors — the
    build just quietly uses yesterday's data.
    """
    return (not out.exists()) or src.stat().st_mtime > out.stat().st_mtime


def load_lines(path):
    """Read a source CSV, restoring the '?'-clobbered control byte first."""
    raw = path.read_bytes().replace(b"\xc3\x3f", b"\xc3\x83")
    return raw.decode("latin-1").split("\r\n")


def process(path, write=True):
    lines = load_lines(path)
    damaged = [i for i, l in enumerate(lines)
               if any(m in l for m in MOJIBAKE_MARKERS)]

    repaired = list(lines)
    fixed = 0
    for i in damaged:
        r = repair_text(lines[i])
        repaired[i] = r
        if not any(m in r for m in MOJIBAKE_MARKERS):
            fixed += 1

    out_path = path.with_suffix(".utf8.csv")
    if write:
        out_path.write_text("\r\n".join(repaired), encoding="utf-8")

    return {
        "source": path.name,
        "output": out_path.name,
        "total_lines": len(lines),
        "damaged_lines": len(damaged),
        "fully_repaired": fixed,
        "still_damaged": len(damaged) - fixed,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true",
                    help="rewrite outputs even if they already exist")
    ap.add_argument("--report", action="store_true",
                    help="report what would change without writing")
    args = ap.parse_args()

    print(f"{'source':<12} {'lines':>10} {'damaged':>9} {'repaired':>9} {'residual':>9}")
    print("-" * 54)

    for name in TARGETS:
        src = DATA_DIR / name
        out = src.with_suffix(".utf8.csv")

        if not is_stale(src, out) and not (args.force or args.report):
            print(f"{name:<12} {'-- up to date, skipping --':>48}")
            continue

        r = process(src, write=not args.report)
        print(f"{r['source']:<12} {r['total_lines']:>10,} {r['damaged_lines']:>9,} "
              f"{r['fully_repaired']:>9,} {r['still_damaged']:>9,}")

    if args.report:
        print("\n(--report: nothing was written)")


if __name__ == "__main__":
    main()
