# Stack collapse — 5 Gordon Street

**Built 2026-10-02, not uploaded.** One building, one changeset:
[`5-gordon-street.osm`](5-gordon-street.osm).

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

Conflation is unaffected: a collapsed candidate already matches the building
way by housenumber, so the import proposes nothing at 5 Gordon either way.

`build.py` reads everything live from the API and refuses to write if any node
has gained a tag, joined another way or a relation, or if the building already
lists flats. Rebuild it right before uploading.

## Is it a pattern?

No. [`survey.py`](survey.py) groups every live `addr:flats` object by civic
(464 objects, 212 civics). 32 civics have their listing split over 2+
objects, but **5 Gordon is the only one split over nodes**. The other 31 are
separate buildings each listing their own units (190 Fife, 941 Gordon,
32 Arkell, 560 Woolwich, …). That is containment, which `addr:flats` means,
and edit 6 / the import's door nodes already cover those.
See `survey.csv`.

## Before upload

This is an ordinary survey edit on one building, not a mechanical campaign.
But it deletes 13 objects from ARandomThumbtack's import, so a line on
[thread #135103](https://community.openstreetmap.org/t/135103) is a courtesy
worth paying, before or with the upload.
