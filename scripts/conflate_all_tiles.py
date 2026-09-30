"""Run the gap-fill conflation over every tile, in this process, writing only
to the local tool.db.

This is `t2.run_for_all` without the process pool: same four stages per tile
(ingest -> fetch -> conflate -> checks), one tile at a time, no subprocesses.
It does not authenticate to OSM and it does not upload — uploading is a
per-batch human action in the web UI, which is the promise the wiki page and
forum post #14 both make.

    python scripts/conflate_all_tiles.py [--limit N] [--only SUBSTRING]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

CITY_DIR = Path(__file__).resolve().parent.parent
ENGINE = CITY_DIR.parent / "address-importer-friend"

os.environ.setdefault("T2_CITY_DIR", str(CITY_DIR))
sys.path.insert(0, str(ENGINE))

import t2.config  # noqa: E402

t2.config.OSM_ENV = "prod"  # which OSM the *extract* describes; nothing uploads

from t2 import pipeline  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0, help="stop after N tiles")
    ap.add_argument("--only", default="", help="only tiles whose id/name contains this")
    args = ap.parse_args()

    cfg = t2.config.load()
    layer = json.loads((cfg.data_dir / "tiles.json").read_text(encoding="utf-8"))
    stamp = time.strftime("%Y%m%d")

    todo = []
    for t in layer["tiles"]:
        tid, name = str(t["id"]), str(t.get("name") or t["id"])
        if args.only and args.only.lower() not in (tid + " " + name).lower():
            continue
        todo.append((tid, name, t))
    if args.limit:
        todo = todo[:args.limit]

    print(f"{len(todo)} tiles to process", flush=True)
    totals: dict[str, int] = {}
    t0 = time.time()
    for i, (tid, name, t) in enumerate(todo, 1):
        # Deterministic name, as run_for_all uses, so a re-run resumes.
        run_name = f"{tid}-batch-{stamp}"
        run_id = pipeline.start_run(
            run_name,
            bbox=tuple(t["bbox"]),
            polygon_latlon=t.get("polygon_latlon"),
        )
        pipeline.ingest_stage(run_id)
        osm_hash = pipeline.fetch_stage(run_id)
        counts = pipeline.conflate_stage(run_id, osm_hash)
        pipeline.run_checks(run_id)
        for k, v in counts.items():
            totals[k] = totals.get(k, 0) + int(v)
        print(f"  [{i}/{len(todo)}] {name}: "
              + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
              flush=True)

    print(f"\ndone in {time.time() - t0:.0f}s")
    print("totals: " + ", ".join(f"{k}={v}" for k, v in sorted(totals.items())))


if __name__ == "__main__":
    main()
