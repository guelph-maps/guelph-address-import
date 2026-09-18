# Mechanical edits 4 + 5 — notice draft for thread #135103

**Not posted.** Nothing in `batches/` may be uploaded until it is.

**Post after the wiki page is republished** with sections 4 and 5 under
§ Mechanical edits, so the link at the end resolves.

**This is an announcement, not a consultation**, the same as campaign 3 and
the units reversal — decided 2026-09-16, reasoning in
`IMPORT_PROPOSAL.mediawiki` § Status. The post says so in the maintainer's own
words rather than pretending to a window that is not being run. Do not soften
that, and do not add a deadline; there isn't one.

**The hard number to lead with is 81, not 635.** "Removing
`addr:interpolation` from Guelph" reads as a city-wide sweep of a key that is
mostly tagged correctly. It is 81 objects out of 635, and the post has to say
which 554 are being left alone before anyone has to ask.

---

**Two small mechanical edits on the same apartment buildings — dropping
`addr:interpolation` where it cannot mean anything, and tidying
`addr:flats`.** Announcing these together because they land on the same
objects: 74 of the 81 in the first are also in the second, and
running them as two campaigns would mean two changesets, two reverts and two
posts for what is one cleanup.

**First: 81 objects lose `addr:interpolation`, and 554 keep it.** The tag
describes a way drawn between two address nodes — the numbers run from the
housenumber at one end to the one at the other. Guelph has 635 objects
carrying it. 405 are two-node ways, which is exactly what the tag is for, and
they are correctly tagged; 149 are open ways with three or more nodes, which
are legal and want a different question asked of them (do both ends carry
`addr:housenumber`?) that I am not asking here. **Neither group is touched.**
What is left is 78 closed ways and 3 nodes — a building outline has no two
ends, and its corners are geometry that will never carry housenumbers, and a
single node has nothing to interpolate between at all. Those 81 lose the key
and nothing else. This is also what JOSM has been reporting as *"End node
without housenumber in address interpolation"* on those buildings; the warning
is not mine, it is pre-existing, and it is what turned this up.

Worth saying what these 81 are, because it is the same mistake campaign 3 just
fixed under a different key: whoever tagged a building `addr:interpolation=all`
was reaching for *"this building contains a range of addresses"*. That is what
`addr:flats` means and what `addr:interpolation` does not, and 74 of the 81 —
71 of the buildings and all 3 of the nodes — already got `addr:flats` last
week.

**Second: 292 `addr:flats` values get re-rendered, and none of them changes
which units it names.** Campaign 3 moved 447 unit lists from `addr:unit` to
`addr:flats` **verbatim**, on purpose — that promise is what made it trivially
reversible. This is the tidy-up afterwards. Guelph now has 464 objects with
`addr:flats`, and 292 of them are untidy in at least one of four ways:

```
1;10;11;12;13;14;15;2;3;4;5;6;7;8;9   ->  1-15           (803 Gordon Street)
101-113;201-214;301-314;401-414;      ->  no trailing ;
201-209; 301-309; 401-409;            ->  no spaces      (55 Yarmouth Street)
1001-1008;1101-1108;101-106;…         ->  floors in numeric order, not text order
```

The last one is the ugliest in the wild — 358 Waterloo Avenue puts the
eleventh floor above the first, because `1` sorts before `2` as a character.

The rendering is not mine to invent: it is `compress_flats` in the import's
own code, which every collapsed building it uploads already goes through. The
only new code is a parser to read the existing value back. Which is where the
risk is, so:

**Every value is gated on a round trip, and 464 of 464 pass.** Parse the
value, render it, parse the rendering, and demand the set of units be
identical. If normalising ever changed which units a building claims, that
would be data loss dressed up as tidying, and it is the one thing here that
could actually hurt. Anything failing the gate is left alone and goes to a
by-hand list; that list is currently empty. The cases the parser is careful
about, each with a test: `101A` is one unit and never joins a range;
`D101-D112;D201-D212` are two building-D runs and never merge across letters;
`LL01` is a real lower-level floor and keeps its zero — that one needed a fix
in the import itself; and 176 Janefield Avenue is a row of blocks numbered in
steps of two, so `224;234` stays `224;234` rather than becoming `224-234` and
claiming nine units that do not exist.

**325 objects in 22 batches**, one batch per Guelph Area, one changeset each,
same method as edits 2 and 3, uploaded from `skfd imports` with
`mechanical=yes`. 146 objects that were already correct are skipped rather
than uploaded as no-ops. Batch 1 is the pilot — I will post its count and
changeset number here before the rest moves.

**On timing, plainly.** I am not running a 14-day window, same as last time.
Both halves are tagging changes on a well-defined set, nothing is deleted and
no geometry moves, and every edited object is recorded with the version it was
prepared against and its prior value, so a revert is mechanical. I would
rather say that outright than dress an announcement up as a consultation. **If
you object, the batches get reverted on request — no argument first.**
@ARandomThumbtack, your standing veto is unaffected.

Detail and the counts:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Mechanical_edits>
