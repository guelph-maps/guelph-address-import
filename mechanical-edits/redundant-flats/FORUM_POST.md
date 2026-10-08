# Draft — redundant `addr:flats` listings, for thread #135103

**Not posted.** Post it before batch 1 uploads. It is a reply in
[#135103](https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103),
not a new topic. It tags @ARandomThumbtack because of their #19 request, and
because these values started as their import's.

Three things for skfd to settle before posting:

- **The wait.** `[DATE]` is a placeholder. Earlier cleanups went up on short
  notice with a standing offer to revert. Pick a date, or drop the sentence.
- **5 Gordon Street.** `../stack-collapse/FORUM_NOTE.md` prefers to ride in
  another cleanup's post. Its "As a section" paragraph can be pasted in where
  marked below. Leave it out if that edit is going up on its own.
- **The manifest link** works only once this directory is pushed to
  `guelph-maps/guelph-address-import`.

Numbers are from the 2026-10-07 build. Re-check them against the rebuild on
the day.

---

**A cleanup after the import: listings the new doors made redundant**

The first pass of the gap-fill finished on 7 October: 4,367 address nodes,
1,680 of them unit doors (`addr:unit`) at 143 addresses. At 92 of those
addresses, a building still lists the same units in `addr:flats`. So every
unit there is now in OSM twice: once as its own door, and once in a listing
that says the units share one entrance. They don't share one. That's why
they got doors.

So I'll remove `addr:flats` from those **317 objects** (300 buildings and 17
address nodes). Nothing else on them changes, and nothing is created or
deleted. The rule is strict: a listing goes only if **every** unit it names
now has its own door node at the same address. In practice all 1,069 of those
units are the import's new doors. Examples: the eight semis at
[146 Downey Road](https://www.openstreetmap.org/way/1450184516) (`17A;17B` and
so on), [275 Hanlon Creek Boulevard](https://www.openstreetmap.org/way/794182120)
(`1-5`), and 190 Fife Road (36 buildings, 72 doors).

@ARandomThumbtack, these values started as your import's `addr:unit` lists.
Campaign 3 moved them to `addr:flats` in September, verbatim. Now they come
off, because each unit has its own address node. I didn't touch any listing
that a mapper wrote as `addr:flats`, and in fact none of the 317 is one.

**Not touched (10).** I'll look at these by hand:

- **The seven Janefield slices** at 74/176 Janefield Avenue (the back-to-back
  townhouses from my earlier post). Every unit has a door, but some are at
  the other civic number, so they belong to that separate cleanup.
- **355 Elmira Road North** lists `100-140`. The City has no unit 122, and
  in OSM 122 exists only on a law office's node.
- **120 Country Club Drive** lists unit 32, which has no door and isn't in
  the City's data.
- **7 Kay Crescent**: the tower keeps its listing (that's the shape chosen
  there). It also names the six lower-level units LL01–LL06, which now have
  their own doors. Trimming those would change the value, not remove it, so
  it isn't in this edit.

20 changesets, one per area, tagged `mechanical=yes`. The first is Kortright
Hills (Downey Road and Hanlon Creek Boulevard), and I'll check it on the map
before the rest. Not before `[DATE]`. Each object's old value is in the repo
([`redundant-flats/manifest.csv`](https://github.com/guelph-maps/guelph-address-import/blob/main/mechanical-edits/redundant-flats/manifest.csv)),
so if anyone objects I'll revert on request, no argument first.

<!-- Optional: paste stack-collapse/FORUM_NOTE.md "As a section in another
cleanup's post" here. -->
