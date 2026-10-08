# guelph-address-import

The **Guelph city checkout** of the address-import family — city #3,
scaffolded 2026-08-15. Status: **the first gap-fill pass is uploaded** —
4,367 address nodes in 131 changesets, 2026-10-03 to 2026-10-07 — and
every mechanical edit that was going to run before it has run. What follows
is the monthly re-run, plus the cleanups held until the import was done. See
[`mechanical-edits/TODO.md`](mechanical-edits/TODO.md) for the edit ledger.
`ARandomThumbtack_Import` imported Guelph's addresses solo in 2025 (first
changeset 2025-09-16, declared complete 2025-10-23 on the
[wiki page](https://wiki.openstreetmap.org/wiki/Guelph/Address_Import)),
leaving only ~2,523 of 40,634 civic addresses missing (6.2%, diffuse — 2026-08-10
survey). What is proposed here is **continuous gap-fill and QA over that
finished import**, not a re-import: create-only, human-reviewed per batch,
re-run when the City publishes.

Part of the [guelph-maps](https://github.com/guelph-maps) organisation, which
indexes every Guelph project. Addresses were one of the City open-data layers
tiered for OSM import by
[`guelph-osm-import-audit`](https://github.com/guelph-maps/guelph-osm-import-audit)
(private).

**Prior importer contacted — go-ahead given.** `ARandomThumbtack` was asked
directly and is content for this project to take on continuous upkeep. (The
draft message that was written for this, `CONTACT_PRIOR_IMPORTER.md`, was
superseded by that conversation and removed; it is in git history at `0c268bb`.)

Guelph is **not a cold start**, and neither is the forum. Two things the
scaffold docs predate:

- The import's own forum thread is
  [#135103](https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103),
  tagged `import` / `import-proposal`, and we are already in it — posts #11 and
  #13 (2026-08-20/21). Announcements go **there**, not in a new topic.
- We have already edited Guelph addresses: changesets 187773424, 187776928,
  187822533 fixed all 29 `addr:unit`-only objects (2026-08-21/22).

Publication state:

1. ✅ `IMPORT_PROPOSAL.mediawiki` — **published 2026-08-27** as
   [`Guelph/Address_Import/Continuous`](https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous),
   a subpage of the 2025 import because this continues it. Deliberately short:
   defers to `Guelph/Address_Import` for the import itself and to
   `Toronto/Import/AddressPoints` for the shared machinery. **This file stays
   the source of truth** — edit here and re-publish rather than letting the
   wiki and the repo diverge. Their page is theirs: link, never edit.
2. ✅ `config.toml` `[export] import_plan` set to that live URL. The engine
   refuses to open a changeset while it is empty, so this gated every upload.
3. ✅ `WIKI_CATALOGUE_ENTRY.mediawiki` — **published**; both rows are live in
   `Import/Catalogue` § Ongoing Imports, Semi-Automated (checked against the
   raw wikitext 2026-09-15). Guelph's row still read status `Planned` on
   2026-10-07, after the first pass had uploaded. It wants `In progress`, and
   stays there: the import is continuous, so it is never marked complete.
4. ✅ `FORUM_ANNOUNCEMENT.md` — **posted 2026-08-28** as post #14 on thread
   #135103, `addr:full` withdrawal included. The 14-day objection window ran to
   2026-09-10 and closed with no objections; ARandomThumbtack replied
   supportively in #15, and #16 (2026-09-01) followed up on the open questions.
   The unit split is consented. **The province edit was not covered by it** —
   #14 asked for it at ~3,699 objects and it is 44,796. Its true scale reached
   the thread in #21 on 2026-09-18 (item 7), without a fresh window.
5. ✅ `FINDINGS_POST.md` — **posted 2026-09-16** as post #18, in condensed
   form, the night before the province count was re-measured. It therefore
   carries neither the correction nor the notices campaigns 4 and 5 need.
6. ➖ `PROVINCE_CORRECTION_POST.md` — **superseded, never posted.** #21 was
   edited inside Discourse's five-minute grace window (2026-09-18 21:20Z, so
   no revision shows) to announce removing `addr:province` from all 44,796 —
   the corrected figure, stated as a go-ahead rather than asked as a question,
   so the draft's question about a fresh window is moot. Still owed: its
   admission that #14's ~3,699 was a sample published as a census. That
   paragraph now lives in
   [`POST21_ADDENDUM.md`](mechanical-edits/flats-hygiene/POST21_ADDENDUM.md),
   for #21's promised update.
7. ✅ `mechanical-edits/flats-hygiene/ANNOUNCEMENT.md` — **posted 2026-09-18**
   as post #21, in condensed form, like #18 before it. What went up: the two
   campaigns named together — plus campaign 1 at 44,796, edited in four
   minutes later — the 74-of-81 overlap, and the four `addr:flats`
   defects with their examples. What did **not**: the 81-of-635 figure and the
   554 left alone — which the draft called the hard number to lead with — the
   round-trip gate, the 325-objects-in-22-batches plan with its pilot, and the
   plain no-window-plus-revert-on-request paragraph carrying
   ARandomThumbtack's standing veto. The post closes "Will update this post
   when it's done", so those four can still be added there rather than in a
   second post.

**The original importer is reading and wants to be told.** In #19 (2026-09-17)
ARandomThumbtack asked: *"when making such a change like the Unit-level
addresses, I would love it if you could post that change into this forum
post."* That closes the cadence question from #15/#16 — announce here, do not
go quiet. They also gave `per-door-or-collapse` explicit assent, quoting the
wiki's reasoning back, and weighed in on the parked `44B` idea (see
[`IDEAS.md`](IDEAS.md)).

**Five mechanical edits** ride along with the proposal, each announced
separately under the Automated Edits code of conduct. 2 went through a
14-day window, and 1 through the same one at a twelfth of its real size; 1's
true scale, and 3, 4 and 5, were announced on short notice instead, with the
standing offer to revert on request:

1. **Remove `addr:province`** — ✅ **done 2026-09-30**, 44,763 objects in
   25 changesets, one per area. **The consented count was wrong by 12×**:
   the thread was told ~3,699, the real figure is 44,796 (44,155 `Ontario`,
   607 `ON`, 1 `On`) — very nearly every address object in the city. 3,699 was
   a sample count published as a census. The edit is unchanged and still
   right; its size was misstated. Its true scale was announced in #21 on
   2026-09-18 without a fresh window. Rebuilt 2026-09-29 (155 versions had
   moved); uploads **after** campaigns 4 and 5, which share all 325 of their
   objects with it. See
   [`mechanical-edits/province-removal/README.md`](mechanical-edits/province-removal/README.md).
2. **Split double-encoded unit housenumbers** — ✅ **done 2026-09-16**, 5,521
   objects in 36 changesets. `addr:housenumber=714-30` + `addr:unit=30` →
   `addr:housenumber=714`, unit untouched. The original importer defended the
   combined form, so the wiki page records the argument and the 2026-08-21
   Nominatim evidence rather than just the conclusion. Rationale in full at
   `~/Code/obsidian/skfd/OSM Research/Guelph Unit Addresses (tagging convention).md`.
3. **Move unit lists to `addr:flats`** — ✅ **done 2026-09-17**, 447 objects in
   23 changesets. Announced on short notice rather than through a fresh
   14-day window; the wiki page records that choice and the standing offer to
   revert on request.

4. **Remove meaningless `addr:interpolation`** — ✅ **done 2026-09-30**,
   81 objects, sharing campaign 5's changesets. Announced 2026-09-18 as post
   #21. Withdraws a non-goal the wiki published on 2026-08-27; the page
   strikes it rather than deleting it.
5. **Normalise `addr:flats` formatting** — ✅ **done 2026-09-30**, 292 of 464
   values re-rendered through the engine's own `compress_flats`, every one
   gated on a round trip. Announced 2026-09-18 as post #21. The full
   before→after list is
   [`mechanical-edits/flats-hygiene/FLATS_NORMALISATION_LIST.md`](mechanical-edits/flats-hygiene/FLATS_NORMALISATION_LIST.md).
   Its batches were cut just before the engine stopped writing a pair as a
   range, so 126 values went up as `1-2`. A follow-up spelled them out as
   `1;2` (done 2026-10-03, 14 changesets):
   [`mechanical-edits/flats-pairs/`](mechanical-edits/flats-pairs/).

Plus 32 stragglers the rules first refused and the City's roster later
settled. None of the five is on the import path, and the import does not wait
on them — but the split had to run **before** conflation, or door candidates
would have duplicated against the badly-encoded objects.

**The first gap-fill pass uploaded 2026-10-03 to 2026-10-07** (local
time): **4,367 address nodes in 131 changesets, 189912383–190173922**, one
run per tile. Before it, every group of unit addresses got a shape at
`/units/shapes`: 414 groups, 12 judged automatically from OSM building
outlines. Then all runs were deleted and rebuilt from a fresh extract.

| | |
|---|---|
| Source points (snapshot 47) | 53,847 |
| Already in OSM, skipped | 42,408 |
| Rejected in review | 1,099 |
| **Uploaded** | **4,367** |
| — door nodes (`addr:unit`), across 143 addresses | 1,680 |
| — one node per building, units in `addr:flats` | 8 |
| — plain civic addresses | 2,679 |
| — carrying the City's postcode | 3,531 |

The wrap-up page, generated from `tool.db` by
`python -m t2.static_export --stats`, is
[`docs/stats/index.html`](docs/stats/index.html).

**One correction went up afterwards.** Conflation measured a park or school
from its centre, so five City points inside an addressed park or school
uploaded as new nodes. They were deleted on 2026-10-07 in changeset
190174014, and the engine now matches areas by their edges. See
[`mechanical-edits/area-duplicates/`](mechanical-edits/area-duplicates/).

**What comes next:**

- **The monthly re-run** when the City publishes. This is continuous upkeep:
  the wiki status stays `In progress` and is never marked complete.
- **The cleanups held until the import was done** (see the
  [ledger](mechanical-edits/TODO.md)): the 149 interpolation ways with 3 or
  more nodes; campaign 7, `addr:flats` naming another civic's units; the
  `addr:flats` listings the new door nodes have made redundant (what is left
  of edit 6); and the 5 Gordon Street stack collapse. Each one is announced
  on the thread before it uploads.
- **Still unbuilt:** the maintenance path for unit groups (a new unit at an
  address whose shape is already in OSM), and the footprint guard inside the
  unit rule itself. Verdicts cover both for now.

**[`mechanical-edits/TODO.md`](mechanical-edits/TODO.md) is the ledger** for
all five campaigns. The two found *while* running the others are now **built
as one batch set** in
[`mechanical-edits/flats-hygiene/`](mechanical-edits/flats-hygiene/) and
**announced 2026-09-18** (post #21) and **uploaded 2026-09-30** — 81 objects carrying `addr:interpolation` where it
cannot mean anything (against 405 legitimate ones that stay untouched, and 149
multi-node ones out of scope), plus a real `addr:flats` normaliser, re-measured
at 292 of 464 values untidy. 325 objects, 22 batches; 48 take both edits,
which is why they are one campaign rather than two. Every value is gated on a
round trip through the engine's own renderer, so a normalisation that changed
which units a building claims could not reach a batch.

**[`IDEAS.md`](IDEAS.md) is the other half of that ledger** — projection ideas
the data suggested and that are *not* being built, each with the numbers that
made it tempting and the numbers that stopped it. Two so far, both from asking
how `44B` should be mapped.

**The reference layer** for this source is
[`guelph-address-layer`](https://github.com/guelph-maps/guelph-address-layer) —
the same address points drawn as iD/JOSM overlays, live at
<https://guelph-maps.github.io/guelph-address-layer/>, rebuilt daily (set up
2026-09-29). Use it to check an address against the City's data without
leaving the editor.

The pipeline lives in the engine repo,
[`address-importer-friend`](https://github.com/skfd/address-importer-friend)
(see its README for setup). This repo carries only Guelph's `config.toml`,
credentials (`.env.*`, gitignored, from the `.example` files), and — locally,
gitignored — `data/` with the OSM extract and `data/guelph/tool.db`.

```bash
cd ../address-importer-friend
python run.py --city-dir ../guelph-address-import
```

Source data: City of Guelph address points, consumed via the sibling
[`ontario-address-changes`](https://github.com/skfd/ontario-address-changes)
tracker (`data/guelph/guelph.db`, 53,846 active rows / 40,634 civic addresses
at snapshot 39, 2026-08-13). 24.4% of rows carry units, uploaded by shape per
the `[units] policy = "per-door-or-collapse"`. Tiles subdivide the city's 23 "Guelph Areas" polygons
(99.47% point coverage, probed 2026-08-15).
The same 23 polygons become OSM boundary relations in
[`guelph-boundaries`](https://github.com/guelph-maps/guelph-boundaries).

Entry state re-confirmed 2026-08-15 by `scripts/entry_state_probe.py`
(evidence: `onboarding/entry-state-2026-08-15.json`): the importer holds 85.6%
of sampled elements, 2026 activity is 49 elements and the latest 100
changesets carry no import tags — complete and quiet, not active. The probe's
tag-convention note said to stay consistent with `addr:province=Ontario`
(3,699 vs 178 `ON`); that was **superseded 2026-08-27** — province is now
dropped and the existing tags stripped, see the mechanical edits above. Those
two figures are the probe's own 4,244-element sample, and quoting them as
city-wide counts is the error corrected on 2026-09-17.
Postcode on the dominant combo still holds, as does the observation that 725
sampled elements already carry `addr:unit`.
The probe was a one-off reading; [`guelph-beholder`](https://github.com/guelph-maps/guelph-beholder)
keeps taking it, auditing how completely Guelph's address points are
represented in OSM over time.

Baseline conflation runs in full regardless of entry state (house rule —
entering a brownfield city in maintenance-only mode inherits prior errors
invisibly). Expect the review queue to be MATCH/MATCH_FAR-dominated, the
opposite of Hamilton; the interesting outputs are street-name disagreements and
OSM-only addresses. (The scaffold called the unit situation a "~52% gap" —
13,162 source unit rows against 6,289 `addr:unit`. That reading is wrong: most
of those units *are* in OSM, double-encoded into the housenumber. See the
mechanical edits above.)

MIT licensed.
