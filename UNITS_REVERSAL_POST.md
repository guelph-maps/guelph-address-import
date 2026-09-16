# Units reversal — forum post draft

**Reply on thread #135103.** This has to go up *before* the import of missing
objects runs, because it reverses a non-goal that is currently published on
the wiki page: "No unit-level addresses uploaded."

Post #17 says the import runs next week. That is only true if this goes up
now and nobody objects — the clock starts when this is posted, not when the
batches finish.

Republish `IMPORT_PROPOSAL.mediawiki` to the wiki first, so the links resolve.

---

**Changing my mind about units — please shout if this is wrong**

The wiki page currently says, as a non-goal, **"No unit-level addresses
uploaded."** I want to reverse that before I upload anything, because I now
think it was the wrong call, and I would rather be told so here than in a
revert.

**Why it was wrong.** The old plan treated "unit" as one thing to keep or
drop. The City's data doesn't. 13,162 of its rows carry a unit, and they
describe two different situations: a townhouse front door, and suite 906 of a
tower. Collapsing both to one civic point throws away the doors — which are
real, separately addressed places with their own position. Uploading both as
nodes would scatter 142 points through one apartment building. Neither is
right, because they are not the same thing at different resolutions.

**What I want to do instead.** Decide per building, on the unit numbering:

- Units that are **separate front doors** — sequential numbering, spaced like
  doors — become **one node each**, with `addr:unit`.
- Units **stacked inside a building** — floor- or building-coded, like
  101–112, 201–212 — collapse to **one civic node** carrying `addr:flats`.

The numbering is what decides, not the spacing. I tried spacing first and it
was wrong: 93 Arthur Street South is a fourteen-storey building, and a spacing
test called it 193 front doors in 66 m. Stripping the last two digits off each
unit and seeing whether the remainder varies catches the floor codes properly.
Spacing is kept only as a guard — under 2 m apart there is no distinct
location to map, so it collapses whatever the numbers say.

Over the 514 stacked groups in the source: 240 groups (6,111 units) come out
as doors, 109 groups (5,668 units) collapse, and 58 groups (1,381 units) sit
in a middle band — sequential but tighter than a townhouse can be — where I
emit them collapsed and flag them, rather than guess. 252 Stone Road West is
the case that convinced me not to automate that band: it is a mall, its 140
"units" are storefronts, and whether a storefront is a front door is not
something a rule should decide quietly.

**The part I most want opinions on: `addr:flats`.** Ontario has 58 objects
with `addr:flats` against 29,312 with `addr:unit`. This would be close to a
first at scale here, which is exactly why I am not slipping it in. I picked it
because it means containment — this node *serves* these units — where
`addr:unit` means identity, this node *is* that unit. No node would get both.

Values are semicolon-separated ranges broken wherever the numbering skips,
because a single range would be false — Guelph's towers are floor-coded, so
19 Woodlawn Road East runs 101 to 915 while holding 142 units, and only 2 of
46 all-numeric towers are contiguous. 23 Woodlawn Road East, 103 units, comes
out as:

```
101-110;201-212;301-312;401-412;501-512;601-612;701-705;707-712;801-812;901-909;911
```

Median length across the 167 collapsed buildings is 23 characters. **Three do
not fit** OSM's 255-character limit — 85 Mullin Drive is 421 characters
because its units are 1A;1B;2A;2B. Those three get **no listing at all**
rather than a truncated one, since a truncated list would claim the building
ends where the cut landed. They are flagged for me to look at.

@ARandomThumbtack — this is the same ground as our earlier exchange about
units, so I especially want your read. You were right that units matter; I was
too quick to drop them.

**Two things I am not claiming.** This does not make units searchable —
Nominatim discards `addr:unit` and `addr:full` alike, tested 2026-08-21, so
unit-level search is unavailable under every scheme and I am not pretending
otherwise. And the maintenance side is deliberately unbuilt: a new unit
appearing in an already-collapsed building needs `addr:flats` *modified*, and
this import only creates, so those go to a review queue rather than an upload
until I have built it properly.

Full write-up, with the counts and the classifier:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Unit-level_addresses>

**Objections welcome for 14 days.** Nothing unit-bearing uploads until then.
The mechanical unit-split batches already running are unaffected — those only
fix `addr:housenumber=714-30` on objects that are already in OSM, and they
stand on their own regardless of how this lands.
