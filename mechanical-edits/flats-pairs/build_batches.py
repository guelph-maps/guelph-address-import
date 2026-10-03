"""Mechanical edit 5, catching up: a pair of units is `1;2`, not `1-2`.

Campaign 5 re-rendered every `addr:flats` value through the engine's
`t2.units.compress_flats`. Its batches were built at 20:58 on 2026-09-29; at
21:51 the engine learned that a range starts at three units (commit 34a40061,
`MIN_RANGE_UNITS`), because `5-6` is no shorter than `5;6` and reads as a span.
The batches were not rebuilt before the 2026-09-30 upload, so campaign 5 wrote
the old rendering onto 126 objects:

    addr:flats = 1-2           ->  1;2
    addr:flats = 101-102;201-202  ->  101;102;201;202
    addr:flats = 1-2;4-5;7     ->  1;2;4;5;7

Every run of three or more stays a range. Nothing else changes.

In Guelph a bare `1-2` has a second reading too: it is the shape of the
unit-civic housenumber that campaign 2 removed from 5,521 objects. A pair
written as `1;2` cannot be mistaken for it.

**How.** The same pipe as campaign 5 — `flats_parse.normalise`, which parses,
renders through the current engine, and refuses anything whose unit set does
not survive the round-trip. On top of that, one gate of its own: the rendering
must hold exactly the parts of the live value with its two-unit ranges spelled
out — in whatever order the renderer sorts them — and *nothing else* altered. A value the current renderer would change in some other way
(somebody edited it since 2026-09-30, or the engine moved again) goes to
review.csv as `not-only-pairs` rather than riding in under this notice.

Campaign 5's own directory is left alone: its manifest.csv and uploads.csv
are the revert record for 325 uploaded objects, and rebuilding there would
overwrite them.

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py
    ... build_batches.py --refetch    # pull OSM again first; do this on the day

Writes, under this directory: live.osm (cached fetch), batches/NN-<area>.osm,
manifest.csv (the revert record), review.csv, index.html (the run sheet).

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "flats-hygiene"))

import _runsheet  # noqa: E402
from _common import (AREA_ID, Campaign, assign_area, batchable, centre,  # noqa: E402
                     changed, element_tags, fetch_live, index_live,
                     load_areas, make_batches, promote_pilot, write_batch,
                     write_csvs)
from flats_parse import normalise  # noqa: E402

BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"
# Campaign 5's cached neighbourhood partition. Same areas, same batch names,
# so a reader can line the two run sheets up.
AREAS = HERE.parent / "flats-hygiene" / "areas.geojson"

QUERY = f"""
[out:xml][timeout:900];
area({AREA_ID})->.guelph;
nwr["addr:flats"](area.guelph);
out meta;
>;
out meta;
"""

# One range part, `LL01-LL02` or `101-102`: both ends under the same prefix,
# no suffix. The padding is kept exactly as written.
RANGE = re.compile(r"([A-Za-z]*)(\d+)-\1(\d+)")


def split_pairs(value: str) -> str:
    """The value with every two-unit range written as two designators, and
    every other part untouched — the whole of what this edit is allowed to do.
    """
    out = []
    for part in value.split(";"):
        m = RANGE.fullmatch(part)
        if m and int(m.group(3)) - int(m.group(2)) == 1:
            prefix, lo, hi = m.groups()
            out += [prefix + lo, prefix + hi]
        else:
            out.append(part)
    return ";".join(out)


def only_pairs(value: str, rendered: str) -> bool:
    """True when `rendered` holds exactly the parts of `split_pairs(value)`,
    in any order. Order is the renderer's to choose: once `101-102` is two
    designators, a suffixed `101A` sorts between them (511 Edinburgh Road
    South goes back to `101;101A;102;201;202`, its value before campaign 5).
    """
    return sorted(rendered.split(";")) == sorted(split_pairs(value).split(";"))


def classify(tags: dict[str, str]) -> tuple[str, str | None]:
    """(safe | review, reason). `safe` means the value parses, round-trips,
    and the current renderer changes it only by splitting pairs — or not at
    all, which `changed()` then drops as a no-op."""
    value = tags["addr:flats"]
    rendered, reason = normalise(value)
    if reason:
        return "review", f"flats-{reason}"
    if rendered != value and not only_pairs(value, rendered):
        return "review", "not-only-pairs"
    return "safe", None


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    """Pure. Tag order kept; only `addr:flats` can change."""
    new = dict(tags)
    before = new["addr:flats"]
    rendered, reason = normalise(before)
    if not reason and only_pairs(before, rendered):
        new["addr:flats"] = rendered
    return new, {"flats_before": before, "flats_after": new["addr:flats"]}


REVIEW_REASONS = {
    "not-only-pairs": (
        "The renderer would change more than the pairs",
        "Re-rendering this value does more than spell out a two-unit range "
        "— a mapper edited it since campaign 5, or the engine has moved "
        "again. That edit is not what this notice covers, so the object is "
        "left exactly as it is."),
    "flats-unparsed": (
        "<code>addr:flats</code> value not understood",
        "The parser refuses rather than guesses. Hand work."),
    "flats-round-trip": (
        "<code>addr:flats</code> failed its round-trip",
        "Re-reading the rendering named a different set of units, so the "
        "parser is wrong about this value. It is left alone."),
    "flats-too-long": (
        "Rendered <code>addr:flats</code> is over 255 characters",
        "Splitting a pair costs no characters, so this was already too long "
        "for the renderer and is not this edit's business."),
    "relation": (
        "A relation",
        "Never batched: <code>_common.batchable()</code> refuses relations."),
}

STEPS = [
    "<strong>Covered by post #21?</strong> #21 on "
    "<a href='https://community.openstreetmap.org/t/"
    "import-addresses-from-city-of-guelph-data/135103'>#135103</a> announced "
    "re-rendering every <code>addr:flats</code> value through the import's "
    "renderer. This is that renderer as it stood 53 minutes after the "
    "campaign-5 batches were built. Whether it needs a line on the thread "
    "first is skfd's call — see README.",
    "On the day: <code>build_batches.py --refetch</code>. The pair gate runs "
    "against whatever OSM holds that morning.",
    "Sign JOSM in as <code>skfd imports</code>.",
    "Batch 1 is the pilot. Upload it and check it with "
    "<code>../verify_changeset.py</code> before the rest.",
    "Then the rest, ticking each row here as it goes up.",
]

CAMPAIGN = Campaign(
    slug="flats-pairs",
    generator="guelph-address-import flats-pairs (mechanical edit 5, pairs)",
    title="Mechanical edit 5, pairs — <code>1-2</code> becomes <code>1;2</code>",
    blurb=("Spell out the two-unit ranges campaign 5 wrote into "
           "<code>addr:flats</code> before the renderer learned that a range "
           "starts at three. Runs of three or more are not touched."),
    comment=lambda where, index, total: (
        f"Guelph addresses: write two-unit addr:flats ranges as 1;2, not 1-2 "
        f"- {where} ({index}/{total})"),
    transform=transform,
    manifest_extra=["flats_before", "flats_after"],
    review_reasons=REVIEW_REASONS,
    steps=STEPS,
    sample=lambda row: f"{row['flats_before']} &rarr; {row['flats_after']}",
    review_columns=["flats"],
    max_per_batch=250,
    pilot_min=25,
)


def verify_modify_set(records: list[dict]) -> None:
    """Read the batch files back: every object marked `action="modify"` is in
    exactly one batch, and the marked set is the manifest. Campaign 1 found 58
    objects double-marked through shared child nodes before
    `_common.geometry_stub` existed; this is the check that caught them."""
    expected = {(row["type"], row["id"]) for rec in records for row in rec["rows"]}
    seen: dict[tuple[str, str], list[int]] = {}
    for rec in records:
        for el in ET.parse(rec["path"]).getroot():
            if el.attrib.get("action") == "modify":
                seen.setdefault((el.tag, el.attrib["id"]), []).append(rec["index"])
    dupes = {k: v for k, v in seen.items() if len(v) > 1}
    if dupes or set(seen) != expected:
        raise SystemExit(f"batch verification failed: {len(dupes)} double-marked, "
                         f"{len(set(seen) ^ expected)} differ from the manifest")
    print(f"  verified: {len(seen)} objects marked modify, each in one batch, "
          f"matching the manifest")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refetch", action="store_true",
                    help="pull the addr:flats set from Overpass again first")
    args = ap.parse_args()

    root = fetch_live(QUERY, LIVE, args.refetch, "addr:flats")
    selected, coords = index_live(root, lambda tags: "addr:flats" in tags)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    areas = load_areas(AREAS)
    print(f"{len(selected)} objects with addr:flats, {len(areas)} areas")

    safe: list[dict] = []
    review: list[dict] = []
    skipped = 0
    for (kind, oid), el in selected.items():
        tags = element_tags(el)
        cls, reason = classify(tags)
        if cls == "safe" and not batchable(kind):
            cls, reason = "review", "relation"
        lon, lat = centre(el, coords)
        record = {
            "type": kind, "id": oid,
            "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "flats": tags["addr:flats"],
            "area": assign_area(lon, lat, areas),
        }
        if cls == "review":
            record["reason"] = reason
            review.append(record)
            continue
        new_tags, _ = transform(tags)
        if not changed(tags, new_tags):
            skipped += 1
            continue
        safe.append(record)

    by_reason: dict[str, int] = {}
    for row in review:
        by_reason[row["reason"]] = by_reason.get(row["reason"], 0) + 1
    print(f"  {len(safe)} to change, {skipped} already right, {len(review)} "
          f"refused ({', '.join(f'{k} {v}' for k, v in sorted(by_reason.items()))})")

    batches = promote_pilot(make_batches(safe, CAMPAIGN.max_per_batch),
                            CAMPAIGN.pilot_min)
    # A rebuild can renumber; files left from the last one would share a
    # batch number with the new ones, and the upload loop loads by number.
    for old in BATCH_DIR.glob("*.osm"):
        old.unlink()
    records = []
    for index, batch in enumerate(batches, 1):
        print(f"  batch {index}/{len(batches)}: {batch['area']} "
              f"({len(batch['items'])} objects)")
        records.append(write_batch(CAMPAIGN, BATCH_DIR, batch, index,
                                   len(batches), selected, by_node_id))

    # The whole claim of this edit, checked on what was actually written.
    for rec in records:
        for row in rec["rows"]:
            assert only_pairs(row["flats_before"], row["flats_after"]), row
            assert row["flats_after"] != row["flats_before"], row
            assert len(row["flats_after"]) == len(row["flats_before"]), row

    verify_modify_set(records)
    write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp,
                           len(selected))
    print(f"\n{len(batches)} batches, {sum(r['count'] for r in records)} "
          f"objects, every change a pair split and no value longer")
    print(f"run sheet: {page}")
    print("NOT uploaded.")


if __name__ == "__main__":
    main()
