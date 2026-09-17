# Mechanical edits — what is done, and what is queued

Campaigns 1–3 have their own directories here. This file is for the ones that
have been *found* but not yet proposed, so they do not live only in a chat log.

| # | Campaign | State |
|---|---|---|
| 1 | Remove `addr:province=Ontario` (~3,699) | consented 2026-09-10, **not built** |
| 2 | Split double-encoded unit housenumbers | **done** 2026-09-16, 5,521 objects, 36 changesets |
| — | Campaign 2/3 leftovers, corroborated by the City roster | **done**, 32 objects |
| 3 | Unit lists `addr:unit` → `addr:flats` (452) | announced 2026-09-16, uploading |
| 4 | **Remove meaningless `addr:interpolation`** (81) | ← queued, see below |
| 5 | **Tidy the `addr:flats` separators** (51) | ← queued, see below |

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

**Consent.** Not announced. It is a fourth mechanical edit and needs its own
notice on [thread #135103][thread] before anything uploads, the same as 3 —
and it should say plainly that the 405 real interpolation ways are being left
alone, because "removing addr:interpolation from Guelph" sounds much larger
than it is.

**Build note.** The same `build_batches.py` shape as the others. Small enough
(81) that it is one or two batches, not twenty-three. Fetch fresh: several of
these objects are being edited by campaign 3 right now, so their versions will
have moved.

## 5. Tidy the `addr:flats` separators

**Found 2026-09-16**, when skfd spotted `101-113;201-214;301-314;401-414;` on
the campaign 3 pilot and asked whether the trailing semicolon belonged.

It does not — a trailing `;` reads as an empty final element — but it was
inherited honestly: campaign 3 moves the value **verbatim**, and the trailing
`;` was in the `addr:unit` the original mapper wrote. Holding the verbatim rule
mid-campaign was the right call; this pass cleans up afterwards.

Of campaign 3's 452 values: **402 clean, 49 with a trailing `;`, 2 with spaces
around the separator** (`201-209; 301-309; …`, 55 Yarmouth Street). 51 objects.

**Why bother.** The import's own `addr:flats` renderer writes clean values
(`101-110;201-212;701-705;707-712`). Leave these and Guelph carries two
formats for one key, written by the same maintainer days apart — the "two
conventions in one city" problem this project objects to everywhere else.

**Pair it with campaign 4.** Overlapping objects, both pure tag hygiene on
apartment buildings, one changeset, one revert, one notice. Doing them
separately means announcing twice for what a reader will see as one cleanup.

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
