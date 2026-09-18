# Ideas found, not decided

Things the data suggested that are **not** being built. Each one is written
down with the numbers that made it tempting and the numbers that stopped it,
so it can be picked up during the import rather than re-derived from a chat
log. Nothing here is proposed, consented or scheduled.

| # | Idea | State |
|---|---|---|
| 1 | Synthesize the missing first unit (`addr:unit=1`) | **parked** 2026-09-16 — scope must shrink from 124 groups to 22, and it would be the import's first invented value |
| 2 | Letter units as civic suffixes (`44B`) | **parked** 2026-09-16 — the shape that motivates it also occurs with digits, where the reading is impossible |

---

## 1. Synthesize the missing first unit

**The idea.** Where the City lists a bare address *and* units that start at 2,
write the first unit explicitly: `52 Alma Street North` gains a door tagged
`addr:unit=1` beside the existing `addr:unit=2`.

**Why it is tempting.** In the class it targets — small houses — the bare row
really does behave like the first dwelling. Among numeric-unit groups with at
most 3 units and a bare row present: **15 start at 2, 6 carry a real unit 1.**
A house with a unit 2 and no unit 1 is a house whose first dwelling is the
plain address.

**What has to shrink first.** Stated as "skips unit 1" the rule is far too
wide:

| Lowest unit number | Groups |
|---|---|
| 100–102 | 80 |
| 2 | 22 |
| 201+ | 8 |
| other | 14 |
| **total skipping unit 1** | **124** |

Eighty of the 124 are floor-numbered towers running 101–608. Adding a `unit=1`
to those invents a unit that does not exist and never did. The rule can only
ever be **"starts at 2"** — 22 groups — and even there the 6 counterexamples
above make it a ~70% inference rather than a fact.

**What it would cost.** Under `[units] policy = "per-door-or-collapse"` a
2-unit house becomes door nodes, not a collapsed civic node, so the main door
takes `addr:unit=1` — which asserts *identity*, "this node is unit 1". That is
the distinction [FINDINGS_POST.md](FINDINGS_POST.md) line 25 was written
about; `addr:flats=1;2` would claim only containment, but the policy will not
collapse a group that small. It would also be **the first value the import
writes that is not in the source**, against a project that has so far moved
everything verbatim.

**The 12 concrete cases** (bare row + a lone unit 2): 52 Alma Street North,
53 Ferndale Avenue, 93 Vaughan Street, 127 Silurian Drive, 36 Ridgeway Avenue,
245 Stephanie Drive, 264 Exhibition Street, 24 Queensdale Crescent,
167 Municipal Street, 41 Gladstone Avenue, 18 Mclachlan Place,
1 Mccorkindale Place. OSM already has all 12 buildings; **11 carry no unit at
all**, and the one that does — [way 935207286](https://www.openstreetmap.org/way/935207286),
53 Ferndale — uses `53` + `addr:unit=2`.

---

## 2. Letter units as civic suffixes

**The idea.** Project a single-letter unit onto the housenumber:
`44 Regent Street` + `UNIT_NO=B` becomes `addr:housenumber=44B` rather than
`addr:housenumber=44` + `addr:unit=B`.

**Why it is tempting.** 44 Regent Street is a bare row (`HAS_UNIT=N`) plus a
single `B`, with no `A`. A unit scheme with no unit A is not a unit scheme —
the bare address is the A. And unit-level search does not work: the project's
own Nominatim test (2026-08-21, proposal line 178) found `addr:unit` is
discarded, so the unit form loses the address while `44B` is findable.

**What stopped it.** The same shape occurs with digits, where the suffix
reading is impossible. `52 Alma Street North` + unit `2` with no unit `1` is
structurally identical to `44 Regent Street` + unit `B` with no unit `A`, and
nobody would write `522`. The City records "a second dwelling added to a
house" this way whether it labels the second one `2` or `B`, so **the shape
cannot decide which is a civic number and which is a unit.** Only the door
can, and the source file has no field for what is on the door.

Two other tests were tried and do not work either. All 71 letter groups sit on
a **single PIN**, so parcel identity does not discriminate — a house and its
lettered ADU share a parcel by construction. And `ROLL_NO` shape fails its own
calibration: only 160 of 227 apartment towers show the parent-roll pattern
that would have to mean "parcel parent".

**Community practice does not settle it either.** At numbers where the City
publishes no letter at all, Guelph mappers have written the suffix form **31
times** and the unit form **31 times**. Dead even — there is no local
convention to defer to.

**The scope question, unanswered.** Does the rule apply to all 169 letter
rows, or only to the 51 groups that also have a bare row? The 20 letters-only
groups (72 rows) all start at A, which is what a unit-lettered building looks
like.

**Edge cases it would leave**, if it is ever taken up:

1. **Letters beside digit units in one building** — 1219 Gordon Street
   (A, B, C *and* 101–608) and 20 Stevenson Street South (A–D *and* 5, 6).
   `1219A` would be a civic number while `1219` unit 101 stays a unit, in the
   same building. Needs a carve-out.
2. **253 and 263 Exhibition Street run A–K** — 22 civic numbers out of two
   buildings.
3. **15 existing OSM objects would be re-touched**, 11 of them edited by
   campaign 2 on 2026-09-16 (`787-B` to `787` + unit B to `787B`). A third
   edit on the same node.
4. **31 city-silent objects stay unit-form** regardless, so OSM keeps both
   encodings either way.
5. **5 groups carry `HAS_UNIT=N` while carrying a letter** — the source
   contradicting itself.
6. **531 rows in other unit shapes** are untouched — 291 like `18D`, 196 like
   `D8`, 44 like `PH`, `BLD E`, `LL01`. Worth stating explicitly that `18D`
   stays a unit so it is not later read as a suffix.
7. **Conflation would need three forms.** `44B`, `44` + `addr:unit=B` and
   `44-B` must all match one door.

**Green lights, for whoever picks it up.** Zero collisions — no proposed
`NNNL` hits an existing source address or an existing OSM housenumber. All 169
source letters are uppercase. 154 of the 169 would be new nodes rather than
retags.

**The original importer weighed in, 2026-09-17 (posts #19 and #20).** Asked
about exactly this, ARandomThumbtack came down on **respecting the source**:

> Even if it's silly, I think the unitless + unit B data from the City should
> be respected, because who knows what sort of edge case then fails because we
> didn't faithfully propagate the data from the dataset.

That is the same conclusion this idea was parked on, now with a second voice
behind it. **Idea 2 stays parked, and is closer to closed than open.**

They did offer a route *if* it were ever taken up — and it is worth writing
down why it cannot be taken as-is. Their suggestion is to write the
housenumber as `44-A` and `44-B`, so that numeric cases become `53-1` and
`53-2`:

> However, if we wanted to proceed with Fixing it idea 1, then a solution: map
> the housenumbers so that it turns into "44-A" and "44-B". That way, numeric
> units turn into "53-1" and "53-2".

**`53-1` is the exact form campaign 2 just spent 5,521 edits removing.**
`addr:housenumber=714-30` alongside `addr:unit=30` is the double encoding the
whole campaign was about, and it is not even in Canada Post's order. Adopting
`53-1` as a civic number would re-create that shape city-wide, one year after
arguing it away — and conflation could no longer tell a genuine `53-1` civic
number from a leftover double encoding, because they would be spelled
identically. It also collides with edge case 7 above, which already needs
three forms to match one door.

The hyphen-free suffix (`44B`, no hyphen) does not have this problem, which is
what this idea actually proposed. The distinction is small on the page and
total in the data, and it is the thing to raise if the question comes back.

**What is decided and unaffected:** the import projects the source verbatim,
`44` + `addr:unit=B`, exactly as it will write `52` + `addr:unit=2`. Edge
case 7 is worth writing into the proposal *regardless* of this idea, because
31 suffix-form objects already exist in OSM and conflation has to match them.

---

## Also noticed, not ideas

* **[config.toml](config.toml) illustrates the source `ADDRESS` column as
  `"12-100 Main St"`**, but the real values append the unit at the end —
  `39 Dawson Road 12`, `44 Regent Street B`. The reasoning for not using
  `full` holds; only the example is wrong.
* **[Node 11120060764](https://www.openstreetmap.org/node/11120060764)** is
  the `380-400 Waterloo Avenue` hand case (row 44 of
  `mechanical-edits/unit-split/review.csv`, reason `no-unit`). It is an
  `amenity=parking_entrance` whose physical tagging is sound, but the City
  lists only 380 and 400 on that stretch — nothing between them — so
  `380-400` is two endpoints, not a range, and both addresses are already
  carried by the two buildings and the mapper's own `entrance=main` nodes.
  Suggested verdict: **remove `addr:*`, not split.** Not recorded in
  `hand-cases/complex.csv` yet, and not something to edit silently — it is
  eireidium's hand-mapping.
