# `addr:flats` listings that name another civic's units — follow-up, not built

**Found 2026-10-02**, from skfd asking how
[way 1349287990](https://www.openstreetmap.org/way/1349287990) — `176 Janefield
Avenue`, `addr:flats=156;200` — could list two units 44 apart. **Not part of
the import**, which only creates; this is a cleanup for after it, and it wants
its own post on thread #135103 before any edit.

## How it happened

The Janefield complex is two civic numbers on one site. The City puts one side
of each row at **74 Janefield Avenue** (units 152–178) and the other at
**176 Janefield Avenue** (units 180–330). The OSM footprints there come from
Microsoft's building data and slice each row into narrow pieces, each covering
one home from either side: every pair sums to a constant (152+204, 154+202,
156+200, …), the signature of back-to-back townhouses numbered up one side and
back down the other.

The 2025 import tagged each slice with one housenumber and every City unit
point that fell inside it as a multi-valued `addr:unit`, whichever civic the
point belonged to (way 1349287990 v2, changeset 173653735). Campaign 3 moved
the value to `addr:flats` verbatim (v3, 2026-09-17). So the listing is the 2025
importer's spatial join, not anything the City says.

## The 14

Every OSM object listing units (462, extract of 2026-09-28) checked against
the City's units at the same civic number (snapshot 47). "→" is the civic the
City actually puts that unit at; "—" means the City has no such unit on the
street at all.

| Civic in OSM | Object | Listing | Units not at this civic |
|---|---|---|---|
| 74 Janefield Avenue | [w1349287991](https://www.openstreetmap.org/way/1349287991) | `158;198` | 198→176 |
| 74 Janefield Avenue | [w1349287992](https://www.openstreetmap.org/way/1349287992) | `160;196` | 196→176 |
| 74 Janefield Avenue | [w1349287993](https://www.openstreetmap.org/way/1349287993) | `162;194` | 194→176 |
| 74 Janefield Avenue | [w1349287996](https://www.openstreetmap.org/way/1349287996) | `164;192` | 192→176 |
| 176 Janefield Avenue | [w1349287989](https://www.openstreetmap.org/way/1349287989) | `154;202` | 154→74 |
| 176 Janefield Avenue | [w1349287990](https://www.openstreetmap.org/way/1349287990) | `156;200` | 156→74 |
| 176 Janefield Avenue | [w1349287997](https://www.openstreetmap.org/way/1349287997) | `152;204` | 152→74 |
| 454 Janefield Avenue | [w1349266419](https://www.openstreetmap.org/way/1349266419) | `101-108;201-208` | 204→176 |
| 7 Ajax Street | [w502064547](https://www.openstreetmap.org/way/502064547) | `104-108;205-210;306-311;406-411` | 208→10 |
| 53 Conroy Crescent | [w802528770](https://www.openstreetmap.org/way/802528770) | `101-107;201-208;301-308` | 105→105/91 |
| 23 Woodlawn Road East | [w178085151](https://www.openstreetmap.org/way/178085151) | `101-110;…;901-909;911` | 706→19 |
| 395 Edinburgh Road North | [w1042083497](https://www.openstreetmap.org/way/1042083497) | `105-108;…;709-713;717` | 414, 415, 416 → — |
| 358 Waterloo Avenue | [w819734215](https://www.openstreetmap.org/way/819734215) | `1001-1008;1101-1108;101-106;…` | 903 → — |
| 355 Elmira Road North | [w344325628](https://www.openstreetmap.org/way/344325628) | `100-140` | 122 → — |

Two different things are in this table:

- **The 7 Janefield slices (74/176) are wrong by construction**: one footprint,
  two civics, one housenumber. Both groups get door nodes in the import (176 by
  the building judge, 74 by the rule), so each unit arrives as its own node at
  the right civic and these listings become redundant as well as wrong. They
  fall inside edit 6's scope (strip listings on door groups) if it is revived.
- **The other 7 are one or three stray units on a tower's listing.** 454
  Janefield, 7 Ajax, 53 Conroy and 23 Woodlawn East name a unit the City puts at
  the building next door; Edinburgh, Waterloo and Elmira name units the City
  does not have at all. Which side is wrong — the 2025 join, a renumbering, or
  the City — is not knowable from here. These want a look, not a rule.

## What not to do

Do not "fix" them by moving the stray unit onto the other civic's listing:
for the Janefield slices that writes a second wrong listing, and for the towers
it asserts a containment nobody has checked. Removing the stray value is the
most an edit should claim, and only after the import's door nodes are up.

To regenerate the list: compare each `listing_ids` entry on
`/units/shapes` rows (`unit_shapes.collect()`) against the row's own `units`,
as in the session of 2026-10-02.
