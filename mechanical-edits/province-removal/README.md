# Campaign 1 — remove `addr:province`

Consented 2026-09-10 on [thread #135103][thread]. Built 2026-09-17.

## The scope is twelve times what we told the community

**Do not upload this campaign on the existing consent.** Re-measured against
live Overpass on 2026-09-17:

| Value | Objects |
|---|---|
| `Ontario` | 44,307 |
| `ON` | 637 |
| `On` | 1 |
| **total** | **44,945** |

An independent `out count;` query the same afternoon returned 44,796 for
`nwr["addr:province"]` inside the city relation — the two disagree by ~150
because one is a cached extract and the other is live, and the number drifts
daily. Either way the order of magnitude is settled: **~44,800**, against
47,050 objects in Guelph carrying `addr:housenumber`. Effectively every
address object in the city has this tag.

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
* **Batch count.** At campaign 3's 250-per-batch this is ~180 changesets. The
  builder uses **600**, giving ~75 — still a lot, and the run sheet is
  explicit that this is a multi-evening job, not a sitting.
* **The `ON` variants are a separate ask.** The wiki §1 says they are removed
  on the same pass; the forum post names only `Ontario`. They are built into
  their own batches at the end of the run, so the operator can upload the
  `Ontario` ones and hold the 638 `ON`/`On` ones if the thread prefers.

### What it does not change

The edit itself is unchanged and still right: Canadian convention omits the
province, the Toronto import does not write it, and the value is fully implied
by the enclosing admin boundary. Only the count was wrong.

## What the builder does

Remove `addr:province`. Change nothing else. An object whose only tag change
would be a no-op is dropped rather than uploaded.

Routed to `review.csv` rather than batched:

| Reason | What it is |
|---|---|
| `relation` | Relations are never batched — `_common.batchable()` refuses them, because this tooling fetches neither their members nor a position for them. |
| `no-address` | Carries `addr:province` but no `addr:housenumber` — a boundary, a `place=*` node, something that is not an address. Worth a human's eye before stripping. |

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
