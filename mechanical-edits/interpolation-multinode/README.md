# Interpolation lines with three or more nodes — the 149 campaign 4 left alone

```
addr:interpolation line, N to N         ->  deleted (with its bare middle nodes)   29, built
addr:interpolation line, every address  ->  deleted, if the thread agrees          62, not built
  between its ends already mapped
addr:interpolation line, no City        ->  deleted, if the thread agrees          48, not built
  address between its ends
line whose street the City spells       ->  hand cases                              8
  differently
line with one bare end                  ->  hand cases                              2
end nodes, all of them                  ->  not touched
```

> **Not uploaded.** Prepared 2026-10-07 against live OSM, after the import's
> last changeset. This is the first mechanical edit that **deletes** rather
> than retags, and what it deletes is other mappers' 2012–2016 work. The
> recommendation below was a 14-day question on [#135103][thread]; skfd decided
> on 2026-10-07 against posting it, so the tiers are skfd's call alone. The
> draft, short and long, is in git history at `5b2afeb`.

## Where this came from

Campaign 4 (`../flats-hygiene/`, done 2026-09-30) removed `addr:interpolation`
from 78 closed ways and 3 nodes, where it cannot mean anything. It left 554
open ways alone: 405 with two nodes, and **149 with three or more**, because
node count is the wrong test for an open way — an interpolation line may bend
through intermediate nodes. The test that matters is the one JOSM makes: do
both **end** nodes carry `addr:housenumber`, on the same street? This
directory asks that, and then a second question the import made answerable:
does the line still tell anyone something the map does not already say?

## The survey

[`survey.py`](survey.py) → [`survey.csv`](survey.csv), one row per line.
Two Overpass fetches (Guelph is admin_level 6), the City's points from
`config.toml`'s `sqlite_path` (snapshot 51, 53,850 rows), and `tool.db`'s 131
changesets to tell the import's own nodes apart.

**All 149 are still there**, unchanged in number since 2026-09-16: 0 gone, 0
new. The import created address nodes, never interpolation lines, so it could
not have added to them — but it could have added the addresses they stand for,
and it did.

### By the ends

| Ends | Lines | Verdict |
|---|---|---|
| Both numbered, same street, parity matches `even`/`odd` | **147** | **Valid** as interpolation. JOSM has nothing to say about them |
| One numbered, one bare | **2** | Broken — JOSM's *"End node without housenumber"* |
| Neither numbered | **0** | — |

No line has a numbered intermediate node, none is in a relation, and every
way carries exactly `addr:interpolation` and `source` — nothing else to lose.
`interpolation` is `even` on 77 and `odd` on 72; no `all`.

So the brief's "meaningless" class is **empty**, and "fixable" is two lines.
By the JOSM test, 147 of 149 are correct.

### By what they add

That is not the same as useful. A line's job is to stand in for the
addresses between its ends until they are mapped; the question is whether any
still need standing in for. For each valid line, every City address on its
street, in its parity, strictly between its end numbers, was looked up in OSM
by (street, housenumber):

| Tier | Lines | City addresses between the ends | Already mapped | …by our import |
|---|---|---|---|---|
| **same-number** — runs from N to N | **29** | 0 by construction | — | — |
| **covered** — every one already mapped | **62** | 261 | **261** | 44 |
| **empty** — the City has none between the ends | **48** | 0 | — | — |
| **unmatched-street** — the City has no street spelt that way | **8** | ? | — | — |
| adds an address the map lacks | **0** | | | |

**Not one of the 139 that can be checked supplies an address OSM does not
already have as a real object.** 44 of those 261 are there because the import put them there
this month; Burns Drive 37–83 odd spans 15, and 14 of them are ours.

The lookup is by (street, housenumber) anywhere in Guelph, not by position:
it asks whether the address exists in OSM, not whether it sits beside the
line. 75 of the 261 sit more than 60 m from their line, which is what a range
bound drawn along a road centreline looks like next to a point on a lot.

The 48 **empty** lines are worse than redundant. They can only generate
numbers that do not exist: Beaumont Crescent 63–83 odd, where the City has no
odd number below 109; Brant Avenue 20–24 even, where it has no 20, 22 or 24.
That is what the `source` tags say they are — **121 from NRCan CanVec, 28
from StatCan 92-500-X**, block-face address *ranges* from road-network files,
not addresses anyone lives at. A range bound is a number a block face could
hold.

That reaches the end nodes too. Of the 147, **76 have neither end number in
the City's data**, and 34 of those are empty lines: two address nodes and a
line between them, none of which the City knows. Every empty line's street
does exist in the City's data under that spelling; the gaps are in the
numbers, not the names.

### The eight on streets the City spells differently

Found by checking exactly that, and taken *out* of empty, because "the City
has no address between the ends" means nothing when the City has no street of
that name:

| Lines | As the end nodes spell it | The City has |
|---|---|---|
| 2 | Glenholme Drive (16–46 even, 15–27 odd) | Glenholm Drive, 11 points, 15–80 |
| 2 | Lowes Road (20–24 even, 21–25 odd) | Lowes Road East, Lowes Road West |
| 1 | Spencer Court (10–54 even) | Spencer Crescent |
| 1 | Watson Rang South (533–537 odd) | Watson Road South, up to 290 |
| 2 | Powerhouse Lane (26–168 even, 53–101 odd) | no such street |

All eight are StatCan 92-500-X. Their end nodes are address nodes with a
misspelt street, which is the more useful thing to fix; whether the line then
covers anything can be asked again afterwards. Hand cases, not batched.
(Poppy Lane 1–1 has the same problem — the City has Poppy Drive East and West
— but a 1-to-1 line says nothing whatever the street is called, so it stays
in same-number.) They are not touched here —
see [Not this edit](#not-this-edit).

### The two broken ones

| Way | Line | Bare end |
|---|---|---|
| [539311557](https://www.openstreetmap.org/way/539311557) | Dunlop Drive ?–80 even, 537 m | 18 m from 110 Dunlop Drive (node 1880280085) |
| [180286485](https://www.openstreetmap.org/way/180286485) | Hanlon Road 1806–? even, 236 m | 158 m from 1806 Hanlon Road — **our** import node 14257046637 |

Neither has a City address within 60 m of its line, so there is no number to
give the bare end that the data supports. Hand cases: whoever opens them
decides between numbering the end and deleting the line. Not batched.

## The edit

**Delete the line.** Stripping `addr:interpolation` would leave a way tagged
`source=NRCan-CanVec-10.0` and nothing else — an untagged-way warning in
place of an interpolation warning. So:

- the way is deleted;
- its intermediate nodes are deleted **only** if they are untagged, belong to
  no other way and sit in no relation (19 middle nodes across the 147 fail
  that and are kept);
- **both end nodes are kept, untouched.** They are address nodes, and whether
  each is a real address is a separate question.

### Built: same-number, 29 lines

[`batches/01-same-number.osm`](batches/) — **29 ways and 47 nodes deleted,
62 nodes written as untouched reference geometry**, one changeset:

```
Guelph addresses: delete addr:interpolation lines that run from a number to the same number - 29 lines (1/1)
```

A line from 306 to 306 interpolates nothing, whatever the City says — this is
the one tier whose case does not rest on the City roster. Downey Road has two
of them, a kilometre each; Imperial Road South has 30 to 30 twice. Each pair of
end nodes is the same address twice, which is a duplicate-node question for a
later pass and stays exactly as it is.

### Not built: covered (62) and empty (48)

```bash
C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe build_batches.py --tiers same-number,covered,empty
```

builds them as batches 2 and 3 — **62 ways + 138 nodes** and **48 ways + 87
nodes**, checked by the same gate. They are left out of the default because
both rest on one premise: **that the City's roster is the whole truth about
which addresses exist.** That is what the import has assumed throughout, and
the City is the addressing authority, but it is a premise a reader can reject
— a numbered house the City omitted would be geocoded by the line today and
by nothing tomorrow. The thread should be asked that question, plainly, before
these go.

## Recommendation

1. ~~Post a question with a 14-day window.~~ Decided 2026-10-07: no forum
   post. Steps 2 and 3 are skfd's choice instead of the thread's.
2. **All three tiers, 139 lines.** The survey says
   none of them carries an address the map lacks, and 48 of them invent ones.
   Rebuild with `--refetch --tiers same-number,covered,empty` on the day.
3. **Or same-number only** (29), if the City's list is not to be trusted as
   complete. The City letter now asks exactly that.
4. **The 2 broken lines and the 8 on misspelt streets** go to whoever opens
   them, by hand, from the personal account.

## The gate

`build_batches.py` reads its batches back and refuses the set — raises, not
warns — unless:

- every object marked `action="delete"` is in exactly one batch, and that set
  is `manifest.csv` exactly;
- nothing is marked `modify` or `create`;
- no deleted way carries a key beyond `addr:interpolation` and `source`, and
  each is at its live version;
- no deleted node is tagged, is an end of its line, belongs to any other way,
  or is a relation member.

Every element carries its live `version`, so a line someone has touched since
the fetch conflicts in JOSM rather than being deleted from under them.
`manifest.csv` is the revert record: each way with its version, tags and node
list, each node with its version and position — enough to recreate both.
`verify_changeset.py` learned deletions for this (8f7a773): the deleted set
must be the manifest's delete rows exactly, each at its prepared version plus
one, and a batch without delete rows still fails on any deletion.

## Running it

```bash
cd mechanical-edits/interpolation-multinode
PY=C:/Users/kk/Code/address-importer-friend/.venv/Scripts/python.exe

$PY survey.py                     # tallies from the cached fetches
$PY build_batches.py --refetch    # on the day: re-survey live OSM, rebuild
python ../verify_changeset.py . 1 # after the upload
```

`live_interp.osm`, `live_addr.osm` (30 MB) and `batches/` are derived and
gitignored. `survey.csv`, `survey_2node.csv` and `manifest.csv` are tracked.

## Not this edit

- **The 405 two-node lines give the same answer**, in
  [`survey_2node.csv`](survey_2node.csv): 396 valid, 9 with a bare end; 77
  same-number, 120 covered, 190 empty, 9 on unmatched streets, **0 adding an
  address** — 407 City
  addresses spanned, all mapped, 71 by the import. They are the same CanVec
  and StatCan ranges with fewer bends. Campaign 4 called them "real
  interpolation, correctly tagged", and by the JOSM test they are; by this
  test, they are as redundant as the 139. A follow-up, announced on its own.
- **End nodes the City does not know.** 76 of the 147 lines have both ends
  outside the City's data, 26 one end. Those are address nodes asserting a
  number the authority says does not exist — the reverse-beholder question
  (find OSM items the source lacks), not an interpolation question.
- **Same-number end pairs** are the same address on two nodes, 23 m to a
  kilometre apart. Duplicate-address cleanup, later.

## Checklist

- [x] Survey against live OSM, 2026-10-07
- [x] Batch 1 (same-number) built and gated; covered/empty buildable
- [ ] The 2 bare-ended lines and the 8 unmatched-street lines, by hand
- [x] ~~`ANNOUNCEMENT.md` posted to #135103~~ no post (decided 2026-10-07)
- [ ] Decide the tiers
- [ ] `build_batches.py --refetch --tiers …` on the day
- [ ] JOSM signed in as `skfd imports`
- [ ] Each batch uploaded, then `python ../verify_changeset.py . N`, which
      writes `uploads.csv`
- [ ] Wiki § Mechanical edits gains this section

[thread]: https://community.openstreetmap.org/t/import-addresses-from-city-of-guelph-data/135103
