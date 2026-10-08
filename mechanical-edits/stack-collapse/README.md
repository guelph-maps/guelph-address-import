# Stack collapse — 5 Gordon Street

**Built 2026-10-02, rebuilt 2026-10-07, not uploaded.** One building, one
changeset: [`5-gordon-street.osm`](5-gordon-street.osm). Upload-ready. No
forum note: skfd decided on 2026-10-07 that none of the post-import cleanups
gets one (the draft is in git history at `5b2afeb`).

## What was there

[Way 413398801](https://www.openstreetmap.org/way/413398801) (6 storeys, with
`addr:housenumber=5`) is ringed by **13 address-only nodes**, n13150618368–380.
ARandomThumbtack's import created them on 2025-09-17
([changeset 172078824](https://www.openstreetmap.org/changeset/172078824)). Each node is one
**vertical column of suites**, `100;200;300;400;500;600` or `208;308;408;507;607`:
the City geocodes every suite in a column to the same point, and that import
made one node per point. Campaign 3 later moved the lists from `addr:unit` to
`addr:flats`, and campaign 1 dropped their `addr:province`. Seven of the nodes
are vertices of the building outline.

On survey (skfd, 2026-10-02) none of them is an entrance. A column of flats is
not something a node can represent, so the positions carry no meaning. The
suite list does: this is the only place OSM names the 61 suites.

## The edit

Our classifier calls 5 Gordon `collapse` (floor-coded, prefixes 1–6), and
collapse means one object listing every suite. The building already carries
the civic number, so the list goes there:

- way 413398801 gains
  `addr:flats=100;102A;102B;105-107;200-212;300-312;400-412;500-507;600-607`
  (61 suites, 61 chars, checked to expand back to exactly the 13 lists);
- the 13 stack nodes are deleted. Seven come out of the outline's node list,
  and each sat within 0.27 m of the straight edge between its neighbours, so
  the footprint does not move (14 → 7 vertices);
- Balzac's (`addr:unit=100`), Rica and Cut Bar are not touched.

Conflation is unaffected, though not for the reason first written here. The
import's candidate (run 334, candidate 6111, `collapse`) matched **stack node
n13150618380** at 6.5 m and was SKIPPED; it did not match the way. Once the
nodes are gone, the nearest `5 Gordon Street` is the building itself, about
7 m away (the City point sits in the notch of the L), and a collapse candidate
matching a building polygon is SKIPPED: 77 of them were in the first pass. So
the monthly re-run still proposes nothing here, and the building's listing is
identical to what it would propose.

`build.py` reads everything live from the API and refuses to write if any node
has gained a tag, joined another way or a relation, or if the building already
lists flats. Rebuild it right before uploading.

## After the import (checked 2026-10-07)

The gap-fill import finished uploading on 2026-10-07. At 5 Gordon:

- **The import added nothing.** `tool.db` has one candidate for the civic,
  the collapse above, SKIPPED; no door nodes (no `unit` candidates under
  `5|GORDON STREET|GUELPH`) and no collapse node. Its eight uploaded collapse
  nodes are all elsewhere. Run 334 (changeset 190123287) did add neighbours:
  1, 17, 19 and 21 Gordon and 7, 9 and 11 Nottingham, all outside this
  footprint and none carrying housenumber 5.
- **Nothing here moved in OSM.** The rebuild against the live API came out
  byte-identical to the 2026-10-02 file: way v8 and stack nodes v3/v4, all
  last touched by campaigns 1 and 3 on 2026-09-30. A map call over the block
  and an Overpass query for every `5 Gordon Street` object found the 13 stacks,
  the building and the three shops, unchanged.
- **Still the only civic in this shape.** Re-measured straight from Overpass
  (base 2026-10-08T01:10Z): 475 `addr:flats` objects (421 ways, 54 nodes) over
  223 civics, 32 split over 2+ objects, and 5 Gordon the only one split over
  more than one node. `survey.csv` is the 2026-10-02 run and was not
  refetched, because `survey.py --refetch` rewrites `unit-doors/live_flats.osm`,
  which another campaign keeps.

The import's own collapse nodes carry the listing on a node because no
building there had the civic. Here the building does, so the listing goes on
it: the same shape on a different carrier.

## Is it a pattern?

No. [`survey.py`](survey.py) groups every live `addr:flats` object by civic
(464 objects, 212 civics). 32 civics have their listing split over 2+
objects, but **5 Gordon is the only one split over nodes**. The other 31 are
separate buildings each listing their own units (190 Fife, 941 Gordon,
32 Arkell, 560 Woolwich, …). That is containment, which `addr:flats` means,
and edit 6 / the import's door nodes already cover those.
See `survey.csv`.

## The post

This is an ordinary survey edit on one building, not a mechanical campaign
(`mechanical=no`). But it deletes 13 objects from ARandomThumbtack's import,
and they asked to be told about unit changes (#19), so it gets a line on
[thread #135103](https://community.openstreetmap.org/t/135103) before or with
the upload.

**Recommendation: ride in another cleanup's post.** By size it is the smallest
edit this project has made: 14 objects (13 deleted, 1 way modified), one
changeset, one civic, nothing else of its kind in the city. The other
cleanups waiting on the thread are campaign 7 (14 objects, a post already
drafted), the redundant listings left of edit 6, and the 149 multi-node
interpolation ways. The redundant-listings post is the natural host: both are
`addr:flats` listings giving way to the shape the import writes. A post of its
own for one building would be the thread's noisiest-to-useful ratio yet.

**Superseded 2026-10-07:** no post at all, for this or the sibling edits.

## Upload

1. Re-run `python build.py` right before uploading; it must print the same
   61 suites and `git diff 5-gordon-street.osm` must be empty (or show only
   version bumps you can account for).
2. Open the file in JOSM as `skfd imports`, upload as one changeset. The
   changeset tags ride in the file.
3. Read it back from `/api/0.6/changeset/<id>/download`: exactly 13 deletes
   (n13150618368–n13150618380) and one modify (w413398801, gaining only
   `addr:flats` and losing only the seven vertices), as area-duplicates did
   for 190174014. `../verify_changeset.py` does not fit: it refuses any
   deletion and expects `mechanical=yes` and a batch manifest. Record the
   changeset id in this README and in `../TODO.md`.
