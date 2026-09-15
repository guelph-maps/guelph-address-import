# guelph-address-import

The **Guelph city checkout** of the address-import family — city #3,
scaffolded 2026-08-15. Status: **wiki page live, feedback window closed with
both mechanical edits consented, nothing uploaded yet** — the unit split is
prepared and waiting for an operator in
[`mechanical-edits/unit-split/`](mechanical-edits/unit-split/README.md).
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
   **Both mechanical edits are therefore consented.**

Two **mechanical edits** ride along with the proposal, announced with it but
consented separately under the Automated Edits code of conduct:

- **Remove `addr:province=Ontario`** (~3,699 objects). Canadian convention omits
  province; Toronto's import doesn't write it. Not written on new nodes either.
- **Split double-encoded unit housenumbers** (5,422 objects):
  `addr:housenumber=714-30` + `addr:unit=30` → `addr:housenumber=714`, unit
  untouched. The original importer defended the combined form, so the wiki page
  records the argument and the 2026-08-21 Nominatim evidence rather than just
  the conclusion. Rationale in full at
  `~/Code/obsidian/skfd/OSM Research/Guelph Unit Addresses (tagging convention).md`.

Neither is on the import path, and the import does not wait on them.

**Blockers before the pilot upload** (not before publishing — the wiki page
states intent):

- The engine writes `addr:housenumber`, `addr:street`, `addr:source` and the
  enriched `addr:postcode`, and no `source:license` on the changeset. Still
  missing for Guelph: the constant `addr:city=Guelph`, and the changeset
  `source:license`. (Dropping `addr:province` removed one of the two constants
  this used to need; `addr:source` and `created_by=address-importer-friend`
  landed in the engine 2026-08-27.)
- The engine has **no tag-modification path at all** — it creates nodes. Both
  mechanical edits need one, with per-object version checking and prior-value
  capture. Or run them from JOSM, neighbourhood by neighbourhood, as the 2025
  import did — which is the route taken for the unit split:
  `mechanical-edits/unit-split/` prepares 36 JOSM-ready batches over 5,521
  objects, each carrying the live version it was built against, with the
  prior values in `manifest.csv`. The `addr:province` campaign has no
  equivalent yet.

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
at snapshot 39, 2026-08-13). 24.4% of rows carry units, collapsed to civic per
the `[units]` policy. Tiles subdivide the city's 23 "Guelph Areas" polygons
(99.47% point coverage, probed 2026-08-15).

Entry state re-confirmed 2026-08-15 by `scripts/entry_state_probe.py`
(evidence: `onboarding/entry-state-2026-08-15.json`): the importer holds 85.6%
of sampled elements, 2026 activity is 49 elements and the latest 100
changesets carry no import tags — complete and quiet, not active. The probe's
tag-convention note said to stay consistent with `addr:province=Ontario`
(3,699 vs 178 `ON`); that was **superseded 2026-08-27** — province is now
dropped and the existing tags stripped, see the mechanical edits above.
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
