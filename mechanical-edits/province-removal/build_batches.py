"""Mechanical edit 1 - remove addr:province, prepared for JOSM.

    addr:province = Ontario   ->   (removed; nothing else touched)

Canadian convention omits the province, the Toronto import does not write it,
and the value is fully implied by the enclosing admin boundary. Consented on
thread #135103, 2026-09-10.

**Consent covers a number that turned out to be wrong.** The thread was told
"~3,699 Guelph objects"; the real figure is ~44,800, because 3,699 was a
sample count published as a census. See README.md. The edit itself is
unchanged and still right, but nothing here uploads until that correction is
on the thread.

Scope decisions this file makes, each visible in review.csv rather than
silent:

* **Relations are never batched.** `_common.batchable()` refuses them: this
  tooling fetches neither their members nor a position for them.
* **Objects outside the city polygon are refused.** The Overpass fetch uses
  `>;` to pull child nodes of matched ways, and that recursion crosses the
  boundary - Guelph abuts Guelph/Eramosa (see ERAMOSA_OVERLAP.md). ~148 nodes
  arrive that way. They are outside the consented area and go to review.
  "Unplaced" is *not* the same thing: that is inside the city, in the 0.53%
  the 23 area polygons do not cover, and still batches.
* **Objects with no `addr:housenumber` are refused.** Something carrying
  `addr:province` but no housenumber is a boundary or a `place=*` node, not an
  address. A human looks before it is stripped.
* **`ON` and `On` variants batch last, on their own.** The wiki section 1 says
  they come off on the same pass; the forum post names only `Ontario`. Keeping
  them in separate batches at the end of the run lets the operator upload the
  `Ontario` ones and hold the rest if the thread would rather.

    python build_batches.py                  # uses the cached fetch
    python build_batches.py --refetch        # pull OSM again first
    python build_batches.py --per-batch 2000 # one changeset per neighbourhood

Nothing here uploads. The operator opens each batch in JOSM, looks at it, and
presses upload.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from shapely.geometry import Point, shape  # noqa: E402
from shapely.prepared import prep  # noqa: E402

import _common as C  # noqa: E402
import _runsheet  # noqa: E402

HERE = Path(__file__).resolve().parent
BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"
CITY = HERE / "city.geojson"

# One query for the whole campaign. `>;` pulls the child nodes a way needs to
# render in JOSM; the classifier deals with the ones it drags in from over the
# boundary.
LIVE_QUERY = f"""
[timeout:900];
area({C.AREA_ID})->.a;
nwr["addr:province"](area.a);
out meta;
>;
out meta;
"""

# The consented value, and the two variants the wiki says come off with it.
PRIMARY = "Ontario"

REVIEW_REASONS = {
    "relation": (
        "Relations",
        "Never batched. This tooling fetches neither a relation's members nor "
        "a position for it, so batching one would upload an object whose "
        "geometry nobody looked at. Handle by hand, or leave."),
    "outside-city": (
        "Outside the city boundary",
        "Dragged in by the fetch's <code>&gt;;</code> recursion as a child "
        "node of a way that crosses the line - Guelph abuts Guelph/Eramosa. "
        "Outside the consented area, so outside this campaign."),
    "no-address": (
        "No housenumber",
        "Carries <code>addr:province</code> but no <code>addr:housenumber</code>: "
        "a boundary, a <code>place=*</code> node, something that is not an "
        "address. Worth a look before the tag is stripped."),
}


def load_city():
    if not CITY.exists():
        raise SystemExit(
            "city.geojson is missing - it is the outside-city guard and this "
            "builder will not run without it. Rebuild it with the snippet in "
            "README.md (one Overpass call for relation 7486148, out geom).")
    return prep(shape(json.loads(CITY.read_text(encoding="utf-8"))))


def select(tags: dict[str, str]) -> bool:
    return "addr:province" in tags


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    before = tags.get("addr:province", "")
    after = {k: v for k, v in tags.items() if k != "addr:province"}
    return after, {"before_province": before}


def comment(where: str, index: int, total: int) -> str:
    return (f"Guelph address tidy: remove addr:province - {where} "
            f"[batch {index}/{total}]")


def sample_html(row: dict) -> str:
    import html
    return (f"{html.escape(row['housenumber'])} {html.escape(row['street'])}: "
            f"addr:province={html.escape(row['before_province'])} &rarr; removed")


CAMPAIGN = C.Campaign(
    slug="province-removal",
    generator="guelph-province-removal",
    title="Guelph province removal",
    blurb=("Mechanical edit 1: <code>addr:province=Ontario</code> &rarr; removed. "
           "Canadian convention omits the province and the enclosing admin "
           "boundary already implies it. Nothing else on the object is touched."),
    comment=comment,
    transform=transform,
    manifest_extra=["before_province"],
    review_reasons=REVIEW_REASONS,
    sample=sample_html,
    review_columns=["province"],
    steps=[
        "<strong>Do not start.</strong> The thread was told this edit touches "
        "~3,699 objects. It touches ~44,800. Post the correction first - see "
        "README.md.",
        "Upload the pilot, then wait a day and look at what came back before "
        "doing the rest.",
        "The <code>ON</code> / <code>On</code> batches are last and separate. "
        "They are covered by the wiki but not named in the forum post; upload "
        "them only if the thread is content.",
        "Rebuild with <code>--refetch</code> on the day you upload. Versions "
        "prepared earlier will have moved, and a stale one costs you a "
        "conflict per object.",
    ],
    max_per_batch=600,
    pilot_min=25,
)


def main() -> None:
    ap = argparse.ArgumentParser(description="Build campaign 1 JOSM batches.")
    ap.add_argument("--refetch", action="store_true",
                    help="pull the addr:province set from Overpass again")
    ap.add_argument("--per-batch", type=int, default=CAMPAIGN.max_per_batch,
                    help=("objects per batch (default %(default)s, giving ~75 "
                          "changesets). Pass 2000 for one changeset per "
                          "neighbourhood, which is closer to what post #14 "
                          "literally promised but far coarser to revert."))
    args = ap.parse_args()
    CAMPAIGN.max_per_batch = args.per_batch

    root = C.fetch_live(LIVE_QUERY, LIVE, args.refetch,
                        "every object carrying addr:province in Guelph")
    selected, coords = C.index_live(root, select)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    areas = C.load_areas(HERE / "areas.geojson")
    city = load_city()
    print(f"{len(selected)} objects carry addr:province, "
          f"{len(coords)} node positions, {len(areas)} areas")

    safe: list[dict] = []
    review: list[dict] = []
    for (kind, oid), el in selected.items():
        tags = C.element_tags(el)
        lon, lat = C.centre(el, coords)
        record = {
            "type": kind, "id": oid,
            "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "province": tags.get("addr:province", ""),
            "area": C.assign_area(lon, lat, areas),
        }
        after, _ = transform(tags)
        if not C.batchable(kind):
            record["reason"] = "relation"
        elif lon is not None and not city.contains(Point(lon, lat)):
            record["reason"] = "outside-city"
        elif not tags.get("addr:housenumber"):
            record["reason"] = "no-address"
        elif not C.changed(tags, after):
            continue  # cannot happen while select() requires the key, but the
            # transform is the authority on whether this is an edit at all
        if "reason" in record:
            review.append(record)
        else:
            safe.append(record)

    primary = [r for r in safe if r["province"] == PRIMARY]
    variants = [r for r in safe if r["province"] != PRIMARY]
    by_reason = {k: sum(1 for r in review if r["reason"] == k)
                 for k in REVIEW_REASONS}
    print(f"  {len(primary)} '{PRIMARY}', {len(variants)} variants "
          f"({sorted({r['province'] for r in variants})}), "
          f"{len(review)} refused "
          f"({', '.join(f'{k} {v}' for k, v in by_reason.items() if v)})")

    # Ontario first and pilot-promoted; the variants trail as their own
    # batches so they can be held back without unpicking anything.
    batches = C.promote_pilot(
        C.make_batches(primary, CAMPAIGN.max_per_batch), CAMPAIGN.pilot_min)
    batches += C.make_batches(variants, CAMPAIGN.max_per_batch)

    total = len(batches)
    records = []
    for index, batch in enumerate(batches, 1):
        print(f"  batch {index}/{total}: {batch['area']} "
              f"({len(batch['items'])} objects)")
        records.append(C.write_batch(CAMPAIGN, BATCH_DIR, batch, index, total,
                                     selected, by_node_id))

    C.write_csvs(HERE, CAMPAIGN, records, review)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    page = _runsheet.write(HERE, CAMPAIGN, records, review, stamp, len(selected))
    print(f"\n{total} batches, {sum(r['count'] for r in records)} objects, "
          f"{len(review)} left for hand review")
    print(f"run sheet: {page}")


if __name__ == "__main__":
    main()
