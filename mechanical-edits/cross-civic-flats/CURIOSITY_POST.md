# Draft — a curiosity for thread #135103

**Not posted.** A light post, not an announcement: nothing is being edited.
Post it alongside the doors-beside-a-listing notice before the pilot, or on
its own; skfd decides. Condensed from `README.md` beside it.

---

A small Guelph curiosity found while reviewing unit shapes for the import.

[This building slice at 176 Janefield Avenue](https://www.openstreetmap.org/way/1349287990)
lists `addr:flats=156;200`. Two units 44 apart in one narrow footprint looked
impossible — until the City's data explained it. The complex has two civic
numbers: one side of each row is **74 Janefield** (units 152–178), the other
is **176 Janefield** (units 180–330). The footprints slice each row into
pieces that each hold one home from either side, and every pair adds up to the
same number (152+204, 154+202, 156+200…). They are back-to-back townhouses,
numbered up one side and back down the other.

So unit 156 is really 74 Janefield, unit 156 — it ended up under 176 because a
single footprint could only carry one housenumber. Seven slices there are like
this. Across all 462 Guelph objects that list units, 14 name a unit the City
puts somewhere else (or nowhere); the list is in the project repo.

Nothing changes now. The import adds each of those homes as its own door node
at the right civic, which makes these listings redundant; cleaning them up
would be a separate edit, announced here first. If anyone knows the Janefield
complex on the ground, I'd love to hear whether the back-to-back reading is
right.
