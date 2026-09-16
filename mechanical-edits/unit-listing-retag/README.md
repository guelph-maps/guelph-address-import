# Mechanical edit 3 — move unit lists from addr:unit to addr:flats

```
addr:unit  = 101-116;201-215;…   ->   addr:flats = 101-116;201-215;…
                                       (addr:unit removed; nothing else touched)
```

Prepared 2026-09-15 against live OSM, **before consent**, so the counts and
the files could be looked at. `index.html` is the run sheet; it says the same
thing in a banner. This file is for whoever comes back to the machinery later.

## Where the consent is

Nowhere yet. The announcement is drafted in [`ANNOUNCEMENT.md`](ANNOUNCEMENT.md)
beside this file and has **not** been posted to [thread #135103][thread]. The
edit is written up as section 3 of
[Guelph/Address_Import/Continuous § Mechanical edits][wiki]; the post goes up
once that section is synced so its link resolves, and opens a 14-day
objection window. Nothing here may be uploaded until that window has closed
with no objections.

The batches in `batches/` were built against the versions live today. By the
day of upload those will have moved, so the first step that day is
`build_batches.py --refetch`, not JOSM. The announcement also promises the
same pilot gate as edit 2 — one batch posted to the thread with its count and
changeset before anything else moves — and batch 1 is that pilot.

## Why it matters

`addr:unit` is identity: *this address is unit 30*. `addr:flats` is
containment: *this building contains units 101–116*. Guelph currently says
both with one key — 5,863 doors and 453 buildings, told apart only by the
shape of the value — and that is exactly what broke conflation: with both
meanings on `addr:unit` it could only guess from the value, and the first
version of that guess froze 158 buildings for the wrong reason. The
continuous import writes `addr:flats` for collapsed buildings (`policy =
"per-door-or-collapse"`), so without this edit the city would carry the same
fact under two keys, split about evenly, for good.

## What the numbers came to

| | |
|---|---|
| Objects the fetch selected (list-valued `addr:unit`, or any `addr:flats`) | 454 |
| Moved mechanically | **452** in 23 batches (37 nodes, 415 ways) |
| Refused: already carries `addr:flats` | 1 |
| Refused: `addr:housenumber` itself hyphenated | 1 |
| Refused: single designator the fetch caught but the rule does not | 0 |

The wiki says 453 and 1. The 1 is the same object — way 208488213, 40
Northumberland Street, `addr:flats=101-106;201-206;301-306` with no
`addr:unit` at all, so there is nothing to merge; it is simply left alone. The
453rd is way 1349071737, 240-57;240-56 London Road West with
`addr:unit=56;57`: a `;`-list *housenumber*, which is edit 2's review pile
(open question 3) and not this campaign's, so it is refused rather than
retagged under a housenumber that is itself wrong. However the plan's "zero
overlap" was counted, it did not include this one; the classifier refuses it
regardless, which is what the `hyphen-hn` rule is for.

Pilot: batch 1, **Non-Residential - C, 22 objects** — the smallest whole area
at or above `PILOT_MIN = 20`. The largest is West Willow Woods at 74; nothing
comes near the 250 cap, so every area is one batch.

Things worth knowing about the values, all of which move exactly as they are:

- 49 of the 452 end in a trailing `;` (`101-113;201-214;301-314;401-414;`).
  It moves with the value. Tidying it is not this edit.
- 2 have spaces after the `;` (`201-209; 301-309; …`). Same.
- Not every list is a range. 8 are a single range with no `;`; the rest
  include plain enumerations (`1;2;3;4`), small lists on townhouse blocks
  (nine ways at 39 Kay Crescent carry mostly pairs, `32;33`, `34;35`, …, one a
  run of ten), lettered units (`A;B;C` on the nodes at 147 and 151 Arthur
  Street North, `2;4A;6;8` on 2 Taggart Street) and mixes
  (`101-114;…;LL02;LL04;…`). The announcement says "contains `;` or matches a
  range" and "verbatim", and that is what happens.
- 198 distinct `(street, housenumber)` civic groups in the safe set, against
  the 176 the wiki counts. The two were counted differently (the wiki's is
  against the City's 409 multi-unit addresses) and the gap was not reconciled
  here. 34 groups hold more than one object — 190 Fife Road alone is 36 ways,
  each block carrying its own list.
- The longest value is 154 characters (150 Wellington Street East). The run
  sheet truncates for display; the files do not.

## Running it again

```bash
cd mechanical-edits/unit-listing-retag
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py            # cached fetch
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --refetch  # pull OSM again first
```

The engine's venv is for `requests` and `shapely`; nothing else is imported
from it. `build_batches.py` is a sibling of `../unit-split/build_batches.py`,
copied and adapted rather than shared, so each stays runnable on its own;
`diff` the two and only the campaign-specific parts differ.

`live.osm` and `batches/` are gitignored — derived, and stale on contact.
`manifest.csv` is tracked, because it is the revert record
[§ Revert plan][revert] promises: every edited object with the version it was
prepared against and the value that moved. `review.csv` holds the refusals
with their reason.

## Checklist

- [ ] Wiki § Mechanical edits, section 3, synced so the announcement's link resolves
- [ ] `ANNOUNCEMENT.md` posted to #135103 with the deadline filled in
- [ ] 14 days passed, no objections
- [ ] Edit 2 finished (the announcement says "after the split finishes")
- [ ] `build_batches.py --refetch` on the day; counts re-read against this README
- [ ] JOSM signed in as `skfd imports`, not the personal account
- [ ] Batch 1 (pilot) uploaded; count and changeset posted to the thread
- [ ] Remaining batches; `uploads.csv` started and appended per batch, as edit 2 does
- [ ] Wiki section 3 updated with what actually went up

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
[wiki]: https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Mechanical_edits
[revert]: https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Revert_plan
