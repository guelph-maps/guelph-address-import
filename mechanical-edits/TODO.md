# Mechanical edits — what is done, and what is queued

Campaigns 1–3 have their own directories here. This file is for the ones that
have been *found* but not yet proposed, so they do not live only in a chat log.

| # | Campaign | State |
|---|---|---|
| 1 | Remove `addr:province` (44,796, **not** the ~3,699 consented) | **built** 2026-09-17, 44,763 objects, 105 batches — held for a corrected consent |
| 2 | Split double-encoded unit housenumbers | **done** 2026-09-16, 5,521 objects, 36 changesets |
| — | Campaign 2/3 leftovers, corroborated by the City roster | **done**, 32 objects |
| 3 | Unit lists `addr:unit` → `addr:flats` (447) | **done** 2026-09-17, 447 objects, 23 changesets |
| 4 | Remove meaningless `addr:interpolation` (81) | **announced** 2026-09-18 (post #21) with campaign 5, one batch set — uploading 2026-09-19/20 |
| 5 | A real `addr:flats` normalizer (292 of 464 untidy, re-measured) | **announced** 2026-09-18 (post #21), merged with campaign 4 — 325 objects, 22 batches, uploading 2026-09-19/20 |

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
jointly with campaign 5, and uploading the weekend of 2026-09-19/20 without a
14-day window — the same call as campaign 3. The posted form does **not** say
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
