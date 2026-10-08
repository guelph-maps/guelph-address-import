# Draft for thread #135103: campaign 7

**Not posted.** Ready to go now that the import is up. Fill in `[DATE]`, and
post it **before** `redundant-flats/FORUM_POST.md`, which refers back to it
("the back-to-back townhouses from my earlier post"). It started as a
curiosity post on 2026-10-02 and now carries the edit too. Condensed from
`README.md` beside it.

---

A small Guelph curiosity, and a cleanup that comes out of it.

[This building slice at 176 Janefield Avenue](https://www.openstreetmap.org/way/1349287990)
lists `addr:flats=156;200`. Two units 44 apart in one narrow footprint looked
impossible until the City's data explained it. The complex has two civic
numbers: 74 Janefield (units 2–178) and 176 Janefield (units 180–330). In one
row the footprints cut the terrace into slices that each hold one home from
either side, and every pair adds up to the same number (152+204, 154+202,
156+200…). They are back-to-back townhouses, numbered up one side and back
down the other.

So unit 156 is really 74 Janefield, unit 156. It ended up under 176 because
each footprint got one housenumber and a list of every City point inside it.
Seven slices there are like this.

The import has since added each of those 14 homes as its own address node at
the right civic number, and every one sits inside the slice that lists it. So
the lists are redundant as well as half wrong. **I'll remove `addr:flats`
from those seven slices** and change nothing else. Each keeps its one
housenumber.

Checking every Guelph unit list against the City turned up seven more that
name one unit the City doesn't have at that address:

- **7 Ajax Street** (208) and **395 Edinburgh Road North** (414–416): I fixed
  these by hand on 6 October.
- **454 Janefield Avenue** (204), **53 Conroy Crescent** (105) and
  **23 Woodlawn Road East** (706): I'll drop that one unit and leave the rest
  of the list. Each is a single gap in an otherwise regular run of numbers,
  so the City's data could be the one missing it. If you know one of these
  buildings and the unit exists, tell me and I'll put it back.
- **358 Waterloo Avenue** (903) and **355 Elmira Road North** (122) stay as
  they are. At Waterloo, a mapper's `building:flats=86` counts 903. At Melran
  Mall, a law office is mapped at unit 122. OSM has its own evidence in both,
  so these are questions for the City, not edits.

Two changesets, tagged `mechanical=yes`, the Janefield slices first. Not
before `[DATE]`. Every old value is in the repo
([`cross-civic-flats/manifest.csv`](https://github.com/guelph-maps/guelph-address-import/blob/main/mechanical-edits/cross-civic-flats/manifest.csv)),
so if anyone objects I'll revert on request, no argument first.

@ARandomThumbtack, these lists started as your import's `addr:unit` values.
And if anyone knows the Janefield complex on the ground, I'd love to hear
whether the back-to-back reading is right.
