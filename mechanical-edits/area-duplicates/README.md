# Address nodes created inside an area that already had the address

**Found 2026-10-03, in the first 27 import changesets.** Conflation measured a
park or school from its centre and dropped it past the 100 m match radius, so
a City point inside a park carrying the same address read MISSING and
uploaded. The policy is to leave those alone. Fixed in address-importer-friend
`63f641da`: areas are matched by the edge of their bounds. Runs not yet
uploaded were re-checked with `scripts/reconflate_areas.py`: 10 became MATCH
(skipped) and 10 MATCH_FAR (to review).

[`delete-5-area-duplicates.osm`](delete-5-area-duplicates.osm) deletes the
five that went up. It is checked to touch only version-1 nodes of ours that
carry nothing but the address.

| Node | Address | Inside |
|---|---|---|
| 14245022294 | 24 Franchetto Boulevard | Franchetto Park |
| 14245099260 | 22 Eugene Drive | Clair Park |
| 14245110851 | 388 Arkell Road | Two Rivers Secondary School |
| 14245110520 | 71 Lee Street | Lee Street Park |
| 14245110523 | 31 O'connor Lane | O'Connor Lane Park |

Not in the file: 300 Grange Road (node 14245058191) would now be MATCH_FAR,
since a building 46 m away carries the address. That one is a judgement call.
