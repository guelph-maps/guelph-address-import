# Mechanical edit 6 — unit doors

```
building:  addr:flats=1-5            ->  (removed; every other tag kept)
+ new:     node addr:unit=1 ... 5    ->  one per outside door, at the City's unit point
```

Both halves in **one changeset per batch**, so OSM never holds the building
without its units.

## Status — read this first

- **Parked 2026-09-29.** The `addr:flats` listings it replaces are valid OSM (containment), so this is a consistency upgrade, not a fix. Nothing is queued. Note that the continuous import will not converge these groups by itself: `MATCH_LISTED` treats a listed unit as present, and the import never modifies. **Rebuilt 2026-10-03 with `--refetch`** (numbers below), after campaign 1 had changed every listing object; rebuild again before any upload.
- **Not announced.** This edit has **not** been posted to
  [thread #135103](https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103).
  The choice was to fix the data first and announce afterwards. Post before
  anything uploads.
- **Nothing uploaded.** The batches are built and verified on disk only.
- **These door nodes are the import's first units.** Every node this edit
  creates is exactly what the continuous import would write for that City
  unit point — same tags, from the engine's own `osm_export.build_tags`. They
  are the first `addr:unit` nodes the import itself puts into Guelph. The
  changeset still carries `mechanical=yes`, from `_common`; whether a
  changeset that creates 1,246 City-sourced nodes should be tagged as an import
  instead is worth deciding before the post.

## Why

Campaign 3 (`../unit-listing-retag`) moved every list-valued `addr:unit` onto
`addr:flats`. That was the right key for towers — `addr:flats` means *units
reached through this one entrance*. But many of those buildings are groups
where each unit has its own outside door:

- **275 Hanlon Creek Boulevard** — one commercial building (way 794182120),
  five City unit points 8.4 m apart along one wall; OSM says `addr:flats=1-5`.
- **146 Downey Road** — eight semis on one civic, each way listing `17A;17B`.
- **941 Gordon Street** — seventeen townhouse blocks, each listing four units.

For those, `addr:flats` asserts a shared entrance that does not exist, and the
import's own rule for them (`t2.units.classify` → `nodes`) is one node per
door.

## Who is in it

Shape comes **only** from `t2.unit_shapes.collect()` — the whole civic group
as the source has it, with the operator's verdicts applied. Never the per-run
`candidates` table in tool.db, which is tile-cut.

Measured 2026-10-03 against a fresh fetch (`--refetch`). Between 2026-09-29
and this build the unit-shape audit judged the groups that were `review` and
`civic-only` then (84 objects: 59 now batched, 11 held, 13 collapse, 1 split), so
the population grew:

| addr:flats objects | 464 | |
|---|---|---|
| in a `nodes` group, batched | **311** (294 ways, 17 nodes) | 92 civic groups |
| in a `nodes` group, held by a guard | 16 | 3 groups — see review |
| `collapse` | 133 | untouched, in no file — `addr:flats` is right there |
| `split` verdict | 1 | 1 group (7 Kay Crescent) — review.csv |
| no City group at that address | 3 | review.csv |

What the 92 groups become:

| | |
|---|---|
| objects that lose `addr:flats` | **311** |
| door nodes created | **1,246** — 1,232 named by the OSM listing, 14 City-only |
| units **not** created, already in OSM as an `addr:unit` object | **465** |

The 465 are recorded in `manifest.csv` as `action=skip-existing` with the
blocking object — already mapped as their own door ways (361) or nodes (104):
35 Mountford Drive (84), 40 Silvercreek Parkway North (58), 224 Janefield
Avenue (52), 49 Rhonda Road (48), 20 Shackleton Drive (43), and so on.

**The 14 City-only doors are new since 2026-09-29**, when every created door
was a unit the OSM listing named. All 14 are 561 York Road, units 6–19: the
City has them, the listing does not. That follows the import's rule for doors
beside a listing (proposal, 2026-10-01), and it is the one place this edit
adds units OSM did not already list. No OSM building contains units 6–19 yet:
the second block is unmapped. skfd has surveyed it: a commercial building where
not every unit has its own door. Creating a node per unit is accepted anyway
(2026-10-03).

**Overlap with the import.** Since 2026-10-01 the continuous import proposes
these same doors itself: a listing no longer stands in for them. Either may
create them first. Whichever goes second must work from fresh OSM data —
`--refetch` here, so doors the import already created become
`skip-existing`, or a refreshed extract for the import.

The largest groups: 1291 Gordon Street (160 doors), 941 Gordon Street and 190
Fife Road (72 each), 240 Westwood Road (70), 15 Carere Crescent (64 — judged
since it read `civic-only` on 2026-09-29).

Where the listing object is a **node** (17 of them): it loses `addr:flats`
exactly as a way does and stays the civic node; the doors are created beside
it. 12 groups have a single unit.

Door placement: 1,092 of 1,246 created nodes fall inside a listed building
footprint, 33 belong to node listings, and 121 fall outside.
`inside_footprint` in the manifest says which; on 2026-09-29 every outside
door was within 4.4 m of a listed wall, and the 121 have not been re-measured.

**Not created:** the unit-less civic row of a group. The engine's `nodes`
shape would create it too, but here the building way (or civic node) keeps its
`addr:housenumber` + `addr:street` and already is that object.

## Door tags

From `t2.osm_export.build_tags`, fed what `candidates._candidate_values` /
`_emit_group` feed it (street through `apply_street_override` →
`expand_street_name`; unit is the City's `unit_name`, stripped):

```
addr:housenumber=275
addr:street=Hanlon Creek Boulevard
addr:unit=1
addr:city=Guelph
addr:source=Guelph Open Data
```

Each door carries its own City row's `addr:postcode`, through the engine's
`[postcode]` check, so a value the import would omit is omitted here too
(skfd, 2026-10-03: "if we have postal code to write, write it"). No
`addr:province` (Guelph dropped it). The buildings keep whatever postcode they
carry.

In this build 976 of the 1,246 doors carry a postcode. The other 270, in 17
groups (121 at 1291 Gordon Street), have none because the City row has none.

## Guards

A group goes whole to `review.csv` rather than half-edited when:

| reason | this build |
|---|---|
| `osm-unit-not-in-city` — OSM lists a unit the City lacks; removing the listing would lose it | 16 objects, 3 groups |
| `street-mismatch` — engine's street ≠ the OSM object's `addr:street` | 0 |
| `flats-unparsed` / `relation` / `city-duplicate-unit` | 0 |
| `shape-split` / `no-source-group` | 1 / 3 |

The guard hits are real hand work:

- **355 Elmira Road North** — way 344325628 says `100-140`; the City has no 122.
- **74 Janefield Avenue** — ways 1349287991–996 list pairs like `158;198`,
  `164;192`; 192–198 are not units of 74.
- **176 Janefield Avenue** (11 objects, in this edit since its verdict): the
  listings name 152, 154 and 156, which are not units of 176. With 74 next
  door, the mapper paired front and back units per building across two
  civics.

## Batches

20 batches, one per area with door groups, one changeset each. No group is
split across batches (asserted). **Batch 1, the pilot, is Clairfields**: 3
objects at 200 and 245 Southgate Drive, 15 doors. 275 Hanlon Creek Boulevard
is in batch 11, Kortright Hills; the biggest are 17, Grange Hill East (189
doors), and 20, West Willow Woods (179).

Changeset comment:

> Guelph addresses: units with their own outside doors get one addr:unit node
> per door instead of addr:flats on the building - Kortright Hills (11/20)

No longer collides with province-removal: none of the 311 objects carries
`addr:province` in the 2026-10-03 fetch.

## Rebuild, check, upload

```
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --refetch
```

`--refetch` pulls both fetches again: `live.osm` (every `addr:flats` object,
`out meta` plus child nodes) and `live_units.osm` (every `addr:unit` object,
for the dedupe guard). The build then reads back every file it wrote and
refuses the set unless: new nodes have negative ids (minus the City's
`address_point_id`, stable across rebuilds), lat/lon, and no version or
action; the file matches the manifest; no group is split; no created node
duplicates an existing `addr:unit` object; no modified object still has
`addr:flats`.

Upload, from `mechanical-edits/`, signed in to JOSM as `skfd imports`:

```
python upload_loop.py unit-doors 1 1      # the pilot, then look at it
python upload_loop.py unit-doors 2 20
```

`verify_changeset.py` now understands created nodes: for a manifest with
`action=create` rows it matches the changeset's created nodes one-to-one on
their full tag set and position, requires the modified set to be exactly the
`action=modify` rows with only `addr:flats` gone, and ignores
`skip-existing` rows. Other campaigns' manifests have no action column and
verify as before.

## Files

| | |
|---|---|
| `build_batches.py` | the builder |
| `population.py` | the first count (464 / 257 / 76), kept as the record of it |
| `manifest.csv` | one row per stripped object (`modify`), created node (`create`, negative id, tags as JSON), and skipped unit (`skip-existing`, `blocked_by`) |
| `review.csv` | every addr:flats object in a non-collapse group that is not batched, with reason |
| `index.html` | the run sheet |
| `live.osm`, `live_units.osm`, `batches/` | regenerable, not tracked |
