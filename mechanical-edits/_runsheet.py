"""The run sheet - one HTML page per campaign, the thing the operator works from.

Campaigns 2 and 3 each shipped an `index.html` with a JOSM remote-control link
per batch, a tick box that survives a reload, and a table of everything the
rules refused. This renders the same page from a `Campaign`, so campaign 4+5
and campaign 1 do not each re-grow it.

The page is deliberately plain HTML in one file: it is opened from the local
filesystem, days apart, while JOSM is the actual tool. The only state it keeps
is which batches have been uploaded, in `localStorage` under the campaign slug.
"""
from __future__ import annotations

import html
from pathlib import Path

from _common import THREAD, WIKI, WIKI_SECTION, Campaign

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
h3 { font-size:.95rem; margin:1.6rem 0 .3rem; }
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
const KEY = 'guelph-%SLUG%-done';
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


def short(value: str, limit: int = 48) -> str:
    """A tower's list runs to hundreds of characters; the run sheet shows the
    head of it. The file carries the whole thing."""
    value = value or ""
    return value if len(value) <= limit else value[:limit - 1] + "…"


def render(camp: Campaign, records: list[dict], review: list[dict],
           stamp: str, selected: int) -> str:
    total_objects = sum(r["count"] for r in records)
    total_batches = len(records)

    rows_html = []
    for rec in records:
        # JOSM remote control. 127.0.0.1 rather than localhost, matching
        # t2/maintenance.py, and an absolute path because /open_file wants one.
        url = ("http://127.0.0.1:8111/open_file?filename="
               + str(rec["path"]).replace("\\", "/"))
        sample_html = ""
        if rec["sample"]:
            body = camp.sample(rec["sample"])
            if body:
                sample_html = f"<div class='cs mono'>e.g. {body}</div>"
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

    extra_cols = [c for c in camp.review_columns
                  if c not in ("street", "housenumber")]
    review_html = []
    for reason, (title, blurb) in camp.review_reasons.items():
        group = [r for r in review if r.get("reason") == reason]
        if not group:
            continue
        body = "".join(
            f"<tr><td class='mono'>{html.escape(r['type'])} {r['id']}</td>"
            f"<td class='mono'>{html.escape(r.get('housenumber', ''))}</td>"
            + "".join(f"<td class='mono'>{html.escape(short(r.get(c, '')) or '—')}</td>"
                      for c in extra_cols)
            + f"<td>{html.escape(r.get('street', ''))}</td>"
            f"<td><a href='https://www.openstreetmap.org/{r['type']}/{r['id']}'>osm.org</a> · "
            f"<a href='http://127.0.0.1:8111/load_object?objects="
            f"{r['type'][0]}{r['id']}'>JOSM</a></td></tr>"
            for r in sorted(group, key=lambda r: (r.get("street", ""),
                                                  r.get("housenumber", ""))))
        heads = "".join(f"<th>{html.escape(c)}</th>" for c in extra_cols)
        review_html.append(
            f"<h3>{title} — {len(group)}</h3>"
            f"<p class='sub'>{blurb.format(wiki=WIKI, thread=THREAD)}</p>"
            f"<table><thead><tr><th>Object</th><th>housenumber</th>{heads}"
            f"<th>Street</th><th></th></tr></thead><tbody>{body}</tbody></table>")

    steps = "".join(f"<li>{s}</li>" for s in camp.steps)
    js = PAGE_JS.replace("%SLUG%", camp.slug)
    return f"""<!doctype html>
<meta charset="utf-8">
<title>{html.escape(camp.title)} — run sheet</title>
<style>{PAGE_CSS}</style>
<h1>{html.escape(camp.title)} — run sheet</h1>
<p class="sub">{camp.blurb}</p>

<div class="banner warn">
  <strong>Nothing here uploads itself.</strong> Open each batch in JOSM, look at
  it, then press upload. The changeset tags are pre-filled from the file;
  <code>created_by</code> is JOSM's own. Upload from the
  <code>skfd imports</code> account, not a personal one.
</div>

<p class="sub">Built {html.escape(stamp)} — {selected:,} objects selected,
{total_objects:,} batched across {total_batches} batches,
{len(review):,} left for hand review.
Plan: <a href="{WIKI_SECTION}">wiki § Mechanical edits</a> ·
Thread: <a href="{THREAD}">#135103</a></p>

<div class="progress" id="tally"></div>

<h2>Batches</h2>
<table>
  <thead><tr><th></th><th class="n">#</th><th>Area</th><th class="n">Objects</th>
  <th>Open</th></tr></thead>
  <tbody>{''.join(rows_html)}</tbody>
</table>

{'<h2>Order of work</h2><ol class="steps">' + steps + '</ol>' if steps else ''}

{'<h2>Left for hand review</h2>' + ''.join(review_html) if review_html else ''}

<script>
const TOTAL_BATCHES = {total_batches};
const TOTAL_OBJECTS = {total_objects};
{js}
</script>
"""


def write(here: Path, camp: Campaign, records: list[dict], review: list[dict],
          stamp: str, selected: int) -> Path:
    path = here / "index.html"
    path.write_text(render(camp, records, review, stamp, selected),
                    encoding="utf-8")
    return path
