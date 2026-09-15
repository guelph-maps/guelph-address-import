"""Mechanical edit 2/2 — split double-encoded unit housenumbers, prepared for JOSM.

    addr:housenumber = 714-30  ->  addr:housenumber = 714
    addr:unit        = 30          addr:unit        = 30   (untouched)

Consented on thread #135103 (post #14, 2026-08-28; the 14-day window closed
2026-09-10 with no objections, and the prior importer replied supportively in
#15) and documented at Guelph/Address_Import/Continuous#Mechanical_edits.

One Overpass query pulls every hyphenated object in the city *with meta and
child-node geometry*; everything after that is local. An earlier version asked
Overpass once per batch and got itself rate-limited for the trouble.

What this writes, all under this directory:

    live.osm                the raw fetch, cached — delete or --refetch to
                            refresh it
    batches/NN-<area>.osm   one JOSM-ready layer per batch: the live elements
                            with their real `version`, tags rewritten,
                            action="modify", changeset tags pre-filled
    manifest.csv            the revert record — one row per edited object with
                            the version it was prepared against and its
                            before/after housenumber
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
UA = "guelph-address-import/1.0 (unit-split prep; toronto@comentality.com)"

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
# post to the thread.
PILOT_MIN = 50

# `out meta` for the version numbers the upload checks against; `>;` for the
# ways' child nodes, without which JOSM has an incomplete way and refuses to
# upload it. No [out:xml] — XML is the default and some instances 406 on the
# collision with an explicit Accept.
LIVE_QUERY = f"""
[timeout:900];
area({AREA_ID})->.a;
nwr["addr:housenumber"~"-"](area.a);
out meta;
>;
out meta;
"""

_PAIR = re.compile(r"^\s*([0-9A-Za-z]+)\s*-\s*([0-9A-Za-z]+)\s*$")
_UNIT_PREFIX = re.compile(r"(?i)^(unit|suite|ste|apt|apartment|#)\s*\.?\s*")


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
        print("fetching every hyphenated Guelph address from Overpass "
              "(one query, a few minutes)...")
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

def norm_unit(unit: str) -> str:
    """`Unit 30`, `#30` and ` 30 ` all compare as `30`."""
    return _UNIT_PREFIX.sub("", unit.strip()).strip().upper()


def classify(tags: dict[str, str]) -> tuple[str, str | None]:
    """Return (class, new_housenumber).

    safe       the part after the hyphen is exactly addr:unit -> drop it.
               A lettered civic number keeps its letter: `12A-3` + unit 3
               leaves `12A`, per the Toronto import's precedent.
    identical  prefix and suffix are both the unit (`10-10` + unit 10). Every
               reading collapses to the same civic number, so the edit is not
               in doubt — but they go in their own batch so a human sees them
               together rather than buried among 5,500.
    review     anything else: no addr:unit to confirm the split, a `;` list
               form, or a unit matching neither end. Left alone; the published
               plan says these are handled by hand.
    """
    hn = tags.get("addr:housenumber", "")
    unit = tags.get("addr:unit")
    match = _PAIR.match(hn)
    if not match or unit is None:
        return "review", None
    prefix, suffix = match.group(1), match.group(2)
    wanted = norm_unit(unit)
    if not wanted:
        return "review", None
    hit_suffix = suffix.upper() == wanted
    hit_prefix = prefix.upper() == wanted
    if hit_suffix and hit_prefix:
        return "identical", prefix
    if hit_suffix:
        return "safe", prefix
    # Either a Canada Post ordered `30-714` (a different edit, not this one)
    # or a unit matching neither end (not understood). Both want eyes.
    return "review", None


# The three reasons an object lands in the by-hand list are different problems
# with different owners, so the run sheet separates them rather than showing
# one pile of 47.
REVIEW_REASONS = {
    "list": ("A <code>;</code>-separated list of housenumbers",
             "These belong to <a href='{wiki}#Open_questions_for_the_community'>"
             "open question 3</a> — the ~800 <code>;</code>-list objects the "
             "plan proposes as a MapRoulette challenge, not a batch — and not "
             "to this campaign at all. Listed here only because the hyphen "
             "query catches them."),
    "no-unit": ("A single hyphen, but no <code>addr:unit</code> to confirm it",
                "The ~17 the published plan says are done by hand. Each is "
                "either a genuine range (<code>380-400</code>) or a unit that "
                "nothing corroborates — a judgement per object."),
    "odd-unit": ("<code>addr:unit</code> matches neither side of the hyphen",
                 "Mostly spaces and slashes the mechanical rule will not "
                 "touch: <code>130-BLD D</code>, <code>10-6/7</code>. Several "
                 "are obvious splits by eye; do them by eye."),
}


def review_reason(housenumber: str, unit: str) -> str:
    if ";" in housenumber:
        return "list"
    if not unit:
        return "no-unit"
    return "odd-unit"


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
        if "addr:housenumber" in element_tags(el):
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
                       key=lambda r: (r["street"], r["new_hn"], r["id"]))
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
        "comment": (f"Guelph unit tagging: split double-encoded housenumbers "
                    f"(714-30 -> 714 + addr:unit=30) - {where} "
                    f"[batch {index}/{total}]"),
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
                             "generator": "guelph-unit-split"})
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
        before = tags["addr:housenumber"]
        rewrite_tags(el, {**tags, "addr:housenumber": item["new_hn"]})
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
            "before_housenumber": before, "after_housenumber": item["new_hn"],
            "addr_unit": tags.get("addr:unit", ""), "class": item["class"],
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
const KEY = 'guelph-unit-split-done';
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


def render_page(records: list[dict], review: list[dict], stamp: str) -> str:
    total_objects = sum(r["count"] for r in records)
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
                f"{html.escape(sample['before_housenumber'])} "
                f"{html.escape(sample['street'])} &rarr; "
                f"{html.escape(sample['after_housenumber'])} + unit "
                f"{html.escape(sample['addr_unit'])}</div>")
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
            f"<td class='mono'>{html.escape(r['unit'] or '—')}</td>"
            f"<td>{html.escape(r['street'])}</td>"
            f"<td><a href='https://www.openstreetmap.org/{r['type']}/{r['id']}'>osm.org</a> · "
            f"<a href='http://127.0.0.1:8111/load_object?objects="
            f"{r['type'][0]}{r['id']}'>JOSM</a></td></tr>"
            for r in sorted(group, key=lambda r: (r["street"], r["housenumber"])))
        review_html.append(
            f"<h3>{title} — {len(group)}</h3>"
            f"<p class='sub'>{blurb.format(wiki=WIKI)}</p>"
            f"<table><thead><tr><th>Object</th><th>housenumber</th><th>unit</th>"
            f"<th>Street</th><th></th></tr></thead><tbody>{rows}</tbody></table>")

    return f"""<!doctype html>
<meta charset="utf-8">
<title>Guelph unit split — run sheet</title>
<style>{PAGE_CSS}</style>
<h1>Guelph unit split — run sheet</h1>
<p class="sub">Mechanical edit 2 of 2: <code>addr:housenumber=714-30</code> +
<code>addr:unit=30</code> &rarr; <code>addr:housenumber=714</code>, unit
untouched. {total_objects:,} objects in {len(records)} batches, prepared
{html.escape(stamp)} · <a href="{WIKI_SECTION}">wiki</a> ·
<a href="{THREAD}">thread #135103</a></p>

<div class="banner"><strong>Consent is in.</strong> Announced in
<a href="{THREAD}">#135103</a> post #14 on 2026-08-28 with a 14-day objection
window to 2026-09-10. It closed five days ago with no objections, and
ARandomThumbtack — who had defended the combined form — replied supportively
in #15.</div>

<div class="banner warn"><strong>Batch 1 is the pilot, and there is a gate
after it.</strong> The announcement promised “a pilot tile posted here with its
counts and changeset before anything else moves.” Upload batch 1, post its
count and changeset link to the thread, then carry on.</div>

<h2>Before the first one</h2>
<ol class="steps">
  <li>JOSM &rarr; Preferences &rarr; Remote Control &rarr; enable it and tick
      <strong>“Open local files”</strong>. That box is off by default and the
      links below do nothing without it. If a link does nothing, the fallback
      is to open the <code>.osm</code> from
      <code>mechanical-edits/unit-split/batches/</code> by hand.</li>
  <li>Be signed in as the account the announcement named — the same one the
      import uploads from.</li>
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
  <li><strong>Close each layer once it is uploaded.</strong> Thirty-six
      remote-control opens otherwise stack thirty-six layers, and JOSM uploads
      whichever one is active — not necessarily the one you just opened.</li>
  <li>Re-running <code>build_batches.py --refetch</code> <em>renumbers</em>
      everything: objects already fixed drop out of the fetch, the areas
      re-sort, and the pilot may move. The tick boxes are keyed by file name
      rather than number so they survive what they can, but expect to
      re-check. Anything already uploaded simply will not appear.</li>
  <li>Only <code>addr:housenumber</code> changes. Do not fold the
      <code>addr:province</code> campaign into these changesets — it is
      consented and revertable separately, and mixing them would make either
      revert take the other with it.</li>
</ol>

<h2>Batches</h2>
<div class="progress" id="tally"></div>
<table>
  <thead><tr><th></th><th class="n">#</th><th>Area</th><th class="n">Objects</th>
  <th>Open</th></tr></thead>
  <tbody>{''.join(rows_html)}</tbody>
</table>

<h2>By hand — {len(review)} objects this refuses to touch</h2>
<p class="sub">Three different problems, so they are kept apart. None of them
is a mechanical edit; each object wants a look. Same list, with the reason, in
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
                    help="pull the hyphenated set from Overpass again")
    args = ap.parse_args()

    root = fetch_live(args.refetch)
    addressed, coords = index_live(root)
    by_node_id = {el.attrib["id"]: el for el in root if el.tag == "node"}
    areas = load_areas()
    print(f"{len(addressed)} addressed objects in the fetch, "
          f"{len(coords)} node positions, {len(areas)} areas")

    fixable: list[dict] = []
    review: list[dict] = []
    counts = {"safe": 0, "identical": 0, "review": 0}
    for (kind, oid), el in addressed.items():
        tags = element_tags(el)
        if "-" not in tags.get("addr:housenumber", ""):
            continue  # a way's child node can carry its own clean address
        cls, new_hn = classify(tags)
        counts[cls] += 1
        lon, lat = centre(el, coords)
        record = {
            "type": kind, "id": oid, "street": tags.get("addr:street", ""),
            "housenumber": tags.get("addr:housenumber", ""),
            "unit": tags.get("addr:unit", ""), "new_hn": new_hn or "",
            "class": cls, "area": assign_area(lon, lat, areas),
        }
        if cls == "review":
            record["reason"] = review_reason(record["housenumber"],
                                             record["unit"])
        (fixable if cls in ("safe", "identical") else review).append(record)
    print(f"  {counts['safe']} safe, {counts['identical']} identical, "
          f"{counts['review']} for hand review")

    # The `identical` handful rides at the end in its own batch — see classify.
    safe = [r for r in fixable if r["class"] == "safe"]
    identical = [r for r in fixable if r["class"] == "identical"]
    batches = make_batches(safe)
    pilot = next((i for i, b in enumerate(batches)
                  if b["of"] == 1 and len(b["items"]) >= PILOT_MIN), None)
    if pilot is not None:
        batches.insert(0, batches.pop(pilot))
    if identical:
        batches.append({"area": "Prefix and suffix identical (10-10)",
                        "part": 1, "of": 1,
                        "items": sorted(identical,
                                        key=lambda r: (r["street"], r["id"]))})

    total = len(batches)
    records = []
    for index, batch in enumerate(batches, 1):
        print(f"  batch {index}/{total}: {batch['area']} "
              f"({len(batch['items'])} objects)")
        records.append(write_batch(batch, index, total, addressed, by_node_id))

    with (HERE / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "batch", "area", "type", "id", "version", "street",
            "before_housenumber", "after_housenumber", "addr_unit", "class"])
        writer.writeheader()
        for rec in records:
            writer.writerows(rec["rows"])
    with (HERE / "review.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=[
            "type", "id", "street", "housenumber", "unit", "area", "reason"],
            extrasaction="ignore")
        writer.writeheader()
        writer.writerows(sorted(review, key=lambda r: (r["street"],
                                                      r["housenumber"])))

    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    (HERE / "index.html").write_text(render_page(records, review, stamp),
                                     encoding="utf-8")
    print(f"\n{total} batches, {sum(r['count'] for r in records)} objects, "
          f"{len(review)} left for hand review")
    print(f"run sheet: {HERE / 'index.html'}")


if __name__ == "__main__":
    main()
