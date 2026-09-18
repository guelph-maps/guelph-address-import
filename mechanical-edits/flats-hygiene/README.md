# Mechanical edits 4 + 5 — addr:flats hygiene

```
addr:interpolation = all        ->  (removed)     on closed ways and nodes only
addr:flats = 101;102;103;       ->  101-103       re-rendered by the import's own renderer
```

Two campaigns, one builder, one batch set, one revert. 74 of the 81 objects
carrying a meaningless `addr:interpolation` also carry `addr:flats` — 71 of
the 78 closed ways, and all 3 of the nodes. TODO.md says "74 of the 78 closed
ways"; measured on 2026-09-17 it is 71 of 78 plus the 3 nodes, which is why 7
closed ways here lose `addr:interpolation` and have no `addr:flats` at all.
Building the two campaigns separately would have had the second conflicting
against the first on
object version, and would have announced twice what a reader sees as one
cleanup of the same apartment buildings.

Prepared 2026-09-17 against live OSM, **before consent**, so the counts and
the files could be looked at. `index.html` is the run sheet; it says the same
thing in a banner. This file is for whoever comes back to the machinery later.

## Where the consent is

**Posted 2026-09-18 as post #21** on [thread #135103][thread]. Upload is the
weekend of **2026-09-19/20** — no 14-day window, the same call as campaign 3
and the units reversal, with the standing offer to revert on request in
`IMPORT_PROPOSAL.mediawiki` § Status.

The posted form is condensed and drops four things the draft in
[`ANNOUNCEMENT.md`](ANNOUNCEMENT.md) carried: the 81-of-635 figure with the
554 objects left alone, the round-trip gate, the batch plan and its pilot, and
the timing paragraph — which is where the no-window statement and the revert
offer lived. #21 ends "Will update this post when it's done" and can still
take them. That matters most for the timing paragraph: proceeding without a
window is defensible *stated*, and the post does not currently state it.

The batches in `batches/` were built against the versions live on 2026-09-17.
By upload day those will have moved, so the first step that morning is
`build_batches.py --refetch`, not JOSM.

## What is in scope, and what is deliberately not

Re-measured against live OSM on **2026-09-17**, which is after campaign 3
landed. TODO.md's numbers predate that and are not the ones below.

### Campaign 4 — `addr:interpolation`

`addr:interpolation` describes a way drawn between two address nodes: the
numbers run from the housenumber at one end to the housenumber at the other.
Anywhere else it cannot mean anything, because there are no two ends.

| Shape | Count | This campaign |
|---|---|---|
| 2-node open way | 405 | **Not touched.** Real interpolation, correctly tagged. |
| Open way, 3+ nodes | 149 | **Not touched.** Legal in principle; wants a different check — do both ends carry `addr:housenumber`? — which is not this edit. |
| **Closed way** | **78** | **Removed.** A polygon has no two ends, and its corners are geometry that will never carry housenumbers. |
| **Node** | **3** | **Removed.** A single node cannot interpolate between anything. |
| | **635 total** | **81 edited, 554 left alone** |

The 554 are in `review.csv` and on the run sheet, under their own two
headings. "We left 554 alone" should be checkable rather than asserted —
"removing `addr:interpolation` from Guelph" sounds far larger than 81.

This is also what JOSM's *"End node without housenumber in address
interpolation"* warning is about. It was pre-existing, it is what turned the
campaign up while reviewing campaign 3's batches, and it will otherwise nag
every mapper who opens one of those buildings, forever.

### Campaign 5 — `addr:flats`

**464 objects** carry `addr:flats` (45 nodes, 419 ways). Every one is parsed
into the units it names and re-rendered through `t2.units.compress_flats` —
the engine's own renderer, the one the continuous import already writes every
collapsed building through. **292 of the 464 (63%) come out different.**

The only new code is [`flats_parse.py`](flats_parse.py). Re-implementing the
rendering would give Guelph two answers to "how is a flats list rendered",
which is the complaint the campaign exists to fix.

What changes, all of it cosmetic by construction:

| Defect | Example, live | Becomes |
|---|---|---|
| Enumeration that should collapse | `1;10;11;12;13;14;15;2;3;4;5;6;7;8;9` (803 Gordon Street) | `1-15` |
| Trailing `;` | `101-113;201-214;301-314;401-414;` | no trailing separator |
| Sorted as text, not numerically | `1001-1008;1101-1108;101-106;…` (358 Waterloo Avenue) | floors in numeric order, thousands last |
| Spaces around `;` | `201-209; 301-309; 401-409;` (55 Yarmouth Street) | no spaces |

What does **not** change, each with a test in
[`test_flats_parse.py`](test_flats_parse.py):

- **Letter prefixes are building letters** and group on their own.
  `D101-D112;D201-D212` never merges across letters.
- **Letter suffixes cannot join a range.** 511 Edinburgh Road South is
  `101;101A;102;201;202` → `101-102;101A;201-202`: `101A` stays one value and
  sorts beside its neighbours rather than being exiled to the tail.
- **`LL` floors are a real prefix**, and keep their zero padding. See the
  engine fix below.
- **Stepped sequences do not compress.** 176 Janefield Avenue is mapped as a
  row of small ways stepping by two — `224;234`, `226;232`, `228;230` — and 25
  Kay Crescent's lower level is `LL02;LL04;…;LL14`. None of them becomes a
  range, because `224-234` would claim units 225 through 233 exist. That is
  the one way this campaign could actually damage data, so there is also a
  test proving the round-trip would catch it if it happened.

## The round trip

Every value is gated on it, and **nothing is batched that has not passed**:

```
parse(value) -> compress_flats -> parse(rendering) -> the two unit sets must be identical
```

If normalising changes which units a building claims, the parser is wrong, and
that is data corruption rather than cosmetics. `test_flats_parse.py` runs the
gate over **all 464 live values**; `flats_parse.normalise()` is the same
function the builder calls, so the test and the batch cannot disagree.

**Result: 464 parsed, 464 round-tripped, 0 refused.**

## The engine fix that made that true

Three of the 464 failed the round trip on their first run:

```
7 Kay Crescent        101-113;…;LL01-LL06;            ->  …;LL1-LL6
108 Summit Ridge Dr   101-112;…;LL01;LL02;LL03;LL04;  ->  …;LL1-LL4
25 Kay Crescent       101-114;…;LL02;LL04;…;LL14;     ->  …;LL2;LL4;…
```

`t2.units.parse_unit` goes through `int()`, which is right for every
structural caller and wrong for the renderer: `LL01` is how the building signs
its lower level, and `LL1` is a designator it does not use. TODO.md said fix it
in the engine rather than around it, so it is fixed there —
`address-importer-friend` commit `054da405`, adding `unit_pad` and threading a
per-prefix width into `compress_flats`. Four tests alongside the existing
ones; the engine suite passes clean at **415**.

(The commit was first written up as "52 passed, 41 collection errors, all
`ModuleNotFoundError: No module named 'accordeur'`". That was an artefact of
the environment it was built in — `accordeur` is the sibling repo at
`~/Code/accordeur` and resolves normally. The suite was never broken; the
message has been corrected.)

After it, all three normalise and round-trip.

## The 255-character limit

Not a problem here, and not rescuable from here either.

- **No live value is near it.** The longest `addr:flats` in Guelph is 154
  characters (150 Wellington Street East); after normalising the longest is
  **153**. `test_no_live_value_grows_past_the_osm_tag_limit` asserts both that
  nothing crosses 255 and that nothing gets longer than it was.
- **The three known overflows are not in OSM at all.** They are refused
  *source-side* by `t2.units.flats_tag`, which drops a listing rather than
  truncating it, so they were never written and this campaign cannot reach
  them.
- **Normalising would not rescue them anyway.** They are exactly the shapes
  `compress_flats` cannot shorten: 85 Mullin Drive is 110 units numbered
  `1A;1B;2A;2B…`, where every designator carries a letter suffix and nothing
  forms a run, and 176 Janefield Avenue steps by two. Shortening needs dense
  unsuffixed numbering, which is what these two do not have.

## What the numbers came to

| | |
|---|---|
| Objects the fetch selected (`addr:flats` or `addr:interpolation`) | 1,025 |
| **Genuinely changed, and batched** | **325** in 22 batches (13 nodes, 312 closed ways) |
| — `addr:flats` re-rendered only | 244 |
| — `addr:interpolation` removed only | 33 |
| — both | 48 |
| Skipped: already correct, nothing to do | 146 |
| Refused: real 2-node interpolation, out of scope | 405 |
| Refused: 3+-node open interpolation, out of scope | 149 |
| Refused: `addr:flats` unparsed / failed round-trip / too long | **0** |
| Refused: relation | **0** |

The two halves reconcile like this: 292 objects get a new `addr:flats` value
and 81 lose `addr:interpolation`; 48 objects are in both sets, so 292 + 81 −
48 = 325. The 146 skipped are objects whose `addr:flats` was already exactly
what the renderer produces and which had no `addr:interpolation` to drop — a
no-op edit still burns a version and a changeset comment, so `_common.changed()`
drops them rather than uploading them.

Pilot: **batch 1, Hanlon Creek, 26 objects** — the smallest whole area at or
above `pilot_min = 25`. The largest is West Willow Woods at 55; nothing comes
near the 250 cap, so every area is one batch.

`classify` refuses an object *whole* rather than half-editing it: something
with an unreadable `addr:flats` **and** an in-scope `addr:interpolation` would
go to review with both left alone, so that one object is still one edit and
one revert. That case is empty today — 0 flats refusals — so nothing is
actually being deferred by the rule.

## Running it

```bash
cd mechanical-edits/flats-hygiene

# the tests: plain stdlib plus the engine, no pytest and no _common needed
python test_flats_parse.py
python -m pytest test_flats_parse.py -q      # if you prefer

# the builder: needs requests + shapely, so use the engine's venv
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --refetch
```

The renderer comes from `t2.units` in the `address-importer-friend` checkout,
which is **not installed** — not editable, not on `sys.path` — so
`flats_parse.py` puts it there itself, guessing `../../../address-importer-friend`
and honouring `ADDRESS_IMPORTER_FRIEND` if the checkout lives somewhere else.

`build_batches.py` verifies what it wrote before it finishes, and raises rather
than warns:

- no tag key beginning with `_` reached a file (see the gap below);
- every element marked `action="modify"` appears in exactly **one** batch, and
  that set equals the manifest rows exactly — 325 and 325.

`live.osm`, `areas.geojson` and `batches/` are derived. `manifest.csv` is the
revert record [§ Revert plan][revert] promises: every edited object with the
version it was prepared against, the `addr:flats` before and after, and the
`addr:interpolation` value that was removed. `review.csv` holds all 554
refusals with their reason.

## Two gaps in the frozen `_common.py`

Reported rather than worked around in `_common.py`, which is frozen to a
campaign. Both are worked around locally here, and both are noted where the
workaround lives.

1. **`select` / `classify` / `transform` are handed tags and nothing else,
   but campaign 4's entire rule is geometric** — is this way closed? There is
   no supported way to express that. The workaround is a private `_shape` tag
   injected onto the parsed element before classification and stripped by
   `transform` before anything is written, with a post-write assertion that no
   key starting with `_` reached a file. A campaign hook that receives the
   element, or a `shape` argument alongside `tags`, would remove the need.
   Campaign 1 (`addr:province`) did not need it; anything geometry-conditional
   will.
2. **`changed()` has to be called by the campaign, not by `_common`.**
   `write_batch` does not check it, so a campaign that forgets silently
   uploads no-ops. Here it would have been 146 of 471 — nearly a third. It is
   documented in the module docstring as a guarantee (*"a transform that
   changes nothing is dropped, not uploaded"*), but the module does not
   actually enforce it; `write_batch` could drop an unchanged item itself, or
   at least refuse to write one.

## Checklist

- [x] `ANNOUNCEMENT.md` posted to #135103 — 2026-09-18, post #21, condensed
- [ ] Wiki § Mechanical edits gains sections 4 and 5, and § Non-goals retracts
      "no `addr:interpolation` cleanup" — written 2026-09-18, **not republished**.
      The post went up without the wiki link, so nothing dangles, but the page
      still describes three campaigns
- [ ] The four dropped paragraphs added to #21, or deliberately left out
- [ ] `build_batches.py --refetch` on the day; `python test_flats_parse.py` against the fresh fetch; counts re-read against this README
- [ ] JOSM signed in as `skfd imports`, not the personal account
- [ ] Batch 1 (pilot, Hanlon Creek, 26) uploaded; count and changeset posted to the thread
- [ ] Remaining 21 batches; `uploads.csv` appended per batch, as edits 2 and 3 do
- [ ] Wiki sections 4 and 5 updated with what actually went up

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
[revert]: https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Revert_plan
