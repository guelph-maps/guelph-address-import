"""Mechanical edits 4 and 5 — addr:flats hygiene, prepared for JOSM.

Two edits, one builder, one batch set, one revert:

    addr:interpolation = all   ->  (removed)      on closed ways and nodes only
    addr:flats = 101;102;103;  ->  101-103        re-rendered through the engine

They are merged deliberately. 74 of the 81 objects carrying a meaningless
`addr:interpolation` also carry `addr:flats` — 71 of the 78 closed ways, and
all 3 of the nodes — so building them as two campaigns
would have the second one conflicting against the first on object version, and
would announce twice what a reader sees as one cleanup of the same apartment
buildings.

**Consent is PENDING.** The notice is drafted in ANNOUNCEMENT.md beside this
file and has not been posted to thread #135103. Nothing here may be uploaded
until it is up. The run sheet says so in a banner; this is the same sentence.
On the day of upload the batches are rebuilt with --refetch, because the
versions prepared against today will have moved.

What is in scope, re-measured against live OSM on 2026-09-17:

    addr:flats                464 objects (45 nodes, 419 ways) — all of them
    addr:interpolation        635 objects, of which exactly 81 are in scope:
                                78 closed ways + 3 nodes
                              The other 554 are left strictly alone —
                                405 two-node open ways, which are real
                                    interpolation and correctly tagged
                                149 open ways with 3+ nodes, which want a
                                    different check (do both ends carry a
                                    housenumber?) and are not this campaign
                              Both appear in review.csv and on the run sheet,
                              so "not touched" is visible rather than implied.

A closed way is a polygon: it has no two ends to interpolate between, and its
corners are geometry that will never carry housenumbers. That is what JOSM's
"End node without housenumber in address interpolation" warning is about, and
it is the same mistake campaign 3 fixed under a different key.

The `addr:flats` half re-renders through `t2.units.compress_flats` — the
engine's own renderer, the one the continuous import already writes every
collapsed building through. The only new code is `flats_parse.py`, and every
value is gated on a round-trip: parse, render, parse the rendering, and refuse
the object unless the unit *set* is identical. A value that changes which
units a building claims is data corruption, not cosmetics. Anything that fails
goes to review.csv and never into a batch.

Everything else — the fetch, the 23-area partition, live versions on every
element, relations refused, no-op edits dropped — comes from ../_common.py.

    python build_batches.py              # uses the cached fetch if present
    python build_batches.py --refetch    # pull OSM again first

Needs `requests` and `shapely` for ../_common.py, and the address-importer-
friend checkout for the renderer:

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py

What it writes, all under this directory:

    live.osm                the raw fetch, cached
    batches/NN-<area>.osm   one JOSM-ready layer per batch
    manifest.csv            the revert record — every edited object with the
                            version it was prepared against and both values
    review.csv              everything refused, with the reason
    index.html              the run sheet: one remote-control link per batch

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import _common  # noqa: E402
import _runsheet  # noqa: E402
from _common import (AREA_ID, Campaign, assign_area, batchable, centre,  # noqa: E402
                     changed, element_tags, fetch_live, index_live,
                     load_areas, make_batches, promote_pilot, write_batch,
                     write_csvs)
from flats_parse import normalise  # noqa: E402

BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"
AREAS = HERE / "areas.geojson"

# One query for both halves. `out meta` twice so the selected objects and the
# child nodes a way needs for geometry both carry their live version — JOSM
# raises a conflict on a stale one rather than overwriting somebody.
QUERY = f"""
[out:xml][timeout:900];
area({AREA_ID})->.guelph;
(
  nwr["addr:flats"](area.guelph);
  nwr["addr:interpolation"](area.guelph);
);
out meta;
>;
out meta;
"""

# The shapes `addr:interpolation` can mean something on. Everything else keeps
# its tag: a two-node open way is real interpolation, and a longer open way is
# legal in principle and wants a check this campaign is not making.
SCOPE = ("node", "closed")

# `_common`'s contract hands `classify` and `transform` a tag dict and nothing
# else, but campaign 4's whole rule is geometric — is this way closed? So the
# shape is carried in on a private key, injected onto the parsed element before
# classification and stripped by `transform` before anything is written.
# `verify_batches` below asserts no key starting with `_` reaches a file.
# Reported as a gap in ../_common.py rather than fixed there, since it is
# frozen to a campaign.
SHAPE_KEY = "_shape"


def shape_of(el: ET.Element) -> str:
    """node | closed | open2 | openN | relation — the only thing geometric
    this campaign asks.

    A closed way needs three distinct corners before it is a polygon; a
    two-node way whose ends coincide is broken geometry, and lands in `openN`
    with the rest of the out-of-scope ways rather than being edited.
    """
    if el.tag != "way":
        return el.tag
    refs = [nd.attrib["ref"] for nd in el.findall("nd")]
    if len(refs) >= 3 and refs[0] == refs[-1]:
        return "closed"
    if len(refs) == 2 and refs[0] != refs[1]:
        return "open2"
    return "openN"


def select(tags: dict[str, str]) -> bool:
    """Everything either half might touch, in one fetch.

    Wider than what gets edited on purpose: the 554 out-of-scope
    interpolation ways are selected so they can be *counted and shown* as
    untouched. "We left 554 alone" is a claim the announcement makes, and it
    should be a row in review.csv rather than an assertion.
    """
    return "addr:flats" in tags or "addr:interpolation" in tags


def classify(tags: dict[str, str]) -> tuple[str, str | None]:
    """Return (class, review_reason).

    safe       there is something to do here — an `addr:flats` value that
               parses and round-trips, or an `addr:interpolation` on a shape
               that cannot interpolate. Whether it actually *changes* is
               `changed()`'s question, not this one.
    review     left alone; the reason says whose problem it is:
               relation             never batched, `_common.batchable` refuses
                                    them: no geometry this module fetched
               interpolation-live   a two-node open way. Real interpolation,
                                    correctly tagged, explicitly not in scope
               interpolation-multinode
                                    an open way with 3+ nodes. Legal in
                                    principle; wants "do both ends carry a
                                    housenumber?", which is a different edit
               flats-unparsed       the value was not understood
               flats-round-trip     it parsed, but re-reading the rendering
                                    named different units. The parser is wrong
                                    about this value
               flats-too-long       the rendering is past OSM's 255-character
                                    tag limit

    An object that both carries an unreadable `addr:flats` and an out-of-scope
    `addr:interpolation` is refused whole rather than half-edited: one object,
    one edit, one revert. After the engine's padding fix that case is empty —
    see README — so nothing is actually deferred by this rule today.
    """
    shape = tags.get(SHAPE_KEY, "")
    if shape == "relation":
        return "review", "relation"
    value = tags.get("addr:flats")
    if value is not None:
        _rendered, reason = normalise(value)
        if reason:
            return "review", f"flats-{reason}"
        return "safe", None
    # No addr:flats at all: the object is in the fetch for its interpolation.
    if shape in SCOPE:
        return "safe", None
    return "review", ("interpolation-live" if shape == "open2"
                      else "interpolation-multinode")


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Both halves, on one object. Pure; `new_tags` replaces the tags wholesale.

    Tag order is preserved, and no key is added. The only removal is
    `addr:interpolation`, and only where the shape cannot interpolate.
    """
    shape = tags.get(SHAPE_KEY, "")
    new = {k: v for k, v in tags.items() if k != SHAPE_KEY}
    extra = {"shape": shape, "flats_before": new.get("addr:flats", ""),
             "flats_after": new.get("addr:flats", ""),
             "interpolation_removed": "", "edit": ""}

    edits = []
    if shape in SCOPE and "addr:interpolation" in new:
        extra["interpolation_removed"] = new.pop("addr:interpolation")
        edits.append("interpolation")
    if "addr:flats" in new:
        rendered, reason = normalise(new["addr:flats"])
        # classify() has already refused anything with a reason; this is the
        # belt to its braces, and it leaves the value alone rather than
        # guessing.
        if not reason and rendered != new["addr:flats"]:
            new["addr:flats"] = rendered
            extra["flats_after"] = rendered
            edits.append("flats")
    extra["edit"] = "+".join(edits)
    return new, extra


REVIEW_REASONS = {
    "interpolation-live": (
        "Real interpolation — a two-node way, left alone",
        "The 405 ways this campaign is <em>not</em> touching, listed so that "
        "is checkable rather than promised. A way drawn between two address "
        "nodes is exactly what <code>addr:interpolation</code> is for, and "
        "these are tagged correctly."),
    "interpolation-multinode": (
        "Open way with three or more nodes — out of scope",
        "Legal in principle: an interpolation way may have intermediate "
        "nodes. Whether these are <em>right</em> wants a different question — "
        "do both ends carry <code>addr:housenumber</code>? — and that is not "
        "the check this edit makes. Left for a later pass."),
    "flats-unparsed": (
        "<code>addr:flats</code> value not understood",
        "The parser refuses rather than guesses. A value with a designator it "
        "cannot read (<code>PH-2</code>, a backwards range, a range spanning "
        "two prefixes) is hand work, and normalising it blind is how a "
        "cosmetic edit becomes a data-losing one."),
    "flats-round-trip": (
        "<code>addr:flats</code> failed its round-trip",
        "The value parsed, but re-reading its normalised form named a "
        "different set of units. That is the parser being wrong about this "
        "value, so the object is left exactly as it is and the parser wants "
        "a case adding. This row should be empty; see "
        "<a href='{thread}'>#135103</a> if it is not."),
    "flats-too-long": (
        "Normalised <code>addr:flats</code> is over 255 characters",
        "OSM refuses a tag value longer than 255, so this cannot be uploaded "
        "at all. Normalising shortens, so reaching this means the value "
        "compresses worse than it was written."),
    "relation": (
        "A relation",
        "Never batched. <code>_common.batchable()</code> refuses relations: "
        "this builder fetches neither their members nor a position, so "
        "batching one would upload an object whose geometry nobody looked "
        "at."),
}

STEPS = [
    "<strong>Do not start.</strong> <code>ANNOUNCEMENT.md</code> has not been "
    "posted to <a href='https://community.openstreetmap.org/t/"
    "import-addresses-from-city-of-guelph-data/135103'>#135103</a> yet.",
    "On the day: <code>build_batches.py --refetch</code>, then "
    "<code>python test_flats_parse.py</code>. The round-trip runs against "
    "whatever OSM holds that morning, not against today's cache.",
    "Sign JOSM in as <code>skfd imports</code>.",
    "Batch 1 is the pilot. Upload it, then post its count and changeset "
    "number to the thread before anything else moves.",
    "Then the rest, ticking each row here as it goes up.",
]


CAMPAIGN = Campaign(
    slug="flats-hygiene",
    generator="guelph-address-import flats-hygiene (mechanical edit 4+5)",
    title="Mechanical edit 4+5 — addr:flats hygiene",
    blurb=("Drop <code>addr:interpolation</code> where a polygon or a node "
           "cannot interpolate (81 objects), and re-render every "
           "<code>addr:flats</code> value through the import's own renderer. "
           "The 405 real interpolation ways are not touched."),
    comment=lambda where, index, total: (
        f"Guelph addresses: tidy addr:flats, drop addr:interpolation from "
        f"closed ways and nodes - {where} ({index}/{total})"),
    transform=transform,
    manifest_extra=["edit", "shape", "flats_before", "flats_after",
                    "interpolation_removed"],
    review_reasons=REVIEW_REASONS,
    steps=STEPS,
    sample=lambda row: (
        f"{row['flats_before']} &rarr; {row['flats_after']}"
        if row.get("flats_before") and row["flats_before"] != row["flats_after"]
        else (f"addr:interpolation={row['interpolation_removed']} removed"
              if row.get("interpolation_removed") else "")),
    review_columns=["flats", "interpolation", "shape"],
    max_per_batch=250,
    pilot_min=25,
)


def verify_batches(records: list[dict]) -> None:
    """Read back what was written and check the two things that can go wrong.

    1. **No private key reached a file.** `SHAPE_KEY` is a workaround, and a
       workaround that leaks would upload a junk tag to 292 objects.
    2. **No object is marked `action="modify"` in two batches.** The elements
       are shared between batches — `selected` and `by_node_id` hand out the
       same `Element` for a node that is both a campaign item and some way's
       child — and campaign 1 found 58 objects double-marked that way before
       `_common.geometry_stub` was added. Re-checking here is cheap, and the
       assertion is the one that caught it.

    Raises rather than warns: a batch set that fails either of these must not
    be opened in JOSM.
    """
    expected = {(row["type"], row["id"])
                for rec in records for row in rec["rows"]}
    seen: dict[tuple[str, str], list[int]] = {}
    leaks: list[str] = []
    for rec in records:
        root = ET.parse(rec["path"]).getroot()
        for el in root:
            if el.tag not in ("node", "way", "relation"):
                continue
            for tag in el.findall("tag"):
                if tag.attrib["k"].startswith("_"):
                    leaks.append(f"{rec['path'].name}: {el.tag} "
                                 f"{el.attrib['id']} {tag.attrib['k']}")
            if el.attrib.get("action") == "modify":
                seen.setdefault((el.tag, el.attrib["id"]), []).append(
                    rec["index"])

    problems = []
    if leaks:
        problems.append(f"private keys written to a batch: {leaks[:5]}")
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    if dupes:
        problems.append(f"{len(dupes)} objects marked modify in more than one "
                        f"batch: {list(dupes.items())[:5]}")
    if set(seen) != expected:
        problems.append(
            f"modify set != manifest: {len(set(seen) - expected)} marked but "
            f"unlisted, {len(expected - set(seen))} listed but unmarked")
    if problems:
        raise SystemExit("batch verification failed:\n  " +
                         "\n  ".join(problems))
    print(f"  verified: {len(seen)} objects marked modify, each in exactly "
          f"one batch, matching {len(expected)} manifest rows; "
          f"no private keys written")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refetch", action="store_true",
                    help="pull the addr:flats / addr:interpolation set from "
                         "Overpass again before building")
    args = ap.parse_args()

    root = fetch_live(QUERY, LIVE, args.refetch, "addr:flats + "
                                                 "addr:interpolation")
    selected, coords = index_live(root, select)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    areas = load_areas(AREAS)
    print(f"{len(selected)} objects selected, {len(coords)} node positions, "
          f"{len(areas)} areas")

    safe: list[dict] = []
    review: list[dict] = []
    shapes: dict[str, int] = {}
    skipped = 0
    for (kind, oid), el in selected.items():
        shape = shape_of(el)
        shapes[shape] = shapes.get(shape, 0) + 1
        # The shape rides in on the element so `classify`/`transform` can see
        # it through `_common`'s tags-only contract. `transform` strips it.
        ET.SubElement(el, "tag", k=SHAPE_KEY, v=shape)
        tags = element_tags(el)
        before = {k: v for k, v in tags.items() if k != SHAPE_KEY}

        cls, reason = classify(tags)
        if cls == "safe" and not batchable(kind):
            cls, reason = "review", "relation"
        lon, lat = centre(el, coords)
        record = {
            "type": kind, "id": oid, "shape": shape,
            "street": before.get("addr:street", ""),
            "housenumber": before.get("addr:housenumber", ""),
            "flats": before.get("addr:flats", ""),
            "interpolation": before.get("addr:interpolation", ""),
            "area": assign_area(lon, lat, areas),
        }
        if cls == "review":
            record["reason"] = reason
            review.append(record)
            continue

        new_tags, _extra = transform(tags)
        if not changed(before, new_tags):
            # Already tidy and nothing to drop. A no-op edit still burns a
            # version and a changeset comment, so it is dropped rather than
            # uploaded — and it is not a refusal either, so it does not
            # belong in review.csv.
            skipped += 1
            continue
        safe.append(record)

    print("  shapes: " + ", ".join(f"{k} {v}" for k, v in sorted(shapes.items())))
    by_reason: dict[str, int] = {}
    for row in review:
        by_reason[row["reason"]] = by_reason.get(row["reason"], 0) + 1
    print(f"  {len(safe)} to change, {skipped} already correct (skipped), "
          f"{len(review)} refused "
          f"({', '.join(f'{k} {v}' for k, v in sorted(by_reason.items()))})")
    flats_edits = sum(1 for r in safe if r["flats"])
    interp_edits = sum(1 for r in safe
                       if r["interpolation"] and r["shape"] in SCOPE)
    print(f"  of those: {flats_edits} carry addr:flats, "
          f"{interp_edits} lose addr:interpolation")

    batches = promote_pilot(make_batches(safe, CAMPAIGN.max_per_batch),
                            CAMPAIGN.pilot_min)
    total = len(batches)
    records = []
    for index, batch in enumerate(batches, 1):
        print(f"  batch {index}/{total}: {batch['area']} "
              f"({len(batch['items'])} objects)")
        records.append(write_batch(CAMPAIGN, BATCH_DIR, batch, index, total,
                                   selected, by_node_id))

    verify_batches(records)
    write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp,
                           len(selected))

    longest = max((len(r["flats_after"]) for rec in records
                   for r in rec["rows"] if r["flats_after"]), default=0)
    was = max((len(r["flats_before"]) for rec in records
               for r in rec["rows"] if r["flats_before"]), default=0)
    print(f"\n{total} batches, {sum(r['count'] for r in records)} objects, "
          f"{len(review)} left for hand review")
    print(f"longest addr:flats value: {was} chars before, {longest} after "
          f"(OSM's limit is 255)")
    print(f"run sheet: {page}")
    print("Consent is PENDING — ANNOUNCEMENT.md is not posted. Nothing "
          "uploads.")


if __name__ == "__main__":
    main()
