# Addendum for post #21 — paste-ready

Post #21 (2026-09-18) ends *"Will update this post when it's done"*, so it is
editable. What follows is what the condensed post dropped, written to be
appended to it rather than posted separately.

#21 was edited four minutes after it went up — inside Discourse's grace
window, so no revision shows — to add *"removing addr:province from anything
that has it – 44,796 instances"*. So it announces three campaigns, not two,
and this addendum covers all three.

**Two paragraphs matter more than the rest.**

- **The timing paragraph** is the consent. Proceeding without a 14-day window
  is a defensible call, but only when it is stated, and #21 does not say when
  anything lands, that no window is being run, or that it will be reverted on
  request.
- **The province paragraph** admits that #14's ~3,699 was wrong. #21 states
  the true figure without saying it differs from the one consent was asked
  for, so a reader comparing the two posts gets no explanation from the
  thread. The wiki records the error; the thread does not yet.

---

**On `addr:province`, and a number I got wrong.** In #14 I asked to remove
`addr:province` from "the ~3,699 Guelph objects that carry it". That was a
sample count I quoted as if it were city-wide: a survey read 4,244 Guelph
elements and found the tag on 3,878 of them, and I published that sample's
split as a census. The real figure is the 44,796 above — very nearly every
address object in the city. The edit and its reasons haven't changed: Canadian
convention omits the province, the Toronto import doesn't write it, and the
enclosing boundary already implies it. Its size was misstated, and the wiki
page records that rather than quietly overwriting it. 44,763 objects go up in
105 batches; 33 are held back for hand review (29 with no housenumber at all,
4 relations). The 607 `ON` and 1 `On` go in separate batches at the very end,
so they can still be held back if anyone would rather I stuck to the letter of
#14.

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

**Order, and batches.** Flats and interpolation go first: 325 objects in 22
batches, one per Guelph Area. Province follows, rebuilt against live OSM once
those are in — every one of the 325 also carries `addr:province`, so the
second campaign has to be prepared against the versions the first one leaves
behind. Each batch is its own changeset and its own revert, from
`skfd imports` with `mechanical=yes`. Each campaign's first batch is a pilot,
and I will post its count and changeset number here before the rest of that
campaign moves.

**On timing, plainly.** I am not running a 14-day window for any of the
three, the same as for campaign 3. All three are tagging changes on a
well-defined set, nothing is deleted and no geometry moves, and every edited
object is recorded with the version it was prepared against and its prior
value, so a revert is mechanical. I would rather say that outright than let an
announcement pass for a consultation. **If you object, the batches get
reverted on request — no argument first.** @ARandomThumbtack, your standing
veto is unaffected.

Detail and the counts:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Mechanical_edits>
