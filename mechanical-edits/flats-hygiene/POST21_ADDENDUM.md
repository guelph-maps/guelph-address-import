# Addendum for post #21 — paste-ready

Post #21 (2026-09-18) ends *"Will update this post when it's done"*, so it is
editable. What follows is the four things the condensed post dropped, written
to be appended to it rather than posted separately.

**The timing paragraph is the one that matters.** Proceeding without a 14-day
window is a defensible call — campaign 3 and the units reversal both made it —
but it is defensible *stated*. Right now #21 announces two campaigns and does
not say when they land, that no window is being run, or that they will be
reverted on request. The rest is detail; that paragraph is the consent.

---

**Scope, stated plainly: 81 objects lose `addr:interpolation`, and 554 keep
it.** The tag describes a way drawn between two address nodes — the numbers
run from the housenumber at one end to the one at the other. Guelph has 635
objects carrying it. 405 are two-node ways, which is exactly what the tag is
for; 149 are open ways with three or more nodes, which are legal and want a
different question asked of them (do both ends carry `addr:housenumber`?) that
I am not asking here. **Neither group is touched.** What is left is 78 closed
ways and 3 nodes — a building outline has no two ends, and a single node has
nothing to interpolate between.

**Every `addr:flats` value is gated on a round trip, and 464 of 464 pass.**
Parse the value, render it with the import's own `compress_flats`, parse the
rendering, and demand the set of units be identical. If normalising ever
changed which units a building claims, that is data loss dressed up as
tidying, and it is the one thing here that could actually hurt. Anything
failing the gate is left alone. The careful cases, each with a test: `101A` is
one unit and never joins a range; `D101-D112;D201-D212` never merge across
letters; `LL01` keeps its zero — that one needed a fix in the import itself;
and 176 Janefield Avenue is a row of blocks stepping by two, so `224;234`
stays `224;234` rather than claiming nine units that do not exist.

**325 objects in 22 batches**, one batch per Guelph Area, one changeset each,
same method as edits 2 and 3, from `skfd imports` with `mechanical=yes`. 146
objects that were already correct are skipped rather than uploaded as no-ops.
Batch 1 is the pilot — Hanlon Creek, 26 objects — and I will post its count
and changeset number here before the rest moves.

**On timing, plainly.** These upload this weekend, and I am not running a
14-day window, the same as the last two times. Both halves are tagging changes
on a well-defined set, nothing is deleted and no geometry moves, and every
edited object is recorded with the version it was prepared against and its
prior value, so a revert is mechanical. I would rather say that outright than
let an announcement pass for a consultation. **If you object, the batches get
reverted on request — no argument first.** @ARandomThumbtack, your standing
veto is unaffected.

Detail and the counts:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Mechanical_edits>

---

*The closing link only resolves once the wiki page carries sections 4 and 5.
They are written in `IMPORT_PROPOSAL.mediawiki`; drop the link from the paste
if the page has not been republished yet.*
