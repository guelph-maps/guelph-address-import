"""Campaign 1 leftovers - remove addr:province from the 33 objects the main
run refused, prepared for JOSM as one batch.

    python build_batches.py

The main run (../province-removal) batched 44,763 of the 44,796 and sent 33
to review.csv: 4 relations, which its tooling never batches, and 29 objects
with no addr:housenumber. Post #21 promised the tag off "anything that has
it - 44,796", so these are in the consented set; they were held back only so
a human could look first. They have been looked at (../review/index.html).

Unlike the main builder this fetches each object straight from the API, so
the versions are current. A relation is written with its member list and no
members: JOSM loads the members as incomplete, and uploading a tag change on
a relation with incomplete members sends the member list back untouched.

Nothing here uploads. Load with upload_loop.py and press Upload.
"""
from __future__ import annotations

import csv
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import _common as C  # noqa: E402

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "province-removal" / "review.csv"
LIVE = HERE / "live.osm"
API = "https://api.openstreetmap.org/api/0.6"
UA = {"User-Agent": "guelph-address-import province-leftovers (skfd)"}


def get(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return ET.fromstring(r.read())


def transform(tags: dict[str, str]) -> tuple[dict[str, str], dict]:
    before = tags.get("addr:province", "")
    return ({k: v for k, v in tags.items() if k != "addr:province"},
            {"before_province": before})


CAMPAIGN = C.Campaign(
    slug="province-leftovers",
    generator="guelph-province-leftovers",
    title="Guelph province removal - leftovers",
    blurb="The 33 objects campaign 1 held for a human: relations and objects "
          "with no housenumber. <code>addr:province</code> &rarr; removed.",
    comment=lambda where, i, n: (
        f"Guelph address tidy: remove addr:province - {where} [batch {i}/{n}]"),
    transform=transform,
    manifest_extra=["before_province"],
    review_reasons={},
)


def main() -> None:
    rows = list(csv.DictReader(open(SOURCE, encoding="utf-8")))
    root = ET.Element("osm", {"version": "0.6"})
    seen: set[tuple[str, str]] = set()

    def add(el: ET.Element) -> None:
        key = (el.tag, el.attrib["id"])
        if key not in seen:
            seen.add(key)
            root.append(el)

    nodes = [r["id"] for r in rows if r["type"] == "node"]
    for el in get(f"{API}/nodes?nodes={','.join(nodes)}"):
        add(el)
    for r in rows:
        if r["type"] == "way":
            for el in get(f"{API}/way/{r['id']}/full"):
                add(el)
        elif r["type"] == "relation":
            for el in get(f"{API}/relation/{r['id']}"):
                add(el)
    ET.ElementTree(root).write(LIVE, encoding="utf-8", xml_declaration=True)

    selected = {(el.tag, el.attrib["id"]): el for el in root
                if (el.tag, el.attrib["id"]) in {(r["type"], r["id"]) for r in rows}}
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    gone = [(r["type"], r["id"]) for r in rows
            if (r["type"], r["id"]) not in selected]
    items = []
    for (kind, oid), el in selected.items():
        tags = C.element_tags(el)
        if "addr:province" not in tags:
            print(f"  {kind} {oid}: addr:province already gone, skipped")
            continue
        items.append({"type": kind, "id": oid,
                      "street": tags.get("addr:street", ""),
                      "housenumber": tags.get("addr:housenumber", "")})
    if gone:
        print(f"  not returned by the API (deleted?): {gone}")

    batch = {"area": "relations and non-address objects", "part": 1, "of": 1,
             "items": sorted(items, key=lambda i: (i["type"], int(i["id"])))}
    for old in (HERE / "batches").glob("*.osm"):
        old.unlink()
    rec = C.write_batch(CAMPAIGN, HERE / "batches", batch, 1, 1,
                        selected, by_node_id)
    with open(HERE / "manifest.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["batch", "area", "type", "id", "version",
                                           "street", "housenumber", "before_province"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(rec["rows"])
    print(f"{rec['count']} objects -> {rec['path'].name}")
    print(f"comment: {rec['cs_tags']['comment']}")


if __name__ == "__main__":
    main()
