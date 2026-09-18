# addr:flats — every value this campaign rewrites

Generated from `manifest.csv` (built 2026-09-17 against live OSM, re-verify with `build_batches.py --refetch` on the day).

**292 of the 464 live `addr:flats` values change.** The other 172 are already exactly what the renderer produces (146 of them had nothing else to edit either, so they are not uploaded at all).

Every row below round-trips: the set of units named before and after is identical. 163 values get shorter, 129 stay the same length, none gets longer.


A value can carry more than one defect, so the section counts below sum to more than 292:
233 collapse only, 41 trailing only, 9 reorder only, 5 trailing+reorder, 2 trailing+collapse,
1 spaces+trailing, 1 spaces only.

## What deliberately does not change

- Letter **prefixes** are building letters and group on their own — `D101-D112;D201-D212` never merges across letters.
- Letter **suffixes** cannot join a range — `101A` stays its own value and sorts beside its neighbours.
- `LL` floors keep their zero padding (`LL01`, not `LL1`) — this needed an engine fix, `address-importer-friend` `054da405`.
- **Stepped sequences never compress** — `224;234` stays, because `224-234` would claim units 225-233 exist.
- The 172 values already in renderer form are left byte-for-byte alone.

## Enumeration collapsed into a range — 235

| # | Address | Object | Before | After |
|---|---|---|---|---|
| 1 | 45 Airpark Place | [way 802544823](https://www.openstreetmap.org/way/802544823) | `1;2;3;4;5;6;7;8` | `1-8` |
| 2 | 32 Arkell Road | [way 1283416466](https://www.openstreetmap.org/way/1283416466) | `10;11;12;9` | `9-12` |
| 3 | 32 Arkell Road | [way 1283416472](https://www.openstreetmap.org/way/1283416472) | `17;18;19;20` | `17-20` |
| 4 | 32 Arkell Road | [way 1283416476](https://www.openstreetmap.org/way/1283416476) | `1;2;3;4` | `1-4` |
| 5 | 32 Arkell Road | [way 1283416486](https://www.openstreetmap.org/way/1283416486) | `25;26;27;28` | `25-28` |
| 6 | 32 Arkell Road | [way 1443819663](https://www.openstreetmap.org/way/1443819663) | `21;22;23;24` | `21-24` |
| 7 | 32 Arkell Road | [way 1443819664](https://www.openstreetmap.org/way/1443819664) | `5;6;7;8` | `5-8` |
| 8 | 32 Arkell Road | [way 1443819665](https://www.openstreetmap.org/way/1443819665) | `29;30;31;32` | `29-32` |
| 9 | 32 Arkell Road | [way 1443819666](https://www.openstreetmap.org/way/1443819666) | `13;14;15;16` | `13-16` |
| 10 | 31 Arrow Road | [way 475631431](https://www.openstreetmap.org/way/475631431) | `1;10;11;2;3;4;5;6;7;8;9` | `1-11` |
| 11 | 394 Auden Road | [way 803283640](https://www.openstreetmap.org/way/803283640) | `29;30;31;32;33;34;35;36;37;38;39` | `29-39` |
| 12 | 394 Auden Road | [way 803283643](https://www.openstreetmap.org/way/803283643) | `11;12;13;14;15;16;17;18;19` | `11-19` |
| 13 | 467 Auden Road | [way 937956322](https://www.openstreetmap.org/way/937956322) | `14;15;16;17;18;19;20` | `14-20` |
| 14 | 467 Auden Road | [way 937956323](https://www.openstreetmap.org/way/937956323) | `39;40;41;42;43;44` | `39-44` |
| 15 | 467 Auden Road | [way 937956324](https://www.openstreetmap.org/way/937956324) | `10;11;12;13;7;8;9` | `7-13` |
| 16 | 467 Auden Road | [way 937956325](https://www.openstreetmap.org/way/937956325) | `1;2;3;4;5;6` | `1-6` |
| 17 | 467 Auden Road | [way 937956326](https://www.openstreetmap.org/way/937956326) | `33;34;35;36;37;38` | `33-38` |
| 18 | 467 Auden Road | [way 937956327](https://www.openstreetmap.org/way/937956327) | `27;28;29;30;31;32` | `27-32` |
| 19 | 467 Auden Road | [way 937956329](https://www.openstreetmap.org/way/937956329) | `21;22;23;24;25;26` | `21-26` |
| 20 | 470 Auden Road | [way 937552909](https://www.openstreetmap.org/way/937552909) | `37;38;39;40` | `37-40` |
| 21 | 470 Auden Road | [way 937552911](https://www.openstreetmap.org/way/937552911) | `32;33;34;35;36` | `32-36` |
| 22 | 470 Auden Road | [way 937552912](https://www.openstreetmap.org/way/937552912) | `26;27;28;29;30;31` | `26-31` |
| 23 | 470 Auden Road | [way 937552913](https://www.openstreetmap.org/way/937552913) | `41;42;43;44` | `41-44` |
| 24 | 470 Auden Road | [way 937552914](https://www.openstreetmap.org/way/937552914) | `45;46;47;48` | `45-48` |
| 25 | 470 Auden Road | [way 937552915](https://www.openstreetmap.org/way/937552915) | `22;23` | `22-23` |
| 26 | 470 Auden Road | [way 937552916](https://www.openstreetmap.org/way/937552916) | `16;17` | `16-17` |
| 27 | 470 Auden Road | [way 937552917](https://www.openstreetmap.org/way/937552917) | `10;11;12;13;7;8;9` | `7-13` |
| 28 | 470 Auden Road | [way 937552918](https://www.openstreetmap.org/way/937552918) | `1;2;3;4;5;6` | `1-6` |
| 29 | 105 Bagot Street | [way 208356564](https://www.openstreetmap.org/way/208356564) | `101-113;201-215;301-315;401-415;B1;B2;B3;B4` | `101-113;201-215;301-315;401-415;B1-B4` |
| 30 | 3 Burns Drive | [way 1436604425](https://www.openstreetmap.org/way/1436604425) | `1;2;3;4` | `1-4` |
| 31 | 3 Burns Drive | [way 1436604426](https://www.openstreetmap.org/way/1436604426) | `5;6;7;8` | `5-8` |
| 32 | 3 Burns Drive | [way 802123328](https://www.openstreetmap.org/way/802123328) | `10;11;12;9` | `9-12` |
| 33 | 9 Burns Drive | [way 1436604428](https://www.openstreetmap.org/way/1436604428) | `53;54;55;56;57;58` | `53-58` |
| 34 | 9 Burns Drive | [way 1436604429](https://www.openstreetmap.org/way/1436604429) | `59;60;61;62;63;64` | `59-64` |
| 35 | 9 Burns Drive | [way 802123327](https://www.openstreetmap.org/way/802123327) | `65;66;67;68;69;70` | `65-70` |
| 36 | 11 Burns Drive | [way 1436604427](https://www.openstreetmap.org/way/1436604427) | `13;14;15;16` | `13-16` |
| 37 | 11 Burns Drive | [way 802123329](https://www.openstreetmap.org/way/802123329) | `17;18;19;20` | `17-20` |
| 38 | 15 Burns Drive | [way 1436604432](https://www.openstreetmap.org/way/1436604432) | `21;22;23;24` | `21-24` |
| 39 | 15 Burns Drive | [way 802123326](https://www.openstreetmap.org/way/802123326) | `25;26;27;28` | `25-28` |
| 40 | 17 Burns Drive | [way 1436604433](https://www.openstreetmap.org/way/1436604433) | `35;36;37;38;39;40` | `35-40` |
| 41 | 17 Burns Drive | [way 802123325](https://www.openstreetmap.org/way/802123325) | `29;30;31;32;33;34` | `29-34` |
| 42 | 19 Burns Drive | [way 1436604430](https://www.openstreetmap.org/way/1436604430) | `41;42;43;44` | `41-44` |
| 43 | 19 Burns Drive | [way 1436604431](https://www.openstreetmap.org/way/1436604431) | `49;50;51;52` | `49-52` |
| 44 | 19 Burns Drive | [way 802123324](https://www.openstreetmap.org/way/802123324) | `45;46;47;48` | `45-48` |
| 45 | 80 Burns Drive | [way 1436604416](https://www.openstreetmap.org/way/1436604416) | `11;12` | `11-12` |
| 46 | 80 Burns Drive | [way 1436604417](https://www.openstreetmap.org/way/1436604417) | `13;14` | `13-14` |
| 47 | 80 Burns Drive | [way 1436604418](https://www.openstreetmap.org/way/1436604418) | `15;16` | `15-16` |
| 48 | 80 Burns Drive | [way 1436604419](https://www.openstreetmap.org/way/1436604419) | `17;18` | `17-18` |
| 49 | 80 Burns Drive | [way 632319013](https://www.openstreetmap.org/way/632319013) | `19;20` | `19-20` |
| 50 | 86 Burns Drive | [way 1436604420](https://www.openstreetmap.org/way/1436604420) | `1;2` | `1-2` |
| 51 | 86 Burns Drive | [way 1436604421](https://www.openstreetmap.org/way/1436604421) | `3;4` | `3-4` |
| 52 | 86 Burns Drive | [way 1436604422](https://www.openstreetmap.org/way/1436604422) | `5;6` | `5-6` |
| 53 | 86 Burns Drive | [way 1436604423](https://www.openstreetmap.org/way/1436604423) | `7;8` | `7-8` |
| 54 | 86 Burns Drive | [way 632319014](https://www.openstreetmap.org/way/632319014) | `10;9` | `9-10` |
| 55 | 122 Cardigan Street | [way 925775122](https://www.openstreetmap.org/way/925775122) | `1;2;3;4` | `1-4` |
| 56 | 5 Cityview Drive South | [way 939208872](https://www.openstreetmap.org/way/939208872) | `101;102;103;104;105;106;107;108` | `101-108` |
| 57 | 7 Cityview Drive South | [way 939208873](https://www.openstreetmap.org/way/939208873) | `201;202;203;204;205;206;207;208;209;210;211;212` | `201-212` |
| 58 | 9 Cityview Drive South | [way 939208874](https://www.openstreetmap.org/way/939208874) | `301;302;303;304;305;306;307;308` | `301-308` |
| 59 | 37 Conroy Crescent | [way 210083020](https://www.openstreetmap.org/way/210083020) | `1;10;11;12;13;14;15;2;3;4;5;6;7;8;9` | `1-15` |
| 60 | 120 Country Club Drive | [way 761343575](https://www.openstreetmap.org/way/761343575) | `11;12;14-33;` | `11-12;14-33` |
| 61 | 120 Country Club Drive | [way 761343584](https://www.openstreetmap.org/way/761343584) | `58;59;60;61` | `58-61` |
| 62 | 66 Eastview Road | [way 803283699](https://www.openstreetmap.org/way/803283699) | `10;11;7;8;9` | `7-11` |
| 63 | 511 Edinburgh Road South | [way 215069449](https://www.openstreetmap.org/way/215069449) | `101;101A;102;201;202` | `101-102;101A;201-202` |
| 64 | 473 Elmira Road North | [way 399149535](https://www.openstreetmap.org/way/399149535) | `1;2;3;4` | `1-4` |
| 65 | 265 Eramosa Road | [way 208488067](https://www.openstreetmap.org/way/208488067) | `1;2;3;4` | `1-4` |
| 66 | 297 Eramosa Road | [way 240744882](https://www.openstreetmap.org/way/240744882) | `1;2` | `1-2` |
| 67 | 190 Fife Road | [way 1441651733](https://www.openstreetmap.org/way/1441651733) | `59;60` | `59-60` |
| 68 | 190 Fife Road | [way 1441651734](https://www.openstreetmap.org/way/1441651734) | `57;58` | `57-58` |
| 69 | 190 Fife Road | [way 1441651735](https://www.openstreetmap.org/way/1441651735) | `55;56` | `55-56` |
| 70 | 190 Fife Road | [way 1441651736](https://www.openstreetmap.org/way/1441651736) | `51;52` | `51-52` |
| 71 | 190 Fife Road | [way 1441651737](https://www.openstreetmap.org/way/1441651737) | `49;50` | `49-50` |
| 72 | 190 Fife Road | [way 1441651738](https://www.openstreetmap.org/way/1441651738) | `47;48` | `47-48` |
| 73 | 190 Fife Road | [way 1441651739](https://www.openstreetmap.org/way/1441651739) | `77;78` | `77-78` |
| 74 | 190 Fife Road | [way 1441651740](https://www.openstreetmap.org/way/1441651740) | `79;80` | `79-80` |
| 75 | 190 Fife Road | [way 1441651741](https://www.openstreetmap.org/way/1441651741) | `81;82` | `81-82` |
| 76 | 190 Fife Road | [way 1441651742](https://www.openstreetmap.org/way/1441651742) | `61;62` | `61-62` |
| 77 | 190 Fife Road | [way 1441651743](https://www.openstreetmap.org/way/1441651743) | `63;64` | `63-64` |
| 78 | 190 Fife Road | [way 1441651744](https://www.openstreetmap.org/way/1441651744) | `65;66` | `65-66` |
| 79 | 190 Fife Road | [way 1441651745](https://www.openstreetmap.org/way/1441651745) | `67;68` | `67-68` |
| 80 | 190 Fife Road | [way 1441651746](https://www.openstreetmap.org/way/1441651746) | `69;70` | `69-70` |
| 81 | 190 Fife Road | [way 1441651747](https://www.openstreetmap.org/way/1441651747) | `71;72` | `71-72` |
| 82 | 190 Fife Road | [way 1441651748](https://www.openstreetmap.org/way/1441651748) | `73;74` | `73-74` |
| 83 | 190 Fife Road | [way 1441651749](https://www.openstreetmap.org/way/1441651749) | `42;43` | `42-43` |
| 84 | 190 Fife Road | [way 1441651750](https://www.openstreetmap.org/way/1441651750) | `40;41` | `40-41` |
| 85 | 190 Fife Road | [way 1441651751](https://www.openstreetmap.org/way/1441651751) | `38;39` | `38-39` |
| 86 | 190 Fife Road | [way 1441651752](https://www.openstreetmap.org/way/1441651752) | `34;35` | `34-35` |
| 87 | 190 Fife Road | [way 1441651753](https://www.openstreetmap.org/way/1441651753) | `32;33` | `32-33` |
| 88 | 190 Fife Road | [way 1441651754](https://www.openstreetmap.org/way/1441651754) | `30;31` | `30-31` |
| 89 | 190 Fife Road | [way 1441651755](https://www.openstreetmap.org/way/1441651755) | `100;99` | `99-100` |
| 90 | 190 Fife Road | [way 1441651756](https://www.openstreetmap.org/way/1441651756) | `97;98` | `97-98` |
| 91 | 190 Fife Road | [way 1441651757](https://www.openstreetmap.org/way/1441651757) | `95;96` | `95-96` |
| 92 | 190 Fife Road | [way 1441651758](https://www.openstreetmap.org/way/1441651758) | `93;94` | `93-94` |
| 93 | 190 Fife Road | [way 1441651759](https://www.openstreetmap.org/way/1441651759) | `91;92` | `91-92` |
| 94 | 190 Fife Road | [way 1441651760](https://www.openstreetmap.org/way/1441651760) | `89;90` | `89-90` |
| 95 | 190 Fife Road | [way 1441651761](https://www.openstreetmap.org/way/1441651761) | `87;88` | `87-88` |
| 96 | 190 Fife Road | [way 921942596](https://www.openstreetmap.org/way/921942596) | `36;37` | `36-37` |
| 97 | 190 Fife Road | [way 921942597](https://www.openstreetmap.org/way/921942597) | `28;29` | `28-29` |
| 98 | 190 Fife Road | [way 921942598](https://www.openstreetmap.org/way/921942598) | `85;86` | `85-86` |
| 99 | 190 Fife Road | [way 921942599](https://www.openstreetmap.org/way/921942599) | `83;84` | `83-84` |
| 100 | 190 Fife Road | [way 921942600](https://www.openstreetmap.org/way/921942600) | `75;76` | `75-76` |
| 101 | 190 Fife Road | [way 921942601](https://www.openstreetmap.org/way/921942601) | `45;46` | `45-46` |
| 102 | 190 Fife Road | [way 921942602](https://www.openstreetmap.org/way/921942602) | `53;54` | `53-54` |
| 103 | 75 Flaherty Drive | [way 1437043928](https://www.openstreetmap.org/way/1437043928) | `49;50` | `49-50` |
| 104 | 75 Flaherty Drive | [way 1437043929](https://www.openstreetmap.org/way/1437043929) | `45;46` | `45-46` |
| 105 | 75 Flaherty Drive | [way 1437043930](https://www.openstreetmap.org/way/1437043930) | `41;42` | `41-42` |
| 106 | 75 Flaherty Drive | [way 1437043931](https://www.openstreetmap.org/way/1437043931) | `37;38` | `37-38` |
| 107 | 75 Flaherty Drive | [way 1437043932](https://www.openstreetmap.org/way/1437043932) | `35;36` | `35-36` |
| 108 | 75 Flaherty Drive | [way 1437043933](https://www.openstreetmap.org/way/1437043933) | `31;32` | `31-32` |
| 109 | 75 Flaherty Drive | [way 1437043934](https://www.openstreetmap.org/way/1437043934) | `33;34` | `33-34` |
| 110 | 75 Flaherty Drive | [way 1437043935](https://www.openstreetmap.org/way/1437043935) | `3;4` | `3-4` |
| 111 | 75 Flaherty Drive | [way 1437043936](https://www.openstreetmap.org/way/1437043936) | `5;6` | `5-6` |
| 112 | 75 Flaherty Drive | [way 1437043937](https://www.openstreetmap.org/way/1437043937) | `10;9` | `9-10` |
| 113 | 75 Flaherty Drive | [way 1437043938](https://www.openstreetmap.org/way/1437043938) | `11;12` | `11-12` |
| 114 | 75 Flaherty Drive | [way 1437043939](https://www.openstreetmap.org/way/1437043939) | `13;14` | `13-14` |
| 115 | 75 Flaherty Drive | [way 1437043940](https://www.openstreetmap.org/way/1437043940) | `17;18` | `17-18` |
| 116 | 75 Flaherty Drive | [way 1437043941](https://www.openstreetmap.org/way/1437043941) | `19;20` | `19-20` |
| 117 | 75 Flaherty Drive | [way 1437043942](https://www.openstreetmap.org/way/1437043942) | `25;26` | `25-26` |
| 118 | 75 Flaherty Drive | [way 1437043943](https://www.openstreetmap.org/way/1437043943) | `23;24` | `23-24` |
| 119 | 75 Flaherty Drive | [way 1437043944](https://www.openstreetmap.org/way/1437043944) | `21;22` | `21-22` |
| 120 | 75 Flaherty Drive | [way 912221550](https://www.openstreetmap.org/way/912221550) | `39;40` | `39-40` |
| 121 | 75 Flaherty Drive | [way 912221551](https://www.openstreetmap.org/way/912221551) | `43;44` | `43-44` |
| 122 | 75 Flaherty Drive | [way 912221552](https://www.openstreetmap.org/way/912221552) | `47;48` | `47-48` |
| 123 | 75 Flaherty Drive | [way 912221553](https://www.openstreetmap.org/way/912221553) | `27;28` | `27-28` |
| 124 | 75 Flaherty Drive | [way 912221554](https://www.openstreetmap.org/way/912221554) | `15;16` | `15-16` |
| 125 | 75 Flaherty Drive | [way 912221556](https://www.openstreetmap.org/way/912221556) | `29;30` | `29-30` |
| 126 | 75 Flaherty Drive | [way 912221557](https://www.openstreetmap.org/way/912221557) | `1;2` | `1-2` |
| 127 | 75 Flaherty Drive | [way 912221558](https://www.openstreetmap.org/way/912221558) | `7;8` | `7-8` |
| 128 | 65 Frederick Drive | [way 950227736](https://www.openstreetmap.org/way/950227736) | `1;2;3;4;5;6` | `1-6` |
| 129 | 100 Frederick Drive | [way 802540407](https://www.openstreetmap.org/way/802540407) | `1;10;11;12;13;14;15;16;2;3;4;5;6;7;8;9` | `1-16` |
| 130 | 101 Frederick Drive | [way 802540411](https://www.openstreetmap.org/way/802540411) | `1;10;11;12;13;14;15;16;2;3;4;5;6;7;8;9` | `1-16` |
| 131 | 31 Gordon Street | [way 413398803](https://www.openstreetmap.org/way/413398803) | `11;12;14;15;A14;16;17;18;19;2B;1A;A2;1;2;3;4;5;6;7;8;9;20;10` | `1-12;1A;2B;14-20;A2;A14` |
| 132 | 220 Gordon Street | [way 802817805](https://www.openstreetmap.org/way/802817805) | `11;12;14;15;16;17;21;22;23;24;25;26;31;32;33;34;35;36` | `11-12;14-17;21-26;31-36` |
| 133 | 803 Gordon Street | [way 743421919](https://www.openstreetmap.org/way/743421919) | `1;10;11;12;13;14;15;2;3;4;5;6;7;8;9` | `1-15` |
| 134 | 807 Gordon Street | [way 743421918](https://www.openstreetmap.org/way/743421918) | `1;10;11;12;2;3;4;5;6;7;8;9` | `1-12` |
| 135 | 941 Gordon Street | [way 800638895](https://www.openstreetmap.org/way/800638895) | `65;66;67;68` | `65-68` |
| 136 | 941 Gordon Street | [way 800638896](https://www.openstreetmap.org/way/800638896) | `61;62;63;64` | `61-64` |
| 137 | 941 Gordon Street | [way 800638897](https://www.openstreetmap.org/way/800638897) | `57;58;59;60` | `57-60` |
| 138 | 941 Gordon Street | [way 800638898](https://www.openstreetmap.org/way/800638898) | `53;54;55;56` | `53-56` |
| 139 | 941 Gordon Street | [way 800638899](https://www.openstreetmap.org/way/800638899) | `49;50;51;52` | `49-52` |
| 140 | 941 Gordon Street | [way 800638900](https://www.openstreetmap.org/way/800638900) | `45;46;47;48` | `45-48` |
| 141 | 941 Gordon Street | [way 800638901](https://www.openstreetmap.org/way/800638901) | `41;42;43;44` | `41-44` |
| 142 | 941 Gordon Street | [way 800638902](https://www.openstreetmap.org/way/800638902) | `37;38;39;40` | `37-40` |
| 143 | 941 Gordon Street | [way 800638903](https://www.openstreetmap.org/way/800638903) | `21;22;23;24` | `21-24` |
| 144 | 941 Gordon Street | [way 800638904](https://www.openstreetmap.org/way/800638904) | `17;18;19;20` | `17-20` |
| 145 | 941 Gordon Street | [way 800638905](https://www.openstreetmap.org/way/800638905) | `13;14;15;16` | `13-16` |
| 146 | 941 Gordon Street | [way 800638906](https://www.openstreetmap.org/way/800638906) | `10;11;12;9` | `9-12` |
| 147 | 941 Gordon Street | [way 800638907](https://www.openstreetmap.org/way/800638907) | `5;6;7;8` | `5-8` |
| 148 | 941 Gordon Street | [way 800638908](https://www.openstreetmap.org/way/800638908) | `1;2;3;4` | `1-4` |
| 149 | 941 Gordon Street | [way 800638909](https://www.openstreetmap.org/way/800638909) | `33;34;35;36` | `33-36` |
| 150 | 941 Gordon Street | [way 800638910](https://www.openstreetmap.org/way/800638910) | `29;30;31;32` | `29-32` |
| 151 | 941 Gordon Street | [way 800638911](https://www.openstreetmap.org/way/800638911) | `25;26;27;28` | `25-28` |
| 152 | 941 Gordon Street | [way 800638912](https://www.openstreetmap.org/way/800638912) | `69;70;71;72` | `69-72` |
| 153 | 1131 Gordon Street | [way 1156180354](https://www.openstreetmap.org/way/1156180354) | `1;2;3;4;5;6;7;8` | `1-8` |
| 154 | 1467 Gordon Street | [way 399342891](https://www.openstreetmap.org/way/399342891) | `1;2;3` | `1-3` |
| 155 | 1886 Gordon Street | [way 961839908](https://www.openstreetmap.org/way/961839908) | `101;102;201;202` | `101-102;201-202` |
| 156 | 265 Hanlon Creek Boulevard | [way 794182126](https://www.openstreetmap.org/way/794182126) | `1;3;4;5;9` | `1;3-5;9` |
| 157 | 275 Hanlon Creek Boulevard | [way 794182120](https://www.openstreetmap.org/way/794182120) | `1;2;3;4;5` | `1-5` |
| 158 | 39 Kay Crescent | [way 1443052881](https://www.openstreetmap.org/way/1443052881) | `32;33` | `32-33` |
| 159 | 39 Kay Crescent | [way 1443052882](https://www.openstreetmap.org/way/1443052882) | `34;35` | `34-35` |
| 160 | 39 Kay Crescent | [way 1443052883](https://www.openstreetmap.org/way/1443052883) | `36;37` | `36-37` |
| 161 | 39 Kay Crescent | [way 1443052884](https://www.openstreetmap.org/way/1443052884) | `46;47` | `46-47` |
| 162 | 39 Kay Crescent | [way 1443052885](https://www.openstreetmap.org/way/1443052885) | `44;45` | `44-45` |
| 163 | 39 Kay Crescent | [way 1443052886](https://www.openstreetmap.org/way/1443052886) | `42;43` | `42-43` |
| 164 | 39 Kay Crescent | [way 802540386](https://www.openstreetmap.org/way/802540386) | `12;13;14;15;16;17;18;19;20;21` | `12-21` |
| 165 | 39 Kay Crescent | [way 802540388](https://www.openstreetmap.org/way/802540388) | `38;39` | `38-39` |
| 166 | 39 Kay Crescent | [way 802540389](https://www.openstreetmap.org/way/802540389) | `40;41` | `40-41` |
| 167 | 25 Manor Park Crescent | [way 802811015](https://www.openstreetmap.org/way/802811015) | `13;14;15` | `13-15` |
| 168 | 16 Marilyn Drive | [way 802124534](https://www.openstreetmap.org/way/802124534) | `101;102;103;104;105;201;202;203;204;205;206;301;302;303;304;305;306` | `101-105;201-206;301-306` |
| 169 | 27 Monarch Road | [way 802121047](https://www.openstreetmap.org/way/802121047) | `1;2;3;4;5;6` | `1-6` |
| 170 | 1 Mont Street | [node 13164297972](https://www.openstreetmap.org/node/13164297972) | `1;2;3;4;5;6` | `1-6` |
| 171 | 83 Neeve Street | [way 356650876](https://www.openstreetmap.org/way/356650876) | `1;2;3;4;5;6;7` | `1-7` |
| 172 | 110 Norwich Street East | [node 13165533695](https://www.openstreetmap.org/node/13165533695) | `1;2;4` | `1-2;4` |
| 173 | 21 Quebec Street | [node 13159082381](https://www.openstreetmap.org/node/13159082381) | `202;203;204` | `202-204` |
| 174 | 49 Rhonda Road | [way 1441651844](https://www.openstreetmap.org/way/1441651844) | `98;99` | `98-99` |
| 175 | 49 Rhonda Road | [way 1441651845](https://www.openstreetmap.org/way/1441651845) | `94;95` | `94-95` |
| 176 | 49 Rhonda Road | [way 1441651846](https://www.openstreetmap.org/way/1441651846) | `84;85` | `84-85` |
| 177 | 49 Rhonda Road | [way 1441651847](https://www.openstreetmap.org/way/1441651847) | `88;89` | `88-89` |
| 178 | 49 Rhonda Road | [way 1441651848](https://www.openstreetmap.org/way/1441651848) | `90;91` | `90-91` |
| 179 | 49 Rhonda Road | [way 1441651849](https://www.openstreetmap.org/way/1441651849) | `92;93` | `92-93` |
| 180 | 49 Rhonda Road | [way 1441651850](https://www.openstreetmap.org/way/1441651850) | `96;97` | `96-97` |
| 181 | 49 Rhonda Road | [way 1441651851](https://www.openstreetmap.org/way/1441651851) | `100;101` | `100-101` |
| 182 | 49 Rhonda Road | [way 1441651852](https://www.openstreetmap.org/way/1441651852) | `102;103` | `102-103` |
| 183 | 49 Rhonda Road | [way 1441651853](https://www.openstreetmap.org/way/1441651853) | `104;105` | `104-105` |
| 184 | 49 Rhonda Road | [way 1441651854](https://www.openstreetmap.org/way/1441651854) | `106;107` | `106-107` |
| 185 | 49 Rhonda Road | [way 1441651855](https://www.openstreetmap.org/way/1441651855) | `108;109` | `108-109` |
| 186 | 49 Rhonda Road | [way 1441651856](https://www.openstreetmap.org/way/1441651856) | `110;111` | `110-111` |
| 187 | 49 Rhonda Road | [way 1441651910](https://www.openstreetmap.org/way/1441651910) | `128;129` | `128-129` |
| 188 | 49 Rhonda Road | [way 1441651911](https://www.openstreetmap.org/way/1441651911) | `126;127` | `126-127` |
| 189 | 49 Rhonda Road | [way 1441651912](https://www.openstreetmap.org/way/1441651912) | `122;123` | `122-123` |
| 190 | 49 Rhonda Road | [way 1441651913](https://www.openstreetmap.org/way/1441651913) | `118;119` | `118-119` |
| 191 | 49 Rhonda Road | [way 1441651914](https://www.openstreetmap.org/way/1441651914) | `116;117` | `116-117` |
| 192 | 49 Rhonda Road | [way 1441651915](https://www.openstreetmap.org/way/1441651915) | `124;125` | `124-125` |
| 193 | 49 Rhonda Road | [way 1441651916](https://www.openstreetmap.org/way/1441651916) | `130;131` | `130-131` |
| 194 | 49 Rhonda Road | [way 1441651917](https://www.openstreetmap.org/way/1441651917) | `114;115` | `114-115` |
| 195 | 49 Rhonda Road | [way 803276519](https://www.openstreetmap.org/way/803276519) | `112;113` | `112-113` |
| 196 | 49 Rhonda Road | [way 803276525](https://www.openstreetmap.org/way/803276525) | `120;121` | `120-121` |
| 197 | 49 Rhonda Road | [way 803276526](https://www.openstreetmap.org/way/803276526) | `86;87` | `86-87` |
| 198 | 649 Scottsdale Drive | [way 212559742](https://www.openstreetmap.org/way/212559742) | `100;101` | `100-101` |
| 199 | 649 Scottsdale Drive | [way 212559745](https://www.openstreetmap.org/way/212559745) | `1;2;2B;3;4;5` | `1-5;2B` |
| 200 | 20 Shackleton Drive | [way 942414532](https://www.openstreetmap.org/way/942414532) | `44;45;46;47` | `44-47` |
| 201 | 40 Silvercreek Parkway North | [way 1442367349](https://www.openstreetmap.org/way/1442367349) | `47;48` | `47-48` |
| 202 | 106 Silvercreek Parkway North | [way 208492557](https://www.openstreetmap.org/way/208492557) | `1;2;4;5;7` | `1-2;4-5;7` |
| 203 | 200 Southgate Drive | [way 208650114](https://www.openstreetmap.org/way/208650114) | `1;2;3` | `1-3` |
| 204 | 245 Southgate Drive | [way 337955594](https://www.openstreetmap.org/way/337955594) | `10;11;12;7;8;9` | `7-12` |
| 205 | 245 Southgate Drive | [way 337955609](https://www.openstreetmap.org/way/337955609) | `1;2;3;4;5;6` | `1-6` |
| 206 | 304 Stone Road West | [way 215069452](https://www.openstreetmap.org/way/215069452) | `1;2;3;4` | `1-4` |
| 207 | 304 Stone Road West | [way 215069453](https://www.openstreetmap.org/way/215069453) | `10;11;12;7;8;9` | `7-12` |
| 208 | 10 Stuart Street | [way 929589622](https://www.openstreetmap.org/way/929589622) | `1;10;2;3;4;5;6;7;8;9` | `1-10` |
| 209 | 57 Suffolk Street West | [way 925775200](https://www.openstreetmap.org/way/925775200) | `101;102;203;204;305;306;407;408;PH` | `101-102;203-204;305-306;407-408;PH` |
| 210 | 108 Summit Ridge Drive | [way 803283669](https://www.openstreetmap.org/way/803283669) | `101-112;201-212;301-312;401-412;LL01;LL02;LL03;LL04;` | `101-112;201-212;301-312;401-412;LL01-LL04` |
| 211 | 1 Sunnylea Crescent | [way 802125028](https://www.openstreetmap.org/way/802125028) | `1;2;3;4;5;6;7;8` | `1-8` |
| 212 | 2 Sunnylea Crescent | [way 802125026](https://www.openstreetmap.org/way/802125026) | `1;2;3;4;5;6;7;8` | `1-8` |
| 213 | 3 Sunnylea Crescent | [way 802125029](https://www.openstreetmap.org/way/802125029) | `1;2;3;4;5;6;7;8` | `1-8` |
| 214 | 4 Sunnylea Crescent | [way 802125027](https://www.openstreetmap.org/way/802125027) | `1;2;3;4;5;6;7;8` | `1-8` |
| 215 | 47 Surrey Street East | [way 1431616569](https://www.openstreetmap.org/way/1431616569) | `3C;1;2;4;5;6;7;8;3A;3B` | `1-2;3A;3B;3C;4-8` |
| 216 | 49 Surrey Street East | [way 493155848](https://www.openstreetmap.org/way/493155848) | `11;22;23A;23B;33A;33B;23C;33C;31;32;21` | `11;21-22;23A;23B;23C;31-32;33A;33B;33C` |
| 217 | 199 Victoria Road South | [way 260551704](https://www.openstreetmap.org/way/260551704) | `1;2;3;4;5;6;7;8` | `1-8` |
| 218 | 119 Water Street | [way 802815631](https://www.openstreetmap.org/way/802815631) | `101;102;103;104;201;202;203;204` | `101-104;201-204` |
| 219 | 121 Waterloo Avenue | [way 923609578](https://www.openstreetmap.org/way/923609578) | `110;101;102;103;104;105;106;107;108;109` | `101-110` |
| 220 | 360 Waterloo Avenue | [way 819734214](https://www.openstreetmap.org/way/819734214) | `107;108;209;210;211;212` | `107-108;209-212` |
| 221 | 70 Watson Parkway South | [way 802544817](https://www.openstreetmap.org/way/802544817) | `1;2;3;4;5;6;7;8` | `1-8` |
| 222 | 3 Watson Road South | [way 802544833](https://www.openstreetmap.org/way/802544833) | `1;2;3;8` | `1-3;8` |
| 223 | 120 Westmount Road | [way 1369220540](https://www.openstreetmap.org/way/1369220540) | `13;14` | `13-14` |
| 224 | 120 Westmount Road | [way 1369220544](https://www.openstreetmap.org/way/1369220544) | `15;16` | `15-16` |
| 225 | 100 Woodlawn Road East | [way 803281467](https://www.openstreetmap.org/way/803281467) | `5;6` | `5-6` |
| 226 | 100 Woodlawn Road East | [way 803281468](https://www.openstreetmap.org/way/803281468) | `1;2` | `1-2` |
| 227 | 100 Woodlawn Road East | [way 954036919](https://www.openstreetmap.org/way/954036919) | `3;4` | `3-4` |
| 228 | 100 Woodlawn Road East | [way 954036924](https://www.openstreetmap.org/way/954036924) | `7;8` | `7-8` |
| 229 | 200 Woolwich Street | [way 123242060](https://www.openstreetmap.org/way/123242060) | `101;102;201;103;202;203;204` | `101-103;201-204` |
| 230 | 560 Woolwich Street | [way 882913721](https://www.openstreetmap.org/way/882913721) | `A1;A2;A3;A4;A5;A6;A7;A8;A9` | `A1-A9` |
| 231 | 560 Woolwich Street | [way 882913722](https://www.openstreetmap.org/way/882913722) | `B1;B2;B3;B4;B5;B6;B7;B8;B9` | `B1-B9` |
| 232 | 116 Wyndham Street North | [node 13159082353](https://www.openstreetmap.org/node/13159082353) | `1;2;3;4` | `1-4` |
| 233 | 143 Wyndham Street North | [way 1344915931](https://www.openstreetmap.org/way/1344915931) | `201;202;203;204;301` | `201-204;301` |
| 234 | 31 Yarmouth Street | [node 12314152369](https://www.openstreetmap.org/node/12314152369) | `101;201;301;202;302;203;303;204;304;106;205;305;206;107;306;207;307` | `101;106-107;201-207;301-307` |
| 235 | 561 York Road | [way 1054125923](https://www.openstreetmap.org/way/1054125923) | `1;2;3;4` | `1-4` |

## Re-sorted numerically instead of as text — 14

| # | Address | Object | Before | After |
|---|---|---|---|---|
| 1 | 10 Ajax Street | [way 502064546](https://www.openstreetmap.org/way/502064546) | `401-409;201-209;301-309;101-108` | `101-108;201-209;301-309;401-409` |
| 2 | 5 Gordon Street | [node 13150618373](https://www.openstreetmap.org/node/13150618373) | `202;302;402;502;602;102B` | `102B;202;302;402;502;602` |
| 3 | 5 Gordon Street | [node 13150618374](https://www.openstreetmap.org/node/13150618374) | `201;301;401;501;601;102A` | `102A;201;301;401;501;601` |
| 4 | 5 Gordon Street | [node 13150618376](https://www.openstreetmap.org/node/13150618376) | `212;312;412;107` | `107;212;312;412` |
| 5 | 5 Gordon Street | [node 13150618377](https://www.openstreetmap.org/node/13150618377) | `211;311;411;106` | `106;211;311;411` |
| 6 | 5 Gordon Street | [node 13150618378](https://www.openstreetmap.org/node/13150618378) | `210;310;410;105` | `105;210;310;410` |
| 7 | 160 MacDonell Street | [way 177696219](https://www.openstreetmap.org/way/177696219) | `101;1001-1009;1101-1109;1201-1209;1301-1309;1401-1409;1501-1509;1601-1609;1701-1705;1801-1804;301-308;401-406;501-509;601-609;701-709;801-809;901-909;` | `101;301-308;401-406;501-509;601-609;701-709;801-809;901-909;1001-1009;1101-1109;1201-1209;1301-1309;1401-1409;1501-1509;1601-1609;1701-1705;1801-1804` |
| 8 | 24 Marilyn Drive | [way 178085152](https://www.openstreetmap.org/way/178085152) | `1001-1006;101-103;201-205;301-306;401-406;501-506;601-606;701-706;801-806;901-906;` | `101-103;201-205;301-306;401-406;501-506;601-606;701-706;801-806;901-906;1001-1006` |
| 9 | 65 Silvercreek Parkway North | [way 502064544](https://www.openstreetmap.org/way/502064544) | `201-210;301-311;101-109;401-410` | `101-109;201-210;301-311;401-410` |
| 10 | 75 Silvercreek Parkway North | [way 502064545](https://www.openstreetmap.org/way/502064545) | `401-408;201-208;301-308;101-107` | `101-107;201-208;301-308;401-408` |
| 11 | 358 Waterloo Avenue | [way 819734215](https://www.openstreetmap.org/way/819734215) | `1001-1008;1101-1108;101-106;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908;` | `101-106;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908;1001-1008;1101-1108` |
| 12 | 150 Wellington Street East | [way 675436618](https://www.openstreetmap.org/way/675436618) | `1001-1008;101-104;1101-1108;1201-1208;1301-1308;1401-1408;1501-1508;1601-1606;1701-1704;1801-1802;301-314;401-414;501-514;601-614;701-707;801-808;901-908;` | `101-104;301-314;401-414;501-514;601-614;701-707;801-808;901-908;1001-1008;1101-1108;1201-1208;1301-1308;1401-1408;1501-1508;1601-1606;1701-1704;1801-1802` |
| 13 | 120 Westmount Road | [way 1369220542](https://www.openstreetmap.org/way/1369220542) | `11;9` | `9;11` |
| 14 | 60 Wyndham Street South | [way 177695409](https://www.openstreetmap.org/way/177695409) | `1001-1012;101-112;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-912;` | `101-112;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-912;1001-1012` |

## Trailing `;` dropped — 49

| # | Address | Object | Before | After |
|---|---|---|---|---|
| 1 | 107 Bagot Street | [way 208356615](https://www.openstreetmap.org/way/208356615) | `101-113;201-215;301-315;401-415;501-515;601-615;` | `101-113;201-215;301-315;401-415;501-515;601-615` |
| 2 | 106 Bard Boulevard | [way 878035921](https://www.openstreetmap.org/way/878035921) | `101-114;201-220;301-320;401-418;` | `101-114;201-220;301-320;401-418` |
| 3 | 2 Colonial Drive | [way 878035915](https://www.openstreetmap.org/way/878035915) | `101-110;201-211;301-313;401-414;` | `101-110;201-211;301-313;401-414` |
| 4 | 120 Country Club Drive | [way 761343575](https://www.openstreetmap.org/way/761343575) | `11;12;14-33;` | `11-12;14-33` |
| 5 | 395 Edinburgh Road North | [way 1042083497](https://www.openstreetmap.org/way/1042083497) | `105-108;110-114;201-207;209-213;217;301-307;309-313;317;401-407;409-417;501-507;509-513;517;601-607;609-613;617;701-707;709-713;717;` | `105-108;110-114;201-207;209-213;217;301-307;309-313;317;401-407;409-417;501-507;509-513;517;601-607;609-613;617;701-707;709-713;717` |
| 6 | 37 Goodwin Drive | [way 287908449](https://www.openstreetmap.org/way/287908449) | `101-113;201-214;301-314;401-414;` | `101-113;201-214;301-314;401-414` |
| 7 | 39 Goodwin Drive | [way 287908442](https://www.openstreetmap.org/way/287908442) | `101-111;201-212;301-312;401-412;` | `101-111;201-212;301-312;401-412` |
| 8 | 41 Goodwin Drive | [way 287908447](https://www.openstreetmap.org/way/287908447) | `101-111;201-212;301-312;401-412;` | `101-111;201-212;301-312;401-412` |
| 9 | 43 Goodwin Drive | [way 287908444](https://www.openstreetmap.org/way/287908444) | `101-113;201-214;301-314;401-414;` | `101-113;201-214;301-314;401-414` |
| 10 | 45 Goodwin Drive | [way 287908445](https://www.openstreetmap.org/way/287908445) | `101-111;201-212;301-312;401-412;` | `101-111;201-212;301-312;401-412` |
| 11 | 1077 Gordon Street | [way 801555971](https://www.openstreetmap.org/way/801555971) | `112-142;212-242;312-342;412-442;` | `112-142;212-242;312-342;412-442` |
| 12 | 1083 Gordon Street | [way 801555970](https://www.openstreetmap.org/way/801555970) | `101-111;201-211;301-311;401-411;` | `101-111;201-211;301-311;401-411` |
| 13 | 1219 Gordon Street | [way 659406271](https://www.openstreetmap.org/way/659406271) | `101-108;201-211;301-315;401-415;501-515;601-613;A;B;C;` | `101-108;201-211;301-315;401-415;501-515;601-613;A;B;C` |
| 14 | 1280 Gordon Street | [way 499045964](https://www.openstreetmap.org/way/499045964) | `101-118;201-219;301-319;401-419;` | `101-118;201-219;301-319;401-419` |
| 15 | 1284 Gordon Street | [way 499049867](https://www.openstreetmap.org/way/499049867) | `101-131;201-231;301-331;401-431;` | `101-131;201-231;301-331;401-431` |
| 16 | 1291 Gordon Street | [way 499046190](https://www.openstreetmap.org/way/499046190) | `101-125;201-227;301-327;401-427;501-527;601-627;` | `101-125;201-227;301-327;401-427;501-527;601-627` |
| 17 | 1440 Gordon Street | [way 801657260](https://www.openstreetmap.org/way/801657260) | `101-122;201-223;301-323;401-423;` | `101-122;201-223;301-323;401-423` |
| 18 | 1878 Gordon Street | [way 862511297](https://www.openstreetmap.org/way/862511297) | `101-116;201-215;301-314;401-414;501-514;601-614;701-714;801-814;901-914;1001-1014;1101-1114;1201-1206;1301-1305;1401-1404;` | `101-116;201-215;301-314;401-414;501-514;601-614;701-714;801-814;901-914;1001-1014;1101-1114;1201-1206;1301-1305;1401-1404` |
| 19 | 1880 Gordon Street | [way 862511298](https://www.openstreetmap.org/way/862511298) | `101-115;201-215;301-314;401-414;501-514;601-614;701-714;801-814;901-914;1001-1014;1101-1114;1201-1206;1301-1306;1401-1404;` | `101-115;201-215;301-314;401-414;501-514;601-614;701-714;801-814;901-914;1001-1014;1101-1114;1201-1206;1301-1306;1401-1404` |
| 20 | 1882 Gordon Street | [node 13241233182](https://www.openstreetmap.org/node/13241233182) | `101-115;201-209;301-312;401-412;501-512;601-612;701-712;801-805;` | `101-115;201-209;301-312;401-412;501-512;601-612;701-712;801-805` |
| 21 | 1884 Gordon Street | [node 13241233183](https://www.openstreetmap.org/node/13241233183) | `101-114;201-214;301-312;401-412;501-512;601-612;701-712;801-805;` | `101-114;201-214;301-312;401-412;501-512;601-612;701-712;801-805` |
| 22 | 415 Grange Road | [way 333632635](https://www.openstreetmap.org/way/333632635) | `101-111;201-213;301-313;401-413;` | `101-111;201-213;301-313;401-413` |
| 23 | 142 Imperial Road North | [way 557515464](https://www.openstreetmap.org/way/557515464) | `101-108;201-208;301-308;401-408;` | `101-108;201-208;301-308;401-408` |
| 24 | 146 Imperial Road North | [way 557515432](https://www.openstreetmap.org/way/557515432) | `101-108;201-208;301-308;401-408;` | `101-108;201-208;301-308;401-408` |
| 25 | 150 Imperial Road North | [way 557515399](https://www.openstreetmap.org/way/557515399) | `101-108;201-208;301-308;401-408;` | `101-108;201-208;301-308;401-408` |
| 26 | 7 Kay Crescent | [way 741807532](https://www.openstreetmap.org/way/741807532) | `101-113;201-215;301-315;401-415;501-515;601-615;LL01-LL06;` | `101-113;201-215;301-315;401-415;501-515;601-615;LL01-LL06` |
| 27 | 17 Kay Crescent | [way 900493343](https://www.openstreetmap.org/way/900493343) | `101-111;201-212;301-312;401-412;` | `101-111;201-212;301-312;401-412` |
| 28 | 25 Kay Crescent | [way 900493342](https://www.openstreetmap.org/way/900493342) | `101-114;201-214;301-314;401-414;LL02;LL04;LL06;LL08;LL10;LL12;LL14;` | `101-114;201-214;301-314;401-414;LL02;LL04;LL06;LL08;LL10;LL12;LL14` |
| 29 | 35 Kingsbury Square | [way 837634910](https://www.openstreetmap.org/way/837634910) | `101-109;116-127;201-210;212;214-227;301-327;401-427;` | `101-109;116-127;201-210;212;214-227;301-327;401-427` |
| 30 | 45 Kingsbury Square | [way 802540405](https://www.openstreetmap.org/way/802540405) | `101-112;201-214;301-314;401-414;` | `101-112;201-214;301-314;401-414` |
| 31 | 67 Kingsbury Square | [way 802540406](https://www.openstreetmap.org/way/802540406) | `101-112;201-214;301-314;401-414;` | `101-112;201-214;301-314;401-414` |
| 32 | 26 Lowes Road West | [way 1004013623](https://www.openstreetmap.org/way/1004013623) | `101-108;110;112;201-216;301-316;401-416;501-514;601-614;` | `101-108;110;112;201-216;301-316;401-416;501-514;601-614` |
| 33 | 60 Lynnmore Street | [way 287946730](https://www.openstreetmap.org/way/287946730) | `101-112;201-214;301-314;401-414;` | `101-112;201-214;301-314;401-414` |
| 34 | 160 MacDonell Street | [way 177696219](https://www.openstreetmap.org/way/177696219) | `101;1001-1009;1101-1109;1201-1209;1301-1309;1401-1409;1501-1509;1601-1609;1701-1705;1801-1804;301-308;401-406;501-509;601-609;701-709;801-809;901-909;` | `101;301-308;401-406;501-509;601-609;701-709;801-809;901-909;1001-1009;1101-1109;1201-1209;1301-1309;1401-1409;1501-1509;1601-1609;1701-1705;1801-1804` |
| 35 | 22 Marilyn Drive | [way 178085148](https://www.openstreetmap.org/way/178085148) | `103-108;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908;` | `103-108;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908` |
| 36 | 24 Marilyn Drive | [way 178085152](https://www.openstreetmap.org/way/178085152) | `1001-1006;101-103;201-205;301-306;401-406;501-506;601-606;701-706;801-806;901-906;` | `101-103;201-205;301-306;401-406;501-506;601-606;701-706;801-806;901-906;1001-1006` |
| 37 | 104 Summit Ridge Drive | [way 803283670](https://www.openstreetmap.org/way/803283670) | `101-112;201-212;301-312;401-412;` | `101-112;201-212;301-312;401-412` |
| 38 | 108 Summit Ridge Drive | [way 803283669](https://www.openstreetmap.org/way/803283669) | `101-112;201-212;301-312;401-412;LL01;LL02;LL03;LL04;` | `101-112;201-212;301-312;401-412;LL01-LL04` |
| 39 | 19 Waterford Drive | [way 287946734](https://www.openstreetmap.org/way/287946734) | `101-112;201-214;301-314;401-414;` | `101-112;201-214;301-314;401-414` |
| 40 | 43 Waterford Drive | [way 287946731](https://www.openstreetmap.org/way/287946731) | `101-112;201-214;301-314;401-414;` | `101-112;201-214;301-314;401-414` |
| 41 | 358 Waterloo Avenue | [way 819734215](https://www.openstreetmap.org/way/819734215) | `1001-1008;1101-1108;101-106;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908;` | `101-106;201-208;301-308;401-408;501-508;601-608;701-708;801-808;901-908;1001-1008;1101-1108` |
| 42 | 308 Watson Parkway North | [way 941667226](https://www.openstreetmap.org/way/941667226) | `101-120;201-221;301-321;401-421;` | `101-120;201-221;301-321;401-421` |
| 43 | 150 Wellington Street East | [way 675436618](https://www.openstreetmap.org/way/675436618) | `1001-1008;101-104;1101-1108;1201-1208;1301-1308;1401-1408;1501-1508;1601-1606;1701-1704;1801-1802;301-314;401-414;501-514;601-614;701-707;801-808;901-908;` | `101-104;301-314;401-414;501-514;601-614;701-707;801-808;901-908;1001-1008;1101-1108;1201-1208;1301-1308;1401-1408;1501-1508;1601-1606;1701-1704;1801-1802` |
| 44 | 19 Woodlawn Road East | [way 178085150](https://www.openstreetmap.org/way/178085150) | `101-115;201-216;301-316;401-416;501-516;601-616;701-716;801-816;901-915;` | `101-115;201-216;301-316;401-416;501-516;601-616;701-716;801-816;901-915` |
| 45 | 23 Woodlawn Road East | [way 178085151](https://www.openstreetmap.org/way/178085151) | `101-110;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-909;911;` | `101-110;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-909;911` |
| 46 | 70 Woodlawn Road East | [way 1436028337](https://www.openstreetmap.org/way/1436028337) | `101-114;201-218;301-318;` | `101-114;201-218;301-318` |
| 47 | 72 Woodlawn Road East | [way 353492157](https://www.openstreetmap.org/way/353492157) | `101-103;201-207;301-307;401-407;501-507;601-607;` | `101-103;201-207;301-307;401-407;501-507;601-607` |
| 48 | 60 Wyndham Street South | [way 177695409](https://www.openstreetmap.org/way/177695409) | `1001-1012;101-112;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-912;` | `101-112;201-212;301-312;401-412;501-512;601-612;701-712;801-812;901-912;1001-1012` |
| 49 | 55 Yarmouth Street | [node 12314155787](https://www.openstreetmap.org/node/12314155787) | `201-209; 301-309; 401-409; 501-509; 601-609; 701-709; 801-809; 901-909;` | `201-209;301-309;401-409;501-509;601-609;701-709;801-809;901-909` |

## Spaces around `;` dropped — 2

| # | Address | Object | Before | After |
|---|---|---|---|---|
| 1 | 55 Yarmouth Street | [node 12314155787](https://www.openstreetmap.org/node/12314155787) | `201-209; 301-309; 401-409; 501-509; 601-609; 701-709; 801-809; 901-909;` | `201-209;301-309;401-409;501-509;601-609;701-709;801-809;901-909` |
| 2 | 86 Yarmouth Street | [way 409855358](https://www.openstreetmap.org/way/409855358) | `101-104; 201-208; 301-306` | `101-104;201-208;301-306` |
