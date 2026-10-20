# Does the redundant listing hurt a geocoder? Tested 2026-10-20 — no.

This edit's case rested on the listings being harmful rather than merely
spare. The sharpest version of that claim is that a geocoder returns each
unit **twice** when both the building's `addr:flats` and the doors'
`addr:unit` exist. Tested against live Nominatim. It does not.

## Subject

**275 Hanlon Creek Boulevard** — the clean case, and one of this edit's own
pilot examples:

- way 794182120, `building=yes`, `addr:housenumber=275`, `addr:flats=1-5`
- nodes 14256460997/460999/461000/476102/476103, `addr:unit` 1–5

## What Nominatim has actually indexed

`/details` on each object, `extratags` requested:

| Object | category/type | housenumber | extratags |
|---|---|---|---|
| way 794182120 (the listing) | `building/yes` | 275 | `{building: yes}` |
| node 14256461000 (unit 3 door) | `place/house` | 275 | `{}` |

**`addr:flats` is not indexed at all.** Neither is `addr:unit`. Both objects
are indexed on `addr:housenumber=275` and nothing else.

## What searches return

| Query | Results |
|---|---|
| `275 Hanlon Creek Boulevard, Guelph, Ontario` | **3** — the building way and two door nodes, none carrying `addr:flats` or `addr:unit` in its response |
| `unit 3, 275 Hanlon Creek Boulevard, Guelph` | **0** |
| `3-275 Hanlon Creek Boulevard, Guelph` | 3, all of them stretches of road — no address match |

## What this settles

- **No duplicate-per-unit effect exists, so stripping cannot remove one.**
  The listing contributes no unit-level result to delete.
- **Stripping `addr:flats` would not change a single Nominatim answer.** The
  way is indexed on its own `addr:housenumber`, which this edit does not
  touch. Before and after are identical to the geocoder.
- **Unit-level search still fails**, which confirms the 2026-08-21 finding on
  the same question, measured then for the unit-split campaign.
- The civic *does* return several results for one housenumber — the building
  plus its doors. That is caused by the **per-door shape the import chose**,
  not by the listings, and this edit would not reduce it.

## What it does not settle

Nominatim is one consumer. `addr:flats` not being indexed also means it is
invisible *to Nominatim* either way; its value is to anything reading raw OSM
tags, where a building-level unit range answers "what units are here?"
without a spatial join from door nodes to the enclosing way. Nothing here
argues the listings are useless — only that keeping them costs no geocoding
accuracy.

The remaining argument for stripping is **drift**: the same fact in two
places, on two different objects, so a mapper renumbering a door has no
reason to see the listing. That is a real but slow failure, and it is a
judgement call rather than a defect to fix.
