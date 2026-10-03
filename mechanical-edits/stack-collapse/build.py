"""5 Gordon Street: fold the per-stack `addr:flats` nodes into the building.

ARandomThumbtack's 2025 import left 13 nodes here, one per vertical column of
suites (`100;200;...;600`), because the City geocodes a whole column to one
point. A column is not something a node can mean, and on survey (skfd,
2026-10-02) none of them is an entrance. Our classifier calls the civic
`collapse`, so its shape is one object listing every suite: the building way
already carries `addr:housenumber=5`, so the merged list goes there and the
nodes go. Seven of them are vertices of the outline; they come out of its node
list, after checking that each sits on the straight edge between its
neighbours, so the footprint does not move.

survey.py found no other civic in this shape (2026-10-02). Reads live from the
API and writes 5-gordon-street.osm for JOSM. Uploads nothing.
"""
from __future__ import annotations

import json
import math
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "flats-hygiene"))
sys.path.insert(0, str(HERE.parent))

from flats_parse import normalise, parse_flats  # noqa: E402
import _common  # noqa: E402

API = "https://api.openstreetmap.org/api/0.6/"
WAY = 413398801
STACKS = list(range(13150618368, 13150618381))
POIS = {9793948572, 9793948573, 9793948574}   # Balzac's, Rica, Cut Bar: untouched
OUT = HERE / "5-gordon-street.osm"
MAX_OFF_EDGE_M = 0.5
COMMENT = ("5 Gordon Street: merge the per-stack addr:flats nodes into one "
           "listing on the building; a column of suites is not a place, and "
           "none of these nodes is an entrance (survey)")


def get(path: str) -> ET.Element:
    req = urllib.request.Request(API + path, headers={"User-Agent": _common.UA})
    with urllib.request.urlopen(req, timeout=60) as res:
        return ET.fromstring(res.read())


def off_edge_m(p, a, b) -> float:
    """Distance of p from segment a-b, metres, on a local flat projection."""
    k = math.cos(math.radians(p[0])) * 111_320
    def xy(q): return ((q[1] - p[1]) * k, (q[0] - p[0]) * 110_540)
    (ax, ay), (bx, by) = xy(a), xy(b)
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, -(ax * dx + ay * dy) / (dx * dx + dy * dy)))
    return math.hypot(ax + t * dx, ay + t * dy)


def main() -> None:
    full = get(f"way/{WAY}/full")
    way = full.find("way")
    coords = {int(n.get("id")): (float(n.get("lat")), float(n.get("lon")))
              for n in full.iter("node")}
    stacks = {int(n.get("id")): n for n in
              get("nodes?nodes=" + ",".join(map(str, STACKS))).iter("node")}
    assert set(stacks) == set(STACKS), "a stack node is gone or was never there"

    units: list[str] = []
    for nid, n in stacks.items():
        tags = _common.element_tags(n)
        extra = set(tags) - {"addr:city", "addr:flats", "addr:housenumber",
                             "addr:postcode", "addr:street"}
        assert not extra, f"n{nid} carries more than an address: {extra}"
        assert (tags["addr:housenumber"], tags["addr:street"]) == ("5", "Gordon Street"), nid
        units += parse_flats(tags["addr:flats"])
        # No other way and no relation may lose this node from under it.
        others = {int(w.get("id")) for w in get(f"node/{nid}/ways").iter("way")} - {WAY}
        assert not others, f"n{nid} is also in ways {others}"
        assert not list(get(f"node/{nid}/relations").iter("relation")), f"n{nid} is in a relation"
    assert len(units) == len(set(units)), "a suite is listed on two stacks"
    flats, why = normalise(";".join(units))
    assert flats and len(flats) <= 255, why
    assert set(parse_flats(flats)) == set(units), "the merge lost or invented a suite"

    refs = [int(nd.get("ref")) for nd in way.findall("nd")]
    ring = refs[:-1]                           # closed: last ref repeats the first
    keep = [r for r in ring if r not in stacks]
    for i, r in enumerate(ring):
        if r not in stacks:
            continue
        j = i
        while ring[j % len(ring)] in stacks: j -= 1
        prev = ring[j % len(ring)]
        j = i
        while ring[j % len(ring)] in stacks: j += 1
        nxt = ring[j % len(ring)]
        d = off_edge_m(coords[r], coords[prev], coords[nxt])
        assert d <= MAX_OFF_EDGE_M, f"n{r} is {d:.2f} m off the edge; removing it moves the outline"
        print(f"  vertex n{r}: {d:.2f} m off the edge n{prev}-n{nxt}")
    new_refs = keep + [keep[0]]

    wtags = _common.element_tags(way)
    assert "addr:flats" not in wtags, "the building already lists flats; look first"
    wtags["addr:flats"] = flats

    out = ET.Element("osm", {"version": "0.6", "generator": "guelph-stack-collapse"})
    cs = ET.SubElement(out, "changeset")
    for k, v in {"comment": COMMENT, "source": "survey;Guelph Open Data",
                 "source:license": "OGL-Canada-2.0", "mechanical": "no",
                 "import_plan": _common.WIKI_SECTION}.items():
        ET.SubElement(cs, "tag", k=k, v=v)
    # Every node the way still uses, as context; the stacks marked for deletion.
    for n in full.iter("node"):
        nid = int(n.get("id"))
        if nid in stacks:
            n.set("action", "delete")
        out.append(n)
    for nid, n in stacks.items():
        if nid not in coords:
            n.set("action", "delete")
            out.append(n)
    for nd in way.findall("nd"):
        way.remove(nd)
    for r in new_refs:
        ET.SubElement(way, "nd", ref=str(r))
    _common.rewrite_tags(way, wtags)
    way.set("action", "modify")
    out.append(way)
    ET.ElementTree(out).write(OUT, encoding="utf-8", xml_declaration=True)

    on_way = sum(1 for s in stacks if s in coords)
    print(f"way {WAY}: {len(ring)} -> {len(keep)} vertices; addr:flats={flats} ({len(flats)} chars)")
    print(f"{len(stacks)} stack nodes deleted ({on_way} were outline vertices); "
          f"{len(units)} suites, none lost; POIs untouched: {sorted(POIS)}")
    print("wrote", OUT.name)


if __name__ == "__main__":
    main()
