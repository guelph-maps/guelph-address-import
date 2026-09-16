# Pilot post — POSTED 2026-09-16 as #17

Up as [post #17](https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103/17),
which satisfies the gate post #14 promised: "a pilot tile posted here with its
counts and changeset before anything else moves."

**What went up is shorter than this draft**, which is fine — it is skfd's
thread and skfd's voice. Dropped: the counts (5,568 / 5,521 / 36 batches), the
three-way breakdown of the 47 hand cases, the method paragraph and the repo
link, and the `created_by` note.

**One omission is not cosmetic: the account disclosure.** We agreed to
disclose rather than revert, and #17 does not mention that the pilot went from
`skfd` rather than the `skfd imports` the page names in bold. Until it is
said, the pilot is an undisclosed deviation from a published commitment. One
sentence appended to #17, or a line in the next batch post, closes it — the
wording is in the last section below.

The draft is kept as written, because it is the record of what was offered.

---

**Mechanical edit 2 — unit split, pilot batch**

First batch of the double-encoded unit split is up:
**[changeset 189086416](https://www.openstreetmap.org/changeset/189086416)** —
69 objects, the June Avenue area, one changeset for the whole area.

What each object got:

```
addr:housenumber = 33-2   →   addr:housenumber = 33
addr:unit        = 2          addr:unit        = 2    (unchanged)
```

Nothing else was touched — no geometry, no other tags, and deliberately not
`addr:province`, which is the other campaign and gets its own changesets so
either can be reverted without taking the other with it.

**Counts.** 5,568 Guelph objects currently carry a hyphen in
`addr:housenumber`. 5,521 of them split mechanically, across 36 batches of at
most 250, one batch per area from the same 23-area partition the import uses.
The announcement said 5,422 — that was measured in August, and the number has
drifted up since.

**47 are not being touched mechanically**, and they are three different
things:

- **27** are `;`-separated lists (`137-B;139-A;137-A;137`). These belong to
  open question 3 — the MapRoulette idea — not to this campaign. They only
  show up here because a query for hyphens catches them.
- **17** carry the combined form with no `addr:unit` to corroborate the split.
  These are the ~17 the wiki page already said would be done by hand. Each is
  either a genuine range (`380-400 Waterloo Avenue`) or a unit that nothing
  confirms.
- **3** have an `addr:unit` matching neither side of the hyphen —
  `130-BLD D`, `10-6/7`. Obvious enough by eye, not by rule.

**Method,** for anyone who wants to check it. Each batch is prepared as an
`.osm` file carrying the live version number of every object, opened in JOSM
and uploaded by hand. If someone else has edited an object since the batch was
prepared, the upload conflicts rather than overwriting them — that is the
"skipped and re-examined rather than overwritten" the wiki page promises. Every
edited object is recorded with the version it was prepared against and its
prior housenumber, so any batch can be reverted on its own.
Scripts and records:
<https://github.com/guelph-maps/guelph-address-import/tree/main/mechanical-edits/unit-split>

**Two notes on the changeset tags.** `created_by` reads `JOSM` rather than the
tool named in the wiki table, because these batches are uploaded from JOSM
rather than by the importer — JOSM stamps its own and a value that cannot
survive the upload was not worth writing. And this pilot went out from my
personal account `skfd` rather than the dedicated `skfd imports` the plan
names; that was my mistake, the edit itself is unaffected, and the remaining
35 batches will come from `skfd imports`. I would rather leave 69 correct
objects alone than revert and re-upload them to fix the name on the box.

The rest follows over the next few days unless someone objects here.
