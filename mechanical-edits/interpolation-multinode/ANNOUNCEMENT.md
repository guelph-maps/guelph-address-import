# Interpolation lines — draft for thread #135103

**Not posted.** Written 2026-10-07 from `README.md` beside it.

**This one is a question with a window, not a notice.** Every earlier
mechanical edit retagged objects and ran without a 14-day window. This one
deletes ways other mappers drew in 2012–2016, and @ARandomThumbtack asked in
post #19 to be told about edits like it. Put a date in the last paragraph
when posting — 14 days out — and do not upload before it.

**Lead with 0, not 149.** The headline is that none of these lines supplies
an address the map does not already have; the count is secondary. And say
what is *not* deleted — the end nodes, the 405 two-node lines — before anyone
has to ask.

## Short version — the one to post (2026-10-07)

skfd asked for a short version. The long one stays below for reference.

---

**Old address interpolation lines: OK to delete the ones that add nothing?**

Guelph still has 149 address interpolation lines with three or more nodes.
Most came from CanVec in 2012 and StatCan in 2016: road-network address
*ranges*, drawn before the City's points were mapped. I checked each one
against the City's address list, and none of them adds an address OSM
doesn't already have:

- **29** run from a number to the same number (306 to 306 Downey Road), so
  they interpolate nothing.
- **62** span 261 City addresses, and all 261 are already mapped as real
  objects.
- **48** span no City address at all, so they can only invent numbers. For
  example, [Beaumont Crescent 63–83 odd](https://www.openstreetmap.org/way/177608148):
  the City's only odd number on that street is 109.

The plan is to delete the lines and their untagged middle nodes. The end
nodes stay. The 62 and the 48 are only redundant if the City's list is
complete, so if anyone doubts that, I'll delete just the 29. I'll wait until
**October 21** for objections. The 10 lines with a missing end or a
misspelt street I'll fix by hand.

Details per line: https://github.com/guelph-maps/guelph-address-import/tree/main/mechanical-edits/interpolation-multinode

---

## Long version

---

**Proposal: delete 139 address interpolation lines in Guelph that no longer
add any address — questions welcome before anything moves.**

When we removed `addr:interpolation` from building outlines last month (post
#21), I left 149 open interpolation ways with three or more nodes alone,
saying they needed a different check. Here it is.

**By JOSM's test they're fine.** 147 of the 149 have a numbered address node
at both ends, on the same street, with the right odd/even parity. Two have a
bare end and are genuinely broken; I'll leave those to be fixed by hand, along
with 8 whose end nodes misspell the street (Glenholme Drive, Watson Rang
South, Spencer Court for Spencer Crescent…).

**But none of the other 139 adds an address OSM doesn't already have.** For each
line I took every City address on that street, on that side, between its end
numbers, and looked it up in OSM:

- **29** run from a number to *the same* number — 306 to 306 Downey Road, a
  kilometre long. They interpolate nothing at all.
- **62** span 261 City addresses, and **all 261 are already mapped** as real
  nodes or buildings (44 of them added by the gap-fill this month).
- **48** span *no* City address. They can only produce numbers that don't
  exist: Beaumont Crescent 63–83 odd, where the City's only odd number is
  109; Brant Avenue 20–24 even, where there is no 20, 22 or 24.

Their `source` tags explain it: 121 come from NRCan CanVec and 28 from StatCan
92-500-X — block-face address *ranges* from road-network files, which were the
best Guelph had before the City's points were imported. They've done their
job.

**What I'd delete:** the line, plus any of its middle nodes that carry no tags
and belong to nothing else. **The end nodes stay exactly as they are** — they
are address nodes, and whether each is a real address is a separate question.
Every object goes up at its current version, so anything edited since my
survey conflicts in JOSM instead of being deleted, and the manifest keeps each
way's tags and node list so any of it can be put back.

**The one thing I'd like a view on:** the 62 and the 48 are only redundant if
the City's address list is taken as complete — a house the City left out
would lose the line that geocodes it today. The import has assumed the City is
authoritative throughout, but that's a judgement, not a fact. So:

- if nobody objects by **[DATE, 14 days out]**, I'll delete all 139, in three
  changesets (one per group above), from `skfd imports`;
- if anyone doubts the City's list, I'll delete only the 29 same-number lines,
  which don't depend on it, and leave the rest.

Not part of this: the 405 two-node interpolation lines, which turn out the
same way (0 of them add an address either) and would be a separate post, and
the end nodes whose numbers the City doesn't have at all, which deserve their
own look. Full numbers, per line:
https://github.com/guelph-maps/guelph-address-import/tree/main/mechanical-edits/interpolation-multinode
