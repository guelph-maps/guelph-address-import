# Mechanical edit 2 — split double-encoded unit housenumbers

```
addr:housenumber = 714-30   ->   addr:housenumber = 714
addr:unit        = 30            addr:unit        = 30   (untouched)
```

Prepared 2026-09-15 against live OSM. **Open `index.html`** — that is the run
sheet, and everything an operator needs is on it. This file is for whoever
comes back to the machinery later.

## Where the consent is

Announced on [thread #135103][thread] as post #14 on 2026-08-28, with a 14-day
objection window to 2026-09-10. It closed with no objections, and
ARandomThumbtack — who had defended the combined form in post #12 — replied
supportively in #15. The edit itself is documented at
[Guelph/Address_Import/Continuous § Mechanical edits][wiki].

The announcement also promised **a pilot posted to the thread with its counts
and changeset before anything else moves**. Batch 1 is that pilot; the run
sheet carries the gate.

## Why this has to happen before any conflation

Not cosmetics, and not optional. Guelph now uploads units by shape
(`policy = "per-door-or-collapse"`), so a door candidate is `(714, unit 30)`.
Against an OSM object still carrying `addr:housenumber=714-30` that compare
fails, the door reads MISSING, and conflation proposes a *second* node beside
the badly-encoded one. 5,568 hyphenated objects against 6,111 door candidates
is a mass-duplication event. `config.toml` records the argument at length, and
the engine has a test named for it
(`test_a_door_does_not_recognise_its_own_double_encoded_self`).

## What the numbers came to

| | |
|---|---|
| Hyphenated objects in the city | 5,568 (741 nodes, 4,827 ways) |
| Split mechanically | **5,521** in 36 batches |
| Left for hand work | 47 |

The 47 are three different problems and the run sheet keeps them apart: 27 are
`;`-separated lists that belong to [open question 3][wiki] (the MapRoulette
one) rather than to this campaign, **17** are single hyphens with no
`addr:unit` to corroborate the split, and 3 have a unit matching neither side
(`130-BLD D`, `10-6/7`).

That 17 is exactly the "~17 objects carry the combined form with no
`addr:unit`" the published plan promised to do by hand — the one count that
has not drifted. The mechanical total has: the plan said 5,422 against
today's 5,521, which is what re-measuring is for.

## Running it again

```bash
cd ../address-importer-friend           # for the venv: requests + shapely
./.venv/Scripts/python.exe ../guelph-address-import/mechanical-edits/unit-split/build_batches.py
```

`--refetch` pulls OSM again instead of reusing `live.osm`. Regenerating is
cheap and entirely local once the fetch is cached; do it whenever the batches
have gone stale, which they do the moment anyone edits Guelph addresses.

`live.osm` and `batches/` are gitignored — derived, large, and stale on
contact. `manifest.csv` is tracked, because it is the revert record
[§ Revert plan][revert] promises: every edited object with the version it was
prepared against and its prior value.

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
[wiki]: https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Mechanical_edits
[revert]: https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Revert_plan
