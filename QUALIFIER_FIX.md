# QUALIFIER fix — what went stale (2026-10-03)

Guelph keeps 155A Bristol Street as STREETNO `155` + QUALIFIER `A`. The engine read the number from STREETNO alone, so 155A came out as 155. `config.toml` now declares `number_suffix = "props:QUALIFIER"`, a new engine key in address-importer-friend. The housenumber is now `155A`: upper-cased, with no space.

Measured at snapshot 47, through the engine's own projection:

| | before | after |
|---|---|---|
| active rows | 53,847 | 53,847 |
| civic groups | 40,635 | 40,767 |
| unit-bearing groups | 409 | 414 |
| groups with more than one unit-less row | 111 | 0 |
| groups repeating a unit designator | 4 | 0 |

All of the "111 intra-source duplicates" were lettered siblings. None were City duplicates.

## Unit-shape verdicts to re-judge

The engine will **not** flag these as stale. `unit_hash` covers the *distinct* designators, and each half of a split group has the same set the merged group had (B, C / 2, 3). That means the saved verdict silently keeps applying to the plain-number half, while the lettered half has no verdict and falls to the rule.

| civic_key | saved | was judged on | now |
|---|---|---|---|
| `155\|BRISTOL STREET\|GUELPH` | nodes | 6 rows (155 + 155A, units B, C each) | 155: plain, B, C · 155A: plain, B, C |
| `8\|ORCHARD CRESCENT\|GUELPH` | nodes | 6 rows (8 + 8A, units 2, 3 each) | 8: plain, 2, 3 · 8A: plain, 2, 3 |
| `10\|ORCHARD CRESCENT\|GUELPH` | nodes | 6 rows (10 + 10A, units 2, 3 each) | 10: plain, 2, 3 · 10A: plain, 2, 3 |

To re-judge them, clear or confirm each verdict at `/units/shapes?focus=<civic_key>`, then judge the new 155A / 8A / 10A groups.

**Cleared 2026-10-03 at the operator's request.** The three verdicts above were deleted with `unit_verdicts.clear` so they show up unjudged. Their old values are recorded in the table above.

One more merged group carried units but had no verdict: `38|RIDGEWAY AVENUE|GUELPH` (38, 38A, 38B, each with a plain point and unit 2). It is now three groups, and all three are unjudged.

None of these groups is frozen, because nothing has been uploaded.

## Runs that must be re-ingested before the initial import

The `tool.db` candidates were built before the fix. 203 of them carry a QUALIFIER, spread across 36 runs: 86 APPROVED, 107 REVIEW_PENDING and 10 SKIPPED. They still hold the bare number (`155`) and the merged `civic_key`. None is UPLOADED. The approvals were given to the wrong housenumber, so those runs need rebuilding rather than uploading.

The worst runs by approved count are 65, 33, 67, 85, 13, 36 and 49 (all `-batch-20260929`).

## What OSM holds at the lettered points

Checked against the Geofabrik extract of 2026-09-28 (`data/osm`): OSM addresses within 30 m on the same normalized street. There are 198 lettered civic addresses (206 rows):

- **28** already have their lettered number in OSM (`155A`). After the fix they match.
- **152** have nothing nearby with the bare number or the lettered one, so they will read MISSING and get imported as their own addresses.
- **18** have only a bare-number object nearby. For 14 of these, the City also publishes the plain number, so that object belongs to the plain address and is correct.

That leaves **4 OSM objects with a bare number at a spot where the City publishes only the lettered pair**:

- way 1442154696 at 114 Surrey St E (City: 114A, 114B)
- node 1880282526 at 38 Dublin St S (38A, 38B)
- node 11082000915 at 54 Carden St (54A, 54B)
- node 4028442011 at 616 Woodlawn Rd E (616A, 616B)

Each could be a building-level address for a duplex as easily as a mis-tag. Look at them while reviewing; they are not a mechanical edit.

So `[prior_import] tag_mapping` (STREETNO → addr:housenumber) does not mean the 2025 import wrote bare numbers at lettered points: the counts above show no such pattern. That table is a record only, and the engine never reads it.

## Not covered

`t2/reverse_sweep.py` hard-codes `number AS address_number` and Toronto's `LO_NUM_SUF`, so it still reads 155A as 155. It is Toronto-shaped and is not part of the Guelph import path.
