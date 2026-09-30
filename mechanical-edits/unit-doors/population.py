"""Who is in edit 6: every live OSM object carrying `addr:flats` whose civic
group the engine's classifier (verdicts applied) does not call `collapse`.

Reads shapes from `unit_shapes.collect()` -- the whole group from the source,
never the per-run candidates table, which is tile-cut and can read a tower as
two rows of doors.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CITY_DIR = HERE.parents[1]
ENGINE = CITY_DIR.parent / "address-importer-friend"
os.environ.setdefault("T2_CITY_DIR", str(CITY_DIR))
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(HERE.parent))

import t2.config  # noqa: E402
t2.config.OSM_ENV = "prod"
t2.config.load()
from t2 import unit_shapes  # noqa: E402

import _common  # noqa: E402

LIVE = HERE / "live_flats.osm"
QUERY = (f"[out:xml][timeout:900];area({_common.AREA_ID})->.g;"
         'nwr(area.g)["addr:flats"];out meta center;')


def fetch_flats(refetch: bool) -> list[dict]:
    root = _common.fetch_live(QUERY, LIVE, refetch, "every addr:flats object")
    els = []
    for el in root:
        if el.tag not in ("node", "way", "relation"):
            continue
        c = el.find("center")
        src = c if c is not None else el
        els.append({
            "type": el.tag, "id": int(el.get("id")), "version": int(el.get("version")),
            "center": {"lat": float(src.get("lat")), "lon": float(src.get("lon"))},
            "tags": _common.element_tags(el),
        })
    return els


def norm(s: str) -> str:
    return " ".join(str(s or "").lower().split())


def population(refetch: bool = False) -> list[dict]:
    data = unit_shapes.collect()
    by_civic = {(norm(r["number"]), norm(r["street"])): r for r in data["rows"]}
    out = []
    for el in fetch_flats(refetch):
        t = el.get("tags", {})
        row = by_civic.get((norm(t.get("addr:housenumber")), norm(t.get("addr:street"))))
        c = el.get("center") or el
        out.append({
            "type": el["type"], "id": el["id"], "version": el["version"],
            "lat": c.get("lat"), "lon": c.get("lon"),
            "housenumber": t.get("addr:housenumber"), "street": t.get("addr:street"),
            "flats": t.get("addr:flats"), "tags": t,
            "shape": row["shape"] if row else "no-source-group",
            "reason": row.get("reason") or row.get("rule_reason") if row else "",
            "key": row["key"] if row else None,
        })
    return out


if __name__ == "__main__":
    import collections
    pop = population("--refetch" in sys.argv)
    print(len(pop), "live objects with addr:flats")
    print(collections.Counter(p["shape"] for p in pop))
    groups = collections.defaultdict(set)
    for p in pop:
        groups[p["shape"]].add(p["key"])
    print({k: len(v) for k, v in groups.items()}, "civic groups")
