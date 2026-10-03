# Mechanical edit 6 — unit doors

```
building:  addr:flats=1-5            ->  (removed; every other tag kept)
+ new:     node addr:unit=1 ... 5    ->  one per outside door, at the City's unit point
```

Both halves in **one changeset per batch**, so OSM never holds the building
without its units.

## Status — read this first

- **Parked 2026-09-29.** The `addr:flats` listings it replaces are valid OSM (containment), so this is a consistency upgrade, not a fix. Nothing is queued. Note that the continuous import will not converge these groups by itself: `MATCH_LISTED` treats a listed unit as present, and the import never modifies. Campaign 1 has since changed every one of the 252 objects, so `--refetch` is mandatory if this is revived.
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
  changeset that creates 868 City-sourced nodes should be tagged as an import
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

Measured 2026-09-29 against a fresh fetch (`--refetch`, after the flats-hygiene
uploads landed):

| addr:flats objects | 464 | |
|---|---|---|
| in a `nodes` group, batched | **252** (240 ways, 12 nodes) | 74 civic groups |
| in a `nodes` group, held by a guard | 5 | 2 groups — see review |
| `collapse` | 120 | untouched, in no file — `addr:flats` is right there |
| `review` | 41 | 32 groups — review.csv |
| `civic-only` | 43 | 2 groups — review.csv |
| no City group at that address | 3 | review.csv |

What the 74 groups become:

| | |
|---|---|
| objects that lose `addr:flats` | **252** |
| door nodes created | **868** — every one a unit the OSM listing named |
| units **not** created, already in OSM as an `addr:unit` object | **389** |

The 389 are recorded in `manifest.csv` as `action=skip-existing` with the
blocking object. 386 of them are City units the listing never named, already
mapped as their own door ways (297) or nodes (89) — 35 Mountford Drive (84),
40 Silvercreek Parkway North (58), 49 Rhonda Road (48), 20 Shackleton Drive
(43), and so on. So the groups where the City has far more units than the OSM
listing are groups whose other doors are already in OSM, and **no unit is
created that OSM did not already list**. The remaining 3 are listed units that
a POI node already carries (304 Stone Road West unit 11, 649 Scottsdale Drive
unit 1, 350 Speedvale Avenue West unit 1); the listing goes and the POI keeps
the unit.

Where the listing object is a **node** (12 of them — Janefield Avenue, Mason
Court, Woolwich Street): it loses `addr:flats` exactly as a way does and stays
the civic node; the doors are created beside it. 10 groups have a single unit.

Door placement: 781 of 868 created nodes fall inside a listed building
footprint, 18 belong to node listings, and 69 fall outside — all within 4.4 m
of a listed wall (100 Frederick Drive, 45 Airpark Place, 146 Downey Road, the
Burns Drive rows). City door points on or just outside the wall; `inside_footprint`
in the manifest says which.

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

No `addr:postcode` and no `addr:province` (Guelph dropped it). The buildings
keep whatever postcode they carry. The postcode was left off because, when this
campaign was cut, the engine wrote one only from a POI fallback. Since
2026-10-03 the engine writes the City's `POSTCODE` on every node it creates
(proposal, § Tagging plan), so these doors would be the exception: decide
before upload whether `build_batches.py` should copy the City row's postcode
too, through the same check (`[postcode] prefixes` in `config.toml`).

## Guards

A group goes whole to `review.csv` rather than half-edited when:

| reason | this build |
|---|---|
| `osm-unit-not-in-city` — OSM lists a unit the City lacks; removing the listing would lose it | 5 objects, 2 groups |
| `street-mismatch` — engine's street ≠ the OSM object's `addr:street` | 0 |
| `flats-unparsed` / `relation` / `city-duplicate-unit` | 0 |
| `shape-review` / `shape-civic-only` / `no-source-group` | 41 / 43 / 3 |

The two guard hits are real hand work:

- **355 Elmira Road North** — way 344325628 says `100-140`; the City has no 122.
- **74 Janefield Avenue** — ways 1349287991–996 list pairs like `158;198`,
  `164;192`; 192–198 are not units of 74. Next door, 176 Janefield Avenue
  (civic-only) has ways listing `154;202`, `220;238`: the mapper paired
  front and back units per building across two civics.

Worth a verdict on the audit page: **15 Carere Crescent** is 32 semis each
listing `28A;28B` and reads like a door group, but the engine calls it
`civic-only` (the listing is past 255 characters), so it is not in this edit.

## Batches

17 batches, one per area with door groups, one changeset each. No group is
split across batches (asserted). **Batch 1, the pilot, is Non-Residential - B**:
3 buildings (2 Taggart Street, 3 Watson Road South, 70 Watson Parkway South),
16 doors. 275 Hanlon Creek Boulevard is in batch 9, Kortright Hills.

Changeset comment:

> Guelph addresses: units with their own outside doors get one addr:unit node
> per door instead of addr:flats on the building - Kortright Hills (9/17)

**Collides with province-removal on version.** All 252 of these objects still
carry `addr:province` (way 794182120 does). Whichever of edit 1 and edit 6
uploads second must be rebuilt with `--refetch` first, or JOSM will raise
conflicts on the shared objects.

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
python upload_loop.py unit-doors 2 17
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
