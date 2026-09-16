"""Mechanical edit 3 — move unit lists from addr:unit to addr:flats, prepared for JOSM.

    addr:unit  = 101-116;201-215;...  ->  addr:flats = 101-116;201-215;...
                                          (addr:unit removed; nothing else touched)

Consent is PENDING. The announcement is drafted in ANNOUNCEMENT.md beside this
file and has not been posted to thread #135103; the edit is written up as
section 3 of Guelph/Address_Import/Continuous#Mechanical_edits. Nothing here
may be uploaded until the post is up and its 14-day window has closed with no
objections — and on that day the batches are rebuilt with --refetch, because
the versions prepared against today will have moved.

One Overpass query pulls every list-valued addr:unit in the city (and every
addr:flats, so the ones already done can be reported and skipped) *with meta
and child-node geometry*; everything after that is local. Edit 2's first
version asked Overpass once per batch and got itself rate-limited for the
trouble.

What this writes, all under this directory:

    live.osm                the raw fetch, cached — delete or --refetch to
                            refresh it
    batches/NN-<area>.osm   one JOSM-ready layer per batch: the live elements
                            with their real `version`, tags rewritten,
                            action="modify", changeset tags pre-filled
    manifest.csv            the revert record — one row per edited object with
                            the version it was prepared against and the value
                            that moved
    review.csv              the objects this refuses to touch, for hand work
    index.html              the run sheet: one remote-control link per batch

Nothing here uploads. The operator opens each batch in JOSM, looks at it, and
presses upload.

    python build_batches.py              # uses the cached fetch if present
    python build_batches.py --refetch    # pull OSM again first
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import requests
from shapely.geometry import Point, shape
from shapely.prepared import prep

HERE = Path(__file__).resolve().parent
BATCH_DIR = HERE / "batches"
LIVE = HERE / "live.osm"

# Guelph is single-tier: the city boundary is admin_level 6, relation 7486148.
AREA_ID = 3607486148
OVERPASS = "https://overpass-api.de/api/interpreter"
STATUS = "https://overpass-api.de/api/status"
UA = "guelph-address-import/1.0 (unit-listing-retag prep; toronto@comentality.com)"

# The 23 "Guelph Areas" polygons — the same partition the import uses, and the
# one the announcement promised these batches would follow.
# From config.toml [city] neighbourhoods_url.
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

# One batch is one changeset is one revert. Small enough that a reviewer can
# actually scan it and that a revert stays surgical.
MAX_PER_BATCH = 250

# The pilot has to be evidence, so it is the smallest batch that is both a
# whole area in one changeset and big enough to prove anything. Ordering by
# size alone put a single object first, which would have been a poor thing to
# post to the thread. Lower than edit 2's 50: there are ~450 objects in the
# whole campaign, and 50 would have skipped most areas.
PILOT_MIN = 20

# A list is a `;` anywhere or a single numeric range (`101-116`, `A1-A9`).
# The same expression is handed to Overpass and re-applied in Python, so the
# fetch and the classifier cannot disagree about what a list is.
_LISTING_RE = r"(;|^[A-Za-z]*[0-9]+-[A-Za-z]*[0-9]+$)"
_LISTING = re.compile(_LISTING_RE)

# `out meta` for the version numbers the upload checks against; `>;` for the
# ways' child nodes, without which JOSM has an incomplete way and refuses to
# upload it. No [out:xml] — XML is the default and some instances 406 on the
# collision with an explicit Accept. addr:flats rides along so the objects
# that already carry it are reported rather than silently absent.
LIVE_QUERY = f"""
[timeout:900];
area({AREA_ID})->.a;
(
  nwr["addr:unit"~"{_LISTING_RE}"](area.a);
  nwr["addr:flats"](area.a);
);
out meta;
>;
out meta;
"""


# ---------------------------------------------------------------- fetching

def wait_for_slot() -> None:
    """Overpass gives an IP two slots. Ask before knocking.

    /api/status reports when the next one frees; sleeping that out is both
    faster and politer than retrying into a 429.
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
    print(f"    Overpass slots busy — waiting {delay}s")
    time.sleep(delay)


def fetch_live(refetch: bool) -> ET.Element:
    if refetch or not LIVE.exists():
        print("fetching every list-valued addr:unit (and every addr:flats) "
              "in Guelph from Overpass (one query, a few minutes)...")
        last = None
        for attempt in range(5):
            wait_for_slot()
            try:
                resp = requests.post(
                    OVERPASS, data={"data": LIVE_QUERY},
                    headers={"User-Agent": UA,
                             "Accept": "application/xml, text/xml, */*"},
                    timeout=960,
                )
                resp.raise_for_status()
                LIVE.write_bytes(resp.content)
                break
            except Exception as exc:  # noqa: BLE001 — Overpass fails variously
                last = exc
                print(f"    attempt {attempt + 1}: {exc}", file=sys.stderr)
                time.sleep(60)
        else:
            raise SystemExit(f"Overpass would not serve the fetch: {last}")
    size = LIVE.stat().st_size / 1e6
    print(f"parsing {LIVE.name} ({size:.1f} MB)")
    return ET.parse(LIVE).getroot()


def load_areas() -> list[tuple[str, object]]:
    cache = HERE / "areas.geojson"
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


# ------------------------------------------------------------- classifying

def is_listing(unit: str | None) -> bool:
    return bool(unit) and _LISTING.search(unit) is not None


def classify(tags: dict[str, str]) -> tuple[str, str | None]:
    """Return (class, review_reason).

    safe       addr:unit is a list by the same test Overpass applied, there is
               no addr:flats to collide with, and addr:housenumber has no
               hyphen -> move the value, verbatim, to addr:flats.
    review     anything else. Left alone; the reason says whose problem it is:
               has-flats   already carries addr:flats — the published plan
                           leaves it alone; merging two lists is hand work
               hyphen-hn   addr:housenumber is itself hyphenated, so edit 2
                           owns the object first. We measured zero overlap;
                           this refuses rather than assumes
               single      a lone designator (`PH-2`) or a value the fetch
                           caught that Python's test does not — a door, not a
                           building; not this campaign

    Nothing is compressed, sorted or reconciled against the City: the value
    moves as it is, so the edit is exactly reversible.
    """
    unit = tags.get("addr:unit")
    if "addr:flats" in tags:
        return "review", "has-flats"
    if not is_listing(unit):
        return "review", "single"
    if "-" in tags.get("addr:housenumber", ""):
        return "review", "hyphen-hn"
    return "safe", None


# The three reasons an object lands in the by-hand list are different problems
# with different owners, so the run sheet separates them rather than showing
# one pile.
REVIEW_REASONS = {
    "has-flats": ("Already carries <code>addr:flats</code>",
                  "The published plan says the existing "
                  "<code>addr:flats</code> is left alone. Where one of these "
                  "also has a list in <code>addr:unit</code>, merging the two "
                  "is a judgement per object, not a key move. Listed so the "
                  "count on the wiki can be checked."),
    "hyphen-hn": ("<code>addr:housenumber</code> is itself hyphenated",
                  "Edit 2 owns these first: the housenumber has to be split "
                  "before anything is said about the unit. Measured overlap "
                  "was zero, so this row should be empty; if it is not, run "
                  "edit 2 on it and <code>--refetch</code>."),
    "single": ("A lone designator the fetch caught but the rule does not",
               "Overpass's regex and Python's agree by construction, so this "
               "is normally empty. Anything here is a door "
               "(<code>PH-2</code>), not a building, and stays on "
               "<code>addr:unit</code>."),
}


# -------------------------------------------------------------- the fetch

def element_tags(el: ET.Element) -> dict[str, str]:
    return {t.attrib["k"]: t.attrib["v"] for t in el.findall("tag")}


def index_live(root: ET.Element) -> tuple[dict, dict]:
    """Split the fetch into (addressed elements, node coordinates).

    The `>;` recursion means most nodes in the file are plain geometry with no
    tags of their own; they are kept for JOSM to draw and for the way-centroid
    that decides which area a way lands in.
    """
    coords: dict[str, tuple[float, float]] = {}
    addressed: dict[tuple[str, str], ET.Element] = {}
    for el in root:
        if el.tag not in ("node", "way", "relation"):
            continue
        oid = el.attrib.get("id")
        if oid is None:
            continue
        if el.tag == "node" and "lat" in el.attrib:
            coords[oid] = (float(el.attrib["lat"]), float(el.attrib["lon"]))
        tags = element_tags(el)
        if "addr:unit" in tags or "addr:flats" in tags:
            addressed[(el.tag, oid)] = el
    return addressed, coords


def centre(el: ET.Element, coords: dict) -> tuple[float | None, float | None]:
    if el.tag == "node":
        pos = coords.get(el.attrib["id"])
        return (pos[1], pos[0]) if pos else (None, None)
    pts = [coords[nd.attrib["ref"]] for nd in el.findall("nd")
           if nd.attrib["ref"] in coords]
    if not pts:
        return (None, None)
    return (sum(p[1] for p in pts) / len(pts), sum(p[0] for p in pts) / len(pts))


def assign_area(lon, lat, areas) -> str:
    if lon is None or lat is None:
        return "Unlocated"
    point = Point(lon, lat)
    for name, poly in areas:
        if poly.contains(point):
            return name
    # 0.53% of the city's addresses fall outside the area fabric by
    # construction — config.toml [city] records the same gap.
    return "Outside the area fabric"


# ---------------------------------------------------------------- batching

def make_batches(rows: list[dict]) -> list[dict]:
    """One batch per area, split at MAX_PER_BATCH along street boundaries.

    Areas come smallest-first so batch 1 — the pilot the announcement promised
    to post before anything else moves — is one a human can finish in a
    sitting. Within a batch, rows sort by street then number so the JOSM layer
    reads in an order a reviewer can follow.
    """
    by_area: dict[str, list[dict]] = {}
    for row in rows:
        by_area.setdefault(row["area"], []).append(row)

    batches: list[dict] = []
    for area in sorted(by_area, key=lambda a: (len(by_area[a]), a)):
        items = sorted(by_area[area],
                       key=lambda r: (r["street"], r["housenumber"], r["id"]))
        chunks = [items[i:i + MAX_PER_BATCH]
                  for i in range(0, len(items), MAX_PER_BATCH)]
        for part, chunk in enumerate(chunks, 1):
            batches.append({"area": area, "part": part, "of": len(chunks),
                            "items": chunk})
    return batches


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "area"


def batch_path(index: int, batch: dict) -> Path:
    suffix = "" if batch["of"] == 1 else f"-p{batch['part']}"
    return BATCH_DIR / f"{index:02d}-{_slug(batch['area'])}{suffix}.osm"


def changeset_tags(batch: dict, index: int, total: int) -> dict[str, str]:
    """The published table (§ Changeset tags), with `import=yes` replaced by
    `mechanical=yes` and `import_plan` pointing at § Mechanical edits.

    `created_by` is deliberately absent. JOSM stamps its own on upload and
    overwrites anything put here, so the table's `address-importer-friend`
    would be a tag that never survives the trip; the run sheet says so rather
    than the file claiming it. `import:client_token` is absent too — it exists
    for the engine's idempotent retry, and JOSM is doing the uploading.
    """
    where = (batch["area"] if batch["of"] == 1
             else f"{batch['area']} {batch['part']}/{batch['of']}")
    return {
        "comment": (f"Guelph unit tagging: move unit lists from addr:unit "
                    f"to addr:flats - {where} [batch {index}/{total}]"),
        "source": "Guelph Open Data",
        "source:license": "OGL-Canada-2.0",
        "mechanical": "yes",
        "bot": "no",
        "import_plan": WIKI_SECTION,
    }


# ----------------------------------------------------------------- writing

def rewrite_tags(el: ET.Element, tags: dict[str, str]) -> None:
    for tag in el.findall("tag"):
        el.remove(tag)
    for key, value in tags.items():
        ET.SubElement(el, "tag", k=key, v=value)


def write_batch(batch: dict, index: int, total: int,
                addressed: dict, by_node_id: dict) -> dict:
    """Emit one .osm. Returns the record the manifest and run sheet need."""
    out = ET.Element("osm", {"version": "0.6",
                             "generator": "guelph-unit-listing-retag"})
    # JOSM reads a <changeset> child into the layer and pre-fills the upload
    # dialog from it (OsmReader -> ds.addChangeSetTag, then
    # UploadDialog.initLifeCycle). No `id` attribute: JOSM accepts the element
    # only when its id equals the root's `upload-changeset`, and null == null
    # is the match a hand-built file wants. Only `.osm` does this — the same
    # tags in an `.osc` are ignored.
    cs_tags = changeset_tags(batch, index, total)
    cs = ET.SubElement(out, "changeset")
    for key, value in cs_tags.items():
        ET.SubElement(cs, "tag", k=key, v=value)

    rows: list[dict] = []
    nodes: list[ET.Element] = []
    ways: list[ET.Element] = []
    seen_nodes: set[str] = set()
    for item in batch["items"]:
        el = addressed[(item["type"], item["id"])]
        tags = element_tags(el)
        before = tags["addr:unit"]
        # Key only. The value is not stripped, split, sorted or compressed.
        rewrite_tags(el, {**{k: v for k, v in tags.items() if k != "addr:unit"},
                          "addr:flats": before})
        el.set("action", "modify")
        if el.tag == "way":
            ways.append(el)
            for nd in el.findall("nd"):
                ref = nd.attrib["ref"]
                if ref not in seen_nodes and ref in by_node_id:
                    seen_nodes.add(ref)
                    nodes.append(by_node_id[ref])
        else:
            if el.attrib["id"] not in seen_nodes:
                seen_nodes.add(el.attrib["id"])
                nodes.append(el)
        rows.append({
            "batch": index, "area": batch["area"], "type": item["type"],
            "id": item["id"], "version": el.attrib.get("version", ""),
            "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "before_unit": before, "after_flats": before, "class": item["class"],
        })

    # Nodes first so JOSM has the referenced geometry when it parses the ways.
    for el in nodes + ways:
        out.append(el)

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    path = batch_path(index, batch)
    ET.ElementTree(out).write(path, encoding="utf-8", xml_declaration=True)
    return {"index": index, "area": batch["area"], "part": batch["part"],
            "of": batch["of"], "path": path, "count": len(rows),
            "rows": rows, "cs_tags": cs_tags,
            "streets": sorted({r["street"] for r in rows if r["street"]}),
            "sample": rows[0] if rows else None}


# ---------------------------------------------------------------- run sheet

PAGE_CSS = """
:root { color-scheme: light dark; --line:#d5d7db; --muted:#6b7177;
        --ok:#1f7a3f; --warn:#8a5a00; --bg:#fff; --fg:#16181d; --card:#fafbfc; }
@media (prefers-color-scheme: dark) {
  :root { --line:#3a3f46; --muted:#9aa1a9; --ok:#6fcf8f; --warn:#e0b25c;
          --bg:#14171a; --fg:#e8eaed; --card:#1b1f23; } }
* { box-sizing: border-box; }
body { margin:0 auto; padding:2rem 1.25rem 6rem; max-width:64rem;
       background:var(--bg); color:var(--fg);
       font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif; }
h1 { font-size:1.5rem; margin:0 0 .25rem; }
h2 { font-size:1.05rem; margin:2.25rem 0 .6rem; }
.sub { color:var(--muted); margin:0 0 1.5rem; }
.banner { border:1px solid var(--line); border-left:4px solid var(--ok);
          background:var(--card); padding:.85rem 1rem; border-radius:6px;
          margin:0 0 1rem; }
.banner.warn { border-left-color:var(--warn); }
code, .mono { font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
              font-size:.86em; }
table { border-collapse:collapse; width:100%; }
th, td { text-align:left; padding:.5rem .55rem; border-bottom:1px solid var(--line);
         vertical-align:top; }
th { font-size:.78rem; text-transform:uppercase; letter-spacing:.04em;
     color:var(--muted); font-weight:600; }
tr.done td { opacity:.42; }
tr.pilot td { background:color-mix(in srgb, var(--ok) 9%, transparent); }
td.n { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
a.open { display:inline-block; padding:.3rem .65rem; border:1px solid var(--line);
         border-radius:5px; text-decoration:none; color:inherit;
         background:var(--card); white-space:nowrap; }
a.open:hover { border-color:var(--ok); }
.cs { color:var(--muted); font-size:.8rem; margin-top:.3rem; word-break:break-word; }
.copy { cursor:pointer; border:1px solid var(--line); background:var(--card);
        border-radius:4px; font-size:.72rem; padding:.1rem .4rem; color:inherit; }
.progress { position:sticky; top:0; background:var(--bg); padding:.7rem 0;
            border-bottom:1px solid var(--line); z-index:2; font-weight:600; }
ol.steps li, ul.steps li { margin:.4rem 0; }
"""

PAGE_JS = """
const KEY = 'guelph-unit-listing-retag-done';
const done = new Set(JSON.parse(localStorage.getItem(KEY) || '[]'));
function paint() {
  let objs = 0, batches = 0;
  document.querySelectorAll('tr[data-key]').forEach(tr => {
    const on = done.has(tr.dataset.key);
    tr.classList.toggle('done', on);
    tr.querySelector('input').checked = on;
    if (on) { batches++; objs += Number(tr.dataset.count); }
  });
  document.getElementById('tally').textContent =
    batches + ' of ' + TOTAL_BATCHES + ' batches uploaded \\u2014 ' +
    objs.toLocaleString() + ' of ' + TOTAL_OBJECTS.toLocaleString() + ' objects';
}
document.addEventListener('change', e => {
  if (e.target.matches('tr[data-key] input')) {
    const id = e.target.closest('tr').dataset.key;
    e.target.checked ? done.add(id) : done.delete(id);
    localStorage.setItem(KEY, JSON.stringify([...done]));
    paint();
  }
});
document.addEventListener('click', e => {
  if (e.target.matches('.copy')) {
    navigator.clipboard.writeText(e.target.dataset.text);
    const was = e.target.textContent;
    e.target.textContent = 'copied';
    setTimeout(() => { e.target.textContent = was; }, 900);
  }
});
paint();
"""


def _short(value: str, limit: int = 48) -> str:
    """A tower's list runs to hundreds of characters; the run sheet shows the
    head of it. The file carries the whole thing."""
    return value if len(value) <= limit else value[:limit - 1] + "…"


def render_page(records: list[dict], review: list[dict], stamp: str,
                fetched: int) -> str:
    total_objects = sum(r["count"] for r in records)
    by_reason = {reason: sum(1 for r in review if r["reason"] == reason)
                 for reason in REVIEW_REASONS}
    rows_html = []
    for rec in records:
        # JOSM remote control. 127.0.0.1 rather than localhost, matching
        # t2/maintenance.py, and an absolute path because /open_file wants one.
        url = ("http://127.0.0.1:8111/open_file?filename="
               + str(rec["path"]).replace("\\", "/"))
        sample = rec["sample"]
        sample_html = ""
        if sample:
            sample_html = (
                f"<div class='cs mono'>e.g. "
                f"{html.escape(sample['housenumber'])} "
                f"{html.escape(sample['street'])}: addr:unit="
                f"{html.escape(_short(sample['before_unit']))} &rarr; "
                f"addr:flats, same value</div>")
        streets = rec["streets"]
        street_html = ""
        if streets:
            shown = ", ".join(streets[:4])
            more = f" +{len(streets) - 4} more" if len(streets) > 4 else ""
            street_html = f"<div class='cs'>{html.escape(shown + more)}</div>"
        label = rec["area"] + ("" if rec["of"] == 1
                               else f" ({rec['part']}/{rec['of']})")
        is_pilot = rec["index"] == 1
        rows_html.append(f"""
      <tr class="{'pilot' if is_pilot else ''}" data-key="{rec['path'].stem}" data-count="{rec['count']}">
        <td><input type="checkbox" aria-label="batch {rec['index']} uploaded"></td>
        <td class="n">{rec['index']}{' <strong>PILOT</strong>' if is_pilot else ''}</td>
        <td><strong>{html.escape(label)}</strong>{street_html}{sample_html}</td>
        <td class="n">{rec['count']}</td>
        <td><a class="open" href="{html.escape(url)}">Open in JOSM</a>
            <div class="cs">{html.escape(rec['path'].name)}
            <button class="copy" data-text="{html.escape(rec['cs_tags']['comment'])}">copy comment</button></div></td>
      </tr>""")

    review_html = []
    for reason, (title, blurb) in REVIEW_REASONS.items():
        group = [r for r in review if r["reason"] == reason]
        if not group:
            continue
        rows = "".join(
            f"<tr><td class='mono'>{html.escape(r['type'])} {r['id']}</td>"
            f"<td class='mono'>{html.escape(r['housenumber'])}</td>"
            f"<td class='mono'>{html.escape(_short(r['unit']) or '—')}</td>"
            f"<td class='mono'>{html.escape(_short(r['flats']) or '—')}</td>"
            f"<td>{html.escape(r['street'])}</td>"
            f"<td><a href='https://www.openstreetmap.org/{r['type']}/{r['id']}'>osm.org</a> · "
            f"<a href='http://127.0.0.1:8111/load_object?objects="
            f"{r['type'][0]}{r['id']}'>JOSM</a></td></tr>"
            for r in sorted(group, key=lambda r: (r["street"], r["housenumber"])))
        review_html.append(
            f"<h3>{title} — {len(group)}</h3>"
            f"<p class='sub'>{blurb.format(wiki=WIKI)}</p>"
            f"<table><thead><tr><th>Object</th><th>housenumber</th><th>unit</th>"
            f"<th>flats</th><th>Street</th><th></th></tr></thead><tbody>{rows}</tbody></table>")

    return f"""<!doctype html>
<meta charset="utf-8">
<title>Guelph unit listing retag — run sheet</title>
<style>{PAGE_CSS}</style>
<h1>Guelph unit listing retag — run sheet</h1>
<p class="sub">Mechanical edit 3: <code>addr:unit=101-116;201-215;…</code>
&rarr; <code>addr:flats=101-116;201-215;…</code>, key only, value verbatim,
<code>addr:unit</code> removed. {total_objects:,} objects in {len(records)}
batches, prepared {html.escape(stamp)} · <a href="{WIKI_SECTION}">wiki</a> ·
<a href="{THREAD}">thread #135103</a></p>

<div class="banner warn"><strong>Not consented yet. Nothing on this page may
be uploaded.</strong> The announcement is drafted in
<code>ANNOUNCEMENT.md</code> beside this file and has <em>not</em> been posted
to <a href="{THREAD}">#135103</a>. It goes up after the wiki’s section 3 is
synced, opens a 14-day objection window, and only when that window has closed
with no objections do these batches become uploadable. These were prepared
before consent so the counts and the files could be looked at; on the day of
upload rebuild them with <code>build_batches.py --refetch</code>, because
every <code>version</code> in them will have moved by then.</div>

<div class="banner"><strong>What the fetch found.</strong>
{fetched:,} objects came back from Overpass carrying a list-valued
<code>addr:unit</code> or any <code>addr:flats</code>.
<strong>{total_objects:,} safe</strong> — a list, no <code>addr:flats</code>,
no hyphen in the housenumber. Refused: {by_reason['has-flats']} already carrying
<code>addr:flats</code>, {by_reason['hyphen-hn']} with a hyphenated
housenumber (edit 2’s), {by_reason['single']} single designators the fetch
caught but the rule does not. The wiki says 453 and 1.</div>

<div class="banner warn"><strong>Batch 1 is the pilot, and there is a gate
after it.</strong> Same promise as edit 2: a pilot posted to the thread with
its counts and changeset before anything else moves. Upload batch 1, post its
count and changeset link to the thread, then carry on.</div>

<div class="banner warn"><strong>One box to tick before any link here
works.</strong> JOSM &rarr; Preferences &rarr; Remote Control &rarr;
<strong>“Open local files”</strong>. Checked on this machine when the batches
were built: Remote Control is enabled, but that permission is not — so the
buttons below will silently do nothing until you tick it. The permission is
off by default in JOSM and has to be granted from JOSM’s own UI. If you would
rather not, every button has a file name beside it: drag that file out of
<code>mechanical-edits/unit-listing-retag/batches/</code> into JOSM, or File
&rarr; Open. Identical result.</div>

<h2>Before the first one</h2>
<ol class="steps">
  <li>The announcement has been posted and its 14-day window has closed with
      no objections. If that is not true, close this page.</li>
  <li>Be signed in as the account the announcement names — <code>skfd
      imports</code>, the one the import uploads from. Edit 2’s pilot went
      from the personal account by mistake; do not repeat it.</li>
  <li>Each file carries its own changeset comment, <code>source</code>,
      <code>source:license</code>, <code>mechanical=yes</code>,
      <code>bot=no</code> and <code>import_plan</code>; JOSM fills the upload
      dialog in from them, so there is nothing to paste.
      <code>created_by</code> will read <code>JOSM/…</code> rather than the
      wiki table’s <code>address-importer-friend</code> — JOSM always stamps
      its own, and a value that cannot survive the upload was not worth
      writing. Worth a line when you post the pilot.</li>
  <li>Every object carries the <code>version</code> it was prepared against.
      If someone else has edited it since, the upload 409s and JOSM raises a
      conflict — that is the promised “skipped and re-examined rather than
      overwritten”, working. Discard ours and re-run
      <code>build_batches.py --refetch</code> later.</li>
  <li><strong>Close each layer once it is uploaded.</strong> Remote-control
      opens otherwise stack layers, and JOSM uploads whichever one is active
      — not necessarily the one you just opened.</li>
  <li>Re-running <code>build_batches.py --refetch</code> <em>renumbers</em>
      everything: objects already fixed drop out of the fetch, the areas
      re-sort, and the pilot may move. The tick boxes are keyed by file name
      rather than number so they survive what they can, but expect to
      re-check. Anything already uploaded simply will not appear.</li>
  <li>Only the key changes: <code>addr:unit</code> goes,
      <code>addr:flats</code> arrives with the same bytes. Do not tidy the
      value in JOSM, and do not fold edit 2 or the <code>addr:province</code>
      campaign into these changesets — each is consented and revertable
      separately, and mixing them would make either revert take the other
      with it.</li>
</ol>

<h2>Batches</h2>
<div class="progress" id="tally"></div>
<table>
  <thead><tr><th></th><th class="n">#</th><th>Area</th><th class="n">Objects</th>
  <th>Open</th></tr></thead>
  <tbody>{''.join(rows_html)}</tbody>
</table>

<h2>By hand — {len(review)} objects this refuses to touch</h2>
<p class="sub">Three different reasons, so they are kept apart. None of them
is this campaign’s to change. Same list, with the reason, in
<code>review.csv</code>.</p>
{''.join(review_html)}

<h2>Records</h2>
<p class="sub"><code>manifest.csv</code> is the revert record: every edited
object with the version it was prepared against and its prior value, as
<a href="{WIKI}#Revert_plan">§ Revert plan</a> promises. The tick boxes above
live in this browser’s local storage, not in the file.</p>

<script>
const TOTAL_BATCHES = {len(records)};
const TOTAL_OBJECTS = {total_objects};
{PAGE_JS}
</script>
"""


# -------------------------------------------------------------------- main

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refetch", action="store_true",
                    help="pull the list-valued set from Overpass again")
    args = ap.parse_args()

    root = fetch_live(args.refetch)
    addressed, coords = index_live(root)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    areas = load_areas()
    print(f"{len(addressed)} addressed objects in the fetch, "
          f"{len(coords)} node positions, {len(areas)} areas")

    safe: list[dict] = []
    review: list[dict] = []
    fetched = 0
    for (kind, oid), el in addressed.items():
        tags = element_tags(el)
        if not (is_listing(tags.get("addr:unit")) or "addr:flats" in tags):
            continue  # a way's child node can carry its own single-unit door
        fetched += 1
        cls, reason = classify(tags)
        lon, lat = centre(el, coords)
        record = {
            "type": kind, "id": oid, "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "unit": tags.get("addr:unit", ""), "flats": tags.get("addr:flats", ""),
            "class": cls, "area": assign_area(lon, lat, areas),
        }
        if cls == "review":
            record["reason"] = reason
        (safe if cls == "safe" else review).append(record)
    by_reason = {reason: sum(1 for r in review if r["reason"] == reason)
                 for reason in REVIEW_REASONS}
    print(f"  {fetched} selected, {len(safe)} safe, {len(review)} refused "
          f"({', '.join(f'{k} {v}' for k, v in by_reason.items())})")

    batches = make_batches(safe)
    pilot = next((i for i, b in enumerate(batches)
                  if b["of"] == 1 and len(b["items"]) >= PILOT_MIN), None)
    if pilot is not None:
        batches.insert(0, batches.pop(pilot))

    total = len(batches)
    records = []
    for index, batch in enumerate(batches, 1):
        print(f"  batch {index}/{total}: {batch['area']} "
              f"({len(batch['items'])} objects)")
        records.append(write_batch(batch, index, total, addressed, by_node_id))

    with (HERE / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "batch", "area", "type", "id", "version", "street", "housenumber",
            "before_unit", "after_flats", "class"])
        writer.writeheader()
        for rec in records:
            writer.writerows(rec["rows"])
    with (HERE / "review.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "type", "id", "street", "housenumber", "unit", "flats", "area",
            "reason"], extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(review, key=lambda r: (r["street"],
                                                      r["housenumber"])))

    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    (HERE / "index.html").write_text(
        render_page(records, review, stamp, fetched), encoding="utf-8")
    print(f"\n{total} batches, {sum(r['count'] for r in records)} objects, "
          f"{len(review)} left for hand review")
    print(f"run sheet: {HERE / 'index.html'}")


if __name__ == "__main__":
    main()
