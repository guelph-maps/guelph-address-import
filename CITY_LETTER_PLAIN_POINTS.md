**To:** gisadmin@guelph.ca
**Cc:** opengov@guelph.ca
**Subject:** Addresses open data: what does the point without a unit number mean?

Hello,

I map Guelph's addresses in OpenStreetMap using your Addresses dataset
(explore.guelph.ca/datasets/cityofguelph::addresses-1). Thank you for publishing
it. I have a few questions I can't answer from the data itself.

332 civic addresses have unit points (with a UNIT_NO) and also one point with no
UNIT_NO. For example, 147 Arthur Street North has units A, B and C
plus a plain "147" (ADDID 34872).

Does that plain point stand for a separate dwelling or door with no unit letter,
or for the building or property as a whole?

The data points both ways. Where only unit B exists alongside the plain point,
the plain one looks like the main dwelling. Where 47 units exist, it looks like
the building. If there is a field or a rule that tells the two apart, I'd be
glad to know it.

A smaller related question: 82 addresses have unit points but no plain point at
all. Is that expected, or should each of them have one? I can send that list too.
Two of them have only a single unit point: 139 Arthur Street North, unit A
(ADDID 8349), and 2053 Gordon Street, unit 119 (ADDID 19158). The second puzzles
me most. It looks like a single detached house with its own PIN and roll number,
and the neighbouring lots have no units. What does the 119 stand for?

Last, a few UNIT_NO values I can't read:

- 32 Regent Street: COMMON. Is this the condominium's common elements?
- 130 Silvercreek Parkway North: BLD D and BLD E, beside units 1 to 24. Are
  these whole buildings rather than units?
- 53, 63 and 73 Arthur Street South: AT1 to AT8, RL1 to RL6, BHA, BHB, BHC-1,
  BHC-2 and RR-A1 to RR-B2. What do the prefixes stand for?

A few smaller things I noticed on the way, in case they are useful:

Some POSTCODE values look like they belong somewhere else, maybe an owner's
mailing address:

- 254 Colonial Drive (ADDID 9539): K8V 5P4
- 91 Poppy Drive East, unit 14 (ADDID 48658): M6N 2N8
- 88 Decorso Drive, unit 88 (ADDID 51877): L7P 0N4
- 82 Farquhar Street (ADDID 53855): 0
- 33 and 35 Lambeth Way (ADDID 30480, 55312): N0L 0H1
- 1 Cox Court (ADDID 18992): N0B 1C0
- 1423 Gordon Street (ADDID 43586): N1B 0B8, the only N1B in the layer

HAS_UNIT doesn't always agree with UNIT_NO. 286 points that have a UNIT_NO say
HAS_UNIT = N, across 24 addresses; 155 Bristol Street units B and C (ADDID 57311,
57312) are two of them. Nine points with no UNIT_NO say HAS_UNIT = Y: ADDID
25459, 41799, 57263, 57290, 57291, 57292, 57300, 57301 and 57302. Which of the
two fields should I trust? I can send the 24 addresses too.

On Gosling Gardens, the 30 points numbered 175 to 239 (odd side) have STDIR =
West, while FULLNAME and STREETNAME have no direction and every other point on
the street has none. As far as I know there is no Gosling Gardens West, so the
West looks like a leftover.

13 active points have STREETNO 0. Two are bridges by their LANDMKNAME: Gow's
Bridge on Mccrae Boulevard (ADDID 56660) and Norwich Street Bridge on Norwich
Street East (56662). The other 11 have no name or note, yet all have a PIN and
ten have a roll number: Stephanie Drive (7699), Edinburgh Road South (23417), Watson
Parkway North (26087), York Road (39610), London Road West (44938), Poppy Drive
East (48703), Massey Road (23545), Woodlawn Road East (39535), Scottsdale Drive
(20168), Imperial Road North (56574) and Yarmouth Street (56663). What do these
points stand for? Is 0 a placeholder for a property with no civic number yet?
For now I am leaving them out of OpenStreetMap, since nobody would write 0 on a
door.

The full list of the 332 addresses is below, taken from the live layer on
2 October 2026.

Thanks,
skfd
toronto@comentality.com
OpenStreetMap Guelph address import: https://github.com/guelph-maps/guelph-address-import

---

## Addresses with both unit points and a plain point

### Up to four units (86 addresses)

- 35 Airpark Place: 1, 3 (plain point ADDID 37020)
- 52 Alma Street North: 2 (plain point ADDID 45969)
- 28 Arthur Street North: A, B, C, D (plain point ADDID 25904)
- 137 Arthur Street North: A, B (plain point ADDID 16368)
- 147 Arthur Street North: A, B, C (plain point ADDID 34872)
- 66 Bagot Street: A, B (plain point ADDID 39391)
- 96 Bagot Street: A (plain point ADDID 54094)
- 151 Bristol Street: B, C (plain point ADDID 11859)
- 153 Bristol Street: B, C (plain point ADDID 57307)
- 155 Bristol Street: B, C (plain point ADDID 57310)
- 155A Bristol Street: B, C (plain point ADDID 57313)
- 122 Cardigan Street: 1, 2, 3, 4 (plain point ADDID 24180)
- 25 Dublin Street South: D (plain point ADDID 16747)
- 27 Dublin Street South: A, B, C (plain point ADDID 54369)
- 473 Elmira Road North: 1, 2, 3, 4 (plain point ADDID 19338)
- 265 Eramosa Road: 1, 2, 3, 4 (plain point ADDID 6570)
- 297 Eramosa Road: 1, 2 (plain point ADDID 47692)
- 264 Exhibition Street: 2 (plain point ADDID 8413)
- 53 Ferndale Avenue: 2 (plain point ADDID 3882)
- 41 Gladstone Avenue: 2 (plain point ADDID 14622)
- 161 Goodwin Drive: B (plain point ADDID 24595)
- 1467 Gordon Street: 1, 2, 3 (plain point ADDID 17222)
- 1474 Gordon Street: C1, C2, C3 (plain point ADDID 54075)
- 1886 Gordon Street: 101, 102, 201, 202 (plain point ADDID 57292)
- 18 Grove Street: A (plain point ADDID 21356)
- 47 Huron Street: A, B (plain point ADDID 13151)
- 338 Imperial Road South: B (plain point ADDID 46230)
- 27 Janefield Avenue: B (plain point ADDID 42817)
- 33 Janefield Avenue: B, C (plain point ADDID 56790)
- 35 Janefield Avenue: B, C (plain point ADDID 33960)
- 37 Janefield Avenue: B (plain point ADDID 56793)
- 39 Janefield Avenue: B (plain point ADDID 57013)
- 41 Janefield Avenue: B (plain point ADDID 46139)
- 43 Janefield Avenue: B (plain point ADDID 57015)
- 23 Liverpool Street: A, B, C (plain point ADDID 13358)
- 25 Liverpool Street: A, B, C (plain point ADDID 55241)
- 6 Mason Court: B (plain point ADDID 56779)
- 8 Mason Court: B (plain point ADDID 56781)
- 10 Mason Court: B, C (plain point ADDID 56786)
- 12 Mason Court: B, C (plain point ADDID 56788)
- 1 Mccorkindale Place: 2 (plain point ADDID 22496)
- 18 Mclachlan Place: 2 (plain point ADDID 38772)
- 42 Mctague Street: A, B, C (plain point ADDID 40750)
- 38 Milson Crescent: B (plain point ADDID 25459)
- 167 Municipal Street: 2 (plain point ADDID 44148)
- 115 Neeve Street: A, B (plain point ADDID 24673)
- 10 Nicklin Crescent: B (plain point ADDID 3057)
- 110 Norwich Street East: 1, 2, 4 (plain point ADDID 25329)
- 8 Orchard Crescent: 2, 3 (plain point ADDID 57266)
- 8A Orchard Crescent: 2, 3 (plain point ADDID 57267)
- 10 Orchard Crescent: 2, 3 (plain point ADDID 16451)
- 10A Orchard Crescent: 2, 3 (plain point ADDID 57268)
- 37 Ottawa Crescent: B (plain point ADDID 23296)
- 22 Oxford Street: A, B, C (plain point ADDID 25086)
- 305 Paisley Road: A, B (plain point ADDID 25777)
- 307 Paisley Road: A, B (plain point ADDID 55291)
- 47 Paisley Street: 1, 2, 3 (plain point ADDID 32727)
- 111 Paisley Street: B (plain point ADDID 54295)
- 118 Paisley Street: A (plain point ADDID 36989)
- 19 Quebec Street: 201 (plain point ADDID 30522)
- 21 Quebec Street: 202, 203, 204 (plain point ADDID 57040)
- 24 Queensdale Crescent: 2 (plain point ADDID 14930)
- 32 Regent Street: COMMON (plain point ADDID 25831)
- 44 Regent Street: B (plain point ADDID 55147)
- 160 Renfield Street: 2, 3 (plain point ADDID 9369)
- 36 Ridgeway Avenue: 2 (plain point ADDID 39327)
- 38 Ridgeway Avenue: 2 (plain point ADDID 57281)
- 38A Ridgeway Avenue: 2 (plain point ADDID 57282)
- 38B Ridgeway Avenue: 2 (plain point ADDID 57283)
- 615 Scottsdale Drive: A, B (plain point ADDID 43573)
- 127 Silurian Drive: 2 (plain point ADDID 40604)
- 460 Speedvale Avenue West: 1 (plain point ADDID 15857)
- 245 Stephanie Drive: 2 (plain point ADDID 41799)
- 2 Taggart Street: 2, 4A, 6, 8 (plain point ADDID 41929)
- 1 University Avenue West: B (plain point ADDID 56797)
- 93 Vaughan Street: 2 (plain point ADDID 9642)
- 3 Watson Road South: 1, 2, 3, 8 (plain point ADDID 36946)
- 210 Woolwich Street: A, B, C (plain point ADDID 57172)
- 323 Woolwich Street: A, B (plain point ADDID 21945)
- 430 Woolwich Street: A (plain point ADDID 42446)
- 432 Woolwich Street: A (plain point ADDID 54279)
- 448 Woolwich Street: B (plain point ADDID 20328)
- 765 Woolwich Street: A (plain point ADDID 55167)
- 116 Wyndham Street North: 1, 2, 3, 4 (plain point ADDID 12317)
- 77 Yarmouth Street: A, B, C, D (plain point ADDID 57175)
- 208 Yorkshire Street North: B (plain point ADDID 55093)

### Five or more units (246 addresses)

- 45 Airpark Place: 8 units, 1 to 8 (plain point ADDID 18048)
- 7 Ajax Street: 22 units, 104 to 411 (plain point ADDID 49771)
- 9 Ajax Street: 22 units, 101 to 505 (plain point ADDID 49772)
- 10 Ajax Street: 35 units, 101 to 409 (plain point ADDID 49770)
- 9 Amos Drive: 20 units, 1 to 20 (plain point ADDID 48146)
- 14 Amos Drive: 33 units, 1 to 33 (plain point ADDID 57110)
- 4 Applewood Crescent: 13 units, D1 to D14 (plain point ADDID 33348)
- 32 Arkell Road: 32 units, 1 to 32 (plain point ADDID 57109)
- 60 Arkell Road: 93 units, 1 to 124 (plain point ADDID 50650)
- 167 Arkell Road: 54 units, 1 to 54 (plain point ADDID 8086)
- 361 Arkell Road: 29 units, 1 to 29 (plain point ADDID 7018)
- 403 Arkell Road: 7 units, 1 to 7 (plain point ADDID 24184)
- 31 Arrow Road: 11 units, 1 to 11 (plain point ADDID 43922)
- 196 Arthur Street North: 10 units, 1 to 10 (plain point ADDID 54088)
- 53 Arthur Street South: 133 units, 101 to RL6 (plain point ADDID 50900)
- 63 Arthur Street South: 132 units, 101 to BHC-2 (plain point ADDID 51200)
- 73 Arthur Street South: 123 units, 101 to RR-B2 (plain point ADDID 55590)
- 93 Arthur Street South: 193 units, 101 to 1411 (plain point ADDID 55182)
- 394 Auden Road: 61 units, 1 to 61 (plain point ADDID 42897)
- 467 Auden Road: 44 units, 1 to 44 (plain point ADDID 41924)
- 470 Auden Road: 48 units, 1 to 48 (plain point ADDID 25424)
- 105 Bagot Street: 62 units, 101 to B4 (plain point ADDID 9382)
- 107 Bagot Street: 88 units, 101 to 615 (plain point ADDID 54860)
- 121 Bagot Street: 50 units, 1 to 50 (plain point ADDID 46127)
- 105 Bard Boulevard: 53 units, 1 to 53 (plain point ADDID 26495)
- 106 Bard Boulevard: 72 units, 101 to 418 (plain point ADDID 44240)
- 65 Bayberry Drive: 36 units, C101 to C409 (plain point ADDID 21760)
- 71 Bayberry Drive: 45 units, D101 to D409 (plain point ADDID 25308)
- 281 Bristol Street: 28 units, 201 to 804 (plain point ADDID 50800)
- 283 Bristol Street: 28 units, 201 to 604 (plain point ADDID 35363)
- 3 Burns Drive: 12 units, 1 to 12 (plain point ADDID 36879)
- 33 Burns Drive: 17 units, 1 to 17 (plain point ADDID 42424)
- 60 Cardigan Street: 18 units, 101 to 210 (plain point ADDID 45486)
- 15 Carere Crescent: 66 units, 9A to 48B (plain point ADDID 45438)
- 245 Chancellors Way: 32 units, 101 to 316 (plain point ADDID 22163)
- 8 Christopher Court: 54 units, 101 to 708 (plain point ADDID 54255)
- 5 Cityview Drive South: 8 units, 101 to 108 (plain point ADDID 51479)
- 7 Cityview Drive South: 12 units, 201 to 212 (plain point ADDID 51478)
- 9 Cityview Drive South: 8 units, 301 to 308 (plain point ADDID 51477)
- 151 Clairfields Drive East: 68 units, 1 to 68 (plain point ADDID 34299)
- 125 Cole Road: 82 units, 1 to 82 (plain point ADDID 43909)
- 264 College Avenue West: 43 units, 2 to 44 (plain point ADDID 35453)
- 302 College Avenue West: 214 units, 1 to 214 (plain point ADDID 49775)
- 2 Colonial Drive: 50 units, 101 to 414 (plain point ADDID 46620)
- 37 Conroy Crescent: 15 units, 1 to 15 (plain point ADDID 46621)
- 53 Conroy Crescent: 22 units, 101 to 308 (plain point ADDID 49756)
- 57 Conroy Crescent: 12 units, 101 to 304 (plain point ADDID 49765)
- 63 Conroy Crescent: 30 units, 1 to 58 (plain point ADDID 49766)
- 91 Conroy Crescent: 47 units, 102 to 512 (plain point ADDID 49767)
- 105 Conroy Crescent: 47 units, 102 to 512 (plain point ADDID 49755)
- 120 Country Club Drive: 74 units, 1 to 75 (plain point ADDID 54886)
- 20 Cowan Place: 12 units, 1 to 12 (plain point ADDID 16395)
- 210 Dawn Avenue: 44 units, 1 to 44 (plain point ADDID 15421)
- 39 Dawson Road: 36 units, 1 to 37 (plain point ADDID 40733)
- 88 Decorso Drive: 98 units, 1 to 98 (plain point ADDID 57111)
- 166 Deerpath Drive: 114 units, 1 to 114 (plain point ADDID 23371)
- 115 Downey Road: 10 units, 1 to 10 (plain point ADDID 15589)
- 146 Downey Road: 45 units, 1 to 37 (plain point ADDID 2442)
- 66 Eastview Road: 30 units, 1 to 30 (plain point ADDID 3805)
- 395 Edinburgh Road North: 87 units, 105 to 717 (plain point ADDID 52490)
- 383 Edinburgh Road South: 40 units, 1 to 41 (plain point ADDID 55372)
- 511 Edinburgh Road South: 101, 101A, 102, 201, 202 (plain point ADDID 30781)
- 920 Edinburgh Road South: 80 units, 1 to 80 (plain point ADDID 35385)
- 355 Elmira Road North: 40 units, 100 to 140 (plain point ADDID 57094)
- 33 Farley Drive: 1, 7, 8, 10, 11, 14 (plain point ADDID 14756)
- 80 Ferman Drive: 38 units, 1 to 38 (plain point ADDID 10832)
- 90 Ferman Drive: 45 units, 1 to 45 (plain point ADDID 22461)
- 50 Fife Road: 29 units, 1 to 39 (plain point ADDID 33808)
- 158 Fife Road: 25 units, 1 to 25 (plain point ADDID 42542)
- 186 Fife Road: 27 units, 1 to 27 (plain point ADDID 7571)
- 190 Fife Road: 72 units, 28 to 100 (plain point ADDID 44133)
- 75 Flaherty Drive: 50 units, 1 to 50 (plain point ADDID 25842)
- 64 Frederick Drive: 16 units, 101 to 404 (plain point ADDID 7344)
- 65 Frederick Drive: 1, 2, 3, 4, 5, 6 (plain point ADDID 46888)
- 100 Frederick Drive: 16 units, 1 to 16 (plain point ADDID 4361)
- 101 Frederick Drive: 16 units, 1 to 16 (plain point ADDID 46889)
- 12 Glasgow Street South: 14 units, 1 to 15 (plain point ADDID 31857)
- 37 Goodwin Drive: 55 units, 101 to 414 (plain point ADDID 49751)
- 39 Goodwin Drive: 47 units, 101 to 412 (plain point ADDID 47755)
- 41 Goodwin Drive: 47 units, 101 to 412 (plain point ADDID 49750)
- 43 Goodwin Drive: 55 units, 101 to 414 (plain point ADDID 55321)
- 45 Goodwin Drive: 47 units, 101 to 412 (plain point ADDID 37312)
- 5 Gordon Street: 61 units, 100 to 607 (plain point ADDID 6111)
- 31 Gordon Street: 23 units, 1 to A14 (plain point ADDID 8471)
- 220 Gordon Street: 18 units, 11 to 36 (plain point ADDID 8283)
- 803 Gordon Street: 15 units, 1 to 15 (plain point ADDID 22053)
- 807 Gordon Street: 12 units, 1 to 12 (plain point ADDID 42508)
- 941 Gordon Street: 72 units, 1 to 72 (plain point ADDID 55303)
- 1055 Gordon Street: 60 units, 1 to 60 (plain point ADDID 44263)
- 1077 Gordon Street: 124 units, 112 to 442 (plain point ADDID 12213)
- 1083 Gordon Street: 44 units, 101 to 411 (plain point ADDID 50237)
- 1131 Gordon Street: 8 units, 1 to 8 (plain point ADDID 7678)
- 1155 Gordon Street: 130 units, 1 to 130 (plain point ADDID 19374)
- 1219 Gordon Street: 80 units, 101 to C (plain point ADDID 50303)
- 1280 Gordon Street: 75 units, 101 to 419 (plain point ADDID 14206)
- 1284 Gordon Street: 124 units, 101 to 431 (plain point ADDID 51611)
- 1291 Gordon Street: 160 units, 101 to 627 (plain point ADDID 14461)
- 1398 Gordon Street: U1, U2, U3, U4, U6, U7 (plain point ADDID 36589)
- 1440 Gordon Street: 91 units, 101 to 423 (plain point ADDID 7364)
- 1460 Gordon Street: 7 units, A2 to B4 (plain point ADDID 37646)
- 1498 Gordon Street: 28 units, 1 to 28 (plain point ADDID 34762)
- 1550 Gordon Street: 46 units, 1 to 47 (plain point ADDID 43442)
- 1671 Gordon Street: 14 units, 1 to 14 (plain point ADDID 46820)
- 1878 Gordon Street: 172 units, 101 to 1404 (plain point ADDID 57291)
- 1880 Gordon Street: 172 units, 101 to 1404 (plain point ADDID 57010)
- 1882 Gordon Street: 89 units, 101 to 805 (plain point ADDID 57290)
- 124 Gosling Gardens: 88 units, 1 to 88 (plain point ADDID 38261)
- 254 Gosling Gardens: 36 units, 1 to 36 (plain point ADDID 48448)
- 332 Gosling Gardens: 88 units, 101 to 808 (plain point ADDID 48456)
- 259 Grange Road: 14 units, 1A to 14 (plain point ADDID 12885)
- 415 Grange Road: 50 units, 101 to 413 (plain point ADDID 3510)
- 426 Grange Road: 60 units, 1 to 60 (plain point ADDID 10656)
- 16 Hadati Road: 62 units, 1 to 62 (plain point ADDID 47187)
- 265 Hanlon Creek Boulevard: 1, 3, 4, 5, 9 (plain point ADDID 46917)
- 275 Hanlon Creek Boulevard: 1, 2, 3, 4, 5 (plain point ADDID 48461)
- 40 Imperial Road North: 76 units, 1 to 76 (plain point ADDID 17954)
- 142 Imperial Road North: 32 units, 101 to 408 (plain point ADDID 27773)
- 146 Imperial Road North: 32 units, 101 to 408 (plain point ADDID 7324)
- 150 Imperial Road North: 32 units, 101 to 408 (plain point ADDID 27233)
- 30 Imperial Road South: 118 units, 1 to 118 (plain point ADDID 20294)
- 74 Janefield Avenue: 89 units, 2 to 178 (plain point ADDID 16873)
- 176 Janefield Avenue: 76 units, 180 to 330 (plain point ADDID 57118)
- 224 Janefield Avenue: 58 units, 332 to 446 (plain point ADDID 57119)
- 454 Janefield Avenue: 15 units, 101 to 208 (plain point ADDID 49795)
- 456 Janefield Avenue: 20 units, 109 to 218 (plain point ADDID 55374)
- 458 Janefield Avenue: 16 units, 119 to 226 (plain point ADDID 55375)
- 460 Janefield Avenue: 16 units, 127 to 234 (plain point ADDID 55376)
- 7 Kay Crescent: 94 units, 101 to LL06 (plain point ADDID 54248)
- 17 Kay Crescent: 47 units, 101 to 412 (plain point ADDID 49539)
- 25 Kay Crescent: 63 units, 101 to LL14 (plain point ADDID 55064)
- 39 Kay Crescent: 47 units, 1 to 47 (plain point ADDID 49698)
- 35 Kingsbury Square: 100 units, 101 to 427 (plain point ADDID 54848)
- 45 Kingsbury Square: 54 units, 101 to 414 (plain point ADDID 46852)
- 67 Kingsbury Square: 54 units, 101 to 414 (plain point ADDID 46853)
- 160 Kortright Road West: 9 units, 1 to 15 (plain point ADDID 7361)
- 240 London Road West: 105 units, 1 to 105 (plain point ADDID 5312)
- 26 Lowes Road West: 86 units, 101 to 614 (plain point ADDID 55928)
- 42 Lowes Road West: 150 units, 1 to 150 (plain point ADDID 27242)
- 60 Lynnmore Street: 54 units, 101 to 414 (plain point ADDID 47466)
- 355 Macalister Boulevard: 29 units, 1 to 29 (plain point ADDID 35326)
- 160 Macdonell Street: 132 units, 101 to 1804 (plain point ADDID 40276)
- 25 Manor Park Crescent: 15 units, 1 to 15 (plain point ADDID 57112)
- 16 Marilyn Drive: 17 units, 101 to 306 (plain point ADDID 32197)
- 22 Marilyn Drive: 70 units, 103 to 908 (plain point ADDID 47874)
- 24 Marilyn Drive: 56 units, 101 to 1006 (plain point ADDID 47875)
- 45 Marksam Road: 65 units, 1 to 129 (plain point ADDID 47876)
- 180 Marksam Road: 98 units, 1 to 98 (plain point ADDID 43774)
- 22 Marshall Drive: 20 units, 1 to 20 (plain point ADDID 8446)
- 117 Marshall Drive: 51 units, 1 to 51 (plain point ADDID 10428)
- 27 Monarch Road: 1, 2, 3, 4, 5, 6 (plain point ADDID 47882)
- 70 Monarch Road: 1, 2, 3, 4, 5, 6 (plain point ADDID 15161)
- 1 Mont Street: 1, 2, 3, 4, 5, 6 (plain point ADDID 35239)
- 35 Mountford Drive: 124 units, 1 to 124 (plain point ADDID 32166)
- 85 Mullin Drive: 110 units, 1A to 55B (plain point ADDID 43577)
- 83 Neeve Street: 7 units, 1 to 7 (plain point ADDID 15222)
- 190 Norfolk Street: B, C, D, E, F (plain point ADDID 42059)
- 40 Northumberland Street: 18 units, 101 to 306 (plain point ADDID 47911)
- 26 Ontario Street: 82 units, 101 to 327 (plain point ADDID 26232)
- 700 Paisley Road: 100 units, 1 to 100 (plain point ADDID 34424)
- 901 Paisley Road: 34 units, 101 to 409 (plain point ADDID 9526)
- 91 Poppy Drive East: 51 units, 1 to 51 (plain point ADDID 48610)
- 87 Poppy Drive West: 20 units, 1 to 20 (plain point ADDID 57521)
- 39 Ptarmigan Drive: 36 units, 1 to 36 (plain point ADDID 55319)
- 60 Ptarmigan Drive: 40 units, 1 to 40 (plain point ADDID 55379)
- 35 Rhonda Road: 18 units, 30 to 47 (plain point ADDID 55313)
- 41 Rhonda Road: 29 units, 1 to 29 (plain point ADDID 28575)
- 49 Rhonda Road: 96 units, 48 to 143 (plain point ADDID 55323)
- 66 Rodgers Road: 60 units, 1 to 60 (plain point ADDID 55390)
- 31 Schroder Crescent: 55 units, 1 to 55 (plain point ADDID 35538)
- 649 Scottsdale Drive: 8 units, 1 to 101 (plain point ADDID 22543)
- 650 Scottsdale Drive: 8 units, 1 to 6 (plain point ADDID 43533)
- 20 Shackleton Drive: 47 units, 1 to 47 (plain point ADDID 21600)
- 65 Silvercreek Parkway North: 40 units, 101 to 410 (plain point ADDID 55387)
- 70 Silvercreek Parkway North: 66 units, 1 to 66 (plain point ADDID 2790)
- 75 Silvercreek Parkway North: 31 units, 101 to 408 (plain point ADDID 55388)
- 106 Silvercreek Parkway North: 1, 2, 4, 5, 7 (plain point ADDID 54831)
- 130 Silvercreek Parkway North: 22 units, 1 to BLD E (plain point ADDID 41785)
- 219 Silvercreek Parkway North: 9 units, 1 to 37 (plain point ADDID 21811)
- 19 Simmonds Drive: 46 units, 1 to 46 (plain point ADDID 21596)
- 245 Southgate Drive: 12 units, 1 to 12 (plain point ADDID 43466)
- 350 Speedvale Avenue West: 12 units, 1 to 12 (plain point ADDID 55367)
- 7 Stevenson Street North: 7 units, 1 to 7 (plain point ADDID 54590)
- 20 Stevenson Street South: 5, 6, A, B, C, D (plain point ADDID 55046)
- 252 Stone Road West: 140 units, 1 to 140 (plain point ADDID 7580)
- 292 Stone Road West: 11 units, 1 to 8 (plain point ADDID 6010)
- 304 Stone Road West: 10 units, 1 to 12 (plain point ADDID 2335)
- 370 Stone Road West: 15 units, 1 to 16 (plain point ADDID 41083)
- 414 Stone Road West: 72 units, 1 to 72 (plain point ADDID 16023)
- 10 Stuart Street: 10 units, 1 to 10 (plain point ADDID 54817)
- 57 Suffolk Street West: 9 units, 101 to PH (plain point ADDID 40446)
- 254 Summerfield Drive: 42 units, 1 to 42 (plain point ADDID 43427)
- 255 Summerfield Drive: 33 units, 1 to 40 (plain point ADDID 35752)
- 104 Summit Ridge Drive: 48 units, 101 to 412 (plain point ADDID 50632)
- 108 Summit Ridge Drive: 52 units, 101 to LL04 (plain point ADDID 50633)
- 1 Sunnylea Crescent: 8 units, 1 to 8 (plain point ADDID 54196)
- 2 Sunnylea Crescent: 8 units, 1 to 8 (plain point ADDID 29323)
- 3 Sunnylea Crescent: 8 units, 1 to 8 (plain point ADDID 10180)
- 4 Sunnylea Crescent: 8 units, 1 to 8 (plain point ADDID 44463)
- 55 Teal Drive: 48 units, 1 to 48 (plain point ADDID 18957)
- 165 Terraview Crescent: 101 units, 1 to 101 (plain point ADDID 35591)
- 30 Vaughan Street: 53 units, 1 to 73 (plain point ADDID 15688)
- 129 Victoria Road North: 91 units, 1 to 91 (plain point ADDID 35593)
- 427 Victoria Road North: 18 units, B11 to C29 (plain point ADDID 57300)
- 453 Victoria Road North: 10 units, A1 to A10 (plain point ADDID 57301)
- 675 Victoria Road North: 31 units, 1 to 31 (plain point ADDID 57095)
- 199 Victoria Road South: 8 units, 1 to 8 (plain point ADDID 50352)
- 1035 Victoria Road South: 117 units, 2 to 151 (plain point ADDID 40346)
- 119 Water Street: 8 units, 101 to 204 (plain point ADDID 54884)
- 295 Water Street: 96 units, 1 to 193 (plain point ADDID 5324)
- 19 Waterford Drive: 54 units, 101 to 414 (plain point ADDID 55070)
- 43 Waterford Drive: 54 units, 101 to 414 (plain point ADDID 31093)
- 121 Waterloo Avenue: 10 units, 101 to 110 (plain point ADDID 54895)
- 358 Waterloo Avenue: 85 units, 101 to 1108 (plain point ADDID 55369)
- 360 Waterloo Avenue: 107, 108, 209, 210, 211, 212 (plain point ADDID 55370)
- 269 Watson Parkway North: 20 units, 1 to 20 (plain point ADDID 42109)
- 308 Watson Parkway North: 83 units, 101 to 421 (plain point ADDID 2988)
- 365 Watson Parkway North: 12 units, 1 to 12 (plain point ADDID 44220)
- 70 Watson Parkway South: 8 units, 1 to 8 (plain point ADDID 28444)
- 150 Wellington Street East: 143 units, 101 to 1802 (plain point ADDID 19133)
- 120 Westmount Road: 28 units, 1 to 28 (plain point ADDID 26991)
- 107 Westra Drive: 72 units, 1 to 72 (plain point ADDID 49013)
- 89 Westwood Road: 66 units, 101 to 612 (plain point ADDID 55300)
- 93 Westwood Road: 66 units, 101 to 612 (plain point ADDID 55301)
- 199 Westwood Road: 104 units, 1 to 104 (plain point ADDID 9742)
- 240 Westwood Road: 70 units, 1A to 20D (plain point ADDID 2647)
- 15 Willow Road: 49 units, 1 to 50 (plain point ADDID 14850)
- 234 Willow Road: 20 units, 101 to 308 (plain point ADDID 55316)
- 500 Willow Road: 11 units, 2 to 30 (plain point ADDID 7017)
- 539 Willow Road: 69 units, 1 to 69 (plain point ADDID 15815)
- 714 Willow Road: 35 units, 1 to 35 (plain point ADDID 21728)
- 755 Willow Road: 42 units, 1 to 42 (plain point ADDID 9681)
- 19 Woodlawn Road East: 142 units, 101 to 915 (plain point ADDID 50481)
- 23 Woodlawn Road East: 103 units, 101 to 911 (plain point ADDID 50482)
- 70 Woodlawn Road East: 50 units, 101 to 318 (plain point ADDID 9357)
- 72 Woodlawn Road East: 39 units, 101 to 607 (plain point ADDID 4440)
- 527 Woodlawn Road East: 16 units, D1 to E17 (plain point ADDID 57302)
- 200 Woolwich Street: 7 units, 101 to 204 (plain point ADDID 23358)
- 560 Woolwich Street: 18 units, A1 to B9 (plain point ADDID 31361)
- 708 Woolwich Street: 96 units, 101 to 424 (plain point ADDID 55938)
- 824 Woolwich Street: 200 units, 1 to 200 (plain point ADDID 56562)
- 60 Wyndham Street South: 120 units, 101 to 1012 (plain point ADDID 3767)
- 55 Yarmouth Street: 72 units, 201 to 909 (plain point ADDID 8185)
- 86 Yarmouth Street: 18 units, 101 to 306 (plain point ADDID 41105)
- 72 York Road: 22 units, 1 to 22 (plain point ADDID 34034)
- 142 York Road: 24 units, 1 to 24 (plain point ADDID 30562)
- 561 York Road: 19 units, 1 to 19 (plain point ADDID 11269)
