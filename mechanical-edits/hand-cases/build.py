"""The leftovers from campaigns 2 and 3, sorted into what a rule can still do.

Both campaigns refused an object when its own tags could not corroborate the
edit. That was the right rule — but the City's address roster is a second
witness those campaigns never asked, and against it most of the leftovers stop
being ambiguous. 32 of the 48 become decidable, 3 are real ranges to be
left alone, 1 was already correct, and 12 genuinely need a person.

    corroborated   one civic number, units confirmed by the City roster.
                   Three shapes, all landing on the same destination as the
                   campaigns they fell out of:
                     37-1        (no addr:unit)   -> hn 37,  addr:unit 1
                     130-BLD D   (unit BLD D)     -> hn 130, addr:unit kept
                     33;33-C;33-B                 -> hn 33,  addr:flats B;C
    complex        several civic numbers on one object. No rule splits one way
                   into six addresses; these want door positions and a human.
    range          a real span of civic numbers. Left alone deliberately —
                   this is the case the campaigns were built to leave behind.
    settled        already correct. Listed so it is visibly not forgotten.

Writes batches/01-corroborated.osm (JOSM-ready, live versions, changeset tags
pre-filled), manifest.csv, complex.csv and index.html.

    python build.py
"""
from __future__ import annotations

import csv
import html
import re
import sqlite3
import sys
import time
from pathlib import Path
from xml.etree import ElementTree as ET

import requests

HERE = Path(__file__).resolve().parent
SPLIT = HERE.parent / "unit-split"
RETAG = HERE.parent / "unit-listing-retag"
API = "https://api.openstreetmap.org/api/0.6"
UA = {"User-Agent": "guelph-address-import/1.0 (hand-cases; toronto@comentality.com)"}
CITY_DB = Path(r"C:\Users\kk\Code\ontario-address-changes\data\guelph\guelph.db")

WIKI = "https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous"
WIKI_SECTION = WIKI + "#Mechanical_edits"
THREAD = ("https://community.openstreetmap.org/t/"
          "import-addresses-from-city-of-guelph-data/135103")

_PART = re.compile(r"^(\d+)(?:-(.+))?$")


# ------------------------------------------------------------- the roster

def city_units(db, snapshot, street, number) -> list[str]:
    return sorted(u for (u,) in db.execute(
        "SELECT unit FROM addresses WHERE street=? AND number=? AND max_snapshot_id=?",
        (street, str(number), snapshot)) if u)


def city_has(db, snapshot, street, number) -> bool:
    return db.execute(
        "SELECT 1 FROM addresses WHERE street=? AND number=? AND max_snapshot_id=? LIMIT 1",
        (street, str(number), snapshot)).fetchone() is not None


# ---------------------------------------------------------- classifying

def classify(row, db, snapshot) -> dict:
    """Decide one leftover. Returns the row with verdict/plan/evidence added."""
    hn = row["housenumber"]
    unit = (row.get("unit") or "").strip()
    street = row["street"]
    out = {**row, "new_hn": "", "new_unit": "", "new_flats": "", "evidence": ""}

    parts = [p.strip() for p in hn.split(";") if p.strip()]
    bases, suffixes = set(), []
    for part in parts:
        m = _PART.match(part)
        if not m:
            bases.add(part)
            continue
        bases.add(m.group(1))
        if m.group(2):
            suffixes.append(m.group(2))

    if len(bases) != 1:
        out["verdict"] = "complex"
        out["evidence"] = f"{len(bases)} distinct civic numbers on one object"
        return out

    base = next(iter(bases))
    roster = city_units(db, snapshot, street, base)

    wanted = sorted(set(suffixes) | ({unit.upper()} if unit else set()))
    wanted = [w for w in wanted if w]
    if not wanted:
        out["verdict"] = "complex"
        out["evidence"] = "nothing to move out of the housenumber"
        return out

    # The unit reading wins whenever the roster backs it. This has to come
    # first: `37-1` on Bond Court is unit 1 of number 37, and the City says so
    # — but read as a span it would be "37 down to 1", which is also a street
    # full of real odd-numbered addresses. Corroboration breaks the tie, and
    # getting this order wrong quietly moved twelve townhouses into the
    # leave-alone pile.
    roster_upper = {u.upper() for u in roster}
    if set(wanted) <= roster_upper:
        out["verdict"] = "corroborated"
        out["new_hn"] = base
        out["evidence"] = f"City lists {base} {street} with unit(s) {', '.join(roster)}"
        if len(parts) > 1 or len(wanted) > 1:
            out["new_flats"] = ";".join(wanted)   # building carrying its units
        else:
            out["new_unit"] = unit or wanted[0]   # one object, one unit
        return out

    # Not units, then. A single part with a numeric tail above the base, where
    # the City publishes BOTH ends as addresses of their own, is a real span.
    if len(parts) == 1 and not unit and len(wanted) == 1 and wanted[0].isdigit():
        hi = wanted[0]
        if (int(hi) > int(base) and city_has(db, snapshot, street, base)
                and city_has(db, snapshot, street, hi)):
            out["verdict"] = "range"
            out["evidence"] = (f"City publishes {base} and {hi} {street} as separate "
                               f"addresses, so this spans them — not a unit")
            return out
        out["verdict"] = "complex"
        missing = [n for n in (base, hi) if not city_has(db, snapshot, street, n)]
        out["evidence"] = (f"reads as the span {base}-{hi}, but the City has no "
                           f"{' or '.join(missing)} {street}"
                           if missing else
                           f"reads as the span {base}-{hi}, which runs backwards")
        return out

    out["verdict"] = "complex"
    out["evidence"] = (f"City lists units {roster or 'none'} at {base} {street}; "
                       f"OSM claims {wanted} — not corroborated")
    return out



def load_leftovers() -> list[dict]:
    rows, seen = [], set()
    for path, kind in ((SPLIT / "review.csv", "split"),
                       (RETAG / "review.csv", "retag")):
        if not path.exists():
            continue
        for r in csv.DictReader(open(path, encoding="utf-8")):
            key = (r["type"], r["id"])
            if key in seen:
                continue  # one object can fall out of both campaigns
            seen.add(key)
            rows.append({"type": r["type"], "id": r["id"], "street": r["street"],
                         "housenumber": r["housenumber"], "unit": r.get("unit", ""),
                         "area": r.get("area", ""), "from": kind})
    return rows


# -------------------------------------------------------------- the batch

def fetch_live(rows) -> dict:
    by_type = {}
    for r in rows:
        by_type.setdefault(r["type"], []).append(r["id"])
    live = {}
    for t, ids in by_type.items():
        plural = t + "s"
        for k in range(0, len(ids), 400):
            chunk = ids[k:k + 400]
            resp = requests.get(f"{API}/{plural}", params={plural: ",".join(chunk)},
                                headers=UA, timeout=180)
            resp.raise_for_status()
            for el in ET.fromstring(resp.content):
                if el.tag in ("node", "way"):
                    live[(el.tag, el.get("id"))] = el
            time.sleep(1)
    # Ways need their nodes for JOSM to have complete geometry.
    need = set()
    for (t, _), el in list(live.items()):
        if t == "way":
            need.update(nd.get("ref") for nd in el.findall("nd"))
    need -= {i for (t, i) in live if t == "node"}
    need = sorted(need)
    for k in range(0, len(need), 400):
        chunk = need[k:k + 400]
        resp = requests.get(f"{API}/nodes", params={"nodes": ",".join(chunk)},
                            headers=UA, timeout=180)
        resp.raise_for_status()
        for el in ET.fromstring(resp.content):
            if el.tag == "node":
                live[("node", el.get("id"))] = el
        time.sleep(1)
    return live


def element_tags(el):
    return {t.get("k"): t.get("v") for t in el.findall("tag")}


def write_batch(rows, live) -> tuple[Path, list[dict]]:
    out = ET.Element("osm", {"version": "0.6", "generator": "guelph-hand-cases"})
    cs = ET.SubElement(out, "changeset")
    cs_tags = {
        "comment": ("Guelph unit tagging: split the combined form on objects the "
                    "City roster corroborates (the campaign 2/3 leftovers)"),
        "source": "Guelph Open Data",
        "source:license": "OGL-Canada-2.0",
        "mechanical": "yes",
        "bot": "no",
        "import_plan": WIKI_SECTION,
    }
    for k, v in cs_tags.items():
        ET.SubElement(cs, "tag", k=k, v=v)

    manifest, edited, keep_nodes = [], [], set()
    for r in rows:
        el = live.get((r["type"], r["id"]))
        if el is None:
            continue
        tags = element_tags(el)
        before_hn = tags.get("addr:housenumber", "")
        before_unit = tags.get("addr:unit", "")
        new = dict(tags)
        new["addr:housenumber"] = r["new_hn"]
        if r["new_flats"]:
            new["addr:flats"] = r["new_flats"]
            new.pop("addr:unit", None)
        else:
            new["addr:unit"] = r["new_unit"]
        for t in el.findall("tag"):
            el.remove(t)
        for k, v in new.items():
            ET.SubElement(el, "tag", k=k, v=v)
        el.set("action", "modify")
        edited.append(el)
        if el.tag == "way":
            keep_nodes.update(nd.get("ref") for nd in el.findall("nd"))
        manifest.append({
            "type": r["type"], "id": r["id"], "version": el.get("version"),
            "street": r["street"], "area": r["area"],
            "before_housenumber": before_hn, "before_unit": before_unit,
            "after_housenumber": r["new_hn"], "after_unit": r["new_unit"],
            "after_flats": r["new_flats"], "evidence": r["evidence"],
        })

    nodes = [live[("node", i)] for i in sorted(keep_nodes) if ("node", i) in live]
    seen = {id(e) for e in edited}
    for el in nodes:
        if id(el) not in seen:
            out.append(el)
    for el in edited:
        if el.tag == "node":
            out.append(el)
    for el in edited:
        if el.tag == "way":
            out.append(el)

    (HERE / "batches").mkdir(exist_ok=True)
    path = HERE / "batches" / "01-corroborated.osm"
    ET.ElementTree(out).write(path, encoding="utf-8", xml_declaration=True)
    return path, manifest


# ---------------------------------------------------------------- the page

CSS = """
:root { color-scheme: light dark; --line:#d5d7db; --muted:#6b7177; --ok:#1f7a3f;
        --warn:#8a5a00; --stop:#a33; --bg:#fff; --fg:#16181d; --card:#fafbfc; }
@media (prefers-color-scheme: dark) { :root { --line:#3a3f46; --muted:#9aa1a9;
  --ok:#6fcf8f; --warn:#e0b25c; --stop:#e08585; --bg:#14171a; --fg:#e8eaed; --card:#1b1f23; } }
* { box-sizing:border-box; }
body { margin:0 auto; padding:2rem 1.25rem 6rem; max-width:64rem; background:var(--bg);
       color:var(--fg); font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif; }
h1 { font-size:1.5rem; margin:0 0 .25rem; } h2 { font-size:1.1rem; margin:2.2rem 0 .5rem; }
.sub { color:var(--muted); margin:0 0 1.2rem; }
.banner { border:1px solid var(--line); border-left:4px solid var(--ok); background:var(--card);
          padding:.85rem 1rem; border-radius:6px; margin:0 0 1rem; }
.banner.warn { border-left-color:var(--warn); } .banner.stop { border-left-color:var(--stop); }
code,.mono { font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:.86em; }
table { border-collapse:collapse; width:100%; }
th,td { text-align:left; padding:.45rem .5rem; border-bottom:1px solid var(--line); vertical-align:top; }
th { font-size:.75rem; text-transform:uppercase; letter-spacing:.04em; color:var(--muted); }
a.btn { display:inline-block; padding:.3rem .65rem; border:1px solid var(--line); border-radius:5px;
        text-decoration:none; color:inherit; background:var(--card); white-space:nowrap; }
a.btn:hover { border-color:var(--ok); }
.ev { color:var(--muted); font-size:.8rem; }
.arrow { color:var(--ok); font-weight:600; }
"""


def josm_all(rows) -> str:
    objs = ",".join(f"{r['type'][0]}{r['id']}" for r in rows)
    return f"http://127.0.0.1:8111/load_object?objects={objs}"


def links(r) -> str:
    t, i = r["type"], r["id"]
    return (f"<a class='btn' href='https://www.openstreetmap.org/{t}/{i}'>osm</a> "
            f"<a class='btn' href='http://127.0.0.1:8111/load_object?objects={t[0]}{i}'>josm</a> "
            f"<a class='btn' href='https://www.openstreetmap.org/edit?editor=id&{t}={i}'>iD</a> "
            f"<a class='btn' href='https://osmlab.github.io/osm-deep-history/#/{t}/{i}'>history</a>")


def render(groups, batch_path, stamp) -> str:
    def rows_html(rows, plan=True):
        out = []
        for r in sorted(rows, key=lambda x: (x["street"], x["housenumber"])):
            after = ""
            if plan and r["verdict"] == "corroborated":
                bits = [f"<code>{html.escape(r['new_hn'])}</code>"]
                if r["new_flats"]:
                    bits.append(f"<code>addr:flats={html.escape(r['new_flats'])}</code>")
                else:
                    bits.append(f"<code>addr:unit={html.escape(r['new_unit'])}</code>")
                after = "<span class='arrow'>&rarr;</span> " + " + ".join(bits)
            out.append(
                f"<tr><td>{html.escape(r['street'])}</td>"
                f"<td class='mono'>{html.escape(r['housenumber'])}"
                + (f" <span class='mono'>[unit {html.escape(r['unit'])}]</span>" if r['unit'] else "")
                + f"</td><td>{after}<div class='ev'>{html.escape(r['evidence'])}</div></td>"
                f"<td>{links(r)}</td></tr>")
        return "".join(out)

    corro, complex_, rng, settled = (groups["corroborated"], groups["complex"],
                                     groups["range"], groups["settled"])
    return f"""<!doctype html>
<meta charset="utf-8"><title>Guelph hand cases</title><style>{CSS}</style>
<h1>Guelph — what the campaigns left behind</h1>
<p class="sub">{len(corro) + len(complex_) + len(rng) + len(settled)} objects that
campaigns 2 and 3 refused, re-decided against the City's address roster.
Prepared {html.escape(stamp)} · <a href="{WIKI_SECTION}">wiki</a> ·
<a href="{THREAD}">thread #135103</a></p>

<div class="banner"><strong>The roster is the second witness.</strong> Both
campaigns refused an object when its own tags could not corroborate the edit.
The City publishes the unit roster for every civic address, and against it
<strong>{len(corro)} of these stop being ambiguous</strong> — every unit OSM
claims is a unit the City lists at that address.</div>

<h2>Mechanical after all — {len(corro)} objects, one changeset</h2>
<p class="sub">Open <code>{html.escape(batch_path.name)}</code> in JOSM, or
<a href="{josm_all(corro)}">load all {len(corro)} live</a> to look before
deciding.</p>
<p><a class="btn" href="http://127.0.0.1:8111/open_file?filename={html.escape(str(batch_path).replace(chr(92), '/'))}">Open the batch in JOSM</a></p>
<table><thead><tr><th>Street</th><th>OSM now</th><th>Becomes</th><th>Links</th></tr></thead>
<tbody>{rows_html(corro)}</tbody></table>

<h2 id="complex">Yours, definitely — {len(complex_)} objects</h2>
<div class="banner stop"><strong>No rule fixes these.</strong> Most carry
several distinct civic numbers on one object, and nothing can split one way
into six addresses — they want door positions, which is a survey decision, not
a tagging one. The rest are cases where OSM and the City disagree about what
exists, and that disagreement has to be resolved before any tag is right.</div>
<p class="sub"><a href="{josm_all(complex_)}">Load all {len(complex_)} in JOSM
at once</a>, or take them one at a time below.</p>
<table><thead><tr><th>Street</th><th>OSM now</th><th>Why it is yours</th><th>Links</th></tr></thead>
<tbody>{rows_html(complex_, plan=False)}</tbody></table>

<h2>Leave alone — {len(rng)} genuine ranges</h2>
<p class="sub">A real span of civic numbers, confirmed by the City publishing
both ends as separate addresses. This is the case the campaigns were built to
leave behind: once the double encoding is gone, a hyphen that survives is a
range.</p>
<table><thead><tr><th>Street</th><th>OSM now</th><th>Evidence</th><th>Links</th></tr></thead>
<tbody>{rows_html(rng, plan=False)}</tbody></table>

<h2>Already correct — {len(settled)}</h2>
<table><thead><tr><th>Street</th><th>OSM now</th><th>Note</th><th>Links</th></tr></thead>
<tbody>{rows_html(settled, plan=False)}</tbody></table>
"""


def main() -> None:
    if not CITY_DB.exists():
        sys.exit(f"City roster not found at {CITY_DB}")
    db = sqlite3.connect(CITY_DB)
    snapshot = db.execute("SELECT max(max_snapshot_id) FROM addresses").fetchone()[0]

    rows = load_leftovers()
    print(f"{len(rows)} distinct leftovers from both campaigns "
          f"(City snapshot {snapshot})")

    decided = [classify(r, db, snapshot) for r in rows]
    for r in decided:
        # The one object already carrying addr:flats is correct, not complex.
        if r["from"] == "retag" and not r["housenumber"].count(";") and r["verdict"] == "complex" \
                and "nothing to move" in r["evidence"]:
            r["verdict"] = "settled"
            r["evidence"] = "already carries addr:flats; campaign 3 skipped it by design"

    groups = {k: [r for r in decided if r["verdict"] == k]
              for k in ("corroborated", "complex", "range", "settled")}
    for k, v in groups.items():
        print(f"  {k:>13}: {len(v)}")

    corro = groups["corroborated"]
    print("fetching live elements...")
    live = fetch_live(corro)
    batch_path, manifest = write_batch(corro, live)
    print(f"wrote {batch_path.name} with {len(manifest)} objects")

    with (HERE / "manifest.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)
    with (HERE / "complex.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["type", "id", "street", "housenumber",
                                           "unit", "area", "evidence"],
                           extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(groups["complex"], key=lambda r: r["street"]))

    stamp = __import__("datetime").datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
    (HERE / "index.html").write_text(render(groups, batch_path, stamp), encoding="utf-8")
    print(f"page: {HERE / 'index.html'}")


if __name__ == "__main__":
    main()
