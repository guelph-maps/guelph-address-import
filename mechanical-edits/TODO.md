# Mechanical edits — what is done, and what is queued

Campaigns 1–3 have their own directories here. This file is for the ones that
have been *found* but not yet proposed, so they do not live only in a chat log.

| # | Campaign | State |
|---|---|---|
| 1 | Remove `addr:province` (44,796, **not** the ~3,699 consented) | **done** 2026-09-30, 44,763 objects, 25 changesets (one per area) 189754709–189754880, all verified. The 33 held for hand review followed in 189755505 (32; one had already lost the tag) |
| 2 | Split double-encoded unit housenumbers | **done** 2026-09-16, 5,521 objects, 36 changesets |
| — | Campaign 2/3 leftovers, corroborated by the City roster | **done**, 32 objects |
| 3 | Unit lists `addr:unit` → `addr:flats` (447) | **done** 2026-09-17, 447 objects, 23 changesets |
| 4 | Remove meaningless `addr:interpolation` (81) | **done** 2026-09-30, with campaign 5 — changesets 189752405–189752690, all verified |
| 5 | A real `addr:flats` normalizer (292 of 464 untidy, re-measured) | **done** 2026-09-30, merged with campaign 4 — 325 objects, 22 changesets, each read back from the API and verified |
| 6 | Unit doors: `addr:flats` on door groups → one `addr:unit` node per door (252 objects, 868 nodes) | **Rebuilt 2026-10-07 as what is left: strip the listings the import's doors made redundant. Not uploaded; no forum post (decided 2026-10-07).** The import created the doors itself (1,680 at 143 civics, 2026-10-03..07). At 92 of those civics, 327 objects still list units in `addr:flats`. **317** list only units that now have their own door node (300 ways, 17 civic nodes, 1,069 units). They lose `addr:flats` and nothing else, in 20 batches, one per area, pilot Kortright Hills. Every value was written by campaign 3 (301) or the hand cases (16). Held: 10 (7 Janefield slices → campaign 7, 355 Elmira Road North, 120 Country Club Drive, 7 Kay Crescent). Next: `--refetch` and upload. See `redundant-flats/README.md`; `unit-doors/` is superseded and its batches must not be loaded |
| — | 5 Gordon Street: 13 per-stack `addr:flats` nodes → one listing on the building | **built 2026-10-02, rebuilt 2026-10-07 byte-identical, upload-ready** — survey edit, one changeset, 14 objects; still the only civic in this shape. The import added nothing at 5 Gordon (its collapse candidate SKIPPED). No forum post (decided 2026-10-07). See `stack-collapse/README.md` |
| 5b | Campaign 5's pairs: `addr:flats` `1-2` → `1;2` (126 objects, all written by campaign 5) | **done 2026-10-03**, 126 objects, 14 changesets 189908359–189908514, all verified. Campaign 5's batches were cut 53 minutes before the engine stopped writing two-unit runs as ranges. Covered by post #21; no separate notice. See `flats-pairs/README.md` |
| 7 | `addr:flats` naming units the City puts elsewhere (14 recorded 2026-10-02; 7 are the 74/176 Janefield back-to-back slices) | **Built 2026-10-07, not uploaded; no forum post (decided 2026-10-07).** Re-checked live after the import. Batch 1: the 7 Janefield slices lose `addr:flats` (the import's 190115284 put a door for all 14 of their units at the right civic, each inside the slice that lists it). Batch 2: 454 Janefield (204), 53 Conroy (105) and 23 Woodlawn East (706) lose the one unit the City lacks. Done by hand by skfd 2026-10-06: 7 Ajax, 395 Edinburgh. Held: 358 Waterloo (`building:flats=86` counts 903) and 355 Elmira (a POI at unit 122). 2026-10-09: done by hand in JOSM instead (skfd). Towers **done**, changeset 190277623, verified; the slices are next, split and re-addressed; the City letter asks whether unit lists are complete. See `cross-civic-flats/README.md` |
| 8 | The 149 open `addr:interpolation` ways with 3+ nodes that campaign 4 left out: delete the lines that add no address | **Superseded 2026-10-09 by MapRoulette** (`against-interpolation --city guelph`, all Guelph lines, end nodes included); the batches here are a record, not to be uploaded. Was: **surveyed and built 2026-10-07, not uploaded; no forum post (decided 2026-10-07).** All 149 still live. 147 are valid by JOSM's test (both ends numbered, same street, right parity); 2 have a bare end and 8 have end nodes on a street the City spells differently (Glenholme, Watson Rang South…) — hand cases. 2 more cross into Guelph/Eramosa and span County addresses OSM lacks (Eramosa Road 750/756, Fife Road 7070–7108): never deleted. **None of the other 137 adds an address OSM lacks:** 29 run N to N, 61 span 260 City addresses all already mapped (44 by the import), 47 span no City address at all (CanVec/StatCan block-face ranges). Built: the 29 N-to-N, one batch, 29 ways + 47 bare middle nodes deleted; end nodes untouched. The 61 + 47 build with `--tiers`; they rest on the City roster being complete, which the City letter asks about. First edit that deletes others' objects. The 405 two-node lines answer the same way (0 add an address) — a separate follow-up. See `interpolation-multinode/README.md` |

---

## 4. Remove `addr:interpolation` where it cannot mean anything

**Found 2026-09-16**, while campaign 3's batches tripped JOSM's validator with
*"End node without housenumber in address interpolation"*. The warning was not
caused by our edit; it was pre-existing, and chasing it turned up a
city-wide pattern.

`addr:interpolation` describes **a way drawn between two address nodes** — it
says "the numbers run from the housenumber at one end to the one at the other".
It is meaningless anywhere else, because there are no two ends to interpolate
between.

Surveyed across the whole city (Overpass, admin_level 6, 2026-09-16):

| Shape | Count | Verdict |
|---|---|---|
| 2-node open way | 405 | **Legitimate.** Real interpolation. Do not touch. |
| Open way, 3–26 nodes | 149 | Legal in principle — an interpolation way may have intermediate nodes. Wants a *different* check (do both ends carry `addr:housenumber`?), not this one. Out of scope. |
| **Closed way (building outline)** | **78** | **Wrong.** A polygon has no two ends; its corners are geometry, and they will never carry housenumbers. This is what JOSM is complaining about. |
| **Node** | **3** | **Wrong.** A single node cannot interpolate between anything. |

**Scope: the 81.** Closed ways and nodes only. Remove `addr:interpolation`,
change nothing else. The 405 legitimate ones and the 149 multi-node ones are
explicitly not in this campaign.

**Why it is worth doing, beyond tidiness.** These are the *same mistake*
campaign 3 is fixing, made with a different key. Whoever tagged a building
`addr:interpolation=all` was reaching for "this building contains a range of
addresses" — which is what `addr:flats` means and what `addr:interpolation`
does not. 74 of the 78 closed ways are campaign 3 objects, so they are already
getting the right key; this removes the wrong one. And the warning will
otherwise nag every mapper who opens one of those buildings in JOSM, forever.

**Consent.** Announced 2026-09-18 as post #21 on [thread #135103][thread],
jointly with campaign 5, without a
14-day window. The 2026-09-19/20 weekend it named came and went without an
upload; the batches were rebuilt 2026-09-29 and still wait on JOSM — the same call as campaign 3. The posted form does **not** say
that the 405 real interpolation ways are being left alone, which is the one
thing this entry asked it to say; #21 is editable and that line still belongs
in it.

**Build note.** The same `build_batches.py` shape as the others. Small enough
(81) that it is one or two batches, not twenty-three. Fetch fresh: several of
these objects are being edited by campaign 3 right now, so their versions will
have moved.

## 5. A real `addr:flats` normalizer

**Started 2026-09-16** as "strip the trailing semicolon", when skfd spotted
`101-113;201-214;301-314;401-414;` on the campaign 3 pilot. It is bigger than
that: **171 of campaign 3's 447 values (38%) are untidy in at least one way.**

Campaign 3 moved values **verbatim** and was right to — that promise is what
makes it trivially reversible, and holding it mid-campaign was deliberate.
This is the pass that cleans up afterwards.

### What the normalizer has to do

| Defect | Count | Example | Should be |
|---|---|---|---|
| Enumeration that should collapse | 110 | `12;13;14;15;16;17;18;19;20;21` (39 Kay Crescent) | `12-21` |
| Trailing `;` | 49 | `101-113;201-214;301-314;401-414;` | no trailing separator |
| Sorted as text, not as numbers | 35 | `10;11;12;7;8;9` (245 Southgate Drive) | `7-12` |
| Spaces around `;` | 2 | `201-209; 301-309; 401-409;` (55 Yarmouth) | no spaces |

The text-sorting one is the ugliest in the wild: 358 Waterloo Avenue reads
`1001-1008;1101-1108;101-106;201-208;…` — the eleventh floor sorts above the
first because `1` precedes `2` as a character. Floors must sort **numerically**
so the thousands land at the end where a reader expects them.

### Do not write this twice

`t2/units.py` already has `compress_flats()` and `flats_tag()`, which render a
set of units into exactly the wanted form — gap-broken ranges, numeric order,
no trailing separator. That is the canonical implementation and the import
already writes through it.

So the normalizer is **parse existing value → set of units → `compress_flats`**,
and the only new code is the parser. Reimplementing the rendering would give
Guelph two answers to the same question, which is the whole complaint this
campaign exists to fix.

Cases the parser must not mangle:

* **Letter prefixes are building letters**, and group on their own:
  `D101-D112;D201-D212`. Do not merge across letters.
* **Letter suffixes cannot join a range** — `101A` is a single value and stays
  one.
* **`LL` floors** (`LL01;LL02;LL03`) are a real prefix, not a typo. The engine
  has a known cosmetic wrinkle here (`LL01-LL04` renders as `LL1-LL4` because
  `parse_unit` goes through `int()`); fix that in the engine, not around it.
* **Stepped sequences** (176 Janefield Avenue steps by two) do not compress,
  and must not be forced into a range that claims the missing ones exist.
* **The 255-character limit.** Three groups already blow it and have their
  listing dropped rather than truncated. A normalizer that *shortens* values
  may rescue some of those — worth re-measuring after.

**Round-trip test before any upload:** the parsed unit set must be identical
before and after. If normalizing changes which units a building claims, the
parser is wrong, and that is a data-corrupting bug rather than a cosmetic one.

### Scope

Everything carrying `addr:flats` in Guelph once campaign 3 lands — the 447,
plus the pre-existing handful, plus whatever the import writes. Re-measure
rather than assuming 171.

**Paired with campaign 4, and built as one.** Done 2026-09-17 in
`mechanical-edits/flats-hygiene/` — one builder, one batch set, one revert,
one notice. The pairing turned out to be not just tidier but necessary: 74 of
the 81 interpolation objects also carry `addr:flats`, so two separate batch
sets would have conflicted against each other on object version.

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
