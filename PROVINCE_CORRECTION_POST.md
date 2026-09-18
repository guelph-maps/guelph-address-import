# Province count correction — draft, for thread #135103

**Not posted.** Nothing in `mechanical-edits/province-removal/batches/` may be
uploaded until it is.

Post #18 (2026-09-16) went up the night *before* the province count was
re-measured, so it lists "Remove `addr:province=Ontario`" under *What is next*
with no figure at all. The wrong figure is still standing in **post #14**,
where consent was asked for it, and that is what this corrects.

Keep it short. It is an apology and a question, not an essay — the reasoning
lives on the wiki page, which is already corrected. Do not bury the number.

ARandomThumbtack asked in #19 for exactly this: *"when making such a change
like the Unit-level addresses, I would love it if you could post that change
into this forum post."* So the notice is wanted, not merely tolerated.

---

**Correcting a count in my own proposal: `addr:province` is on ~44,800 objects, not ~3,699.**

In post #14 I asked for consent to remove `addr:province=Ontario` from "the
~3,699 Guelph objects that carry it". That number is wrong by a factor of
twelve, and I would rather say so plainly than let it stand.

Re-measured against Overpass on 2026-09-17, inside the city boundary:

| Value | Objects |
|---|---|
| `Ontario` | 44,155 |
| `ON` | 607 |
| `On` | 1 |
| **total** | **44,796** |

For scale: 47,050 objects in Guelph carry `addr:housenumber`. So this is very
nearly **every address object in the city**, not a stray 8% of them.

**Where the wrong number came from.** A survey I ran when picking the project
up sampled 4,244 Guelph elements and found `addr:province` on 3,878 of them.
I quoted that sample's `Ontario`/`ON` split as though it were a city-wide
count. It never was, and nothing in my write-up said it was a sample. Two
independent queries now agree on 44,796.

**What does not change.** The edit itself, and the reasons for it: Canadian
convention omits the province, the Toronto import does not write it, and the
value is fully implied by the enclosing admin boundary. Removed, no
replacement. I still think that is right.

**What does change is the size of what I asked you to agree to** — so I am
**not** treating the 14-day window that closed on 2026-09-10 as consent for
this. The wiki page now carries the corrected figure and records the error
rather than quietly overwriting it.

**Where it stands.** The edit is built and ready to go but is not going
anywhere yet: 44,763 objects in 105 batches, one per neighbourhood with large
ones split, each batch its own changeset and its own revert, every object
recorded with the version it was prepared against and its prior value. 33
objects are held back for hand review — 29 carry `addr:province` with no
housenumber at all (boundaries and `place=*` nodes), and 4 are relations.
The 607 `ON` and 1 `On` are in separate batches at the end, so they can be
held back independently if anyone would rather I stuck to the letter of #14.

**So, the question:** the edit is unchanged and the count is now right. Does
that want **a fresh 14-day window**, or is **this correction plus a short
notice before the first batch** enough? I lean to the second, because nothing
about what the edit does has moved — but "95% of every address object in
Guelph" is a number that ought to make someone pause, and I would rather be
told to wait than assume I have been told to go.
