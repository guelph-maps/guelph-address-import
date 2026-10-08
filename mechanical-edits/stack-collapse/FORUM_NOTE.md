# Draft — 5 Gordon Street, for thread #135103

**Not posted.** Two forms of the same note: a paragraph that rides in another
cleanup's post (preferred, see `README.md` § The post), and a standalone reply
if nothing else is going up when this is ready to upload. Either way it names
ARandomThumbtack, because it deletes 13 nodes their 2025 import created.

---

## As a section in another cleanup's post

**5 Gordon Street, one building.** The 2025 import left 13 address nodes
around [this six-storey building](https://www.openstreetmap.org/way/413398801),
each listing one vertical column of suites (`100;200;300;400;500;600`, …),
because the City puts every suite in a column on the same point. A column isn't
a place, and on the ground none of those points is an entrance. One changeset
moves the 61 suites onto the building as a single
`addr:flats=100;102A;102B;105-107;200-212;300-312;400-412;500-507;600-607` and
deletes the 13 nodes (seven were corners on the outline's straight edges, so
the footprint doesn't move). The shops at 5 Gordon are untouched. It's the
only address in Guelph shaped like this. @ARandomThumbtack, since these are
your import's nodes — shout if you'd rather keep them.

## As a standalone reply

One small survey edit at 5 Gordon Street, flagged here because it removes
nodes from the 2025 import.

[The building](https://www.openstreetmap.org/way/413398801) is ringed by 13
address-only nodes (n13150618368–n13150618380), each listing one vertical
column of suites — `100;200;300;400;500;600`, `208;308;408;507;607`, and so
on. The City geocodes every suite in a column to the same point, and the
import made one node per point. On the ground none of them is an entrance, so
the positions don't mean anything; the suite list does, and it is the only
place OSM names those 61 suites.

The edit, one changeset:

- the building gains
  `addr:flats=100;102A;102B;105-107;200-212;300-312;400-412;500-507;600-607`
  (checked to expand back to exactly the 13 lists, no suite gained or lost);
- the 13 nodes are deleted. Seven were vertices of the outline, each within
  0.3 m of the straight edge between its neighbours, so the footprint doesn't
  move;
- Balzac's, Rica and Cut Bar are untouched.

This is the shape the gap-fill import itself writes for a tower like this: one
object listing every suite. It's the only address in Guelph where a listing is
split over several nodes (re-checked 2026-10-07 against all 475 objects that
list units), so there's nothing further of this kind coming.

@ARandomThumbtack — these are your import's nodes; let me know if you'd rather
they stayed, and I'll hold it or revert.
