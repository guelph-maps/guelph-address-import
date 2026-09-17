# Campaign 1 — remove `addr:province`

Consented 2026-09-10 on [thread #135103][thread]. Built 2026-09-17.

## The scope is twelve times what we told the community

**Do not upload this campaign on the existing consent.** Re-measured against
live Overpass on 2026-09-17:

| Value | Objects |
|---|---|
| `Ontario` | 44,155 |
| `ON` | 607 |
| `On` | 1 |
| refused, see below | 33 |
| **total carrying the key** | **44,796** |

That agrees to the object with an independent `out count;` query against the
city relation the same afternoon. It is measured against 47,050 objects in
Guelph carrying `addr:housenumber` — so **effectively every address object in
the city has this tag**.

A first pass reported 44,945 and was wrong by 149. The fetch ends
`out meta; >; out meta;`, and the `>;` recursion re-emits any node that both
carries `addr:province` *and* is a child of a matched way — so 149 objects
appear twice in the XML and a naive count counts them twice. Exactly 149
objects are emitted more than once, and every one carries the key. The
builder indexes by `(type, id)`, so it never saw the duplicates; only the
tally did.

The proposal and the forum post both say **~3,699**. That figure is a
**sample count published as a census**. `onboarding/entry-state-2026-08-15.json`
probed 4,244 elements and found `addr:province` on 3,878 of them; the
3,699/178 split is that sample's `Ontario`/`ON` breakdown. Nothing was
measured city-wide, and the sample was never labelled as one in the write-up
that quoted it.

### What that changes

* **Consent.** Post #14 told the community this was "~3,699 Guelph objects".
  The real edit is the largest mechanical edit in the project by a factor of
  eight over campaign 2's 5,521 — and it touches 95% of Guelph's address
  objects. That is a different proposition from what the 14-day window closed
  over, and it needs a correction on the thread before a single batch goes up.
  The correction is owed regardless of whether anyone objects: the number was
  wrong in public.
* **Batch count.** The builder defaults to 600 per batch, giving **105
  changesets** — a multi-evening job, not a sitting. `--per-batch 2000` gives
  ~30, which is closer to what post #14 literally promised ("neighbourhood by
  neighbourhood") but far coarser to revert. Campaigns 2 and 3 both split
  large areas, so splitting is already the established reading of that
  promise; the question is only how fine.
* **The `ON` variants are a separate ask.** The wiki §1 says they are removed
  on the same pass; the forum post names only `Ontario`. They are built into
  their own batches at the end of the run, so the operator can upload the
  `Ontario` ones and hold the 608 `ON`/`On` ones if the thread prefers.

### What it does not change

The edit itself is unchanged and still right: Canadian convention omits the
province, the Toronto import does not write it, and the value is fully implied
by the enclosing admin boundary. Only the count was wrong.

## What the builder does

Remove `addr:province`. Change nothing else. An object whose only tag change
would be a no-op is dropped rather than uploaded.

**Built 2026-09-17: 44,763 objects in 105 batches, 33 refused.**

Routed to `review.csv` rather than batched:

| Reason | Count | What it is |
|---|---|---|
| `no-address` | 29 | Carries `addr:province` but no `addr:housenumber` — a boundary, a `place=*` node, something that is not an address. Worth a human's eye before stripping. |
| `relation` | 4 | Relations are never batched — `_common.batchable()` refuses them, because this tooling fetches neither their members nor a position for them. |
| `outside-city` | 0 | Anything the fetch dragged in from over the boundary. **It found nothing**, which is the useful part: Guelph abuts Guelph/Eramosa and the `>;` recursion does cross ways, so the guard was written expecting spill. There is none. It stays as a cheap invariant that will speak up if a later refetch behaves differently. |

## A bug this campaign found in the shared builder

`write_batch` used to put a way's child nodes into the batch straight from the
fetch index. Those `Element` objects are **shared**: `selected` and
`by_node_id` hand back the same object for a node that is both a campaign item
and some way's child. So once one batch transformed that node and stamped
`action="modify"` on it, every later batch carrying that way inherited the
edit *and* the action — and would have uploaded the same change again, in a
second changeset, against a version the first upload had already bumped.

Campaign 1 had **58** of them. The manifest looked perfect throughout: 44,763
rows, 44,763 distinct objects, no ghosts. The damage was only visible in the
batch `.osm` files, which is where it was found.

Fixed in `_common.py` — child nodes are now written as inert geometry stubs
(`id`, `version`, `lat`, `lon`; no tags, no action), and a child that is also
an item in the same batch still goes in whole. After the fix: 0 objects marked
modify in more than one batch, and no way left with a dangling node reference.

**Campaigns 2 and 3 were audited against their batch files on disk and are
clean** — 5,521 and 447 modify-marked objects, none in more than one batch.
Nothing uploaded in September needs revisiting. The bug needed a campaign
where the edited objects are themselves way children, and only this one is:
almost every address object in Guelph carries `addr:province`, including the
entrance nodes sitting inside building outlines.

## Files

    live.osm            the cached Overpass fetch (gitignored — 68 MB)
    batches/NN-area.osm one JOSM-ready layer per batch
    manifest.csv        the revert record: prior value and version per object
    review.csv          what the rules refused
    index.html          the run sheet

    python build_batches.py              # uses the cached fetch
    python build_batches.py --refetch    # pull OSM again first

Rebuild with `--refetch` on the day of upload: versions prepared today will
have moved.

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
