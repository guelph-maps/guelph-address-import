"""Feed a campaign's batches to JOSM one at a time, and verify each upload.

    python upload_loop.py <campaign-dir> <first> <last>

For each batch not already in uploads.csv: load it into JOSM through Remote
Control, wait for the operator to press Upload, find the closed changeset by
its "(N/TOTAL)" / "[batch N/TOTAL]" comment, and run verify_changeset.py on
it. The next batch is loaded only after the previous one verified; any
failure stops the loop. Nothing here uploads — the operator's click does.
"""
from __future__ import annotations

import csv
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
POLL_S = 10


def say(msg: str) -> None:
    print(time.strftime("%H:%M:%S"), msg, flush=True)


def recorded(camp: Path) -> set[int]:
    f = camp / "uploads.csv"
    if not f.exists():
        return set()
    return {int(r["batch"]) for r in csv.DictReader(open(f, encoding="utf-8"))}


def load(path: Path) -> None:
    url = ("http://127.0.0.1:8111/open_file?filename="
           + urllib.parse.quote(str(path), safe=""))
    with urllib.request.urlopen(url, timeout=60) as r:
        body = r.read().decode().strip()
    if body != "OK":
        raise RuntimeError(f"JOSM refused {path.name}: {body}")


def main() -> None:
    camp = Path(sys.argv[1]).resolve()
    first, last = int(sys.argv[2]), int(sys.argv[3])
    for n in range(first, last + 1):
        if n in recorded(camp):
            say(f"batch {n}: already recorded, skipping")
            continue
        found = sorted((camp / "batches").glob(f"{n:02d}-*.osm"))
        if len(found) != 1:
            # A rebuild that renumbers leaves the old files behind; loading the
            # wrong one put flats-pairs' batch 5 object up as batch 2.
            sys.exit(f"batch {n}: expected one file, found {[p.name for p in found]}")
        path = found[0]
        load(path)
        say(f"batch {n}: LOADED {path.name} — press Upload in JOSM")
        while True:
            time.sleep(POLL_S)
            r = subprocess.run(
                [sys.executable, str(HERE / "verify_changeset.py"), str(camp), str(n)],
                capture_output=True, text=True)
            out = (r.stdout + r.stderr).strip()
            if r.returncode == 0:
                say(f"batch {n}: VERIFIED " + out.splitlines()[-1])
                break
            if "no changeset by" in out or "still open" in out:
                continue  # not uploaded yet
            say(f"batch {n}: FAILED\n{out}")
            sys.exit(1)
    say(f"DONE batches {first}-{last}")


if __name__ == "__main__":
    main()
