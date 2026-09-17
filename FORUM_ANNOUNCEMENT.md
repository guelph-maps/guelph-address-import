# Forum announcement — posted 2026-08-28 as post #14

**This file is the record of what went up, not a draft any more.** It is kept
verbatim on purpose. Corrections go *after* it, or on the thread — editing the
text here would make the repo disagree with what the community actually read
and consented to.

> **Known wrong, found 2026-09-17.** Point 2 below says `addr:province=Ontario`
> is on "the ~3,699 Guelph objects that carry it". The real figure is **44,796**
> — 44,155 `Ontario`, 607 `ON`, one `On` — about twelve times what this post
> claimed, and very nearly every address object in Guelph. 3,699 was a sample
> count (4,244 elements probed) quoted as if it were a census. The 14-day
> window that closed on 2026-09-10 is therefore **not** being treated as
> consent for the corrected scope; the correction is carried in
> `FINDINGS_POST.md` and the campaign is held until the thread answers.

---

**Original posting notes, kept as written:**

**Reply in the existing thread. Do not open a new topic.**
<https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103>
(13 posts, tagged `import` / `import-proposal`; our posts are #11 and #13.)

Post once `Guelph/Address_Import/Continuous` is live so the link resolves. Check the
first line matches what ARandomThumbtack actually agreed to.

---

**Taking over ongoing maintenance of Guelph's addresses — announcement**

@ARandomThumbtack has given me the go-ahead to pick up ongoing upkeep of Guelph's addresses. Thanks to them for the 2025 import — it put Guelph among the two best-covered municipalities in Ontario — and for the handover.

Three things, all documented at **<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous>**:

**1. Continuous gap-fill.** 2,523 of 40,634 City addresses aren't in OSM (measured 2026-08-10) — the tail parked in `RemainingAddresses.osm`, plus everything published since, like the 51 addresses the City added on 2026-08-06. I track the City dataset with a differ; when it changes I re-conflate, hand-review the new candidates and upload one changeset per area. Create-only, every candidate approved by a human, `import=yes` / `bot=no`. Same tooling and same dedicated account as the [Toronto import](https://wiki.openstreetmap.org/wiki/Toronto/Import/AddressPoints) in May.

**2. Removing `addr:province=Ontario`** from the ~3,699 Guelph objects that carry it. Canadian convention omits province; the Toronto import doesn't write it.

**3. Normalising unit tagging.** 5,422 objects encode the unit twice — `addr:housenumber=714-30` *and* `addr:unit=30` — in an order that isn't even the Canada Post one. Splitting to `addr:housenumber=714` + `addr:unit=30`.

@ARandomThumbtack and I have gone back and forth on (3). For the record: I tested against live Nominatim on 2026-08-21, and unit-level search fails under *every* tagging scheme — "72 York Road Unit 5" returns the property with the unit ignored. So searchability doesn't argue for the combined form, while the combined form does break plain "714 Willow Road" queries, because then nothing carries the bare civic number.

**Also withdrawing the `addr:full` suggestion in my post above** — same test, Nominatim discards `addr:full` outright. It buys nothing. Ignore that part.

(2) and (3) are mechanical edits under the [Automated Edits code of conduct](https://wiki.openstreetmap.org/wiki/Automated_Edits_code_of_conduct): documented on the wiki page, run neighbourhood by neighbourhood in separately revertable batches, no other tags touched.

**Objections welcome for 14 days, to 2026-09-10.** Then a pilot tile posted here with its counts and changeset before anything else moves.

toronto@comentality.com · [address-importer-friend](https://github.com/skfd/address-importer-friend) · [guelph-address-import](https://github.com/guelph-maps/guelph-address-import)
