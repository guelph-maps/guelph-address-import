"""Shared machinery for Guelph's mechanical-edit batch builders.

Campaigns 2 and 3 each grew their own 700-line `build_batches.py`, and about
half of each was the same code: ask Overpass politely, cut the city into its
23 areas, write one JOSM-ready `.osm` per batch carrying the live version of
every object, and render a run sheet. Campaigns 1 and 4+5 import that half
from here instead of copying it a third and fourth time.

**The two finished campaigns are deliberately not ported to this module.**
`unit-split/build_batches.py` and `unit-listing-retag/build_batches.py` are the
record of what actually ran against OSM in September 2026; rewriting them to
import a module written afterwards would turn that record into a
reconstruction. They stay as they are.

This module is **frozen** as far as a campaign is concerned: a campaign wires
it up and supplies its own `select` / `classify` / `transform`, and if
something here does not fit, the fix belongs here for everyone rather than
worked around in one campaign.

What a campaign supplies:

    select(tags)     -> bool           is this object in the campaign at all?
    classify(tags)   -> (cls, reason)  "safe" to batch, or "review" and why
    transform(tags)  -> (new_tags, manifest_extra)
                                       the edit itself, pure; `new_tags`
                                       replaces the object's tags wholesale

What this module guarantees, because every campaign needs it identically:

* every batched element carries its **live `version`**, so a stale one raises
  a JOSM conflict instead of overwriting somebody;
* **relations are never batched** — `batchable()` refuses them, and a campaign
  routes them to `review.csv` with reason `relation`;
* one batch is one area is one changeset is one revert;
* a transform that changes nothing is **dropped, not uploaded** — a no-op edit
  still burns a version and a changeset comment. `changed()` is the check.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable
from xml.etree import ElementTree as ET

import requests
from shapely.geometry import Point, shape
from shapely.prepared import prep

HERE = Path(__file__).resolve().parent

# Guelph is single-tier: the city boundary is admin_level 6, relation 7486148.
# admin_level 8 returns nothing here, which has cost an afternoon before.
AREA_ID = 3607486148
OVERPASS = "https://overpass-api.de/api/interpreter"
STATUS = "https://overpass-api.de/api/status"
UA = ("guelph-address-import/1.0 (mechanical-edit prep; "
      "toronto@comentality.com)")

# The 23 "Guelph Areas" polygons - the same partition the import uses, and the
# one every announcement so far has promised batches would follow.
NEIGHBOURHOODS_URL = (
    "https://gismaps.guelph.ca/hosting/rest/services/OpenData/OpenData2"
    "/FeatureServer/17/query?where=1%3D1&outFields=AREA_NAME,CSDNAME"
    "&outSR=4326&f=geojson"
)
NAME_FIELD = "AREA_NAME"

WIKI = "https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous"
WIKI_SECTION = WIKI + "#Mechanical_edits"
THREAD = ("https://community.openstreetmap.org/t/"
          "import-addresses-from-city-of-guelph-data/135103")


# ---------------------------------------------------------------- fetching

def wait_for_slot() -> None:
    """Overpass gives an IP two slots. Ask before knocking.

    /api/status reports when the next one frees; sleeping that out is both
    faster and politer than retrying into a 429. Campaign 2's first version
    asked Overpass once per batch and got itself rate-limited for it.
    """
    try:
        text = requests.get(STATUS, headers={"User-Agent": UA}, timeout=60).text
    except requests.RequestException:
        return
    if re.search(r"(\d+) slots available now", text):
        return
    waits = [int(m) for m in re.findall(r"in (\d+) seconds", text)]
    if not waits:
        return
    delay = min(waits) + 2
    print(f"    Overpass slots busy - waiting {delay}s")
    time.sleep(delay)


def fetch_live(query: str, cache: Path, refetch: bool, what: str) -> ET.Element:
    """One query for the whole campaign, cached on disk. Never per batch."""
    if refetch or not cache.exists():
        print(f"fetching {what} from Overpass (one query, a few minutes)...")
        last = None
        for attempt in range(5):
            wait_for_slot()
            try:
                resp = requests.post(
                    OVERPASS, data={"data": query},
                    headers={"User-Agent": UA,
                             "Accept": "application/xml, text/xml, */*"},
                    timeout=960,
                )
                resp.raise_for_status()
                cache.write_bytes(resp.content)
                break
            except Exception as exc:  # noqa: BLE001 - Overpass fails variously
                last = exc
                print(f"    attempt {attempt + 1}: {exc}", file=sys.stderr)
                time.sleep(60)
        else:
            raise SystemExit(f"Overpass would not serve the fetch: {last}")
    size = cache.stat().st_size / 1e6
    print(f"parsing {cache.name} ({size:.1f} MB)")
    return ET.parse(cache).getroot()


def load_areas(cache: Path) -> list[tuple[str, object]]:
    if not cache.exists():
        print("fetching the 23 Guelph Areas polygons...")
        resp = requests.get(NEIGHBOURHOODS_URL, headers={"User-Agent": UA},
                            timeout=120)
        resp.raise_for_status()
        cache.write_text(resp.text, encoding="utf-8")
    gj = json.loads(cache.read_text(encoding="utf-8"))
    return [((feat.get("properties") or {}).get(NAME_FIELD) or "Unnamed",
             prep(shape(feat["geometry"])))
            for feat in gj["features"]]


# --------------------------------------------------------------- the fetch

def element_tags(el: ET.Element) -> dict[str, str]:
    return {t.attrib["k"]: t.attrib["v"] for t in el.findall("tag")}


def index_live(root: ET.Element,
               select: Callable[[dict[str, str]], bool]) -> tuple[dict, dict]:
    """Split the fetch into the objects the campaign wants and every node
    position, the latter so a way can be given a centre to place it in an area.
    """
    selected: dict[tuple[str, str], ET.Element] = {}
    coords: dict[str, tuple[float, float]] = {}
    for el in root:
        if el.tag == "node":
            try:
                coords[el.attrib["id"]] = (float(el.attrib["lon"]),
                                           float(el.attrib["lat"]))
            except (KeyError, ValueError):
                pass
        if el.tag in ("node", "way", "relation") and select(element_tags(el)):
            selected[(el.tag, el.attrib["id"])] = el
    return selected, coords


def batchable(kind: str) -> bool:
    """Relations are never written into a batch.

    `write_batch` emits nodes and their parent ways; a relation has neither a
    position this module can compute nor members it fetches, so batching one
    would upload an object whose geometry nobody looked at. They go to review.
    """
    return kind in ("node", "way")


def changed(before: dict[str, str], after: dict[str, str]) -> bool:
    """A transform that returns the tags it was given is not an edit."""
    return before != after


def centre(el: ET.Element, coords: dict) -> tuple[float | None, float | None]:
    if el.tag == "node":
        return coords.get(el.attrib["id"], (None, None))
    pts = [coords[nd.attrib["ref"]] for nd in el.findall("nd")
           if nd.attrib["ref"] in coords]
    if not pts:
        return None, None
    return (sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts))


def assign_area(lon, lat, areas) -> str:
    """The polygons cover 99.47% of the city's points (probed 2026-08-15); the
    rest get a named bucket rather than being dropped on the floor."""
    if lon is None:
        return "Unplaced"
    pt = Point(lon, lat)
    for name, poly in areas:
        if poly.contains(pt):
            return name
    return "Unplaced"


# ---------------------------------------------------------------- batching

def make_batches(rows: list[dict], max_per_batch: int) -> list[dict]:
    """One batch per area, split at `max_per_batch` along street boundaries.

    Areas come smallest-first so batch 1 - the pilot every announcement so far
    has promised to post before anything else moves - is one a human can
    finish in a sitting. Within a batch, rows sort by street then number so
    the JOSM layer reads in an order a reviewer can follow.
    """
    by_area: dict[str, list[dict]] = {}
    for row in rows:
        by_area.setdefault(row["area"], []).append(row)

    batches: list[dict] = []
    for area in sorted(by_area, key=lambda a: (len(by_area[a]), a)):
        items = sorted(by_area[area],
                       key=lambda r: (r["street"], r["housenumber"], r["id"]))
        chunks = [items[i:i + max_per_batch]
                  for i in range(0, len(items), max_per_batch)]
        for part, chunk in enumerate(chunks, 1):
            batches.append({"area": area, "part": part, "of": len(chunks),
                            "items": chunk})
    return batches


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "area"


def batch_path(batch_dir: Path, index: int, batch: dict) -> Path:
    suffix = "" if batch["of"] == 1 else f"-p{batch['part']}"
    return batch_dir / f"{index:02d}-{slug(batch['area'])}{suffix}.osm"


def promote_pilot(batches: list[dict], pilot_min: int) -> list[dict]:
    """Move the first whole-area batch of at least `pilot_min` objects to the
    front. A pilot of four objects proves nothing; one of forty does."""
    pilot = next((i for i, b in enumerate(batches)
                  if b["of"] == 1 and len(b["items"]) >= pilot_min), None)
    if pilot is not None:
        batches.insert(0, batches.pop(pilot))
    return batches


# ----------------------------------------------------------------- writing

def rewrite_tags(el: ET.Element, tags: dict[str, str]) -> None:
    for tag in el.findall("tag"):
        el.remove(tag)
    for key, value in tags.items():
        ET.SubElement(el, "tag", k=key, v=value)


@dataclass
class Campaign:
    """Everything that differs between one mechanical edit and another."""
    slug: str                      # directory name, and the localStorage key
    generator: str                 # <osm generator="...">
    title: str                     # run sheet <h1>
    blurb: str                     # run sheet subtitle, HTML
    comment: Callable[[str, int, int], str]   # (where, index, total) -> text
    transform: Callable[[dict[str, str]], tuple[dict[str, str], dict]]
    manifest_extra: list[str]      # extra manifest columns transform returns
    review_reasons: dict[str, tuple[str, str]]
    steps: list[str] = field(default_factory=list)
    sample: Callable[[dict], str] = lambda row: ""
    review_columns: list[str] = field(default_factory=list)
    max_per_batch: int = 250
    pilot_min: int = 25


def changeset_tags(camp: Campaign, batch: dict,
                   index: int, total: int) -> dict[str, str]:
    """The published table (section Changeset tags), with `import=yes` replaced
    by `mechanical=yes` and `import_plan` pointing at section Mechanical edits.

    `created_by` is deliberately absent: JOSM stamps its own on upload and
    overwrites anything put here. `import:client_token` is absent too - it
    exists for the engine's idempotent retry, and JOSM is doing the uploading.
    """
    where = (batch["area"] if batch["of"] == 1
             else f"{batch['area']} {batch['part']}/{batch['of']}")
    return {
        "comment": camp.comment(where, index, total),
        "source": "Guelph Open Data",
        "source:license": "OGL-Canada-2.0",
        "mechanical": "yes",
        "bot": "no",
        "import_plan": WIKI_SECTION,
    }


def geometry_stub(node: ET.Element) -> ET.Element:
    """A way's child node, reduced to the reference geometry JOSM needs.

    Child nodes are in a batch so JOSM can draw the way, nothing more. They
    must not carry `action`, and they must not carry tags, for one reason:
    **the element objects are shared between batches.** `selected` and
    `by_node_id` hand out the same `Element` for a node that is both a
    campaign item and some way's child, so the moment one batch transforms it
    and stamps `action="modify"`, every *other* batch that pulls it in as
    geometry inherits both - and uploads the same edit a second time, in a
    second changeset, against a version the first upload already bumped.

    Campaign 1 hit this: 58 nodes were marked `action="modify"` in two batches
    each. Copying id, version and position and dropping the rest makes a
    child node inert, which is all it was ever meant to be.
    """
    keep = {k: node.attrib[k] for k in ("id", "version", "lat", "lon")
            if k in node.attrib}
    return ET.Element("node", keep)


def write_batch(camp: Campaign, batch_dir: Path, batch: dict, index: int,
                total: int, selected: dict, by_node_id: dict) -> dict:
    """Emit one .osm. Returns the record the manifest and run sheet need."""
    out = ET.Element("osm", {"version": "0.6", "generator": camp.generator})
    # JOSM reads a <changeset> child into the layer and pre-fills the upload
    # dialog from it (OsmReader -> ds.addChangeSetTag, then
    # UploadDialog.initLifeCycle). No `id` attribute: JOSM accepts the element
    # only when its id equals the root's `upload-changeset`, and null == null
    # is the match a hand-built file wants. Only `.osm` does this - the same
    # tags in an `.osc` are ignored.
    cs_tags = changeset_tags(camp, batch, index, total)
    cs = ET.SubElement(out, "changeset")
    for key, value in cs_tags.items():
        ET.SubElement(cs, "tag", k=key, v=value)

    # The nodes this batch is actually editing. A way child that is also an
    # item here must be written in full, not stubbed.
    item_nodes = {item["id"] for item in batch["items"]
                  if item["type"] == "node"}

    rows: list[dict] = []
    nodes: list[ET.Element] = []
    ways: list[ET.Element] = []
    seen_nodes: set[str] = set()
    for item in batch["items"]:
        el = selected[(item["type"], item["id"])]
        tags = element_tags(el)
        new_tags, extra = camp.transform(tags)
        rewrite_tags(el, new_tags)
        el.set("action", "modify")
        if el.tag == "way":
            ways.append(el)
            for nd in el.findall("nd"):
                ref = nd.attrib["ref"]
                if ref not in seen_nodes and ref in by_node_id:
                    seen_nodes.add(ref)
                    if ref in item_nodes:
                        nodes.append(selected[("node", ref)])
                    else:
                        nodes.append(geometry_stub(by_node_id[ref]))
        else:
            if el.attrib["id"] not in seen_nodes:
                seen_nodes.add(el.attrib["id"])
                nodes.append(el)
            else:
                # Already added as some way's child, before we knew it was an
                # item. Swap the stub for the real, edited element.
                nodes[:] = [el if n.attrib.get("id") == el.attrib["id"] else n
                            for n in nodes]
        rows.append({
            "batch": index, "area": batch["area"], "type": item["type"],
            "id": item["id"], "version": el.attrib.get("version", ""),
            "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            **extra,
        })

    # Nodes first so JOSM has the referenced geometry when it parses the ways.
    for el in nodes + ways:
        out.append(el)

    batch_dir.mkdir(parents=True, exist_ok=True)
    path = batch_path(batch_dir, index, batch)
    ET.ElementTree(out).write(path, encoding="utf-8", xml_declaration=True)
    return {"index": index, "area": batch["area"], "part": batch["part"],
            "of": batch["of"], "path": path, "count": len(rows),
            "rows": rows, "cs_tags": cs_tags,
            "streets": sorted({r["street"] for r in rows if r["street"]}),
            "sample": rows[0] if rows else None}


def write_csvs(here: Path, camp: Campaign, records: list[dict],
               review: list[dict]) -> None:
    """manifest.csv is the revert record; review.csv is everything refused."""
    base = ["batch", "area", "type", "id", "version", "street", "housenumber"]
    with (here / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=base + camp.manifest_extra,
                                extrasaction="ignore")
        writer.writeheader()
        for rec in records:
            writer.writerows(rec["rows"])
    cols = (["type", "id", "street", "housenumber"]
            + [c for c in camp.review_columns
               if c not in ("street", "housenumber")]
            + ["area", "reason"])
    with (here / "review.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(
            review, key=lambda r: (r.get("street", ""),
                                   r.get("housenumber", ""))))
