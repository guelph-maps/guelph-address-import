"""Tests for the `addr:flats` parser, including the round-trip over live OSM.

    python test_flats_parse.py      # no pytest needed
    python -m pytest test_flats_parse.py -q

Plain stdlib only — `xml.etree` for the fetch, nothing from `_common` (which
wants `requests` and `shapely`). The parser itself needs the engine on the
path, which `flats_parse` arranges.

The last test is the one that matters. `test_every_live_value_round_trips`
reads all 464 `addr:flats` values out of `live.osm` and asserts that the unit
set is identical before and after normalising. The rest are the individual
cases that test would not have localised: a failure there says *some value*
is mangled, and the named tests say *which shape*.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest import SkipTest
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent))

from flats_parse import normalise, parse_flats  # noqa: E402

HERE = Path(__file__).resolve().parent
LIVE = HERE / "live.osm"


class Skip(SkipTest):
    """`live.osm` is gitignored — derived, and stale on contact. A fresh clone
    has the parser tests but not the data they run against, and that should
    read as "fetch it" rather than as a failure. Subclassing `SkipTest` means
    pytest reports it as a skip too, without pytest being imported here."""


def _live_values() -> list[tuple[str, str, str]]:
    """(type, id, value) for every `addr:flats` in the cached fetch."""
    if not LIVE.exists():
        raise Skip(f"{LIVE.name} is not here — it is derived and gitignored. "
                   f"Run `build_batches.py --refetch` first.")
    root = ET.parse(LIVE).getroot()
    out = []
    for el in root:
        if el.tag not in ("node", "way", "relation"):
            continue
        for tag in el.findall("tag"):
            if tag.attrib["k"] == "addr:flats":
                out.append((el.tag, el.attrib["id"], tag.attrib["v"]))
    return out


# --- the defects the campaign exists to fix ---------------------------------

def test_an_enumeration_collapses_to_a_range():
    # 39 Kay Crescent. 110 of the live values are enumerations like this.
    assert normalise("12;13;14;15;16;17;18;19;20;21") == ("12-21", "")


def test_a_trailing_semicolon_goes():
    # 49 of the live values end in one. Spotted on campaign 3's pilot, which
    # is where this campaign started.
    assert normalise("101-113;201-214;301-314;401-414;")[0] == (
        "101-113;201-214;301-314;401-414")


def test_spaces_around_the_separator_go():
    # 55 Yarmouth Street, and one more like it.
    assert normalise("201-209; 301-309; 401-409;")[0] == (
        "201-209;301-309;401-409")


def test_floors_sort_numerically_not_as_text():
    # 358 Waterloo Avenue. The eleventh floor sorted above the first because
    # `1` precedes `2` as a character; the thousands belong at the end.
    value = "1001-1008;1101-1108;101-106;201-208;301-308"
    assert normalise(value)[0] == (
        "101-106;201-208;301-308;1001-1008;1101-1108")


def test_a_text_sorted_enumeration_becomes_one_range():
    # 245 Southgate Drive: 10;11;12;7;8;9.
    assert normalise("10;11;12;7;8;9") == ("7-12", "")


# --- the cases the parser must not mangle -----------------------------------

def test_building_letters_group_on_their_own():
    # A letter prefix names a building, not a floor, so D1xx and D2xx are two
    # runs and neither merges into the other or into a bare numeric run.
    value = "D101-D112;D201-D212"
    assert normalise(value) == (value, "")
    assert parse_flats("D101-D103")== ["D101", "D102", "D103"]


def test_a_letter_prefixed_run_never_merges_across_letters():
    # C112 and D101 are not neighbours however close their numbers look.
    assert normalise("C101-C102;D101-D102")[0] == "C101-C102;D101-D102"


def test_a_letter_suffix_cannot_join_a_range():
    # 511 Edinburgh Road South. 101A is one value: it is not unit 101, it is
    # not unit 102, and it must not be absorbed into 101-102.
    assert parse_flats("101A") == ["101A"]
    assert normalise("101;101A;102;201;202")[0] == "101-102;101A;201-202"


def test_ll_floors_are_a_real_prefix_and_keep_their_padding():
    # 108 Summit Ridge Drive. `LL` is the lower level, not a typo, and the
    # building signs it `LL01`. Rendering it `LL1` invents a designator — the
    # engine fix (t2.units.unit_pad) is what makes this pass.
    assert normalise("101-112;201-212;301-312;401-412;LL01;LL02;LL03;LL04;")[0] == (
        "101-112;201-212;301-312;401-412;LL01-LL04")


def test_a_padded_floor_that_runs_past_nine_stays_at_one_width():
    # 25 Kay Crescent: LL02..LL14 stepping by two, so LL02-LL08 are padded and
    # LL10-LL14 are two digits anyway.
    assert normalise("101-114;201-214;301-314;401-414;"
                     "LL02;LL04;LL06;LL08;LL10;LL12;LL14;")[0] == (
        "101-114;201-214;301-314;401-414;"
        "LL02;LL04;LL06;LL08;LL10;LL12;LL14")


def test_a_stepped_sequence_is_not_forced_into_a_range():
    # 176 Janefield Avenue is a row of small ways stepping by two: 224;234,
    # 226;232, 228;230. `224-234` would claim nine units that do not exist,
    # which is the one way this campaign could actually damage data.
    assert normalise("224;234") == ("224;234", "")
    assert normalise("2;4;6;8") == ("2;4;6;8", "")
    assert "-" not in normalise("2;4;6;8")[0]


def test_a_genuine_gap_still_breaks_the_run():
    # 23 Woodlawn Road East: 706 does not exist.
    assert normalise("701;702;703;704;705;707;708")[0] == "701-705;707-708"


def test_bare_letter_designators_survive():
    # 77 Yarmouth Street is `A;B;C;D`; 116 live tokens are bare letters.
    assert normalise("A;B;C;D") == ("A;B;C;D", "")


def test_letters_and_numbers_mix_without_either_being_lost():
    # 2 Taggart Street: 2;4A;6;8.
    value = "2;4A;6;8"
    assert set(parse_flats(normalise(value)[0])) == set(parse_flats(value))


# --- what the parser refuses ------------------------------------------------

def test_a_value_naming_nothing_is_refused_rather_than_emptied():
    # Returning "" here would delete the tag on an object nobody asked us to
    # strip. `changed()` would then read it as a real edit.
    assert parse_flats(";") is None
    assert parse_flats("") is None
    assert normalise("  ") == (None, "unparsed")


def test_a_backwards_range_is_refused():
    assert normalise("110-101") == (None, "unparsed")


def test_a_range_across_two_prefixes_is_refused():
    assert normalise("A1-B9") == (None, "unparsed")


def test_an_absurdly_wide_range_is_refused_rather_than_allocated():
    # MAX_RANGE_WIDTH, the engine's own ceiling. `1-1000` is a typo, not a
    # building, and expanding it would write a thousand designators.
    assert normalise("1-1000") == (None, "unparsed")
    assert normalise("1-500")[0] is not None


def test_a_designator_that_is_not_a_range_but_holds_a_hyphen_is_refused():
    # `PH-2` is one designator. The parser cannot tell it from a range, so it
    # refuses the whole value rather than guessing; it lands in review.csv.
    assert normalise("101;PH-2") == (None, "unparsed")


def test_duplicates_collapse_without_changing_the_unit_set():
    assert parse_flats("101;101;102") == ["101", "102"]
    assert normalise("101;101;102") == ("101-102", "")


# --- the gate ---------------------------------------------------------------

def test_every_live_value_round_trips():
    """No live `addr:flats` value may change which units it names.

    All 464 of them, from the cached fetch. A value that cannot be parsed, or
    whose normalised form names a different set, is a failure here and a
    `review.csv` row in the builder — never a batched edit.
    """
    values = _live_values()
    assert len(values) >= 400, f"only {len(values)} values read from {LIVE}"

    refused, mangled = [], []
    for kind, oid, value in values:
        before = parse_flats(value)
        if before is None:
            refused.append((kind, oid, value))
            continue
        rendered, reason = normalise(value)
        if reason:
            refused.append((kind, oid, value, reason))
            continue
        after = parse_flats(rendered)
        if set(after) != set(before):
            lost = sorted(set(before) - set(after))
            gained = sorted(set(after) - set(before))
            mangled.append((kind, oid, value, rendered, lost, gained))

    assert not mangled, "\n".join(
        f"{k} {i}: {v!r} -> {r!r} lost={lost} gained={gained}"
        for k, i, v, r, lost, gained in mangled)
    assert not refused, "\n".join(str(r) for r in refused)


def test_the_round_trip_would_actually_catch_a_mangled_value():
    """The gate above passes on every live value, so prove it can fail.

    A range that claimed the units between its ends — the mistake a naive
    "first to last" compressor makes on a stepped sequence — names units the
    original did not, and set comparison sees it.
    """
    stepped = parse_flats("2;4;6;8")
    naive = parse_flats("2-8")
    assert set(naive) != set(stepped)
    assert set(naive) - set(stepped) == {"3", "5", "7"}


def test_no_live_value_grows_past_the_osm_tag_limit():
    """Normalising shortens; this is the assertion that it never lengthens
    anything past the 255-character ceiling where a tag stops being uploadable.
    """
    worst_before = worst_after = 0
    for _kind, _oid, value in _live_values():
        rendered, reason = normalise(value)
        assert not reason, f"{value!r}: {reason}"
        worst_before = max(worst_before, len(value))
        worst_after = max(worst_after, len(rendered))
    assert worst_after <= 255, worst_after
    assert worst_after <= worst_before, (worst_before, worst_after)


def _main() -> int:
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
        except SkipTest as exc:
            skipped += 1
            print(f"skip {name}: {exc}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {name}\n     {exc}")
        except Exception as exc:  # noqa: BLE001 - report, do not abort the run
            failed += 1
            print(f"ERROR {name}: {type(exc).__name__}: {exc}")
        else:
            print(f"ok   {name}")
    print(f"\n{len(tests) - failed - skipped} passed, {failed} failed"
          + (f", {skipped} skipped" if skipped else ""))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_main())
