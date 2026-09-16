# Mechanical edit 3 — announcement draft, NOT POSTED

Reply in thread #135103, after the wiki section (§ Mechanical edits, 3) is
synced so the link resolves. Set the objection deadline to 14 days from the
day it goes up. It answers ARandomThumbtack's (d) in post #15 directly — the
"one object" in our open question 3 was wrong — so lead with that.

Batches are not prepared yet and should not be until the window closes:
edit #2 was announced 2026-08-28 and prepared 2026-09-15 against live OSM,
and the same order applies here. When the time comes, the selection is
"addr:unit contains `;` or matches `^[A-Za-z]*\d+-[A-Za-z]*\d+$`", and the
engine's listing-aware conflation can emit the batches from its tag diff.

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
