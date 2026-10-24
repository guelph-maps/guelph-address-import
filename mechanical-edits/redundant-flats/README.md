# Mechanical edit 6, what is left — listings the doors made redundant

```
building (or civic node):  addr:flats=1-5   ->  removed; every other tag kept
```

Nothing is created, nothing is deleted, no other tag moves.

## Status — read this first

- **Rebuilt 2026-10-24** against a fresh fetch (Overpass `osm_base`
  2026-10-24T05:01Z). **299 objects in 20 batches**, down from 317 on
  2026-10-07. Rebuild with `--refetch` again if the upload does not follow
  within a few days.
- **Decided 2026-10-24: strip them, on drift.** The harm case is gone (see
  below), so what is left is the surviving argument: the same fact on two
  objects, so a mapper renumbering a door has no reason to see the listing.
  skfd weighed that against keeping the listings and chose to strip.
  **Nothing is uploaded yet.** Pilot batch 1 (Kortright Hills, 10 objects)
  goes up first and gets looked at, then 2-20.
- **The stale batch is resolved, by its listings leaving.** The Janefield
  hand fixes landed (changesets 190278301, 190279486, 190279513) and this
  build sees them: 74, 176 and 224 Janefield Avenue carry no `addr:flats` at
  all any more, so those 18 listings left the edit rather than needing a
  gate, and the seven `cross-civic` holds went with them. Old University is
  now batch 10, six objects.
- **No forum post.** skfd decided on 2026-10-07 that none of the
  post-import cleanups gets one. The draft is in git history at `5b2afeb`.
- **The case is weaker than this file first argued.** Tested 2026-10-20:
  Nominatim does not index `addr:flats` at all, so stripping it changes no
  geocoding answer and removes no duplicate — see
  [`GEOCODER_TEST.md`](GEOCODER_TEST.md). Read that before re-arguing this
  edit in either direction.
- **Supersedes [`../unit-doors/`](../unit-doors/README.md).** That build
  created the doors and stripped the listings in one changeset. The import
  has since created the doors, so its batches are stale and must not be
  loaded.

## Why

Edit 6 was built 2026-09-29 to replace `addr:flats` on door groups with one
`addr:unit` node per door, then parked: the listings are valid OSM. On
2026-10-01 the import stopped letting a listing stand in for doors, and the
first pass (2026-10-03..07) created **1,680 door nodes at 143 civic
addresses**. At 83 of those (92 before the Janefield hand fixes), a building
or civic node still lists the same units in `addr:flats`. Now each unit is in OSM twice: as its own door, and as
an entry in a listing on the building. The doors are the shape the operator
chose for each of these groups at `/units/shapes`.

**This paragraph used to say the listings "contradict that choice and add
nothing". Both halves were overstated, and 2026-10-20 is when that was
admitted.** They do not contradict: `addr:unit` means identity — this node
*is* unit 3 — and `addr:flats` means containment — this building *serves*
units 1-5. A building that contains five units still contains them once the
five doors are mapped, and `addr:flats` on a building outline is good OSM on
its own terms. Nor do they add nothing: a consumer indexing buildings reads
the unit range straight off the way, where otherwise it needs a spatial join
from door nodes to the enclosing outline. The honest case against them is
drift, not error.

## Who is in it

The population is **civics where this import uploaded door nodes**
(`candidates.stage = 'UPLOADED'` with a unit, in tool.db, the same test that
freezes a group's shape). The civic is read from our door nodes' live tags,
so a listing joins on the `addr:housenumber` + `addr:street` OSM actually
carries. A listing whose street is spelled differently, but is the same
street once normalised, goes to review as `street-spelling`. None did.

**The gate is per listing.** A listing is stripped only when **every** unit
it names has an address object of its own at that civic in live OSM: an
`addr:unit` node or way that is not a POI node (the engine's
`conflate._is_poi_node`). Our doors count. So would doors somebody else
mapped before the import, since at such a group the import created only the
doors OSM lacked.

Measured 2026-10-24.

| | |
|---|---|
| `addr:flats` objects in Guelph | 439 (404 ways, 35 nodes) |
| at a civic with uploaded doors | 303, at 83 civics |
| **fully covered → batched** | **299** (288 ways, of which 287 building outlines and 1 address-only area, way 942414532; 11 civic nodes), naming 1,027 units |
| held, `review.csv` | 4 |

**Whose listings these are.** Every one of the 299 had its `addr:flats`
written by this project: 289 by campaign 3 (moving list-valued `addr:unit`
over verbatim) and 10 by the hand cases (campaign 2/3 leftovers). Each value
was the 2025 import's own, moved onto the right key. No mapper wrote any of
them as `addr:flats`. Six have been touched by hand since — `last_user` is
`skfd` rather than `skfd imports` on 561 York Road way 1054125923, 304 Stone
Road West way 215069452 and the four Janefield `B` civic nodes — and each of
those six hand versions left `addr:flats` at the value we wrote, checked
against the objects' own OSM history on 2026-10-24. All 299 live values equal
this project's last write, which is flats-pairs' `flats_after`, else
flats-hygiene's, else campaign 3's or the hand cases' `after_flats` (checked
2026-10-07, and again on the rebuild). `last_user` in the manifest is `skfd
imports` on 293 of them, because campaign 1 touched every one; the `origin`
column is the one that answers the question.

**Doors that are not ours.** The gate would accept another mapper's door,
and this build meets three: at 10 Stuart Street skfd replaced the import's
units 8-10 with hand-mapped entrance nodes. That listing is held anyway, as
`doors-deleted` below. Every other one of the 1,027 listed units has one of
the import's own door nodes. Three units also have a POI carrying the same unit:
649 Scottsdale Drive 1 (Pizza Hut), 304 Stone Road West 11 and 350 Speedvale
Avenue West 1. The only listing that leans on other people's objects is 355
Elmira Road North, and it is held (below).

The 17 civic nodes keep `addr:housenumber` + `addr:street` and stay the
civic address. Their doors sit beside them.

The largest civics: 190 Fife Road (36 objects, 72 units), 15 Carere Crescent
(32), 75 Flaherty Drive (25), 49 Rhonda Road (24), 240 Westwood Road (19, 70
units), 941 Gordon Street (18, 72 units).

## Held — `review.csv`

| Reason | Objects | What |
|---|---|---|
| `doors-deleted` | 1 | **10 Stuart Street**, way 929589622, `1-10`. skfd's hand edit `ker kavan entrances` (changeset 190175390, 2026-10-08) deleted the import's door nodes for units 8, 9 and 10 and mapped entrance nodes of its own there instead. All ten units still have a door, so the gate would pass the listing — but a group a human reshaped after the import is a hand question, so the builder holds it. The seven `cross-civic` rows that stood here are gone: the Janefield hand fixes took those listings out of OSM. |
| `osm-unit-not-in-city` | 1 | **355 Elmira Road North**, way 344325628, `100-140`. The City has no 122. In OSM, 122 is only on a law office POI (node 9139124204). The other 40 units have doors. Stripping the listing would leave 122 only as that business's address. Unit 122 is one of the City letter's questions, so this hold waits on the reply. |
| `unit-without-door` | 1 | **120 Country Club Drive**, way 761343575, `11;12;14-33`. Unit 32 has no door, and the City has no 32 at this civic. The other 21 have doors. It is the same shape as the letter's "OSM lists a unit your layer doesn't have" bullets but is **not** in the letter, which was already final when this came up on 2026-10-24. Ask separately if the City's answer about completeness does not settle it. |
| `shape-split` | 1 | **7 Kay Crescent**, way 741807532: the tower `101-113;…;601-615` plus `LL01-LL06`. The verdict is `split`: doors for the six lower-level units and one listing for the tower. So the listing stays, but it still names LL01–LL06, which now have doors too. Trimming those six would be a value change, not a removal, so it is not in this edit. |

## Found in passing, not in this edit

**2053 Gordon Street, node 14257046648.** This is one of the import's own 8
collapse nodes, `addr:flats=119`, uploaded 2026-10-07 in changeset
190123921. Way 802540385 at the same civic already carried `addr:unit=119`
(a Microsoft footprint, `building=yes`). It is the only listing in Guelph
outside this edit's scope that is fully covered by doors. It looks like a
conflation miss in the import (a unit-carrying building did not match a
single-unit collapse candidate), not a listing to strip. It wants an engine
look and an operator decision.

## Batches

20 batches, one per area, one changeset each (`_common`'s rule). **Batch 1,
the pilot, is Kortright Hills**: 10 objects, which are the eight semis at
146 Downey Road (`17A;17B` … `24A;24B`), 265 Hanlon Creek Boulevard
(`1;3-5;9`) and 275 Hanlon Creek Boulevard (`1-5`). These are edit 6's own
original examples. The largest batch is 20, West Willow Woods (69). Several
are tiny (batch 2, Rickson Ridge, is one building).

Changeset comment:

> Guelph addresses: remove addr:flats where every listed unit now has its own
> addr:unit door node - Kortright Hills (1/20)

Tags are `_common`'s: `mechanical=yes`, `source=Guelph Open Data`,
`import_plan` at the wiki's Mechanical edits section. Edit 6's README left
open whether a changeset creating 1,246 City-sourced nodes should be tagged as
an import. That question closed when the import created the nodes under its
own tags. This edit only removes tags, so `mechanical=yes` is right.

## Rebuild, check, upload

```
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --refetch
```

The build reads every file it wrote back and refuses the set unless:

- every element marked modify is a manifest row and carries a version;
- nothing is created;
- each object's tags are its live tags with `addr:flats` gone and nothing
  else;
- every unit its former listing named has a non-POI `addr:unit` object at its
  civic in `live_units.osm`.

Upload, from `mechanical-edits/`, signed in to JOSM as `skfd imports`:

```
python upload_loop.py redundant-flats 1 1      # the pilot, then look at it
python upload_loop.py redundant-flats 2 20
```

`verify_changeset.py` knows this directory (`EXPECT["redundant-flats"]`, the
same expectation as unit-doors: only `addr:flats` gone). Revert:
`flats_before` in `manifest.csv` is each object's value.

## Files

| | |
|---|---|
| `build_batches.py` | the builder, gate and self-check |
| `manifest.csv` | one row per stripped object: `group` (civic key), `flats_before`, `units`, `origin` (campaign-3 / hand-cases / other), `last_user` |
| `review.csv` | every listing at an uploaded door civic not batched, with reason and detail |
| `index.html` | the run sheet |
| `live.osm`, `live_units.osm`, `batches/` | regenerable, not tracked |
