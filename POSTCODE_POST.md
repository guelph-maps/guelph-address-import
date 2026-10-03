# Postcode change — draft, for thread #135103

**Draft. Not posted.** Reply in the existing thread, don't open a new topic:
<https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103>

Post after the wiki page's tagging-plan row for `addr:postcode` has been
re-published from `IMPORT_PROPOSAL.mediawiki`, so the link shows what the post
says. ARandomThumbtack asked in #19 to hear about changes like this on the
thread, so this is wanted, not just tolerated. Keep it short: what changes,
why, and what stays the same.

Scope, decided 2026-10-03: new nodes only. There is **no** mechanical edit
adding postcodes to existing objects. Those are left to guelph-beholder to
report, so the post asks for no consent to retag anything.

---

**New address nodes will carry the City's postcode**

Correcting something in my own plan. The tagging plan said `addr:postcode`
would be written only when a POI at the same address already had one. That
quietly broke from the 2025 import this one continues: that import wrote the
City's postcode, and most Guelph addresses in OSM carry one (3,773 of 4,244 I
sampled in August). Left alone, every new node would have been the odd one out.

So from the initial gap-fill on, new nodes get `addr:postcode` from the City's
`POSTCODE` field, as the 2025 import did:

- It is written only when it is a well-formed postal code starting with one of
  the six FSAs the City's own data uses: N1C, N1E, N1G, N1H, N1K and N1L. That
  covers 48,949 of 53,847 points.
- The 8 that fail are left off, not corrected. They include a Peterborough
  code on Colonial Drive, a Toronto one on Poppy Drive East, a Burlington one
  on Decorso Drive, and a bare `0`. I'm reporting them to the City.
- Where the City has no postcode, a postcode on a POI at the same address is
  still used, as before. Otherwise the node has none.

What does **not** change: I won't retag existing objects. If an address is
already in OSM with a different postcode, the import leaves it alone and flags
it for me to look at. Existing addresses with no postcode at all (about 700)
are listed by [guelph-beholder](https://github.com/guelph-maps/guelph-beholder),
not edited.

The `addr:postcode` row on the wiki page has the details:
<https://wiki.openstreetmap.org/wiki/Guelph/Address_Import/Continuous#Tagging_plan>
