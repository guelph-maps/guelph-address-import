"""Mechanical edit 6 — unit doors, prepared for JOSM.

Campaign 3 moved every list-valued `addr:unit` in Guelph onto `addr:flats`.
`addr:flats` says "these units are reached through this one entrance" — a
tower. But many of those buildings are groups where every unit has its own
outside door: 275 Hanlon Creek Boulevard is one commercial building with five
City unit points 8.4 m apart along one wall; 146 Downey Road is eight semis on
one civic, each listing `17A;17B`; 941 Gordon Street is seventeen townhouse
blocks listing four units each. For those, `addr:flats` asserts a shared
entrance that is not there.

For every civic group the engine's classifier (verdicts applied) calls
`nodes`, one changeset per batch does both halves at once:

    building(s) carrying addr:flats   ->  addr:flats removed, nothing else
    each City unit point              ->  a new node carrying addr:unit

Atomic on purpose: OSM never holds the building without its units.

**The shape comes from `t2.unit_shapes.collect()` and nothing else** — the
whole civic group as the source has it, with the operator's verdicts applied.
Never the per-run `candidates` table in tool.db: that one is tile-cut, and a
tower cut by a tile boundary reads as rows of doors on both sides.

**The door tags come from the engine's own `osm_export.build_tags`**, fed the
same fields `candidates._candidate_values` / `_emit_group` feed it, so these
nodes are exactly what the continuous import would have written:
addr:housenumber, addr:street, addr:unit, addr:postcode, addr:source,
addr:city. The postcode is the door's own City row's, through the engine's
`[postcode]` check (`candidates._source_postcode`), so a value the import
would omit is omitted here too; skfd, 2026-10-03: "if we have postal code to
write, write it". No addr:province (Guelph dropped it). The unit-less civic row of a group is not
created: the building way, or the existing civic node, keeps its
addr:housenumber and addr:street and *is* that object.

Guards, each sending the whole group to review.csv rather than half-editing it:

* OSM lists a unit the City does not have — removing the listing would lose it;
* the engine's rendering of the street is not the OSM object's addr:street;
* an addr:flats value that does not parse, or a relation carrying one;
* the City has the same unit designator twice at one civic.

And one per unit: a unit is **not created** when live OSM already holds an
object with the same addr:housenumber + addr:street + addr:unit (list values
such as campaign 3's excluded POIs, `119;121`, are expanded). Those skips are
manifest rows with `action=skip-existing` and the blocking object.

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py
    ... build_batches.py --refetch     # pull both Overpass fetches again first

Writes, under this directory:

    live.osm                every addr:flats object + child nodes, `out meta`
    live_units.osm          every object carrying addr:unit (the dedupe guard)
    batches/NN-<area>.osm   one JOSM layer per batch = one changeset
    manifest.csv            one row per stripped object, created node, and
                            skipped unit; the revert and verify record
    review.csv              every addr:flats object not batched, and why
    index.html              the run sheet

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
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
from t2 import candidates, osm_export, source_db, unit_shapes, units  # noqa: E402
from t2.conflate import apply_street_override, expand_street_name  # noqa: E402

import _runsheet  # noqa: E402
from _common import (AREA_ID, Campaign, assign_area, batchable, centre,  # noqa: E402
                     element_tags, fetch_live, index_live, load_areas,
                     make_batches, promote_pilot, write_batch, write_csvs)
from flats_parse import parse_flats  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402

BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"
LIVE_UNITS = HERE / "live_units.osm"
AREAS = HERE.parent / "flats-hygiene" / "areas.geojson"

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
out tags;
"""


def norm(s) -> str:
    return " ".join(str(s or "").lower().split())


def unit_set(value: str) -> set[str]:
    """Every designator a value names, upper-cased. `parse_flats` expands
    ranges the engine's way; a value it cannot read counts as its `;` parts,
    which is the conservative direction for a dedupe guard."""
    parsed = parse_flats(value)
    parts = parsed if parsed is not None else value.split(";")
    return {p.strip().upper() for p in parts if p.strip()}


def door_tags(row: dict) -> dict[str, str]:
    """What the continuous import writes for this City row: the dict
    `candidates._candidate_values` stores, through `osm_export.build_tags`."""
    street_raw = expand_street_name(apply_street_override(
        candidates._street_from_row(row)))
    hn = row.get("address_number") or ""
    postcode, _raw, _why = candidates._source_postcode(row)
    return osm_export.build_tags({
        "housenumber": str(hn).strip().upper() if hn else "",
        "street_raw": street_raw,
        "unit": (row.get("unit_name") or "").strip(),
        "postcode": postcode,
    })


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Remove addr:flats, keep everything else in order."""
    new = {k: v for k, v in tags.items() if k != "addr:flats"}
    return new, {
        "action": "modify",
        "group": f"{tags.get('addr:housenumber', '')} {tags.get('addr:street', '')}",
        "flats_before": tags.get("addr:flats", ""),
    }


REVIEW_REASONS = {
    "osm-unit-not-in-city": (
        "OSM lists a unit the City does not have",
        "Removing the listing would drop a unit nobody is re-creating. Whole "
        "group held back; <code>detail</code> names the units."),
    "street-mismatch": (
        "Engine's street spelling differs from OSM's",
        "A door node carrying a different <code>addr:street</code> from its "
        "building would be two addresses, not one. Held until the override "
        "or the OSM tag is settled."),
    "flats-unparsed": (
        "<code>addr:flats</code> value not understood",
        "The coverage guard cannot prove every listed unit survives, so the "
        "group is left alone."),
    "city-duplicate-unit": (
        "City has the same unit twice at this civic",
        "Two points for one designator: which door is it?"),
    "relation": (
        "A relation carries <code>addr:flats</code>",
        "Never batched; see <code>_common.batchable()</code>."),
    "shape-review": (
        "Classifier is not sure (<code>review</code>)",
        "The engine emits these collapsed plus a reason to look. Exploding a "
        "group the rule is unsure about uploads front doors that may not "
        "exist, so edit 6 leaves them until a verdict says <code>nodes</code>."),
    "shape-civic-only": (
        "Classifier says <code>civic-only</code>",
        "Listing over 255 characters, or an operator's choice. Not a door "
        "group; left alone here."),
    "shape-skip": (
        "Operator verdict <code>skip</code>",
        "Both shapes judged false for this group. Left alone."),
    "no-source-group": (
        "No City civic group at this address",
        "OSM's addr:housenumber + addr:street match nothing in the source, so "
        "there are no unit points to place."),
}

STEPS = [
    "<strong>Not announced.</strong> This edit has not been posted to "
    "<a href='https://community.openstreetmap.org/t/"
    "import-addresses-from-city-of-guelph-data/135103'>#135103</a>; the choice "
    "was to fix the data first. Post before uploading.",
    "On the day: <code>build_batches.py --refetch</code>. Versions move; a "
    "stale batch conflicts in JOSM rather than overwriting, but a rebuild is "
    "cheaper than resolving conflicts.",
    "Sign JOSM in as <code>skfd imports</code>. Run "
    "<code>python upload_loop.py unit-doors 1 N</code> to feed batches and "
    "verify each from the API.",
    "Batch 1 is the pilot. Upload it, check it on the map, then the rest.",
]

CAMPAIGN = Campaign(
    slug="unit-doors",
    generator="guelph-address-import unit-doors (mechanical edit 6)",
    title="Mechanical edit 6 — unit doors",
    blurb=("Where each unit has its own outside door, drop "
           "<code>addr:flats</code> from the building and add one "
           "<code>addr:unit</code> node per door at the City's unit point, in "
           "the same changeset."),
    comment=lambda where, index, total: (
        f"Guelph addresses: units with their own outside doors get one "
        f"addr:unit node per door instead of addr:flats on the building - "
        f"{where} ({index}/{total})"),
    transform=transform,
    manifest_extra=["action", "group", "unit", "flats_before",
                    "in_osm_listing", "inside_footprint", "blocked_by",
                    "lat", "lon", "tags"],
    review_reasons=REVIEW_REASONS,
    steps=STEPS,
    sample=lambda row: (
        f"{row.get('group', '')}: addr:flats={row['flats_before']} removed, "
        f"doors added" if row.get("flats_before") else ""),
    review_columns=["flats", "shape", "units_city", "units_osm", "detail"],
    max_per_batch=250,
    pilot_min=3,
)


def polygon_of(el: ET.Element, coords: dict) -> Polygon | None:
    if el.tag != "way":
        return None
    refs = [nd.attrib["ref"] for nd in el.findall("nd")]
    if len(refs) < 4 or refs[0] != refs[-1]:
        return None
    pts = [coords[r] for r in refs if r in coords]
    if len(pts) < 4:
        return None
    poly = Polygon(pts)
    return poly if poly.is_valid else poly.buffer(0)


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

    # (street, housenumber, unit) -> the OSM objects already carrying it.
    existing: dict[tuple, list[str]] = collections.defaultdict(list)
    for el in units_root:
        if el.tag not in ("node", "way", "relation"):
            continue
        t = element_tags(el)
        for u in unit_set(t.get("addr:unit", "")):
            existing[(norm(t.get("addr:street")),
                      str(t.get("addr:housenumber", "")).strip().upper(), u)
                     ].append(f"{el.tag}/{el.attrib['id']}")
    print(f"{len(selected)} addr:flats objects, "
          f"{sum(1 for e in units_root if e.tag in ('node', 'way', 'relation'))}"
          f" addr:unit objects, {len(areas)} areas")

    data = unit_shapes.collect()
    by_civic = {(norm(r["number"]), norm(r["street"])): r for r in data["rows"]}

    # Group every addr:flats object by its civic group.
    groups: dict[str, list[tuple]] = collections.defaultdict(list)
    shape_of: dict[str, str] = {}
    row_of: dict[str, dict] = {}
    for (kind, oid), el in selected.items():
        t = element_tags(el)
        r = by_civic.get((norm(t.get("addr:housenumber")), norm(t.get("addr:street"))))
        key = r["key"] if r else f"nosrc|{t.get('addr:housenumber')}|{t.get('addr:street')}"
        groups[key].append((kind, oid))
        shape_of[key] = r["shape"] if r else "no-source-group"
        if r:
            row_of[key] = r

    door_keys = [k for k in groups if shape_of[k] == "nodes"]
    src = source_db.fetch_civic_groups(
        [(row_of[k]["number"], row_of[k]["street"], row_of[k]["municipality"])
         for k in door_keys], data["snapshot_id"])

    items: list[dict] = []
    review: list[dict] = []
    skips: dict[str, list[dict]] = {}   # group key -> skip rows
    collapse_objs = 0
    stats = collections.Counter()

    def to_review(key: str, reason: str, detail: str = "",
                  city: int | str = "", osm: int | str = "") -> None:
        for kind, oid in groups[key]:
            el = selected[(kind, oid)]
            t = element_tags(el)
            lon, lat = centre(el, coords)
            review.append({
                "type": kind, "id": oid, "street": t.get("addr:street", ""),
                "housenumber": t.get("addr:housenumber", ""),
                "flats": t.get("addr:flats", ""), "shape": shape_of[key],
                "units_city": str(city), "units_osm": str(osm), "detail": detail,
                "area": assign_area(lon, lat, areas), "reason": reason})

    for key in sorted(groups):
        shape = shape_of[key]
        if shape == "collapse":
            collapse_objs += len(groups[key])
            continue
        if shape != "nodes":
            to_review(key, "no-source-group" if shape == "no-source-group"
                      else f"shape-{shape}")
            continue

        r = row_of[key]
        rows = src.get((r["number"], r["street"], r["municipality"]), [])
        unit_rows = [x for x in rows if (x.get("unit_name") or "").strip()]
        city_units = collections.Counter(
            x["unit_name"].strip().upper() for x in unit_rows)
        objs = sorted(groups[key], key=lambda k: (k[0] != "way", int(k[1])))
        els = [selected[k] for k in objs]
        tags = [element_tags(e) for e in els]

        if any(not batchable(k[0]) for k in objs):
            to_review(key, "relation", city=len(city_units))
            continue
        parsed = [parse_flats(t["addr:flats"]) for t in tags]
        if any(p is None for p in parsed):
            to_review(key, "flats-unparsed", city=len(city_units))
            continue
        osm_units = {u.upper() for p in parsed for u in p}
        dup = sorted(u for u, c in city_units.items() if c > 1)
        if dup:
            to_review(key, "city-duplicate-unit", ";".join(dup),
                      len(city_units), len(osm_units))
            continue
        missing = sorted(osm_units - set(city_units), key=units.unit_sort_key)
        if missing:
            to_review(key, "osm-unit-not-in-city", ";".join(missing),
                      len(city_units), len(osm_units))
            continue
        rendered = {door_tags(x)["addr:street"] for x in unit_rows}
        osm_streets = {t.get("addr:street", "") for t in tags}
        if len(rendered) != 1 or rendered != osm_streets:
            to_review(key, "street-mismatch",
                      f"engine {sorted(rendered)} vs OSM {sorted(osm_streets)}",
                      len(city_units), len(osm_units))
            continue

        polys = [p for p in (polygon_of(e, coords) for e in els) if p is not None]
        create, skipped = [], []
        for x in sorted(unit_rows, key=lambda x: units.unit_sort_key(
                x["unit_name"].strip())):
            dt = door_tags(x)
            unit = dt["addr:unit"]
            lat, lon = float(x["latitude"]), float(x["longitude"])
            if not polys:
                inside = "node-listing"
            else:
                inside = "yes" if any(p.covers(Point(lon, lat)) for p in polys) else "no"
            extra = {
                "action": "create", "group": f"{dt['addr:housenumber']} {dt['addr:street']}",
                "unit": unit,
                "in_osm_listing": "yes" if unit.upper() in osm_units else "no",
                "inside_footprint": inside, "lat": lat, "lon": lon,
                "tags": json.dumps(dt, ensure_ascii=False, sort_keys=True),
            }
            blockers = existing.get((norm(dt["addr:street"]),
                                     dt["addr:housenumber"].upper(), unit.upper()))
            if blockers:
                skipped.append({
                    "type": "", "id": "", "version": "",
                    "street": dt["addr:street"], "housenumber": dt["addr:housenumber"],
                    **extra, "action": "skip-existing", "tags": "",
                    "blocked_by": " ".join(blockers)})
                continue
            create.append({"id": -int(x["address_point_id"]), "lat": lat,
                           "lon": lon, "tags": dt, "street": dt["addr:street"],
                           "housenumber": dt["addr:housenumber"], "extra": extra})

        # The group's area: where its first listing object is. Every item of
        # the group carries the same one, so make_batches keeps them together.
        lon0, lat0 = centre(els[0], coords)
        area = assign_area(lon0, lat0, areas)
        for i, ((kind, oid), t) in enumerate(zip(objs, tags)):
            items.append({"type": kind, "id": oid, "area": area, "group": key,
                          "street": t.get("addr:street", ""),
                          "housenumber": t.get("addr:housenumber", ""),
                          "create": create if i == 0 else []})
        skips[key] = skipped
        stats["groups"] += 1
        stats["node listings"] += sum(1 for k in objs if k[0] == "node")
        stats["single-unit groups"] += len(city_units) == 1

    by_reason = collections.Counter(r["reason"] for r in review)
    groups_by_reason = collections.Counter()
    for reason in by_reason:
        groups_by_reason[reason] = len({(r["housenumber"], r["street"])
                                        for r in review if r["reason"] == reason})
    print(f"  {stats['groups']} door groups batched ({len(items)} objects, "
          f"{stats['node listings']} of them nodes; "
          f"{stats['single-unit groups']} single-unit groups); "
          f"{collapse_objs} collapse objects untouched")
    print("  review: " + ", ".join(
        f"{k} {v} obj/{groups_by_reason[k]} groups" for k, v in sorted(by_reason.items())))

    batches = promote_pilot(make_batches(items, CAMPAIGN.max_per_batch),
                            CAMPAIGN.pilot_min)
    total = len(batches)
    records = []
    for index, batch in enumerate(batches, 1):
        rec = write_batch(CAMPAIGN, BATCH_DIR, batch, index, total,
                          selected, by_node_id)
        for g in sorted({it["group"] for it in batch["items"]}):
            for row in skips[g]:
                rec["rows"].append({"batch": index, "area": batch["area"], **row})
        records.append(rec)
        print(f"  batch {index}/{total}: {batch['area']} "
              f"({len(batch['items'])} objects, "
              f"{sum(1 for r in rec['rows'] if r['action'] == 'create')} doors)")

    verify(records, items, existing)
    write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp, len(selected))

    all_rows = [r for rec in records for r in rec["rows"]]
    acts = collections.Counter(r["action"] for r in all_rows)
    made = [r for r in all_rows if r["action"] == "create"]
    print(f"\n{total} batches: {acts['modify']} objects lose addr:flats, "
          f"{acts['create']} door nodes created, {acts['skip-existing']} units "
          f"skipped as already in OSM")
    print(f"  created doors: {sum(r['in_osm_listing'] == 'yes' for r in made)} "
          f"were in an OSM listing, {sum(r['in_osm_listing'] == 'no' for r in made)} "
          f"are City-only; inside a listed footprint: "
          + ", ".join(f"{k} {v}" for k, v in sorted(
              collections.Counter(r['inside_footprint'] for r in made).items())))
    print(f"run sheet: {page}")
    print("NOT announced, NOT uploaded.")


def verify(records: list[dict], items: list[dict], existing: dict) -> None:
    """Read every written batch back and refuse the set if any of these fail:

    1. well-formed OSM XML; every negative-id node has lat/lon, no version,
       no action; every positive-id element marked modify is a manifest row;
    2. negative ids unique across the campaign;
    3. no civic group split across two batches;
    4. no created node duplicates an addr:unit object already in OSM;
    5. no modified object still carries addr:flats.
    """
    problems: list[str] = []
    group_batches: dict[str, set[int]] = collections.defaultdict(set)
    batch_of = {}
    for rec in records:
        for r in rec["rows"]:
            if r["action"] == "modify":
                batch_of[(r["type"], r["id"])] = rec["index"]
    for it in items:
        group_batches[it["group"]].add(batch_of[(it["type"], it["id"])])
    split = {g: b for g, b in group_batches.items() if len(b) > 1}
    if split:
        problems.append(f"{len(split)} groups split across batches: {list(split)[:3]}")

    neg_seen: set[str] = set()
    for rec in records:
        root = ET.parse(rec["path"]).getroot()
        want_mod = {(r["type"], r["id"]) for r in rec["rows"] if r["action"] == "modify"}
        want_new = {r["id"] for r in rec["rows"] if r["action"] == "create"}
        got_mod, got_new = set(), set()
        for el in root:
            if el.tag not in ("node", "way", "relation"):
                continue
            oid = el.attrib["id"]
            if int(oid) < 0:
                if el.tag != "node" or "version" in el.attrib or "action" in el.attrib \
                        or "lat" not in el.attrib or "lon" not in el.attrib:
                    problems.append(f"{rec['path'].name}: bad new element {el.tag} {oid}")
                if oid in neg_seen:
                    problems.append(f"negative id {oid} reused")
                neg_seen.add(oid)
                got_new.add(oid)
                t = element_tags(el)
                if existing.get((norm(t.get("addr:street")),
                                 t.get("addr:housenumber", "").upper(),
                                 t.get("addr:unit", "").upper())):
                    problems.append(f"new node {oid} duplicates an OSM addr:unit object")
            elif el.attrib.get("action") == "modify":
                got_mod.add((el.tag, oid))
                if "addr:flats" in element_tags(el):
                    problems.append(f"{el.tag} {oid} still carries addr:flats")
                if "version" not in el.attrib:
                    problems.append(f"{el.tag} {oid} has no version")
        if got_mod != want_mod or got_new != want_new:
            problems.append(f"{rec['path'].name}: file != manifest "
                            f"(modify {len(got_mod)}/{len(want_mod)}, "
                            f"new {len(got_new)}/{len(want_new)})")
    if problems:
        raise SystemExit("batch verification failed:\n  " + "\n  ".join(problems[:20]))
    print(f"  verified: {len(batch_of)} modified + {len(neg_seen)} new nodes, "
          f"files match manifest, no group split, no duplicate units")


if __name__ == "__main__":
    main()
