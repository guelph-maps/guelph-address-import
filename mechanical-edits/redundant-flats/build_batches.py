"""What is left of mechanical edit 6: strip `addr:flats` listings the import's
door nodes have made redundant, prepared for JOSM.

Edit 6 (`../unit-doors`) was built to do two things in one changeset: remove
`addr:flats` from a door group's buildings and create one `addr:unit` node per
door. Since 2026-10-01 the import creates those doors itself -- a listing no
longer stands in for a door -- and the first pass uploaded 1,680 of them across
143 civic addresses (2026-10-03..07). The doors are in OSM now. What is left
is the first half alone:

    building (or civic node) carrying addr:flats  ->  addr:flats removed,
                                                      nothing else touched

**Who is in it.** Only civic groups this import uploaded as doors:
`candidates.stage = 'UPLOADED'` with a unit, in tool.db -- the same test
`unit_verdicts.frozen_keys()` uses, so these are exactly the groups whose
shape the import has put in OSM. The civic is read off our own door nodes'
live tags, so a listing joins its group on the addr:housenumber +
addr:street OSM actually carries.

**The gate is coverage, per listing.** A listing is stripped only when every
unit it names has an address object of its own at that civic in live OSM:
an `addr:unit` node or way that is not a POI node (the engine's
`conflate._is_poi_node` rule -- a shop carrying `addr:unit=122` is a business,
not the unit's address). Our door nodes count, and so do doors somebody else
mapped before us. Anything less goes whole to review.csv:

* a listed unit with no door at this civic -- if it has one at another
  uploaded civic on the same street, `cross-civic` (campaign 7's), else
  `unit-without-door`;
* a listed unit the City does not have at this civic (`osm-unit-not-in-city`):
  the doors do not stand in for something the source never said;
* a listed unit carried only by a POI (`unit-on-poi-only`);
* a group the operator judged `split` (`shape-split`): there the listing *is*
  the intended shape for the tower part;
* a value that does not parse, a relation, or an `addr:flats` object at one of
  these civics whose addr:street is spelled differently from the doors'
  (`street-spelling`) -- the join above would otherwise miss it silently.

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py
    ... build_batches.py --refetch     # pull both Overpass fetches again first

Writes, under this directory:

    live.osm                every addr:flats object + child nodes, `out meta`
    live_units.osm          every object carrying addr:unit, `out meta center`
    batches/NN-<area>.osm   one JOSM layer per batch = one changeset
    manifest.csv            one row per stripped object; the revert record
    review.csv              every listing at an uploaded door civic not batched
    index.html              the run sheet

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
CITY_DIR = HERE.parents[1]
ENGINE = CITY_DIR.parent / "address-importer-friend"
os.environ.setdefault("T2_CITY_DIR", str(CITY_DIR))
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "flats-hygiene"))

import t2.config  # noqa: E402
t2.config.OSM_ENV = "prod"
t2.config.load()
from t2 import source_db, unit_shapes, units  # noqa: E402
from t2.conflate import _is_poi_node, normalize_street  # noqa: E402

import _runsheet  # noqa: E402
from _common import (AREA_ID, Campaign, assign_area, batchable, centre,  # noqa: E402
                     element_tags, fetch_live, index_live, load_areas,
                     make_batches, promote_pilot, write_batch, write_csvs)
from flats_parse import parse_flats  # noqa: E402

TOOL_DB = CITY_DIR / "data" / "guelph" / "tool.db"
BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"
LIVE_UNITS = HERE / "live_units.osm"
AREAS = HERE.parent / "flats-hygiene" / "areas.geojson"
# Who wrote each listing's addr:flats: campaign 3 moved list-valued addr:unit
# onto it, and the hand cases (campaign 2/3 leftovers) did the same for 32
# more. Both moved the 2025 import's own values; anything else is a mapper's.
ORIGINS = {"campaign-3": HERE.parent / "unit-listing-retag" / "manifest.csv",
           "hand-cases": HERE.parent / "hand-cases" / "manifest.csv"}

QUERY = f"""
[out:xml][timeout:900];
area({AREA_ID})->.guelph;
nwr["addr:flats"](area.guelph);
out meta;
>;
out meta;
"""

UNITS_QUERY = f"""
[out:xml][timeout:900];
area({AREA_ID})->.guelph;
nwr["addr:unit"](area.guelph);
out meta center;
"""


def norm(s) -> str:
    return " ".join(str(s or "").lower().split())


def hn(tags: dict) -> str:
    return str(tags.get("addr:housenumber", "")).strip().upper()


def unit_set(value: str) -> list[str]:
    """Every designator a value names, upper-cased; a value `parse_flats`
    cannot read counts as its `;` parts."""
    parsed = parse_flats(value)
    parts = parsed if parsed is not None else value.split(";")
    return [p.strip().upper() for p in parts if p.strip()]


def is_address_object(el: ET.Element, tags: dict) -> bool:
    """A door of the unit, rather than a business that happens to sit in it.
    Ways carrying addr:unit are door outlines; a node is a door unless the
    engine would call it a POI."""
    return not _is_poi_node({"type": el.tag, "tags": tags})


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Remove addr:flats, keep everything else in order."""
    new = {k: v for k, v in tags.items() if k != "addr:flats"}
    return new, {"flats_before": tags.get("addr:flats", "")}


REVIEW_REASONS = {
    "cross-civic": (
        "Listing names a unit whose door is at another civic",
        "Campaign 7's (<code>cross-civic-flats/</code>): the 74/176 Janefield "
        "back-to-back slices. Every unit has its door, but not all at this "
        "civic; left to that campaign."),
    "doors-deleted": (
        "This import's doors at the civic are gone",
        "A hand edit deleted a door node the import created, or took "
        "<code>addr:unit</code> off it, so the group changed after the "
        "import. Whatever the listing now names, it is a hand question "
        "rather than a mechanical strip."),
    "unit-without-door": (
        "A listed unit has no door at this civic",
        "Stripping the listing would lose a unit nobody created. "
        "<code>detail</code> names the units."),
    "osm-unit-not-in-city": (
        "OSM lists a unit the City does not have here",
        "The doors stand in for the City's units, not this one. A hand "
        "question, not a rule."),
    "unit-on-poi-only": (
        "A listed unit survives only on a POI",
        "A shop's or office's <code>addr:unit</code> is the business's, not "
        "the unit's address."),
    "shape-split": (
        "Operator verdict <code>split</code>",
        "Doors for the row units, one listing for the tower: the listing is "
        "the intended shape here. Any doors it also names are reported."),
    "street-spelling": (
        "Listing's addr:street spelled differently from the doors'",
        "Same number, same street after normalising, different text. Settle "
        "the spelling first."),
    "flats-unparsed": (
        "<code>addr:flats</code> value not understood",
        "The coverage gate cannot prove every listed unit has a door."),
    "relation": (
        "A relation carries <code>addr:flats</code>",
        "Never batched; see <code>_common.batchable()</code>."),
}

STEPS = [
    "<strong>No forum post</strong> (skfd decided 2026-10-07).",
    "On the day: <code>build_batches.py --refetch</code>. Versions move; a "
    "stale batch conflicts in JOSM rather than overwriting, but a rebuild is "
    "cheaper than resolving conflicts.",
    "Sign JOSM in as <code>skfd imports</code>. Run "
    "<code>python upload_loop.py redundant-flats 1 N</code> to feed batches "
    "and verify each from the API.",
    "Batch 1 is the pilot. Upload it, check it on the map, then the rest.",
]

CAMPAIGN = Campaign(
    slug="redundant-flats",
    generator="guelph-address-import redundant-flats (mechanical edit 6, what is left)",
    title="Mechanical edit 6 — listings the doors made redundant",
    blurb=("Where every unit a building lists now has its own "
           "<code>addr:unit</code> door node, remove <code>addr:flats</code> "
           "from the building. Nothing else changes."),
    comment=lambda where, index, total: (
        f"Guelph addresses: remove addr:flats where every listed unit now has "
        f"its own addr:unit door node - {where} ({index}/{total})"),
    transform=transform,
    manifest_extra=["group", "flats_before", "units", "origin", "last_user"],
    review_reasons=REVIEW_REASONS,
    steps=STEPS,
    sample=lambda row: (f"{row.get('group', '')}: addr:flats={row['flats_before']} "
                        f"removed" if row.get("flats_before") else ""),
    review_columns=["flats", "units_city", "detail", "origin", "last_user"],
    max_per_batch=250,
    pilot_min=10,
)


def uploaded_door_groups() -> dict[str, set[str]]:
    """civic_key -> ids of the door nodes this import uploaded there."""
    conn = sqlite3.connect(TOOL_DB)
    try:
        rows = conn.execute(
            "SELECT civic_key, osm_node_id FROM candidates "
            "WHERE stage = 'UPLOADED' AND coalesce(unit, '') <> ''").fetchall()
    finally:
        conn.close()
    out: dict[str, set[str]] = collections.defaultdict(set)
    for key, nid in rows:
        if nid is None:
            raise SystemExit(f"uploaded door at {key} has no osm_node_id")
        out[key].add(str(nid))
    return out


def listing_origins() -> dict[tuple[str, str], str]:
    out = {}
    for name, path in ORIGINS.items():
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if name == "campaign-3" or r.get("after_flats"):
                    out.setdefault((r["type"], r["id"]), name)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refetch", action="store_true",
                    help="pull both Overpass fetches again before building")
    args = ap.parse_args()

    root = fetch_live(QUERY, LIVE, args.refetch, "every addr:flats object")
    selected, coords = index_live(root, lambda t: "addr:flats" in t)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    units_root = fetch_live(UNITS_QUERY, LIVE_UNITS, args.refetch,
                            "every addr:unit object")
    areas = load_areas(AREAS)
    origins = listing_origins()

    # (housenumber, street) -> unit -> [(ref, is_address_object)]
    doors: dict[tuple, dict[str, list]] = collections.defaultdict(
        lambda: collections.defaultdict(list))
    unit_tags: dict[str, dict] = {}         # node id -> tags, for our doors
    for el in units_root:
        if el.tag not in ("node", "way", "relation"):
            continue
        t = element_tags(el)
        if el.tag == "node":
            unit_tags[el.attrib["id"]] = t
        addr = is_address_object(el, t)
        for u in unit_set(t["addr:unit"]):
            doors[(hn(t), norm(t.get("addr:street")))][u].append(
                (f"{el.tag}/{el.attrib['id']}", addr))

    groups = uploaded_door_groups()
    civic_of: dict[tuple, str] = {}          # OSM (hn, street) -> civic_key
    gone_doors: dict[str, list[str]] = {}    # civic_key -> our doors now gone
    for key, ids in groups.items():
        found = {(hn(unit_tags[i]), norm(unit_tags[i].get("addr:street")))
                 for i in ids if unit_tags.get(i)}
        gone = sorted(i for i in ids if not unit_tags.get(i))
        if gone:
            # A hand edit deleted a door this import uploaded, or took
            # addr:unit off it, so the group changed under us. That is not
            # fatal -- the per-listing gate reads live OSM, and somebody
            # else's door counts -- but it is never silent: every listing at
            # such a civic is held as `doors-deleted`.
            gone_doors[key] = gone
        if len(found) > 1:
            raise SystemExit(f"doors at {key} disagree on their civic: {found}")
        if not found:
            # Every door of ours is gone, so the civic cannot be read off our
            # own live tags. Fall back to the key itself, so a listing there
            # is still seen and held rather than quietly skipped.
            number, street, _municipality = key.split("|")
            found = {(number.strip().upper(), norm(street))}
        civic_of[found.pop()] = key
    loose = {(h, normalize_street(s)): k for (h, s), k in civic_of.items()}
    print(f"{len(selected)} addr:flats objects, {len(groups)} civics with "
          f"uploaded doors ({sum(len(v) for v in groups.values())} nodes), "
          f"{len(areas)} areas")
    if gone_doors:
        print(f"  {sum(len(v) for v in gone_doors.values())} of those doors "
              f"are gone from live OSM, at {len(gone_doors)} civics: "
              + "; ".join(f"{k} ({len(v)})" for k, v in sorted(gone_doors.items()))
              + " - any listing there is held")

    data = unit_shapes.collect()
    shape_of = {k: r["shape"] for k, r in data["by_key"].items()}
    src_keys = {k: (r["number"], r["street"], r["municipality"])
                for k, r in data["by_key"].items() if k in groups}
    src = source_db.fetch_civic_groups(list(src_keys.values()), data["snapshot_id"])
    city_units = {k: {(x.get("unit_name") or "").strip().upper()
                      for x in src.get(sk, []) if (x.get("unit_name") or "").strip()}
                  for k, sk in src_keys.items()}
    # unit -> the civics on a street where it has a door, for `cross-civic`.
    street_units: dict[tuple, set[str]] = collections.defaultdict(set)
    for (h, s), key in civic_of.items():
        for u in doors[(h, s)]:
            street_units[(s, u)].add(h)

    items: list[dict] = []
    review: list[dict] = []
    stats = collections.Counter()
    for (kind, oid), el in sorted(selected.items(), key=lambda kv: (kv[0][0], int(kv[0][1]))):
        t = element_tags(el)
        civic = (hn(t), norm(t.get("addr:street")))
        key = civic_of.get(civic)
        if key is None:
            alt = loose.get((civic[0], normalize_street(t.get("addr:street", ""))))
            if alt is None:
                continue                      # not at an uploaded door civic
            key, reason, detail = alt, "street-spelling", t.get("addr:street", "")
        elif key in gone_doors:
            reason = "doors-deleted"
            detail = (f"{len(gone_doors[key])} of this import's doors are gone "
                      f"from OSM, e.g. node {gone_doors[key][0]}")
        else:
            reason, detail = classify(kind, t, civic, key, doors, city_units,
                                      shape_of, street_units)
        lon, lat = centre(el, coords)
        row = {"type": kind, "id": oid, "street": t.get("addr:street", ""),
               "housenumber": t.get("addr:housenumber", ""),
               "area": assign_area(lon, lat, areas), "group": key,
               "flats": t.get("addr:flats", ""),
               "origin": origins.get((kind, oid), "other"),
               "last_user": el.attrib.get("user", "")}
        if reason:
            review.append({**row, "reason": reason, "detail": detail,
                           "units_city": str(len(city_units.get(key, ())))})
            continue
        items.append({**row, "units": str(len(unit_set(t["addr:flats"])))})
        stats[row["origin"]] += 1
        stats[kind] += 1

    by_reason = collections.Counter(r["reason"] for r in review)
    print(f"  {len(items)} listings fully covered ({stats['way']} ways, "
          f"{stats['node']} nodes; addr:flats written by campaign 3 "
          f"{stats['campaign-3']}, hand cases {stats['hand-cases']}, "
          f"others {stats['other']}) in "
          f"{len({it['group'] for it in items})} civics")
    print("  review: " + ", ".join(f"{k} {v}" for k, v in sorted(by_reason.items())))

    batches = promote_pilot(make_batches(items, CAMPAIGN.max_per_batch),
                            CAMPAIGN.pilot_min)
    total = len(batches)
    extra = {(it["type"], it["id"]): it for it in items}
    records = []
    for index, batch in enumerate(batches, 1):
        rec = write_batch(CAMPAIGN, BATCH_DIR, batch, index, total,
                          selected, by_node_id)
        for r in rec["rows"]:
            it = extra[(r["type"], r["id"])]
            r.update(group=it["group"], units=it["units"], origin=it["origin"],
                     last_user=it["last_user"])
        records.append(rec)
        print(f"  batch {index}/{total}: {batch['area']} ({len(batch['items'])} objects)")

    verify(records, doors)
    write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp, len(selected))
    print(f"\n{total} batches, {len(items)} objects lose addr:flats")
    print(f"run sheet: {page}")
    print("NOT announced, NOT uploaded.")


def classify(kind, t, civic, key, doors, city_units, shape_of,
             street_units) -> tuple[str, str]:
    """('', '') when the listing is redundant, else (reason, detail)."""
    if not batchable(kind):
        return "relation", ""
    parsed = parse_flats(t["addr:flats"])
    if parsed is None:
        return "flats-unparsed", ""
    listed = [u.upper() for u in parsed]
    have = doors[civic]
    if shape_of.get(key) == "split":
        dup = [u for u in listed if u in have]
        return "shape-split", (f"doors also exist for {';'.join(dup)}" if dup else "")
    missing = [u for u in listed if u not in have]
    if missing:
        elsewhere = {u: street_units.get((civic[1], u), set()) - {civic[0]}
                     for u in missing}
        if all(elsewhere.values()):
            return "cross-civic", "; ".join(
                f"{u} at {'/'.join(sorted(h))}" for u, h in elsewhere.items())
        return "unit-without-door", ";".join(missing)
    not_city = [u for u in listed if u not in city_units.get(key, set())]
    poi_only = [u for u in listed if not any(a for _, a in have[u])]
    if not_city:
        why = ";".join(not_city)
        if poi_only:
            why += f" (only on a POI: {';'.join(poi_only)})"
        return "osm-unit-not-in-city", why
    if poi_only:
        return "unit-on-poi-only", ";".join(poi_only)
    return "", ""


def verify(records: list[dict], doors: dict) -> None:
    """Read every written batch back and refuse the set unless:

    1. every element marked modify is a manifest row, and every row is in
       its file, with a version;
    2. nothing is created or deleted: no negative ids;
    3. each modified object's tags are its live tags with addr:flats gone
       and nothing else changed;
    4. every unit its former listing named has a non-POI addr:unit object
       at its civic in live_units.osm.
    """
    live = {(el.tag, el.attrib["id"]): element_tags(el)
            for el in ET.parse(LIVE).getroot() if el.tag in ("node", "way")}
    problems: list[str] = []
    for rec in records:
        want = {(r["type"], r["id"]): r for r in rec["rows"]}
        got = set()
        for el in ET.parse(rec["path"]).getroot():
            if el.tag not in ("node", "way", "relation"):
                continue
            k = (el.tag, el.attrib["id"])
            if int(el.attrib["id"]) < 0:
                problems.append(f"{rec['path'].name}: new element {k}")
            if el.attrib.get("action") != "modify":
                continue
            got.add(k)
            before = live[k]
            after = element_tags(el)
            if after != {a: b for a, b in before.items() if a != "addr:flats"} \
                    or "addr:flats" not in before:
                problems.append(f"{k}: tags are not live minus addr:flats")
            if "version" not in el.attrib:
                problems.append(f"{k} has no version")
            civic = (hn(before), norm(before.get("addr:street")))
            for u in unit_set(before.get("addr:flats", "")):
                if not any(a for _, a in doors[civic].get(u, ())):
                    problems.append(f"{k}: unit {u} has no door")
        if got != set(want):
            problems.append(f"{rec['path'].name}: file != manifest "
                            f"({len(got)} modified, {len(want)} rows)")
    if problems:
        raise SystemExit("batch verification failed:\n  " + "\n  ".join(problems[:20]))
    print(f"  verified: {sum(len(r['rows']) for r in records)} objects, live tags "
          f"minus addr:flats only, every listed unit has a door, nothing created")


if __name__ == "__main__":
    main()
