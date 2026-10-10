# Campaign 7: `addr:flats` naming units the City puts elsewhere

**Done 2026-10-09, by hand.** Built 2026-10-07 as two batches, which were never uploaded.
On 2026-10-09 skfd chose to make both edits by hand in JOSM, on the personal
account, instead of uploading the batches. The towers come first. For the
Janefield slices, the plan is to split them in JOSM and then fix their
addresses. The batch files ([`batches/`](batches/), [`index.html`](index.html))
stay as the reference for what each object should end up as.
[`manifest.csv`](manifest.csv) holds every prior value.

**Towers done 2026-10-09** (local time) by skfd in JOSM:
[changeset 190277623](https://www.openstreetmap.org/changeset/190277623).
It was read back from the API: the three ways changed only `addr:flats`, each
to exactly batch 2's value, from the version the batch was built against.
Recorded in [`uploads.csv`](uploads.csv).

**Janefield done 2026-10-09** by skfd in JOSM, in three changesets. The
operator went further than batch 1, which would only have removed the
listings. Every back-to-back strip on the block was cut into its two homes
(the 7 cross-civic strips plus the same-civic pairs at 176 and 224), and each
half carries its civic and `addr:unit` for the one home inside it, like every
other strip on the street. The import's door nodes there were deleted as now
duplicate. Sheds, fences, driveways and trees that a new development replaced
were removed and its buildings drawn.

- [190278301](https://www.openstreetmap.org/changeset/190278301): the splits.
  Read back: 7 halves kept their strip's old civic though their home was at
  the other, 34 halves used a one-value `addr:flats`, and deleting the old
  `B;C` listing nodes took the plain civic of 6/8/10/12 Mason Court and
  33/35 Janefield with them.
- [190279486](https://www.openstreetmap.org/changeset/190279486): fixes the 7
  civics and turns the one-value `addr:flats` into `addr:unit`.
- [190279513](https://www.openstreetmap.org/changeset/190279513): re-adds the
  six plain civic nodes.

Checked after the third: each of the 36 deleted doors' homes is carried by
the building half that contains it, at the City's civic. No one-value
`addr:flats` is left, and every unit-B/C house has its plain civic again.
Still there: `addr:flats=B` beside a unit-B node at 27, 37, 39, 41 and 43
Janefield. That is the redundant-listings edit's job, and its Old University
batch must be refetched (this work touched 23 of its objects).

**Found in passing:** 12 CanVec-8.0 address nodes from 2018 on the block
carry Janefield numbers the City doesn't have as civics (128, 190, 192, 234,
236, 252, 254, 280, 282, 342, 344, 382). They look like the townhouse unit
numbers mapped as housenumbers. Two duplicate `1 Poppy Lane` nodes are also
there. Both predate this work and are input for the reverse beholder. No forum post: skfd decided on
2026-10-07 that none of the post-import cleanups gets one. The draft is in
git history at `5b2afeb`.

| Batch | Objects | Edit |
|---|---|---|
| 1 | 7 | The Janefield back-to-back slices lose `addr:flats`, whole |
| 2 | 3 | 454 Janefield, 53 Conroy and 23 Woodlawn East each lose one unit the City lacks |

Found 2026-10-02, from skfd asking how
[way 1349287990](https://www.openstreetmap.org/way/1349287990), `176 Janefield
Avenue` with `addr:flats=156;200`, could list two units 44 apart.

## How it happened

The Janefield complex is two civic numbers on one site. The City puts
**74 Janefield Avenue** at units 2–178 and **176 Janefield Avenue** at
180–330. The OSM footprints come from Microsoft's building data. In one row
they cut the terrace into narrow slices that each hold one home from either
side. Every pair sums to 356 (152+204, 154+202, 156+200, …), the signature of
back-to-back townhouses numbered up one side and back down the other.

The 2025 import tagged each slice with one housenumber, and listed as
`addr:unit` every City point that fell inside the slice, whichever civic the
point belonged to (way 1349287990 v2, changeset 173653735). Campaign 3 moved
the list to `addr:flats` verbatim (v3, 2026-09-17). So the listing is the
2025 importer's spatial join, not anything the City says.

## Re-checked 2026-10-07, after the import

All 14 objects were read live from the API, and the City side from snapshot
51 (2026-10-06). Snapshot 52 (2026-10-07) has the same content hash and was
skipped, so 51 is the current data.

| Civic | Object | Listing | City lacks | Now |
|---|---|---|---|---|
| 176 Janefield Avenue | [w1349287989](https://www.openstreetmap.org/way/1349287989) | `154;202` | 154 (at 74) | **batch 1** |
| 176 Janefield Avenue | [w1349287990](https://www.openstreetmap.org/way/1349287990) | `156;200` | 156 (at 74) | **batch 1** |
| 176 Janefield Avenue | [w1349287997](https://www.openstreetmap.org/way/1349287997) | `152;204` | 152 (at 74) | **batch 1** |
| 74 Janefield Avenue | [w1349287991](https://www.openstreetmap.org/way/1349287991) | `158;198` | 198 (at 176) | **batch 1** |
| 74 Janefield Avenue | [w1349287992](https://www.openstreetmap.org/way/1349287992) | `160;196` | 196 (at 176) | **batch 1** |
| 74 Janefield Avenue | [w1349287993](https://www.openstreetmap.org/way/1349287993) | `162;194` | 194 (at 176) | **batch 1** |
| 74 Janefield Avenue | [w1349287996](https://www.openstreetmap.org/way/1349287996) | `164;192` | 192 (at 176) | **batch 1** |
| 454 Janefield Avenue | [w1349266419](https://www.openstreetmap.org/way/1349266419) | `101-108;201-208` | 204 | **batch 2** → `101-108;201-203;205-208` |
| 53 Conroy Crescent | [w802528770](https://www.openstreetmap.org/way/802528770) | `101-107;201-208;301-308` | 105 | **batch 2** → `101-104;106;107;201-208;301-308` |
| 23 Woodlawn Road East | [w178085151](https://www.openstreetmap.org/way/178085151) | `…;701-712;…` | 706 | **batch 2** → `…;701-705;707-712;…` |
| 358 Waterloo Avenue | [w819734215](https://www.openstreetmap.org/way/819734215) | `…;901-908;…` | 903 | **held**: `building:flats=86` |
| 355 Elmira Road North | [w344325628](https://www.openstreetmap.org/way/344325628) | `100-140` | 122 | **held**: a POI carries 122 |
| 7 Ajax Street | [w502064547](https://www.openstreetmap.org/way/502064547) | was `…;205-210;…` | 208 | **done** by skfd, [190114899](https://www.openstreetmap.org/changeset/190114899) |
| 395 Edinburgh Road North | [w1042083497](https://www.openstreetmap.org/way/1042083497) | was `…;409-417;…` | 414–416 | **done** by skfd, [190115369](https://www.openstreetmap.org/changeset/190115369) |

**A correction to the first version of this table.** It drew an arrow from a
tower's stray unit to "the building next door" (204 → 176 Janefield,
208 → 10 Ajax, 105 → 105/91 Conroy, 706 → 19 Woodlawn). That was a
coincidence of numbering. Each of those neighbours has a full run of its own
that includes the number: 10 Ajax has 201–209, and 19 Woodlawn has 701–716.
176 Janefield's 204 is a townhouse. No unit was borrowed from next door. For
all seven towers the fact is the same one: the City has no such unit *at this
civic*. What separates them is whether OSM has its own evidence for the unit.

### The Janefield slices: redundant now, as well as half wrong

The import's changeset
[190115284](https://www.openstreetmap.org/changeset/190115284) (2026-10-06)
created a door node for every one of the 14 units these slices list, each at
the City's civic for it. **Each door lies inside the very slice that lists
it.** That confirms the back-to-back reading on the ground plan, and leaves
every listing saying nothing a door does not already say, half of it under the
wrong civic.

So batch 1 removes `addr:flats` from the seven, and changes nothing else.
The [redundant-listings edit](../redundant-flats/README.md) held exactly these
seven for this campaign (its reason `cross-civic`), so no object is in both.

**The housenumber stays.** Each slice still says `176` (or `74`) while
containing a home of the other civic. That is half right, like every
footprint that straddles two addresses, and changing it is a claim about the
building rather than the listing. It is left to skfd.

### The towers: the City lacks one unit

skfd hand-fixed two of the seven towers on 2026-10-06 in iD ("flat list fix"),
removing exactly the units the City lacks. That is the standard the operator
has already applied. Batch 2 applies it to the three where nothing in OSM
argues otherwise. In each, the listing names every City unit at the civic and
exactly one more:

- **454 Janefield Avenue**: 204 (City: 101–108, 201–203, 205–208)
- **53 Conroy Crescent**: 105 (City: 101–104, 106–107, …)
- **23 Woodlawn Road East**: 706 (City: 701–705, 707–712)

Each is a single gap in an otherwise regular run, so the City's data may be
missing a real unit rather than OSM listing a fake one. Nothing here can tell
which, and it is why batch 2 is separate. The City letter
(`CITY_LETTER_PLAIN_POINTS.md`) asks about all five, and whether a building's
unit list is meant to be complete. If it is partial, put these three back.

Held, because OSM has its own evidence for the unit:

- **358 Waterloo Avenue, 903.** `building:flats=86` was added by Coehill in
  January 2024, before the 2025 import. 86 is the listing's count *with* 903.
  The City has 85.
- **355 Elmira Road North, 122** (Melran Mall). A law office is mapped at
  `addr:unit=122` ([n9139124204](https://www.openstreetmap.org/node/9139124204)).
  The redundant-listings edit holds this way too.

Both are questions for the City, not edits.

## The build

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py

[`build_batches.py`](build_batches.py) reads the 14 ways in full, plus every
address object within ~150 m of each, from the API and not Overpass, and
writes `live.osm` from that. Every gate is decided on the day, and the slice
gates are fatal:

- **Slice:** the listing is a pair. For each unit, the City has it at exactly
  one of 74/176, exactly one OSM object at that civic carries it, that object
  is a node, and it lies inside this slice. The slice carries no `addr:*` tag
  beyond street, number, city, postcode and flats.
- **Tower:** the listing names every City unit and exactly one more. To
  review if another object at the civic carries that unit (`unit-in-osm`),
  if `building:flats` disagrees with the trimmed count (`building-flats`), if
  the live value is not already in the renderer's form (`not-canonical`), or
  if the listing already equals the City (`already-right`).
- **Written:** each batch's units after are its units before less exactly
  the removed ones. Only ways carry an action, and every way carries its live
  version, so a stale one conflicts in JOSM.

Read an upload back with `python ../verify_changeset.py cross-civic-flats N`.
It now knows this campaign: `addr:flats` becomes `flats_after`, or goes when
that is empty.

## What not to do

Do not "fix" a stray by moving it onto the other civic's listing. For the
Janefield slices that writes a second wrong listing, and for the towers it
asserts a containment nobody has checked. Removing a value is the most an
edit should claim.

## Found in passing, not in this edit

**355 Elmira Road North: about 20 units now exist twice.** The import's doors
there (changesets 190123548 and others, 2026-10-06/07) include units that a
business POI at the same civic already carried. Examples: 103 Guelph Budokan
and a door, 123 IKONIK and a door, 112 Melran Holdings plus Cerniuk
Construction and a door. Conflation did not count a POI's `addr:unit` as the
unit being present. The import's other runs may have done the same, so it
wants an engine look and is not a mechanical edit.
