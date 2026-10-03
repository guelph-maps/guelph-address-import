"""How many civics are split across several `addr:flats` objects, one per
stack of suites, the way 5 Gordon Street is.

ARandomThumbtack's 2025 import placed one node per City point, and the City
puts every suite of a vertical column on the same point, so a tower arrived as
a ring of nodes each listing `x01;x02;...` up its floors. A column of flats is
not something a node can mean; the shape our own classifier wants for a
floor-coded tower is one civic object with the whole list.

Prints the population and writes survey.csv. Builds nothing.
"""
from __future__ import annotations

import collections
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "unit-doors"))
sys.path.insert(0, str(HERE.parent / "flats-hygiene"))
sys.path.insert(0, str(HERE.parent))

import population as pop_mod  # noqa: E402  (sets up the engine path and config)
from flats_parse import normalise, parse_flats  # noqa: E402
import _common  # noqa: E402

VERTEX_CACHE = HERE / "live_vertex_ways.osm"
VERTEX_QUERY = (f"[out:xml][timeout:900];area({_common.AREA_ID})->.g;"
                'node(area.g)["addr:flats"]->.f;way(bn.f);out meta;')


def vertex_ways(refetch: bool) -> dict[int, list[tuple[int, dict]]]:
    """Listing node id -> the ways it is a vertex of, with their tags."""
    root = _common.fetch_live(VERTEX_QUERY, VERTEX_CACHE, refetch,
                              "ways through addr:flats nodes")
    out: dict[int, list[tuple[int, dict]]] = collections.defaultdict(list)
    for w in root.iter("way"):
        tags = _common.element_tags(w)
        for nd in w.iter("nd"):
            out[int(nd.get("ref"))].append((int(w.get("id")), tags))
    return out


def main() -> None:
    refetch = "--refetch" in sys.argv
    pop = pop_mod.population(refetch)
    vways = vertex_ways(refetch)

    by_civic: dict[tuple, list[dict]] = collections.defaultdict(list)
    for p in pop:
        by_civic[(p["housenumber"], p["street"])].append(p)

    split = {k: v for k, v in by_civic.items() if len(v) >= 2}
    rows = []
    for (num, street), objs in sorted(split.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        units: list[str] = []
        unparsed = []
        for o in objs:
            got = parse_flats(o["flats"])
            if got is None:
                unparsed.append(f"{o['type'][0]}{o['id']}")
            else:
                units.extend(got)
        merged, why = normalise(";".join(sorted(set(units)))) if units else (None, "nothing parsed")
        nodes = [o for o in objs if o["type"] == "node"]
        on_outline = sum(1 for o in nodes
                         if any("building" in t for _, t in vways.get(o["id"], [])))
        dupes = len(units) - len(set(units))
        rows.append({
            "housenumber": num, "street": street,
            "shape": objs[0]["shape"],
            "objects": len(objs), "nodes": len(nodes),
            "ways": sum(1 for o in objs if o["type"] != "node"),
            "nodes_on_building_outline": on_outline,
            "units": len(set(units)), "duplicate_units": dupes,
            "merged_len": len(merged) if merged else "",
            "merged_flats": merged or "", "merge_note": why if not merged else "",
            "unparsed": " ".join(unparsed),
            "ids": " ".join(f"{o['type'][0]}{o['id']}" for o in objs),
        })

    with open(HERE / "survey.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(len(pop), "addr:flats objects;", len(by_civic), "civics;",
          len(split), "civics split across 2+ objects,",
          sum(r["objects"] for r in rows), "objects")
    print("by shape:", collections.Counter(r["shape"] for r in rows))
    print("objects per civic:", sorted(collections.Counter(r["objects"] for r in rows).items()))
    print("civics with nodes on a building outline:",
          sum(1 for r in rows if r["nodes_on_building_outline"]),
          "| such nodes:", sum(r["nodes_on_building_outline"] for r in rows))
    print("civics with a unit listed twice:", sum(1 for r in rows if r["duplicate_units"]))
    print("merged list over 255:", sum(1 for r in rows if r["merged_len"] and r["merged_len"] > 255),
          "| unmergeable:", sum(1 for r in rows if not r["merged_flats"]))
    for r in rows[:25]:
        print(f"  {r['objects']:3} {r['housenumber']} {r['street']} [{r['shape']}] "
              f"units={r['units']} outline={r['nodes_on_building_outline']} len={r['merged_len']}")


if __name__ == "__main__":
    main()
