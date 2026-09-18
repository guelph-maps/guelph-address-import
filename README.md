# guelph-address-import

The **Guelph city checkout** of the address-import family — city #3,
scaffolded 2026-08-15. Status: **two mechanical campaigns finished and
verified, the gap-fill import not yet run.** 5,968 objects re-tagged over
2026-09-16/17 in 59 changesets — see
[`mechanical-edits/TODO.md`](mechanical-edits/TODO.md) for the ledger.
`ARandomThumbtack_Import` imported Guelph's addresses solo in 2025 (first
changeset 2025-09-16, declared complete 2025-10-23 on the
[wiki page](https://wiki.openstreetmap.org/wiki/Guelph/Address_Import)),
leaving only ~2,523 of 40,634 civic addresses missing (6.2%, diffuse — 2026-08-10
survey). What is proposed here is **continuous gap-fill and QA over that
finished import**, not a re-import: create-only, human-reviewed per batch,
re-run when the City publishes.

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
   raw wikitext 2026-09-15). Guelph's row still reads status `Planned` and
   wants moving to `In progress` once the first batch uploads.
4. ✅ `FORUM_ANNOUNCEMENT.md` — **posted 2026-08-28** as post #14 on thread
   #135103, `addr:full` withdrawal included. The 14-day objection window ran to
   2026-09-10 and closed with no objections; ARandomThumbtack replied
   supportively in #15, and #16 (2026-09-01) followed up on the open questions.
   The unit split is consented. **The province edit is not** — #14 asked for it
   at ~3,699 objects and it is 44,796, so that consent does not cover what the
   campaign actually does. See `PROVINCE_CORRECTION_POST.md`.
5. ✅ `FINDINGS_POST.md` — **posted 2026-09-16** as post #18, in condensed
   form, the night before the province count was re-measured. It therefore
   carries neither the correction nor the notices campaigns 4 and 5 need.
6. ⬜ `PROVINCE_CORRECTION_POST.md` — **not posted.** Corrects #14's figure and
   asks whether the corrected scope wants a fresh window.
7. ⬜ `mechanical-edits/flats-hygiene/ANNOUNCEMENT.md` — **not posted.** The
   notice campaigns 4 and 5 upload behind.

**The original importer is reading and wants to be told.** In #19 (2026-09-17)
ARandomThumbtack asked: *"when making such a change like the Unit-level
addresses, I would love it if you could post that change into this forum
post."* That closes the cadence question from #15/#16 — announce here, do not
go quiet. They also gave `per-door-or-collapse` explicit assent, quoting the
wiki's reasoning back, and weighed in on the parked `44B` idea (see
[`IDEAS.md`](IDEAS.md)).

**Three mechanical edits** ride along with the proposal, each consented
separately under the Automated Edits code of conduct:

1. **Remove `addr:province`** — ✅ **built 2026-09-17**, 44,763 objects in
   105 batches, not yet uploaded. **The consented count was wrong by 12×**:
   the thread was told ~3,699, the real figure is 44,796 (44,155 `Ontario`,
   607 `ON`, 1 `On`) — very nearly every address object in the city. 3,699 was
   a sample count published as a census. The edit is unchanged and still
   right; its size was misstated, so it waits on a correction and the
   community's answer on whether a fresh window is wanted. See
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

Plus 32 stragglers the rules first refused and the City's roster later
settled. None of the three is on the import path, and the import does not wait
on them — but the split had to run **before** conflation, or door candidates
would have duplicated against the badly-encoded objects.

**Blockers before the pilot upload** (not before publishing — the wiki page
states intent):

- The engine writes `addr:housenumber`, `addr:street`, `addr:source` and the
  enriched `addr:postcode`, and no `source:license` on the changeset. Still
  missing for Guelph: the constant `addr:city=Guelph`, and the changeset
  `source:license`. (Dropping `addr:province` removed one of the two constants
  this used to need; `addr:source` and `created_by=address-importer-friend`
  landed in the engine 2026-08-27.)
- The engine still has **no tag-modification path** — it creates nodes. The
  route taken instead was JOSM, area by area, as the 2025 import did: each
  campaign directory under `mechanical-edits/` builds `.osm` batches carrying
  the live version of every object, so a stale one raises a conflict rather
  than overwriting someone, with prior values in `manifest.csv` and
  batch→changeset in `uploads.csv`. Campaign 1 has no equivalent yet.
- **A classifier bug, found 2026-09-17 and not yet fixed.** Three groups whose
  `addr:flats` listing overflows OSM's 255-character limit turn out to be
  complexes 100–200 m across, not buildings — 15 Carere Crescent is 32
  separate townhouse blocks. The collapse branch decides on unit numbering and
  never asks how far apart the units are. Fix the footprint guard before any
  unit-bearing import run, or those three collapse into a single node each.
  `config.toml` carries the measurements.

**[`mechanical-edits/TODO.md`](mechanical-edits/TODO.md) is the ledger** for
all five campaigns. The two found *while* running the others are now **built
as one batch set** in
[`mechanical-edits/flats-hygiene/`](mechanical-edits/flats-hygiene/) and
awaiting their notice — 81 objects carrying `addr:interpolation` where it
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

Baseline conflation runs in full regardless of entry state (house rule —
entering a brownfield city in maintenance-only mode inherits prior errors
invisibly). Expect the review queue to be MATCH/MATCH_FAR-dominated, the
opposite of Hamilton; the interesting outputs are street-name disagreements and
OSM-only addresses. (The scaffold called the unit situation a "~52% gap" —
13,162 source unit rows against 6,289 `addr:unit`. That reading is wrong: most
of those units *are* in OSM, double-encoded into the housenumber. See the
mechanical edits above.)

MIT licensed.
