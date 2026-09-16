# Units: the reversal and campaign 3 — one post, for thread #135103

**Supersedes** `mechanical-edits/unit-listing-retag/ANNOUNCEMENT.md`, which was
written as a 14-day consultation. This is one notice covering both the
non-goal reversal and campaign 3, because they are the same subject and the
same audience.

**Post after the wiki page is republished**, so the section links resolve.

**This is an announcement, not a consultation** — decided 2026-09-16. It says
so in the post, in the maintainer's own words, rather than pretending to a
window that is not being run. Do not soften that; it is the part that keeps it
honest.

---

**Units in Guelph: I changed my mind, and I am correcting a count I got wrong**

Two things, both about units, both of them changes to what this page and I
have previously said.

**1. @ARandomThumbtack, your (d) in #15 deserves a real answer.** You asked
which object carries unit ranges in `addr:unit` where `addr:flats` belongs. I
said "one". It is **453**. I had counted by eye and was wrong by two orders of
magnitude. Measured against a fresh extract on 2026-09-15: 453 Guelph objects
carry a *list* of units in `addr:unit`, like the building way at 37 Goodwin
Drive:

```
addr:unit = 101-113;201-214;301-314;401-414
```

They cover 176 of the City's 409 multi-unit addresses, and 167 of those 176
lists match the City's unit roster exactly — mapped from the same data, and
mapped carefully.

**2. I am reversing a published non-goal.** The wiki page said, in bold, "No
unit-level addresses uploaded." I now think that was wrong and I want to say
why before I act on it rather than after.

The old plan treated "unit" as one thing to keep or drop. The City's data
doesn't. 13,162 of its rows carry a unit, and they are two different
situations: a townhouse front door, and suite 906 of a tower. Collapsing both
to one civic point throws away the doors, which are real separately addressed
places with their own position. Uploading both as nodes scatters 142 points
through one apartment building. Neither is right, because they are not the
same thing at different resolutions.

So: units that are **separate front doors** become **one node each** with
`addr:unit`. Units **stacked in a building** collapse to **one civic node**
carrying `addr:flats`. What decides is the numbering, not the spacing — I
tried spacing first and it was wrong, because 93 Arthur Street South is a
fourteen-storey building and a spacing test called it 193 front doors in 66 m.
Over the 514 stacked groups: 240 groups (6,111 units) are doors, 109 groups
(5,668 units) collapse, and 58 groups (1,381 units) sit in a middle band where
I emit them collapsed and flag them rather than guess.

**Which makes the 453 a problem.** With the import writing `addr:flats` for
collapsed buildings, Guelph would carry the same fact under two keys, split
roughly evenly, indefinitely. So campaign 3 moves them:

```
addr:unit = 101-113;201-214;…   →   addr:flats = 101-113;201-214;…
```

Value verbatim — not re-compressed, not reconciled against the City's list —
so the edit is exactly reversible and asserts nothing the original mapper did
not. Single-valued `addr:unit` is a door and is not touched. 452 objects in 23
batches, one per area, same method as the split now running.

**`addr:flats` is rare here and that is the thing I would most like told I am
wrong about.** Ontario has 58 objects with it against 29,312 with `addr:unit`.
I picked it because it means containment — this node *serves* these units —
where `addr:unit` means identity, this node *is* that unit. No node gets both.

**On timing, plainly.** I am not running a 14-day window for either of these.
Both are tagging changes on a single well-defined set, both are mechanically
reversible with the prior value recorded per object, neither deletes anything
or moves any geometry. I judged a fortnight's pause not worth it and I would
rather say that outright than dress an announcement up as a consultation.
**If you object, the batches get reverted on request — no argument first.**
@ARandomThumbtack, your standing veto is unaffected by my being in a hurry.

Two things I am not claiming. This does not make units searchable: Nominatim
discards `addr:unit` and `addr:full` alike, tested 2026-08-21. And the
maintenance side is deliberately unbuilt — a new unit in an already-collapsed
building needs `addr:flats` *modified*, and this import only creates, so those
go to a review queue rather than an upload until I have built it properly.

Full write-up, with the classifier and the counts:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Unit-level_addresses>
and §&nbsp;Mechanical edits 3 on the same page.
