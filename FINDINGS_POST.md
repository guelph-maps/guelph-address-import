# Findings post — draft, for thread #135103

Post after the mechanical edits are done and before campaign 4 is proposed.
Bullets rather than prose: it is a list of things found, not an argument.

Numbers verified against the live API on 2026-09-17, not from our own records.

---

**Guelph unit tagging — both mechanical edits are done, and here is everything odd we hit**

The two unit campaigns are finished:

* **Splitting double-encoded housenumbers** — 5,521 objects, 36 changesets, one per area.
* **Moving unit lists to `addr:flats`** — 447 objects, 23 changesets.
* Plus 32 stragglers the rules first refused and the City's roster later settled.

Records for both — per-object prior values, versions, and which changeset each object went in — are in [the repo](https://github.com/guelph-maps/guelph-address-import/tree/main/mechanical-edits) as `manifest.csv` and `uploads.csv`.

Below is the honest list. I would rather publish the mistakes than have someone find them.

## Things I got wrong

* **The pilot went from my personal account.** [Changeset 189086416](https://www.openstreetmap.org/changeset/189086416) is `skfd`, not the `skfd imports` account the plan names. My mistake, disclosed above, and the other 35 came from the right account.
* **I retagged a cafe as its own landlord.** [Centurion Coffee](https://www.openstreetmap.org/node/13533404756) had `addr:unit=B3-1` and got `addr:flats=B3-1`. On a POI, `addr:unit` means *this business is in that unit* — identity, not containment — so the rewrite claimed a cafe contains a unit. Fixed by hand. I then swept every remaining batch and pulled four more shop and cafe nodes before they went up.
  * The discriminator turned out to be `building`, not the POI tag. A nursing home tagged `amenity=social_facility` **is** the structure and really does contain its units; a bare node with `shop=shoes` is a tenant of one.
* **A near miss on ordering.** My first classifier read `37-1` on Bond Court as a span "37 down to 1" rather than unit 1 of number 37 — plausible, because Bond Court really does have addresses at 1, 3 and 5. It quietly moved twelve townhouses into the leave-alone pile. Caught before upload, but only because the counts looked wrong.

## Things the data taught me

* **Corroboration beats cleverness.** Both campaigns refused an object whenever its own tags could not confirm the edit, which left 48 leftovers. Asking the City's address roster instead — a second witness the rules never consulted — settled **32 of them**, including twelve Bond Court ways tagged `37-1`…`37-12` with no `addr:unit` at all. The City lists exactly units 1–12 there.
* **`addr:interpolation` is being used to mean "this building contains a range".** 78 closed building outlines and 3 nodes carry it, where it cannot mean anything — a polygon has no two ends to interpolate between. It is the same thought that produced the unit lists, with a different wrong key. **405 genuine two-node interpolation ways in Guelph are correct and are not being touched.**
* **A tag-length limit turned out to be a misclassification detector.** Three buildings had unit listings too long for OSM's 255-character tag limit. Measuring them: [15 Carere Crescent](https://www.openstreetmap.org/#map=18/43.5820/-80.2550) is 66 units over 103 m × 114 m, 85 Mullin Drive is 110 over 186 m × 119 m, 176 Janefield Avenue is 76 over 205 m × 175 m. A tower is about 40 m square. These are *complexes*, not buildings — 15 Carere is 32 separate townhouse blocks — so the listing overflowed precisely because the group should never have been treated as one building. Raising the limit or truncating would have buried that.
* **`addr:flats` on a shopping mall.** [Melran Mall](https://www.openstreetmap.org/way/344325628) now says `addr:flats=100-140`. The key's definition is "the range of **unit** numbers", with flats as the example, and there is no alternative key — but 15 of the 447 are commercial, and **their counts should not be read as dwellings.** Told rather than hidden. The real answer is mapping storefronts individually, which is already happening in that building.
* **Roughly 38% of the values I moved are untidy** — enumerations that should be ranges, trailing semicolons, and sorting done as text so [358 Waterloo Avenue](https://www.openstreetmap.org/way/819734215) opens `1001-1008;1101-1108;101-106;…`, the eleventh floor above the first. I moved every value **verbatim** anyway, because "not re-compressed, not reconciled" is what makes the edit reversible. Tidying is a separate pass with its own notice.
* **Two campaigns, zero shared objects.** A hyphen in `addr:housenumber` is one door encoded twice; a semicolon list in `addr:unit` is a whole building on one object. Nothing was both, which is a neater split than I expected.

## Edge cases, for anyone who enjoys them

* `10-10` with `addr:unit=10` — prefix and suffix both the unit. Every reading collapses to the same civic number, but they got their own batch so a human saw them together.
* `130-BLD D` and `10-6/7` — the rule declined on a space and a slash, correctly, and a person did them.
* [One way on Regent Street](https://www.openstreetmap.org/way/929108639) carries eight distinct civic numbers: `32;34;36;38;40;42;44;44-B;46;`. No rule splits one way into eight addresses.
* Two cases where OSM and the City disagree that an address exists at all — `32-34 Palermo Crescent` (the City has 34, no 32) and `299-301 York Road` (299, no 301).
* 252 Stone Road West is a mall whose 140 "units" are storefronts. Whether a storefront is a front door is a judgement no rule should make quietly, so it was not made quietly.

## What is next

* **Remove `addr:province=Ontario`** — ~3,699 objects, consented back in the first window, not yet run.
* **Remove the meaningless `addr:interpolation`** — the 81 above, leaving the 405 real ones alone. Needs its own notice before anything moves; this post is not it.
* **Normalise `addr:flats` formatting** — the ~38%, using the same renderer the import writes through so Guelph ends up with one answer rather than two.
* **Fix the complex-versus-building rule** before any unit-level import, so 15 Carere and its two siblings are not collapsed into a single node.
* **The remaining twelve by hand** — mostly single ways carrying several civic numbers, which want door positions rather than a tagging rule. A MapRoulette challenge is still the plan, and still an open question.
* **Then the gap-fill import itself**, which is what all of this was clearing the way for.

Objections, corrections and "you have misread this" all welcome, as ever.
