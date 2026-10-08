"""Campaign 7: `addr:flats` values naming units the City does not put at
that civic. 14 objects were recorded on 2026-10-02; this rebuilds against
OSM as it stands after the import, and refuses what the evidence does not
carry.

Two batches, kept apart so the operator can upload one without the other:

1. **Janefield back-to-back slices (7 ways).** Each slice carries one civic's
   housenumber and a listing naming one home from 74 and one from 176
   Janefield Avenue. The import (changeset 190115284, 2026-10-06) created a
   door node for every one of those 14 units at the City's civic. The gate
   re-proves, per listed unit, that exactly one OSM node carries it at the
   City's civic for it, and that the node lies inside this slice. Only then
   is `addr:flats` removed, whole: half of it names the wrong civic, and the
   other half repeats a door node. Nothing else on the slice changes, and
   that includes the housenumber; see the README.

2. **Towers (one unit each).** The listing names exactly one unit the City
   does not have at this civic, and names every unit it does have. That unit
   comes out, and the rest are re-rendered through the engine. Refused, to
   review.csv, when OSM itself argues for the unit:
     `unit-in-osm`         another object at this civic carries `addr:unit`
                           for it (355 Elmira Road North: a law office);
     `building-flats`      the object's `building:flats` count agrees with
                           the listing, not with the City
                           (358 Waterloo Avenue: 86, surveyed 2024);
   and as `already-right` when the listing already equals the City. 7 Ajax
   Street and 395 Edinburgh Road North were hand-fixed by skfd on 2026-10-06,
   in changesets 190114899 and 190115369.

Everything is read live from the API, never from Overpass, because 14 ways
do not justify a city-wide query. The City side is read from the tracker's
newest live snapshot. Writes live.osm, batches/NN-*.osm, manifest.csv,
review.csv and index.html. Uploads nothing.

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py
"""
from __future__ import annotations

import sqlite3
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

from shapely.geometry import Point, Polygon

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "flats-hygiene"))

import _runsheet  # noqa: E402
from _common import UA, Campaign, element_tags, write_batch, write_csvs  # noqa: E402
from flats_parse import normalise, parse_flats  # noqa: E402

API = "https://api.openstreetmap.org/api/0.6/"
CITY_DB = "C:/Users/kk/Code/ontario-address-changes/data/guelph/guelph.db"
BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"

SLICES = [1349287989, 1349287990, 1349287991, 1349287992,
          1349287993, 1349287996, 1349287997]
TOWERS = [1349266419, 802528770, 178085151,          # the three trims
          819734215, 344325628,                      # held: OSM argues back
          502064547, 1042083497]                     # hand-fixed 2026-10-06
SLICE_STREET = "Janefield Avenue"
# Tags a slice or tower may carry and still be edited by rule. Anything else
# addr:* means somebody has been at it since; look first.
ADDR_OK = {"addr:housenumber", "addr:street", "addr:flats", "addr:city",
           "addr:postcode"}
# A door node sitting on a slice edge would be "touching", not "inside";
# 0.5 m is far tighter than any slice is wide.
EDGE_TOL_DEG = 0.5 / 111_000

LABEL_SLICES = "Janefield back-to-back slices"
LABEL_TOWERS = "Towers, one unit each"


def get(path: str) -> ET.Element:
    for attempt in range(4):
        try:
            req = urllib.request.Request(API + path, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as res:
                return ET.fromstring(res.read())
        except Exception as exc:  # noqa: BLE001
            if attempt == 3:
                raise
            print(f"    {path}: {exc}; retrying")
            time.sleep(10)
    raise AssertionError


# ------------------------------------------------------------- the City

def city_snapshot(db: sqlite3.Connection) -> tuple[int, str]:
    """The newest snapshot any row is still live in. A newer snapshot whose
    payload hash equals that one's is the same data; `addresses` is not
    extended for it, so the max over rows is the honest answer."""
    sid = db.execute("select max(max_snapshot_id) from addresses").fetchone()[0]
    when = db.execute("select downloaded from snapshots where id=?", (sid,)).fetchone()[0]
    return sid, when[:10]


def city_units(db, sid: int, number: str, street: str) -> set[str]:
    rows = db.execute("select unit from addresses where max_snapshot_id=? "
                      "and number=? and street=? and unit is not null",
                      (sid, number, street)).fetchall()
    return {r[0].upper() for r in rows}


def city_civics_of(db, sid: int, unit: str, street: str, among: set[str]) -> set[str]:
    rows = db.execute("select number from addresses where max_snapshot_id=? "
                      "and unit=? and street=?", (sid, unit, street)).fetchall()
    return {r[0] for r in rows} & among


# ------------------------------------------------------------- the fetch

def fetch(ids: list[int]) -> tuple[dict, dict, dict]:
    """Each way in full, plus every address-bearing object in a box 150 m
    round it: the door nodes and POIs the gates read."""
    ways: dict[int, ET.Element] = {}
    nodes: dict[str, ET.Element] = {}
    around: dict[tuple[str, str], ET.Element] = {}
    for wid in ids:
        full = get(f"way/{wid}/full")
        for n in full.iter("node"):
            nodes[n.get("id")] = n
        ways[wid] = full.find("way")
        lats = [float(n.get("lat")) for n in full.iter("node")]
        lons = [float(n.get("lon")) for n in full.iter("node")]
        pad = 0.0015
        box = get("map?bbox=%f,%f,%f,%f" % (min(lons) - pad, min(lats) - pad,
                                            max(lons) + pad, max(lats) + pad))
        for el in box:
            if el.tag in ("node", "way", "relation") and any(
                    t.get("k", "").startswith("addr:") for t in el.findall("tag")):
                around[(el.tag, el.get("id"))] = el
        time.sleep(1)
    return ways, nodes, around


def polygon(way: ET.Element, nodes: dict) -> Polygon:
    return Polygon([(float(nodes[nd.get("ref")].get("lon")),
                     float(nodes[nd.get("ref")].get("lat")))
                    for nd in way.findall("nd")])


def write_live(ways: dict, nodes: dict, around: dict) -> None:
    """What every batch was prepared against, for verify_changeset: the
    ways in full, and the address objects the gates read."""
    out = ET.Element("osm", {"version": "0.6",
                             "generator": "guelph cross-civic-flats (API)"})
    els = {("node", i): n for i, n in nodes.items()}
    els.update(around)
    els.update({("way", str(w)): el for w, el in ways.items()})
    order = {"node": 0, "way": 1, "relation": 2}
    for key in sorted(els, key=lambda k: (order[k[0]], int(k[1]))):
        out.append(els[key])
    ET.ElementTree(out).write(LIVE, encoding="utf-8", xml_declaration=True)


# ------------------------------------------------------------- the gates

def at_civic(around: dict, street: str, number: str):
    for el in around.values():
        t = element_tags(el)
        if t.get("addr:street") == street and t.get("addr:housenumber") == number:
            yield el, t


def foreign_addr(tags: dict) -> set[str]:
    return {k for k in tags if k.startswith("addr:")} - ADDR_OK


def judge_slice(way, tags, nodes, around, db, sid) -> dict:
    """Every listed unit has its door: one node, the City's civic for that
    unit, inside this slice. Fatal otherwise; this batch exists on that."""
    wid = way.get("id")
    units = parse_flats(tags["addr:flats"])
    assert units and len(units) == 2, f"w{wid}: listing is not a pair: {tags['addr:flats']}"
    assert tags.get("addr:street") == SLICE_STREET, wid
    assert not foreign_addr(tags), f"w{wid} carries {foreign_addr(tags)}"
    poly = polygon(way, nodes)
    doors = []
    for unit in units:
        civic = city_civics_of(db, sid, unit, SLICE_STREET, {"74", "176"})
        assert len(civic) == 1, f"w{wid} unit {unit}: City civics {civic}"
        civic = civic.pop()
        hits = [el for el, t in at_civic(around, SLICE_STREET, civic)
                if t.get("addr:unit", "").upper() == unit]
        assert len(hits) == 1, f"w{wid} unit {unit}: {len(hits)} OSM objects at {civic}"
        door = hits[0]
        assert door.tag == "node", f"w{wid} unit {unit}: carried by a {door.tag}"
        pt = Point(float(door.get("lon")), float(door.get("lat")))
        assert poly.buffer(EDGE_TOL_DEG).contains(pt), \
            f"w{wid} unit {unit}: door n{door.get('id')} is not inside the slice"
        doors.append(f"{civic}/{unit}=n{door.get('id')}")
    return {"removed": ";".join(units), "doors": " ".join(doors),
            "own_civic_units": ";".join(u for u in units
                                        if city_civics_of(db, sid, u, SLICE_STREET, {"74", "176"})
                                        == {tags["addr:housenumber"]})}


def judge_tower(tags, around, db, sid) -> tuple[str, str | None, dict]:
    """(safe | review | skip, reason, detail)."""
    street, number = tags["addr:street"], tags["addr:housenumber"]
    listed = parse_flats(tags["addr:flats"])
    assert listed, f"{number} {street}: listing does not parse"
    city = city_units(db, sid, number, street)
    extra = [u for u in listed if u not in city]
    short = city - set(listed)
    detail = {"city_units": len(city), "listed_units": len(listed),
              "removed": ";".join(extra)}
    if not extra and not short:
        return "skip", "already-right", detail
    if short or len(extra) != 1:
        return "review", "not-one-stray", detail
    if foreign_addr(tags):
        return "review", "other-addr-tags", detail
    stray = extra[0]
    poi = [el for el, t in at_civic(around, street, number)
           if t.get("addr:unit", "").upper() == stray]
    if poi:
        detail["evidence"] = " ".join(f"{e.tag[0]}{e.get('id')}" for e in poi)
        return "review", "unit-in-osm", detail
    bf = tags.get("building:flats")
    if bf is not None and bf != str(len(listed) - 1):
        detail["evidence"] = f"building:flats={bf}"
        return "review", "building-flats", detail
    if normalise(tags["addr:flats"])[0] != tags["addr:flats"]:
        return "review", "not-canonical", detail
    return "safe", None, detail


def tower_value(tags: dict, stray: str) -> str:
    units = [u for u in parse_flats(tags["addr:flats"]) if u != stray]
    value, reason = normalise(";".join(units))
    assert value and not reason, reason
    assert set(parse_flats(value)) == set(units), "the rendering lost or invented a unit"
    return value


# ------------------------------------------------------------- campaign

PLAN: dict[str, dict] = {}   # way id -> what the transform does


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Pure given PLAN. Only `addr:flats` changes."""
    key = (tags.get("addr:housenumber"), tags.get("addr:street"), tags["addr:flats"])
    plan = PLAN[key]
    new = dict(tags)
    if plan["after"]:
        new["addr:flats"] = plan["after"]
    else:
        del new["addr:flats"]
    return new, {"flats_before": tags["addr:flats"], "flats_after": plan["after"],
                 "removed": plan["removed"], "evidence": plan["evidence"],
                 "city_snapshot": plan["snapshot"]}


REVIEW_REASONS = {
    "unit-in-osm": (
        "Another OSM object at this civic carries the unit",
        "The City lacks it, but a mapped business or door here says it "
        "exists. Removing it from the listing would contradict that. Ask the "
        "City; leave OSM alone."),
    "building-flats": (
        "<code>building:flats</code> counts the unit",
        "A mapper's unit count agrees with the listing, not with the City. "
        "Ask the City; leave OSM alone."),
    "already-right": (
        "Listing already equals the City",
        "Fixed by hand since 2026-10-02. Nothing to do."),
    "not-one-stray": (
        "More than one unit differs from the City",
        "This edit removes exactly one unit. Anything else is hand work."),
    "other-addr-tags": (
        "Carries other <code>addr:*</code> tags",
        "Somebody has been at it since. Look first."),
    "not-canonical": (
        "The listing is not in the renderer's form",
        "Re-rendering would change more than the one unit. Hand work."),
}

STEPS = [
    "<strong>No forum post</strong> (skfd decided 2026-10-07).",
    "On the day, run <code>build_batches.py</code> again. Every gate re-reads OSM.",
    "Sign JOSM in as <code>skfd imports</code>.",
    "Batch 1: the Janefield slices. Upload it, then run "
    "<code>../verify_changeset.py cross-civic-flats 1</code>.",
    "Batch 2: the towers, only if skfd accepts the City over the 2025 listing "
    "(see the README). Then <code>verify_changeset.py cross-civic-flats 2</code>.",
]

CAMPAIGN = Campaign(
    slug="cross-civic-flats",
    generator="guelph-address-import cross-civic-flats (mechanical edit 7)",
    title="Mechanical edit 7: listings naming another civic's units",
    blurb=("Strip the <code>addr:flats</code> pairs the import's door nodes "
           "replaced on seven Janefield slices, and drop one unit the City "
           "does not have from three tower listings."),
    comment=lambda where, index, total: (
        "Guelph addresses: remove addr:flats on Janefield back-to-back slices; "
        "each unit is now its own door node at the right civic "
        f"({index}/{total})" if where == LABEL_SLICES else
        "Guelph addresses: remove one unit the City does not have from three "
        f"addr:flats listings ({index}/{total})"),
    transform=transform,
    manifest_extra=["flats_before", "flats_after", "removed", "evidence",
                    "city_snapshot"],
    review_reasons=REVIEW_REASONS,
    steps=STEPS,
    sample=lambda row: f"{row['flats_before']} &rarr; {row['flats_after'] or '(removed)'}",
    review_columns=["flats", "removed", "evidence"],
    max_per_batch=250,
    pilot_min=1,
)


def main() -> None:
    db = sqlite3.connect(CITY_DB)
    sid, when = city_snapshot(db)
    snap = f"{sid} ({when})"
    print(f"City: snapshot {snap}")
    ways, nodes, around = fetch(SLICES + TOWERS)
    write_live(ways, nodes, around)
    by_node_id = nodes
    selected = {("way", str(w)): el for w, el in ways.items()}

    slice_items, tower_items, review = [], [], []
    for wid in SLICES:
        way = ways[wid]
        tags = element_tags(way)
        if "addr:flats" not in tags:
            review.append({"type": "way", "id": str(wid), "reason": "already-right",
                           "street": tags.get("addr:street", ""),
                           "housenumber": tags.get("addr:housenumber", ""),
                           "area": LABEL_SLICES})
            continue
        got = judge_slice(way, tags, nodes, around, db, sid)
        PLAN[(tags["addr:housenumber"], tags["addr:street"], tags["addr:flats"])] = {
            "after": "", "removed": got["removed"], "evidence": got["doors"],
            "snapshot": snap}
        print(f"  w{wid} {tags['addr:housenumber']} {SLICE_STREET} "
              f"{tags['addr:flats']}: doors {got['doors']}")
        slice_items.append({"type": "way", "id": str(wid),
                            "street": tags["addr:street"],
                            "housenumber": tags["addr:housenumber"]})

    for wid in TOWERS:
        tags = element_tags(ways[wid])
        cls, reason, detail = judge_tower(tags, around, db, sid)
        line = (f"  w{wid} {tags['addr:housenumber']} {tags['addr:street']}: "
                f"{cls}{' (' + reason + ')' if reason else ''} {detail}")
        print(line)
        if cls != "safe":
            review.append({"type": "way", "id": str(wid), "reason": reason,
                           "street": tags["addr:street"],
                           "housenumber": tags["addr:housenumber"],
                           "flats": tags["addr:flats"], "area": LABEL_TOWERS,
                           "removed": detail["removed"],
                           "evidence": detail.get("evidence", "")})
            continue
        after = tower_value(tags, detail["removed"])
        PLAN[(tags["addr:housenumber"], tags["addr:street"], tags["addr:flats"])] = {
            "after": after, "removed": detail["removed"],
            "evidence": f"City has {detail['city_units']} units here, listing {detail['listed_units']}",
            "snapshot": snap}
        tower_items.append({"type": "way", "id": str(wid),
                            "street": tags["addr:street"],
                            "housenumber": tags["addr:housenumber"]})

    batches = [{"area": label, "part": 1, "of": 1,
                "items": sorted(items, key=lambda r: (r["street"], r["housenumber"], r["id"]))}
               for label, items in ((LABEL_SLICES, slice_items),
                                    (LABEL_TOWERS, tower_items)) if items]
    for old in BATCH_DIR.glob("*.osm"):
        old.unlink()
    records = [write_batch(CAMPAIGN, BATCH_DIR, b, i, len(batches), selected, by_node_id)
               for i, b in enumerate(batches, 1)]

    # The claim, checked on what was written: the units after are the units
    # before less exactly the removed ones.
    for rec in records:
        for row in rec["rows"]:
            before = set(parse_flats(row["flats_before"]))
            after = set(parse_flats(row["flats_after"]) or [])
            assert after == before - set(row["removed"].split(";")), row
            assert before - after, row
        for el in ET.parse(rec["path"]).getroot():
            if el.tag == "node":
                assert "action" not in el.attrib and not el.findall("tag") or \
                    el.get("id") in nodes, el.attrib

    write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp,
                           len(SLICES) + len(TOWERS))
    print(f"\n{len(batches)} batches, {sum(r['count'] for r in records)} objects; "
          f"{len(review)} left alone")
    print(f"run sheet: {page}")
    print("NOT uploaded.")


if __name__ == "__main__":
    main()
