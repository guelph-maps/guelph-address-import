# Campaign 5, pairs — `1-2` becomes `1;2`

**Built 2026-10-02, not uploaded.** 126 objects in 12 batches. Every one of
them was written by campaign 5.

Campaign 5 re-rendered `addr:flats` through the engine's `compress_flats`.
Its batches were built at 20:58 on 2026-09-29. At 21:51 the engine changed so
that a range needs three units (`address-importer-friend` 34a40061,
`MIN_RANGE_UNITS`), because `5-6` is no shorter than `5;6` and reads as a
span. The batches were not rebuilt before the 2026-09-30 upload, so the old
rendering went up on 126 objects. The import already writes the new form, so
this edit brings those 126 objects into line with it.

| Live | Becomes |
|---|---|
| `59-60` (190 Fife Road) | `59;60` |
| `101-102;201-202` | `101;102;201;202` |
| `1-2;4-5;7` | `1;2;4;5;7` |
| `101-102;101A;201-202` (511 Edinburgh Road South) | `101;101A;102;201;202`, which is its value from before campaign 5 |

Runs of three or more are not touched, and no value changes length. In Guelph
a bare `1-2` can also be read as the unit-civic housenumber that campaign 2
removed from 5,521 objects. `1;2` can't be.

## The gates

1. `flats_parse.normalise`, the same as campaign 5. It parses the value,
   renders it through the current engine, and refuses the value unless the
   unit set survives the round trip.
2. A gate of this edit's own: the rendering must hold exactly the parts of the
   live value with its two-unit ranges spelled out. The renderer may put them
   in any order, but nothing else may change. Any other change goes to
   `review.csv` as `not-only-pairs`, which stays empty tonight. That catches a
   value someone has edited since 2026-09-30, or an engine that has moved
   again. Neither of those is covered by this edit.
3. After the batches are written, the builder asserts that every manifest row
   changed, kept its length, and passes gate 2.

None of the 126 is in the unuploaded `stack-collapse` set (5 Gordon Street),
so the two batch sets can't conflict.

## Consent

Post #21 on [#135103][thread] announced re-rendering every `addr:flats` value
through the import's own renderer. This edit is that renderer as it stood 53
minutes after the batches were cut, so #21 arguably covers it. **skfd's call**
is whether a one-line note goes on the thread before JOSM opens. A draft is
below.

> Follow-up to #21: campaign 5's batches were built just before the renderer
> stopped writing two-unit runs as ranges, so 126 values went up as `1-2`
> where the import now writes `1;2`. Same units, same length. One small pass
> fixes them. The list is in `mechanical-edits/flats-pairs/manifest.csv`.

## Run

    C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --refetch

Then open `index.html`. Batch 1 (Parkwood Gardens, 36 objects) is the pilot.
Five of the 12 batches hold one or two objects each, because batches are
split by area, the same as every earlier campaign.

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103

## Upload log

- **Batch 1**, Parkwood Gardens: changeset 189908359, 36 objects, verified.
- **Batch 0**: changeset 189908363 holds 1 object, way 212559742 at 649
  Scottsdale Drive (`100-101` → `100;101`). Its comment says "Hanlon Creek
  (2/12)", but this object belongs to batch 5. The tags are correct and it
  verified clean. It went up under the wrong label because the first build
  (before the 511 Edinburgh gate fix) left `02-hanlon-creek.osm` beside the
  rebuild's `02-st-georges-parkway.osm`, and the upload loop picked the stale
  file. The object is filed as batch 0 in the manifest, and its file is kept
  as `00-hanlon-creek-uploaded-as-2.osm`. Batch 5 now holds only 511
  Edinburgh. Since then the builder clears old batch files, the loop refuses a
  batch number that matches two files, and the verifier skips changesets that
  are already recorded.
