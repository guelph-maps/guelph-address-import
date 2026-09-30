"""Read an uploaded batch back from the OSM API and prove it did only what the
manifest says — then record it in the campaign's uploads.csv.

    python verify_changeset.py <campaign-dir> <batch> [--changeset ID]

Without --changeset it finds the newest changeset by `skfd imports` whose
comment names that batch ("(N/TOTAL)"). The checks, each fatal:

- the changeset belongs to `skfd imports` and carries mechanical=yes;
- it deletes nothing, and creates nothing unless the manifest has
  `action=create` rows (edit 6, unit-doors) — then the created nodes must be
  exactly those rows, matched one-to-one on their full tag set and position;
- the set of modified objects is exactly the batch's manifest rows (those with
  `action=modify` when the manifest has an action column; `skip-existing`
  rows are records of what was *not* done and are ignored here);
- on every object, the tags after the upload equal the tags it was prepared
  against with only the campaign's own change applied — nothing else moved.

Only after all of that passes is a row appended to uploads.csv, in the columns
campaigns 2 and 3 already use. Read-only against the API; no credentials.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

API = "https://api.openstreetmap.org/api/0.6"
ACCOUNT = "skfd imports"
UA = {"User-Agent": "guelph-address-import verify_changeset (skfd)"}


def get(url: str) -> ET.Element:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return ET.fromstring(r.read())


def tags_of(el: ET.Element) -> dict[str, str]:
    return {t.get("k"): t.get("v") for t in el.findall("tag")}


def expected_flats_hygiene(before: dict, row: dict) -> dict:
    after = dict(before)
    if row["flats_after"]:
        after["addr:flats"] = row["flats_after"]
    if row["interpolation_removed"]:
        after.pop("addr:interpolation", None)
    return after


def expected_province(before: dict, row: dict) -> dict:
    after = dict(before)
    after.pop("addr:province", None)
    return after


def expected_unit_doors(before: dict, row: dict) -> dict:
    after = dict(before)
    after.pop("addr:flats", None)
    return after


EXPECT = {"flats-hygiene": expected_flats_hygiene,
          "province-removal": expected_province,
          "province-leftovers": expected_province,
          "unit-doors": expected_unit_doors}

# A created node may land a hair off the prepared position once the API has
# stored it at 7 decimal places; 1e-6 degrees is about 11 cm.
POS_TOL = 1e-6


def match_created(created: list[ET.Element], want: list[dict]) -> list[str]:
    """One-to-one: every created element is a node whose tags equal exactly
    one manifest create row's `tags` and whose position is that row's."""
    problems = []
    left = list(want)
    for el in created:
        if el.tag != "node":
            problems.append(f"created a {el.tag} {el.get('id')} - only nodes are expected")
            continue
        tags = tags_of(el)
        lat, lon = float(el.get("lat")), float(el.get("lon"))
        hit = next((r for r in left if json.loads(r["tags"]) == tags
                    and abs(float(r["lat"]) - lat) <= POS_TOL
                    and abs(float(r["lon"]) - lon) <= POS_TOL), None)
        if hit is None:
            problems.append(f"created node {el.get('id')} matches no manifest row: {tags}")
        else:
            left.remove(hit)
    if left:
        problems.append(f"{len(left)} manifest create rows not in the changeset, "
                        f"e.g. {[(r['group'], r['unit']) for r in left[:3]]}")
    return problems


def find_changeset(batch: int, total: int) -> ET.Element:
    root = get(f"{API}/changesets?display_name={urllib.request.quote(ACCOUNT)}")
    # flats-hygiene writes "(1/22)", province-removal "[batch 1/105]".
    markers = (f"({batch}/{total})", f"[batch {batch}/{total}]")
    for cs in root.findall("changeset"):  # newest first
        comment = tags_of(cs).get("comment", "")
        if any(m in comment for m in markers):
            return cs
    sys.exit(f"no changeset by {ACCOUNT!r} with {' or '.join(markers)} in its comment yet")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("campaign_dir")
    ap.add_argument("batch", type=int)
    ap.add_argument("--changeset", type=int)
    args = ap.parse_args()

    here = Path(args.campaign_dir).resolve()
    expect = EXPECT[here.name]
    rows_all = list(csv.DictReader(open(here / "manifest.csv", encoding="utf-8")))
    total = max(int(r["batch"]) for r in rows_all)
    mine = [r for r in rows_all if int(r["batch"]) == args.batch]
    rows = {(r["type"], r["id"]): r for r in mine
            if r.get("action", "modify") == "modify"}
    creates = [r for r in mine if r.get("action") == "create"]
    if not rows and not creates:
        sys.exit(f"batch {args.batch} has no manifest rows")
    batch_file = next((here / "batches").glob(f"{args.batch:02d}-*.osm")).name

    uploads = here / "uploads.csv"
    if uploads.exists():
        for u in csv.DictReader(open(uploads, encoding="utf-8")):
            if int(u["batch"]) == args.batch:
                sys.exit(f"batch {args.batch} already recorded as changeset {u['changeset']}")

    cs = (get(f"{API}/changeset/{args.changeset}").find("changeset")
          if args.changeset else find_changeset(args.batch, total))
    cs_id, user = cs.get("id"), cs.get("user")
    ctags = tags_of(cs)
    problems: list[str] = []
    if user != ACCOUNT:
        problems.append(f"changeset {cs_id} is by {user!r}, not {ACCOUNT!r}")
    if ctags.get("mechanical") != "yes":
        problems.append("changeset lacks mechanical=yes")
    if cs.get("open") == "true":
        sys.exit(f"changeset {cs_id} is still open — wait for JOSM to close it")

    # What the batch was prepared against: the object versions in live.osm.
    wanted = {k: int(r["version"]) for k, r in rows.items()}
    before: dict[tuple[str, str], dict] = {}
    for _, el in ET.iterparse(here / "live.osm"):
        k = (el.tag, el.get("id"))
        if k in wanted and int(el.get("version")) == wanted[k]:
            before[k] = tags_of(el)
        if el.tag in ("way", "relation"):
            el.clear()
    missing = set(wanted) - set(before)
    if missing:
        sys.exit(f"{len(missing)} prepared-against versions not in live.osm "
                 f"(was the campaign refetched after building?) e.g. {sorted(missing)[:3]}")

    change = get(f"{API}/changeset/{cs_id}/download")
    created = [el for blk in change.findall("create") for el in blk]
    deleted = [el for blk in change.findall("delete") for el in blk]
    modified = {(el.tag, el.get("id")): el for blk in change.findall("modify") for el in blk}
    if creates or created:
        problems.extend(match_created(created, creates))
    if deleted:
        problems.append(f"{len(deleted)} objects deleted")
    extra = set(modified) - set(rows)
    short = set(rows) - set(modified)
    if extra:
        problems.append(f"{len(extra)} modified objects not in the batch, e.g. {sorted(extra)[:3]}")
    if short:
        problems.append(f"{len(short)} batch objects not in the changeset, e.g. {sorted(short)[:3]}")

    bad = 0
    for k in set(rows) & set(modified):
        want = expect(before[k], rows[k])
        got = tags_of(modified[k])
        if got != want:
            bad += 1
            if bad <= 5:
                diff = {t: (want.get(t), got.get(t)) for t in set(want) | set(got)
                        if want.get(t) != got.get(t)}
                problems.append(f"{k[0]} {k[1]}: tags differ (want, got) {diff}")
        if int(modified[k].get("version")) != wanted[k] + 1:
            problems.append(f"{k[0]} {k[1]}: version {modified[k].get('version')}, "
                            f"expected {wanted[k] + 1}")
    if bad > 5:
        problems.append(f"... and {bad - 5} more objects with unexpected tags")

    print(f"changeset {cs_id} by {user}: {len(modified)} modified, "
          f"{len(created)} created, {len(deleted)} deleted; batch has "
          f"{len(rows)}" + (f" + {len(creates)} to create" if creates else ""))
    print(f"comment: {ctags.get('comment')}")
    if problems:
        print("\nFAILED — not recorded:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    area = mine[0]["area"]
    new_file = not uploads.exists()
    with open(uploads, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["batch", "file", "area", "objects", "changeset", "uploaded_at", "account"])
        w.writerow([args.batch, batch_file, area, len(rows) + len(creates), cs_id,
                    cs.get("closed_at") or cs.get("created_at"), user])
    print(f"verified: every object changed exactly as the manifest says. "
          f"Recorded batch {args.batch} -> {cs_id} in {uploads.name}.")


if __name__ == "__main__":
    main()
