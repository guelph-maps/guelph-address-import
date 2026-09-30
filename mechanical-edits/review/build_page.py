"""One page for every object the mechanical edits left to a human.

    python build_page.py

Reads the review.csv each campaign already writes, plus its cached live.osm
for the tags, and writes index.html beside this file. Nothing is fetched:
rebuild the campaigns with --refetch first if the caches are old.

Three sections:

* province-removal leftovers - still carry addr:province; relations and
  objects with no housenumber, which the batches refused.
* interpolation ways with 3+ nodes - campaign 4 left them out of scope. Each
  is triaged here by its end nodes: both numbered and matching the parity is
  probably fine; anything else wants eyes.
* unit-door holds - edit 6 is parked, so these only matter if it is revived.

Ticks and notes live in the browser's localStorage, keyed by object, so a
rebuild keeps them.
"""
from __future__ import annotations

import csv
import html
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "index.html"


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_osm(path: Path, wanted: set[tuple[str, str]] | None):
    """Tags of wanted objects (all, if None), way node lists, node tags."""
    tags: dict[tuple[str, str], dict] = {}
    nds: dict[str, list[str]] = {}
    for _, el in ET.iterparse(path, events=("end",)):
        if el.tag not in ("node", "way", "relation"):
            continue
        key = (el.tag, el.attrib["id"])
        if wanted is None or key in wanted:
            tags[key] = {t.attrib["k"]: t.attrib["v"] for t in el.findall("tag")}
            if el.tag == "way":
                nds[el.attrib["id"]] = [n.attrib["ref"] for n in el.findall("nd")]
        el.clear()
    return tags, nds


def num(h: str) -> int | None:
    digits = "".join(c for c in h if c.isdigit())
    return int(digits) if digits and h[: len(digits)].isdigit() else None


def province_items() -> list[dict]:
    rows = read_csv(ROOT / "province-removal" / "review.csv")
    wanted = {(r["type"], r["id"]) for r in rows}
    tags, _ = load_osm(ROOT / "province-removal" / "live.osm", wanted)
    why = {"relation": "Relation — never batched",
           "no-address": "No housenumber — not an address"}
    out = []
    for r in rows:
        t = tags.get((r["type"], r["id"]), {})
        name = t.get("name") or t.get("addr:street") or ""
        kind = next((f"{k}={t[k]}" for k in
                     ("building", "amenity", "shop", "place", "boundary",
                      "leisure", "landuse", "office", "tourism", "highway")
                     if k in t), "")
        out.append({
            "type": r["type"], "id": r["id"], "area": r["area"],
            "title": " ".join(x for x in (r["housenumber"], name) if x) or kind or "(untitled)",
            "sub": kind, "flag": why.get(r["reason"], r["reason"]),
            "tags": t,
        })
    return out


def interpolation_items() -> list[dict]:
    rows = [r for r in read_csv(ROOT / "flats-hygiene" / "review.csv")
            if r["reason"] == "interpolation-multinode"]
    tags, nds = load_osm(ROOT / "flats-hygiene" / "live.osm", None)
    out = []
    for r in rows:
        t = tags.get(("way", r["id"]), {})
        nodes = nds.get(r["id"], [])
        ends = [tags.get(("node", n), {}) for n in (nodes[:1] + nodes[-1:])]
        hn = [e.get("addr:housenumber", "") for e in ends]
        mids = sum(1 for n in nodes[1:-1]
                   if tags.get(("node", n), {}).get("addr:housenumber"))
        street = next((e.get("addr:street") for e in ends if e.get("addr:street")), "")
        kind = t.get("addr:interpolation", "")
        problems = []
        if not all(hn):
            problems.append(f"{2 - sum(1 for h in hn if h)} end(s) without housenumber")
        else:
            a, b = num(hn[0]), num(hn[1])
            if kind in ("odd", "even") and None not in (a, b):
                want = 1 if kind == "odd" else 0
                if a % 2 != want or b % 2 != want:
                    problems.append(f"ends {hn[0]}/{hn[1]} do not fit {kind}")
            if a is not None and a == b:
                problems.append("both ends carry the same number")
        streets = {e.get("addr:street") for e in ends if e.get("addr:street")}
        if len(streets) > 1:
            problems.append("ends on different streets")
        out.append({
            "type": "way", "id": r["id"], "area": r["area"],
            "title": f"{hn[0] or '?'} … {hn[1] or '?'} {street}".strip(),
            "sub": f"interpolation={kind} · {len(nodes)} nodes · "
                   f"{mids} numbered in between",
            "flag": "; ".join(problems) or "Ends numbered — probably fine",
            "ok": not problems,
            "tags": t,
        })
    out.sort(key=lambda i: (i["ok"], i["area"], i["title"]))
    return out


def unit_items() -> list[dict]:
    rows = read_csv(ROOT / "unit-doors" / "review.csv")
    why = {
        "osm-unit-not-in-city": "Guard: OSM lists a unit the City lacks",
        "shape-review": "Classifier says review",
        "shape-civic-only": "Classifier says civic-only",
        "no-source-group": "No City group at this address",
    }
    out = []
    for r in rows:
        out.append({
            "type": r["type"], "id": r["id"], "area": r["area"],
            "group": f"{r['housenumber']} {r['street']}",
            "title": f"{r['housenumber']} {r['street']}",
            "sub": f"addr:flats={r['flats']}"
                   + (f" · {r['detail']}" if r["detail"] else ""),
            "flag": why.get(r["reason"], r["reason"]),
            "hot": r["reason"] == "osm-unit-not-in-city",
            "tags": {},
        })
    out.sort(key=lambda i: (not i["hot"], i["flag"], i["group"]))
    return out


SECTIONS = [
    ("province", "Province leftovers",
     "Refused by campaign 1 and still carrying <code>addr:province</code>. "
     "Relations were never batched; the rest have no housenumber, so they are "
     "streets, campuses, parks or POIs rather than addresses. Usually the "
     "answer is: delete the tag by hand. Sometimes the object wants an address "
     "or is the wrong thing entirely.", province_items),
    ("interp", "Interpolation ways, 3+ nodes",
     "Campaign 4 left these out of scope: an interpolation way may have "
     "intermediate nodes. Triaged here by their ends. Flagged ones first; "
     "&ldquo;probably fine&rdquo; ones are listed so the claim is checkable.",
     interpolation_items),
    ("units", "Unit-door holds (edit 6, parked)",
     "Only matters if edit 6 comes back. The two guard hits are real "
     "data questions either way; the rest are groups the classifier would not "
     "decide.", unit_items),
]


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Guelph manual review</title>
<style>
:root{--bg:#fbfaf7;--fg:#1f2328;--muted:#6b7078;--line:#e3e0d8;--card:#fff;
--accent:#2f6fb0;--warn:#b5471b;--warnbg:#fdf0ea;--ok:#2e7d4f;--okbg:#eaf6ee;--done:.45}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#15171a;--fg:#e6e3dc;
--muted:#9aa0a8;--line:#2c3036;--card:#1c1f23;--accent:#79aee6;--warn:#f08a5d;--warnbg:#3a2219;
--ok:#6fcf97;--okbg:#18301f}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 80px}
h1{font-size:1.5rem;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 20px}
.bar{position:sticky;top:0;z-index:2;background:var(--bg);padding:10px 0;display:flex;
gap:8px;flex-wrap:wrap;align-items:center;border-bottom:1px solid var(--line)}
.bar input[type=search]{flex:1;min-width:180px;padding:7px 10px;border:1px solid var(--line);
border-radius:6px;background:var(--card);color:var(--fg);font:inherit}
.tabs button,.btn{border:1px solid var(--line);background:var(--card);color:var(--fg);
padding:6px 10px;border-radius:6px;font:inherit;cursor:pointer}
.tabs button[aria-pressed=true]{background:var(--accent);color:#fff;border-color:var(--accent)}
.bar label{color:var(--muted);white-space:nowrap}
section{margin-top:28px}
section h2{font-size:1.15rem;margin:0 0 4px;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
section h2 .count{color:var(--muted);font-weight:400;font-size:.95rem}
section>p{color:var(--muted);margin:0 0 12px;max-width:75ch}
.row{display:grid;grid-template-columns:24px 1fr auto;gap:10px;align-items:start;
background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 12px;margin:6px 0}
.row.done{opacity:var(--done)}
.row.done .title{text-decoration:line-through}
.title{font-weight:600}
.meta{color:var(--muted);font-size:.87rem}
.flag{display:inline-block;font-size:.8rem;padding:1px 7px;border-radius:10px;margin-top:3px;
background:var(--warnbg);color:var(--warn)}
.flag.ok{background:var(--okbg);color:var(--ok)}
.links{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.links a,.links button{font-size:.85rem;color:var(--accent);background:none;
border:1px solid var(--line);border-radius:5px;padding:2px 8px;text-decoration:none;cursor:pointer}
details.tags{margin-top:4px;font-size:.82rem}
details.tags summary{color:var(--muted);cursor:pointer}
details.tags table{border-collapse:collapse;margin-top:4px}
details.tags td{padding:1px 8px 1px 0;vertical-align:top;font-family:ui-monospace,monospace;word-break:break-all}
details.tags td:first-child{color:var(--muted);white-space:nowrap}
.note{width:100%;margin-top:6px;padding:4px 8px;border:1px solid var(--line);border-radius:5px;
background:transparent;color:var(--fg);font:inherit;font-size:.87rem}
input[type=checkbox]{width:18px;height:18px;margin-top:2px}
#toast{position:fixed;bottom:16px;left:50%;transform:translateX(-50%);background:var(--fg);
color:var(--bg);padding:8px 14px;border-radius:6px;opacity:0;transition:opacity .2s;pointer-events:none}
#toast.show{opacity:.92}
@media (max-width:640px){.row{grid-template-columns:24px 1fr}.links{grid-column:2;justify-content:flex-start}}
</style></head><body><main>
<h1>Guelph manual review</h1>
<p class="sub">Everything the mechanical edits left to a human. Built __STAMP__ from each
campaign's cached <code>live.osm</code>; regenerate with <code>python build_page.py</code>.
Ticks and notes stay in this browser. JOSM buttons need JOSM running with Remote Control on.</p>
<div class="bar">
 <span class="tabs" id="tabs"></span>
 <input type="search" id="q" placeholder="Filter by street, id, area, flag…">
 <label><input type="checkbox" id="hideDone"> hide done</label>
 <label><input type="checkbox" id="hideOk"> hide “probably fine”</label>
</div>
<div id="out"></div>
<div id="toast"></div>
</main>
<script>
const DATA = __DATA__;
const KEY = "guelph-manual-review";
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || "{}"); } catch (e) {}
const save = () => { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} };
const k = i => i.type[0] + i.id;
let tab = "all";
try { tab = localStorage.getItem(KEY + ":tab") || "all"; } catch (e) {}
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

function toast(msg) {
  const t = document.getElementById("toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove("show"), 1800);
}
function josm(ids) {
  const url = "http://127.0.0.1:8111/load_object?new_layer=false&relation_members=true&objects=" + ids.join(",");
  fetch(url).then(r => toast(r.ok ? "Sent to JOSM" : "JOSM said " + r.status))
    .catch(() => toast("JOSM not reachable on :8111"));
}

function tabs() {
  const el = document.getElementById("tabs");
  const all = [["all", "All"]].concat(DATA.map(s => [s.key, s.name]));
  el.innerHTML = all.map(([key, name]) =>
    `<button data-tab="${key}" aria-pressed="${tab === key}">${esc(name)}</button>`).join(" ");
  el.onclick = e => { const b = e.target.closest("button"); if (!b) return;
    tab = b.dataset.tab; try { localStorage.setItem(KEY + ":tab", tab); } catch (x) {} tabs(); render(); };
}

function render() {
  const q = document.getElementById("q").value.trim().toLowerCase();
  const hideDone = document.getElementById("hideDone").checked;
  const hideOk = document.getElementById("hideOk").checked;
  let html = "";
  for (const s of DATA) {
    if (tab !== "all" && tab !== s.key) continue;
    const done = s.items.filter(i => state[k(i)]?.done).length;
    const vis = s.items.filter(i => {
      if (hideDone && state[k(i)]?.done) return false;
      if (hideOk && i.ok) return false;
      if (!q) return true;
      return [i.title, i.sub, i.flag, i.area, i.id, state[k(i)]?.note || ""]
        .join(" ").toLowerCase().includes(q);
    });
    const ids = vis.map(i => i.type[0] + i.id);
    html += `<section><h2>${esc(s.name)} <span class="count">${done} of ${s.items.length} done` +
      (vis.length !== s.items.length ? ` · ${vis.length} shown` : "") + `</span>` +
      (ids.length ? `<button class="btn" data-all="${ids.join(",")}">Load ${ids.length} shown in JOSM</button>` : "") +
      `</h2><p>${s.blurb}</p>`;
    for (const i of vis) {
      const st = state[k(i)] || {};
      const tags = Object.entries(i.tags);
      html += `<div class="row${st.done ? " done" : ""}" data-k="${k(i)}">
        <input type="checkbox" ${st.done ? "checked" : ""} aria-label="done">
        <div><div class="title">${esc(i.title)}</div>
          <div class="meta">${esc(i.type)} ${esc(i.id)} · ${esc(i.area)}${i.sub ? " · " + esc(i.sub) : ""}</div>
          <span class="flag${i.ok ? " ok" : ""}">${esc(i.flag)}</span>
          ${tags.length ? `<details class="tags"><summary>${tags.length} tags</summary><table>` +
            tags.map(([a, b]) => `<tr><td>${esc(a)}</td><td>${esc(b)}</td></tr>`).join("") + `</table></details>` : ""}
          <input class="note" placeholder="note…" value="${esc(st.note || "")}">
        </div>
        <div class="links">
          <button data-josm="${i.type[0]}${i.id}">JOSM</button>
          <a href="https://www.openstreetmap.org/${i.type}/${i.id}" target="_blank" rel="noopener">OSM</a>
          <a href="https://www.openstreetmap.org/${i.type}/${i.id}/history" target="_blank" rel="noopener">history</a>
        </div></div>`;
    }
    html += `</section>`;
  }
  document.getElementById("out").innerHTML = html || "<p>Nothing matches.</p>";
}

const out = document.getElementById("out");
out.addEventListener("click", e => {
  const j = e.target.closest("[data-josm]"); if (j) return josm([j.dataset.josm]);
  const a = e.target.closest("[data-all]"); if (a) return josm(a.dataset.all.split(","));
});
out.addEventListener("change", e => {
  const row = e.target.closest(".row"); if (!row) return;
  const s = state[row.dataset.k] ||= {};
  if (e.target.type === "checkbox") { s.done = e.target.checked; row.classList.toggle("done", s.done); }
  else if (e.target.classList.contains("note")) s.note = e.target.value;
  save();
});
for (const id of ["q", "hideDone", "hideOk"])
  document.getElementById(id).addEventListener("input", render);
tabs(); render();
</script></body></html>
"""


def main() -> None:
    data = []
    for key, name, blurb, fn in SECTIONS:
        items = fn()
        data.append({"key": key, "name": name, "blurb": blurb, "items": items})
        extra = ""
        if key == "interp":
            extra = f" ({sum(1 for i in items if not i['ok'])} flagged)"
        print(f"{name}: {len(items)}{extra}")
    stamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M")
    page = (PAGE.replace("__STAMP__", html.escape(stamp))
            .replace("__DATA__", json.dumps(data, ensure_ascii=False)
                     .replace("</", "<\\/")))
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
