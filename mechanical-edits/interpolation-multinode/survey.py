"""The 149 open `addr:interpolation` ways with three or more nodes, re-read.

Campaign 4 (flats-hygiene) removed `addr:interpolation` from closed ways and
lone nodes and left these alone, because node count is the wrong test for an
open way: an interpolation line may bend through intermediate nodes. The test
that matters is the one JOSM makes — do both END nodes carry
`addr:housenumber`, on the same street? — plus, now that the import has run,
a second one: is every City address the way stands in for already mapped as a
real object, so the line says nothing that is not said better elsewhere?

Two fetches, both cached beside this file:

    live_interp.osm     every addr:interpolation way in Guelph, its nodes,
                        every way any of those nodes also belongs to, and
                        every relation holding one of the ways or nodes
    live_addr.osm       every object in Guelph carrying addr:housenumber,
                        tags + centre + meta (so our import's nodes can be
                        told apart by changeset)

Writes survey.csv, one row per open 3+-node way, and prints the tallies the
README quotes. Builds nothing; build_batches.py reads survey.csv.

    python survey.py              # cached fetches if present
    python survey.py --refetch
"""
from __future__ import annotations

import collections
import csv
import json
import math
import sqlite3
import sys
import tomllib
from pathlib import Path
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
CITY_DIR = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))

import _common  # noqa: E402

INTERP = HERE / "live_interp.osm"
ADDR = HERE / "live_addr.osm"
OLD_REVIEW = HERE.parent / "flats-hygiene" / "review.csv"

INTERP_QUERY = f"""
[out:xml][timeout:900];
area({_common.AREA_ID})->.g;
way["addr:interpolation"](area.g)->.i;
.i out meta;
node(w.i)->.n;
.n out meta;
way(bn.n)->.p;
(.p; - .i;)->.o;
.o out meta;
(rel(bw.i); rel(bn.n););
out meta;
"""
ADDR_QUERY = (f"[out:xml][timeout:900];area({_common.AREA_ID})->.g;"
              'nwr["addr:housenumber"](area.g);out tags center meta;')

# A City point this far from the line, on the line's street, counts as one the
# line could be standing in for. Interpolation lines in Guelph run along the
# front of the lots, 10-30 m off the parcels' points.
NEAR_M = 60.0


def norm(s: str | None) -> str:
    return " ".join(str(s or "").lower().split())


def num(h: str | None) -> int | None:
    """The integer part of a plain housenumber; None for anything else."""
    h = (h or "").strip()
    return int(h) if h.isdigit() else None


def metres(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat = math.radians((a[1] + b[1]) / 2)
    dx = (a[0] - b[0]) * 111_320 * math.cos(lat)
    dy = (a[1] - b[1]) * 110_540
    return math.hypot(dx, dy)


def seg_dist(p, a, b) -> float:
    """Distance in metres from p to segment ab (lon/lat, locally flat)."""
    lat = math.radians(p[1])
    kx, ky = 111_320 * math.cos(lat), 110_540
    px, py = p[0] * kx, p[1] * ky
    ax, ay, bx, by = a[0] * kx, a[1] * ky, b[0] * kx, b[1] * ky
    dx, dy = bx - ax, by - ay
    t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy)
                                               / (dx * dx + dy * dy)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def city_points() -> list[dict]:
    cfg = tomllib.loads((CITY_DIR / "config.toml").read_text(encoding="utf-8"))
    db = sqlite3.connect(cfg["source"]["sqlite_path"])
    latest = db.execute("select max(max_snapshot_id) from addresses").fetchone()[0]
    out = []
    for number, street, lon, lat, props in db.execute(
            "select number, street, longitude, latitude, props from addresses "
            "where max_snapshot_id = ?", (latest,)):
        p = json.loads(props or "{}")
        q = (p.get("QUALIFIER") or "").strip()
        out.append({"number": number, "qualifier": q, "street": street,
                    "housenumber": f"{number}{q}", "lon": lon, "lat": lat,
                    "unit": p.get("HAS_UNIT") == "Y" and bool(p.get("UNIT"))})
    return out


def import_changesets() -> set[str]:
    db = sqlite3.connect(CITY_DIR / "data" / "guelph" / "tool.db")
    return {str(r[0]) for r in db.execute("select changeset_id from changesets")}


def shape_of(refs: list[str]) -> str:
    if len(refs) >= 3 and refs[0] == refs[-1]:
        return "closed"
    if len(refs) == 2 and refs[0] != refs[1]:
        return "open2"
    return "openN"


def parity_ok(lo: int, hi: int, interp: str) -> bool:
    if interp == "even":
        return lo % 2 == 0 and hi % 2 == 0
    if interp == "odd":
        return lo % 2 == 1 and hi % 2 == 1
    return True


def in_scheme(n: int, interp: str) -> bool:
    return {"even": n % 2 == 0, "odd": n % 2 == 1}.get(interp, True)


def main(refetch: bool | None = None) -> None:
    """build_batches.py --refetch calls this, so tiers are re-read against
    the same fetch the batches are written from."""
    if refetch is None:
        refetch = "--refetch" in sys.argv
    iroot = _common.fetch_live(INTERP_QUERY, INTERP, refetch,
                               "addr:interpolation ways, their nodes and neighbours")
    aroot = _common.fetch_live(ADDR_QUERY, ADDR, refetch,
                               "every addr:housenumber object")
    ours = import_changesets()
    city = city_points()

    nodes = {el.get("id"): el for el in iroot.iter("node")}
    interp_ways = [w for w in iroot.iter("way")
                   if "addr:interpolation" in _common.element_tags(w)]
    other_ways: dict[str, list[ET.Element]] = collections.defaultdict(list)
    for w in iroot.iter("way"):
        if "addr:interpolation" in _common.element_tags(w):
            continue
        for nd in w.findall("nd"):
            other_ways[nd.get("ref")].append(w)
    in_rel = {(m.get("type"), m.get("ref")) for r in iroot.iter("relation")
              for m in r.findall("member")}
    interp_of_node: dict[str, list[str]] = collections.defaultdict(list)
    for w in interp_ways:
        for nd in w.findall("nd"):
            interp_of_node[nd.get("ref")].append(w.get("id"))

    # Every mapped address, by (street, housenumber), and whether it is ours.
    mapped: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for el in aroot:
        if el.tag not in ("node", "way", "relation"):
            continue
        t = _common.element_tags(el)
        c = el.find("center")
        src = c if c is not None else el
        mapped[(norm(t.get("addr:street")), norm(t.get("addr:housenumber")))].append({
            "type": el.tag, "id": el.get("id"),
            "ours": el.tag == "node" and el.get("changeset") in ours,
            "lon": float(src.get("lon")), "lat": float(src.get("lat"))})

    city_by_street: dict[str, list[dict]] = collections.defaultdict(list)
    for p in city:
        city_by_street[norm(p["street"])].append(p)

    old = {r["id"] for r in csv.DictReader(open(OLD_REVIEW, encoding="utf-8"))
           if r["reason"] == "interpolation-multinode"}

    shapes = collections.Counter()
    rows = []
    two_node = []
    for w in interp_ways:
        refs = [nd.get("ref") for nd in w.findall("nd")]
        shape = shape_of(refs)
        shapes[shape] += 1
        if shape not in ("openN", "open2"):
            continue
        wt = _common.element_tags(w)
        interp = wt["addr:interpolation"]
        geom = [(float(nodes[r].get("lon")), float(nodes[r].get("lat"))) for r in refs]
        ntags = [_common.element_tags(nodes[r]) for r in refs]
        ends = (ntags[0], ntags[-1])
        numbered = [i for i, t in enumerate(ntags) if t.get("addr:housenumber")]
        mids_numbered = [i for i in numbered if 0 < i < len(refs) - 1]
        ends_n = sum(1 for t in ends if t.get("addr:housenumber"))
        streets = {norm(t.get("addr:street")) for t in ntags if t.get("addr:housenumber")}
        street = norm(wt.get("addr:street")) or (streets.pop() if len(streets) == 1 else "")
        n_streets = len({norm(t.get("addr:street")) for t in ntags
                         if t.get("addr:housenumber")})
        lo_hi = [num(t.get("addr:housenumber")) for t in ends]
        length = sum(metres(geom[i], geom[i + 1]) for i in range(len(geom) - 1))

        # Untagged intermediate nodes this way alone uses: what deleting the
        # way would also delete. Any tag, any other way, any other
        # interpolation line keeps a node.
        mid_refs = refs[1:-1]
        lone_mids = [r for r in mid_refs
                     if not _common.element_tags(nodes[r])
                     and not other_ways.get(r)
                     and ("node", r) not in in_rel
                     and interp_of_node[r] == [w.get("id")]]
        end_refs = (refs[0], refs[-1])
        end_untagged_lone = [r for r in end_refs
                             if not _common.element_tags(nodes[r])
                             and not other_ways.get(r)
                             and interp_of_node[r] == [w.get("id")]]
        shared_nodes = sum(1 for r in refs if other_ways.get(r))

        # What the line stands in for: City points on its street, within
        # NEAR_M of the drawn line, in its parity scheme, strictly between its
        # end numbers when it has them.
        cands = []
        if street:
            for p in city_by_street.get(street, ()):
                if p["number"] is None or not p["number"].isdigit():
                    continue
                n = int(p["number"])
                if not in_scheme(n, interp):
                    continue
                d = min(seg_dist((p["lon"], p["lat"]), geom[i], geom[i + 1])
                        for i in range(len(geom) - 1))
                if None not in lo_hi:
                    # Numbered ends define the range; distance is only
                    # reported, since a deep lot can sit well back.
                    lo, hi = sorted(lo_hi)
                    if not lo < n < hi:
                        continue
                elif d > NEAR_M:
                    continue
                cands.append({**p, "dist": d})
        seen_civic = {}
        for p in cands:
            seen_civic[p["housenumber"]] = p
        far = sum(1 for p in seen_civic.values() if p["dist"] > NEAR_M)
        # Are the end numbers real? CanVec and StatCan 92-500-X carried
        # block-face address *ranges*, and a range bound need not be an
        # address anyone lives at.
        end_real = sum(1 for t in ends if t.get("addr:housenumber")
                       and any(norm(p["housenumber"]) == norm(t["addr:housenumber"])
                               for p in city_by_street.get(norm(t.get("addr:street")), ())))
        # Does the end node's address also exist on some other OSM object?
        end_dupes = 0
        for r, t in zip(end_refs, ends):
            if not t.get("addr:housenumber"):
                continue
            key = (norm(t.get("addr:street")), norm(t["addr:housenumber"]))
            if any(not (h["type"] == "node" and h["id"] == r) for h in mapped.get(key, ())):
                end_dupes += 1
        end_addr_only = sum(1 for t in ends if t and all(k.startswith("addr:") or k == "source" for k in t))
        covered = ours_cov = 0
        missing = []
        for hn, p in sorted(seen_civic.items(), key=lambda kv: (int(kv[1]["number"]), kv[0])):
            hits = mapped.get((street, norm(hn)), [])
            if hits:
                covered += 1
                if any(h["ours"] for h in hits):
                    ours_cov += 1
            else:
                missing.append(hn)

        # What the line would lose if deleted, in kinds rather than numbers:
        #   same-number  N to N interpolates nothing, by construction
        #   covered      every City address strictly between the ends is
        #                already a real object in OSM
        #   empty        the City has no address strictly between the ends;
        #                the line can only generate numbers that do not exist
        #   unmatched-street
        #                the City has no street spelt the way the line's ends
        #                spell it, so "no address between" means nothing.
        #                Glenholme for Glenholm, Lowes Road with no East/West.
        #                Not a deletion tier: the ends want fixing first
        if ends_n == 2 and None not in lo_hi:
            tier = ("same-number" if lo_hi[0] == lo_hi[1]
                    else "unmatched-street" if street not in city_by_street
                    else "covered" if seen_civic and not missing
                    else "empty" if not seen_civic else "adds-addresses")
        else:
            tier = ""
        # Deleting the line is a plain deletion only if the way carries
        # nothing but the interpolation and its provenance, and no relation
        # holds it.
        extra_keys = sorted(set(wt) - {"addr:interpolation", "source"})
        delete_ok = not extra_keys and ("way", w.get("id")) not in in_rel

        # A one-ended line: what mapped address sits nearest its bare end?
        near_end = ""
        if ends_n == 1:
            bare = geom[0] if not ends[0].get("addr:housenumber") else geom[-1]
            best = min(((metres(bare, (h["lon"], h["lat"])), k, h)
                        for k, hs in mapped.items() if k[0] == street for h in hs),
                       default=None, key=lambda x: x[0])
            if best:
                near_end = f"{best[1][1]} at {best[0]:.0f} m ({best[2]['type']} {best[2]['id']})"

        if ends_n == 2:
            if n_streets != 1:
                cls = "valid-but-streets-differ"
            elif None in lo_hi:
                cls = "valid-nonnumeric-end"
            elif not parity_ok(*sorted(lo_hi), interp):
                cls = "valid-parity-mismatch"
            else:
                cls = "valid"
        elif numbered:
            cls = "fixable"
        else:
            cls = "meaningless"

        rows.append({
            "id": w.get("id"), "version": w.get("version"),
            "user": w.get("user"), "timestamp": w.get("timestamp"),
            "interpolation": interp, "nodes": len(refs),
            "length_m": round(length),
            "way_tags": ";".join(f"{k}={v}" for k, v in wt.items()),
            "street": street,
            "start": ends[0].get("addr:housenumber", ""),
            "end": ends[1].get("addr:housenumber", ""),
            "ends_numbered": ends_n, "mids_numbered": len(mids_numbered),
            "streets_on_line": n_streets,
            "class": cls,
            "ends_in_city": end_real, "ends_duplicated": end_dupes,
            "ends_addr_only": end_addr_only,
            "end_tags": " | ".join(";".join(f"{k}={v}" for k, v in t.items()) for t in ends),
            "city_between": len(seen_civic), "city_far": far, "mapped": covered,
            "mapped_by_import": ours_cov, "missing": ";".join(missing),
            "tier": tier, "delete_ok": int(delete_ok),
            "extra_way_keys": ";".join(extra_keys), "near_bare_end": near_end,
            "lone_mid_nodes": len(lone_mids),
            "lone_untagged_ends": len(end_untagged_lone),
            "shared_nodes": shared_nodes,
            "in_2026_09_16_list": int(w.get("id") in old),
        })
        if shape == "open2":
            two_node.append(rows.pop())

    for name, data in (("survey.csv", rows), ("survey_2node.csv", two_node)):
        data.sort(key=lambda r: (r["class"], r["tier"], r["street"], r["id"]))
        with open(HERE / name, "w", newline="", encoding="utf-8") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(data[0]))
            wr.writeheader()
            wr.writerows(data)

    print(f"addr:interpolation ways: {sum(shapes.values())} "
          f"({', '.join(f'{k} {v}' for k, v in sorted(shapes.items()))})")
    ids = {r["id"] for r in rows}
    print(f"open 3+-node: {len(rows)}; of the 2026-09-16 list of {len(old)}: "
          f"{len(ids & old)} still here, {len(old - ids)} gone, "
          f"{len(ids - old)} new")
    print("class:", dict(collections.Counter(r["class"] for r in rows)))
    print("ends numbered:", dict(collections.Counter(r["ends_numbered"] for r in rows)))
    print("interpolation:", dict(collections.Counter(r["interpolation"] for r in rows)))
    print("valid ends in City:", dict(collections.Counter(r["ends_in_city"] for r in rows if r["class"] == "valid")))
    print("valid ends duplicated elsewhere in OSM:", dict(collections.Counter(r["ends_duplicated"] for r in rows if r["class"] == "valid")))
    print("same number both ends:", sum(1 for r in rows if r["start"] and r["start"] == r["end"]))
    print("tier:", dict(collections.Counter(r["tier"] for r in rows)))
    print("tier x ends_in_city:", dict(collections.Counter((r["tier"], r["ends_in_city"]) for r in rows)))
    print("delete_ok:", sum(int(r["delete_ok"]) for r in rows),
          "| lone mid nodes:", sum(r["lone_mid_nodes"] for r in rows),
          "| mid nodes kept (tagged/shared/in relation):",
          sum(r["nodes"] - 2 - r["lone_mid_nodes"] for r in rows))
    print("relations holding a way or node:", len(in_rel))
    for r in rows:
        if r["class"] == "fixable":
            print(f"  fixable {r['id']} {r['street']} {r['start'] or '?'}-{r['end'] or '?'} "
                  f"({r['length_m']} m): nearest mapped to bare end {r['near_bare_end']}")
    print(f"\n2-node lines, same test (context, not scope): {len(two_node)}")
    print("  class:", dict(collections.Counter(r["class"] for r in two_node)))
    print("  tier:", dict(collections.Counter(r["tier"] for r in two_node)))
    print("  City addresses between ends:", sum(r["city_between"] for r in two_node),
          "mapped:", sum(r["mapped"] for r in two_node),
          "by import:", sum(r["mapped_by_import"] for r in two_node))
    v = [r for r in rows if r["class"] == "valid"]
    print(f"valid: {len(v)}; City addresses between ends {sum(r['city_between'] for r in v)}, "
          f"mapped {sum(r['mapped'] for r in v)}, by import {sum(r['mapped_by_import'] for r in v)}, "
          f"empty range {sum(1 for r in v if r['city_between'] == 0)}")


if __name__ == "__main__":
    main()
