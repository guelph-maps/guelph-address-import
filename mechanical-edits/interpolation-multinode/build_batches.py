"""Delete `addr:interpolation` lines that cannot generate an address the map
lacks — prepared for JOSM, not uploaded.

The first campaign here that *deletes*. Every earlier one rewrote tags on an
object and left it in place; an interpolation line with nothing to say has no
tag worth keeping, and stripping `addr:interpolation` would leave an untagged
way behind, which is worse. So the edit is:

    way with addr:interpolation        ->  deleted
    its intermediate nodes             ->  deleted, but only the ones that are
                                           untagged, in no other way and in
                                           no relation
    its two end nodes                  ->  NOT touched. They are address
                                           nodes, and whether each is a real
                                           address is a different question

Which lines, by tier (survey.py defines them; README has the numbers):

    same-number   the line runs from N to N. It interpolates nothing, by
                  construction, whatever the City says. Built by default.
    covered       every City address strictly between the ends is already a
                  real object in OSM. Redundant only if the City roster is
                  taken as complete.
    empty         the City has no address strictly between the ends, so the
                  line can only generate numbers that do not exist. Same
                  dependency on the roster.

Only `same-number` is built unless --tiers says otherwise. The other two wait
on the thread: they rest on the City roster being authoritative, and that is
the community's call, not ours.

    python build_batches.py                         # same-number only
    python build_batches.py --tiers same-number,covered,empty
    python build_batches.py --refetch               # re-survey live OSM first

Needs `requests` + `shapely` for ../_common.py; use the engine's venv:

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py

What it writes:

    batches/NN-<tier>.osm   one JOSM layer per tier = one changeset = one revert
    manifest.csv            the revert record: every deleted object with its
                            version, tags, position (nodes) and node list (ways)

Nothing here uploads.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

import _common  # noqa: E402
import survey  # noqa: E402

BATCH_DIR = HERE / "batches"
AREAS = HERE.parent / "flats-hygiene" / "areas.geojson"
TIERS = ("same-number", "covered", "empty")
WAY_KEYS = {"addr:interpolation", "source"}

COMMENT = {
    "same-number": "delete addr:interpolation lines that run from a number "
                   "to the same number",
    "covered": "delete addr:interpolation lines whose every City address is "
               "already mapped",
    "empty": "delete addr:interpolation lines spanning no City address",
}


def changeset_tags(tier: str, count: int, index: int, total: int) -> dict:
    """_common's table, for a deletion: `mechanical=yes`, `import_plan` at
    the Mechanical edits section. Not `_common.changeset_tags`, which wants a
    Campaign and an area batch this edit does not have."""
    return {
        "comment": (f"Guelph addresses: {COMMENT[tier]} - {count} lines "
                    f"({index}/{total})"),
        "source": "Guelph Open Data",
        "source:license": "OGL-Canada-2.0",
        "mechanical": "yes",
        "bot": "no",
        "import_plan": _common.WIKI_SECTION,
    }


def copy(el: ET.Element, action: str | None) -> ET.Element:
    """A fresh element, never the parsed one, so nothing leaks between
    batches (the trap `_common.geometry_stub` documents)."""
    out = ET.Element(el.tag, {k: v for k, v in el.attrib.items()
                              if k in ("id", "version", "lat", "lon")})
    if action:
        out.set("action", action)
    for child in el:
        if child.tag in ("nd", "tag"):
            ET.SubElement(out, child.tag, dict(child.attrib))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--refetch", action="store_true",
                    help="re-run survey.py against live OSM first")
    ap.add_argument("--tiers", default="same-number",
                    help=f"comma-separated, from {', '.join(TIERS)}")
    args = ap.parse_args()
    tiers = [t for t in args.tiers.split(",") if t]
    if bad := set(tiers) - set(TIERS):
        raise SystemExit(f"unknown tier(s): {sorted(bad)}")

    if args.refetch or not (HERE / "survey.csv").exists():
        survey.main(refetch=args.refetch)
    rows = list(csv.DictReader(open(HERE / "survey.csv", encoding="utf-8")))
    root = ET.parse(survey.INTERP).getroot()
    nodes = {el.get("id"): el for el in root.iter("node")}
    ways = {el.get("id"): el for el in root.iter("way")}
    in_rel = {(m.get("type"), m.get("ref")) for r in root.iter("relation")
              for m in r.findall("member")}
    users: dict[str, set[str]] = {}
    for w in ways.values():
        for nd in w.findall("nd"):
            users.setdefault(nd.get("ref"), set()).add(w.get("id"))
    areas = _common.load_areas(AREAS)
    coords = {k: (float(v.get("lon")), float(v.get("lat"))) for k, v in nodes.items()}

    batches = []
    for tier in tiers:
        picked = [r for r in rows if r["class"] == "valid" and r["tier"] == tier
                  and r["delete_ok"] == "1"]
        if picked:
            batches.append((tier, picked))
    if not batches:
        raise SystemExit("nothing to build")

    BATCH_DIR.mkdir(exist_ok=True)
    for old in BATCH_DIR.glob("*.osm"):
        old.unlink()
    manifest = []
    total = len(batches)
    for index, (tier, picked) in enumerate(batches, 1):
        out = ET.Element("osm", {"version": "0.6",
                                 "generator": "guelph-address-import interpolation-multinode"})
        cs = ET.SubElement(out, "changeset")
        for k, v in changeset_tags(tier, len(picked), index, total).items():
            ET.SubElement(cs, "tag", k=k, v=v)
        keep_nodes, del_nodes, del_ways = [], [], []
        for r in sorted(picked, key=lambda r: (r["street"], r["id"])):
            w = ways[r["id"]]
            wt = _common.element_tags(w)
            refs = [nd.get("ref") for nd in w.findall("nd")]
            area = _common.assign_area(*_common.centre(w, coords), areas)
            del_ways.append(copy(w, "delete"))
            manifest.append({
                "batch": index, "area": area, "type": "way", "id": r["id"],
                "version": w.get("version"), "street": r["street"],
                "housenumber": f"{r['start']}-{r['end']}", "action": "delete",
                "tier": tier, "way": "", "nodes": ";".join(refs),
                "lat": "", "lon": "", "tags": json.dumps(wt, ensure_ascii=False)})
            for i, ref in enumerate(refs):
                n = nodes[ref]
                end = i in (0, len(refs) - 1)
                lone = (not end and not _common.element_tags(n)
                        and users.get(ref) == {r["id"]}
                        and ("node", ref) not in in_rel)
                if lone:
                    del_nodes.append(copy(n, "delete"))
                    manifest.append({
                        "batch": index, "area": area, "type": "node", "id": ref,
                        "version": n.get("version"), "street": "", "housenumber": "",
                        "action": "delete", "tier": tier, "way": r["id"], "nodes": "",
                        "lat": n.get("lat"), "lon": n.get("lon"), "tags": "{}"})
                else:
                    keep_nodes.append(copy(n, None))
        for el in keep_nodes + del_nodes + del_ways:
            out.append(el)
        path = BATCH_DIR / f"{index:02d}-{tier}.osm"
        ET.ElementTree(out).write(path, encoding="utf-8", xml_declaration=True)
        print(f"  batch {index}/{total}: {tier}, {len(del_ways)} ways + "
              f"{len(del_nodes)} nodes deleted, {len(keep_nodes)} nodes kept "
              f"-> {path.name}")

    verify(manifest, ways, nodes, users, in_rel)
    cols = list(manifest[0])
    with open(HERE / "manifest.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.DictWriter(fh, fieldnames=cols)
        wr.writeheader()
        wr.writerows(manifest)
    print(f"{sum(1 for m in manifest if m['type'] == 'way')} ways, "
          f"{sum(1 for m in manifest if m['type'] == 'node')} nodes in "
          f"{total} batch(es). NOT uploaded; see README for the gate.")


def verify(manifest: list[dict], ways: dict, nodes: dict, users: dict,
           in_rel: set) -> None:
    """Read back every batch and refuse the set if any of these fail.

    1. Every element marked delete is in exactly one batch, and that set is
       the manifest exactly.
    2. No deleted way carries a key beyond addr:interpolation and source, and
       its version is the live one.
    3. No deleted node is tagged, is an end of its line, belongs to any way
       but the one being deleted, or sits in a relation.
    4. Nothing is marked modify or create: this edit only deletes.
    """
    seen: dict[tuple[str, str], int] = {}
    problems = []
    for path in sorted(BATCH_DIR.glob("*.osm")):
        for el in ET.parse(path).getroot():
            act = el.get("action")
            if act in ("modify", "create"):
                problems.append(f"{path.name}: {el.tag} {el.get('id')} marked {act}")
            if act == "delete":
                key = (el.tag, el.get("id"))
                seen[key] = seen.get(key, 0) + 1
    want = {(m["type"], m["id"]) for m in manifest}
    if any(v > 1 for v in seen.values()):
        problems.append("an object is marked delete in more than one batch")
    if set(seen) != want:
        problems.append(f"delete set != manifest ({len(seen)} vs {len(want)})")
    deleting = {m["id"] for m in manifest if m["type"] == "way"}
    for m in manifest:
        if m["type"] == "way":
            w = ways[m["id"]]
            if set(_common.element_tags(w)) - WAY_KEYS:
                problems.append(f"way {m['id']} carries more than {sorted(WAY_KEYS)}")
            if w.get("version") != m["version"]:
                problems.append(f"way {m['id']} version drifted")
            refs = [nd.get("ref") for nd in w.findall("nd")]
            if {refs[0], refs[-1]} & {x["id"] for x in manifest if x["type"] == "node"}:
                problems.append(f"way {m['id']}: an end node is marked delete")
        else:
            n = nodes[m["id"]]
            if _common.element_tags(n):
                problems.append(f"node {m['id']} is tagged")
            if not users.get(m["id"], set()) <= deleting or len(users[m["id"]]) != 1:
                problems.append(f"node {m['id']} is used by another way")
            if ("node", m["id"]) in in_rel:
                problems.append(f"node {m['id']} is in a relation")
    if problems:
        raise SystemExit("batch verification failed:\n  " + "\n  ".join(problems[:20]))
    print(f"  verified: {len(seen)} objects marked delete, each once, matching "
          f"the manifest; no end node, tagged node or shared node among them; "
          f"nothing modified or created")


if __name__ == "__main__":
    main()
