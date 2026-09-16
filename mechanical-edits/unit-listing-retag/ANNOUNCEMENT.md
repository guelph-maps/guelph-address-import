# Mechanical edit 3 — announcement draft, SUPERSEDED 2026-09-16

**Do not post this.** It was written as a 14-day consultation and as a post of
its own. Both are now wrong:

- The 14-day window was dropped on 2026-09-16 — campaign 3 and the units
  reversal are **announced, not consented**, and proceed immediately. The
  reasoning, and the standing offer to revert on request, are in
  `IMPORT_PROPOSAL.mediawiki` § Status.
- It is merged with the units reversal into one post, because they are the
  same subject and the same audience, and because the correction to
  ARandomThumbtack's (d) belongs next to the reversal it motivates.

**The post that goes up is `../../UNITS_REVERSAL_POST.md`.**

This file is kept as the record of what was drafted under the old plan. The
line below saying nothing uploads before the window closes no longer holds.

---

**Mechanical edit 3 — moving unit lists from `addr:unit` to `addr:flats`**

@ARandomThumbtack, your (d) in #15 — "which object is that?" — deserves a
better answer than I gave. Not one object: **453**. I had counted by eye.
Measured against a fresh extract on 2026-09-15, 453 Guelph objects carry a
*list* of units in `addr:unit`, like the building way of 1878 Gordon Street:

```
addr:unit = 101-116;201-215;301-314;401-414;…
```

They cover 176 of the City's 409 multi-unit addresses, and 167 of the 176
lists match the City's unit roster exactly — clearly mapped from the same
data, and mapped carefully.

**Proposal: move the key, touch nothing else.**

```
addr:unit  = 101-116;201-215;…   →   addr:flats = 101-116;201-215;…
```

`addr:unit` means *this address is unit 30*; the wiki allows several values
on it only where one address spans adjacent units. `addr:flats` means *this
building contains units 101–116* — the wiki's words are "the range of unit
numbers within a larger building or complex", on the building or its
entrance, in exactly this `3-7;10;14-18` format. Right now Guelph says both
things with one key: 5,863 doors and 453 buildings, told apart only by the
shape of the value. The continuous import will write `addr:flats` for
collapsed buildings, so without this we would carry the same fact under two
keys for good.

**What it is not.** Single-valued `addr:unit` — the doors — is not touched.
Lists move verbatim: not re-compressed, not reconciled against the City. No
geometry, no other tags. Same mechanics as edit 2: JOSM batches per area,
separately revertable, `mechanical=yes`, from the import account, after the
split finishes. And on your (e): this is the opposite of door positions — the
list stays on the building, exactly where you put it.

I know `addr:flats` is nearly unused in Ontario (58 objects province-wide
against 29,312 `addr:unit`). That is the reason to ask rather than do.
**Objections welcome for 14 days, to <DATE>.** Written up at § Mechanical
edits on <https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous>.
