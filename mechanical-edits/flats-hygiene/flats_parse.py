"""Read an existing `addr:flats` value back into the units it names.

This is the *only* new code in mechanical edit 4+5's `addr:flats` half. The
rendering already exists: `t2/units.py` in the address-importer-friend engine
has `compress_flats()`, which the continuous import writes every collapsed
building through, and which produces exactly the form this campaign is
normalising towards — gap-broken runs inside one prefix, numeric order, no
trailing separator. Writing a second renderer here would give Guelph two
answers to "how is a flats list rendered", which is the complaint the campaign
exists to fix. So:

    existing value  ->  parse_flats  ->  compress_flats  ->  new value

and the parser is what has to be careful.

**What the parser refuses is as important as what it accepts.** A value it
cannot read with confidence returns `None` and goes to `review.csv`; it never
reaches a batch. The rules are deliberately the engine's own, so the two
agree:

* a part is a range only when both ends parse, share a letter prefix, share a
  letter suffix, and run forwards — the same test `t2.units.expand_listing`
  applies, and the same `MAX_RANGE_WIDTH` ceiling, so a typo like `1-1000`
  cannot allocate a thousand designators;
* `101A` has a letter suffix, so it is one value and can never be swallowed
  into a run. `compress_flats` enforces the other side of that;
* `D101-D112;D201-D212` is two runs under building letter D and never merges
  across letters — prefixes group on their own;
* `LL01;LL02;LL03` is a real lower-level floor, and its zero padding survives.
  That needed a fix in the engine (`unit_pad`, commit 054da405): rendering it
  as `LL1` invents a designator the building does not sign, and made three
  live Guelph values fail the round-trip below;
* an empty part is dropped, which is how the trailing `;` on 49 of the live
  values disappears;
* a whole value that names no unit at all returns `None` rather than the empty
  string, so normalising can never silently delete a tag.

`normalise()` is the function both the builder and the tests call, and it is
the round-trip gate: parse, render, parse the rendering, and demand the two
unit *sets* be identical. If normalising changes which units a building
claims, the parser is wrong, and that is data corruption rather than
cosmetics. Nothing is batched that has not passed it.

Stepped sequences are the case that makes the gate worth having. 25 Kay
Crescent's lower level runs `LL02;LL04;…;LL14`, and 176 Janefield Avenue steps
by two throughout; `compress_flats` emits each designator on its own rather
than inventing a range, and the round-trip proves it.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# The engine is not installed — not editable, not on the path — so `import
# t2.units` only resolves from inside its own directory. Point at it, with an
# override for a checkout that lives somewhere else. Reported as a gap; the
# alternative is copying the renderer, which is the thing not to do.
_ENGINE = Path(os.environ.get(
    "ADDRESS_IMPORTER_FRIEND",
    Path(__file__).resolve().parents[3] / "address-importer-friend"))
if str(_ENGINE) not in sys.path:
    sys.path.insert(0, str(_ENGINE))

try:
    from t2.units import (MAX_RANGE_WIDTH, OSM_TAG_VALUE_MAX, compress_flats,
                          parse_unit, unit_pad)
except ModuleNotFoundError as exc:  # pragma: no cover - a setup problem
    raise SystemExit(
        f"cannot import t2.units from {_ENGINE}.\n"
        "The addr:flats renderer is the engine's, deliberately. Point\n"
        "ADDRESS_IMPORTER_FRIEND at your address-importer-friend checkout."
    ) from exc

__all__ = ["parse_flats", "normalise", "MAX_RANGE_WIDTH", "OSM_TAG_VALUE_MAX"]


def parse_flats(value: str | None) -> list[str] | None:
    """The unit designators an `addr:flats` value names, or None.

    Order is the order they were read in, duplicates dropped — the list is a
    set with a stable order for testing. `compress_flats` sorts it anyway.

    None means *this value was not understood*, and the caller must leave the
    object alone. It is never "no units": a value naming nothing at all is
    also None, because rendering it would produce the empty string and delete
    a tag nobody asked us to delete.
    """
    if value is None:
        return None
    units: list[str] = []
    for part in str(value).split(";"):
        part = part.strip().upper()
        if not part:
            # A trailing or doubled `;`. 49 of the 464 live values end in one.
            continue
        lo, sep, hi = part.partition("-")
        if sep:
            a, b = parse_unit(lo.strip()), parse_unit(hi.strip())
            if not (a and b and a[0] == b[0] and a[2] == b[2]
                    and 0 <= b[1] - a[1] <= MAX_RANGE_WIDTH):
                return None
            pad = max(unit_pad(lo.strip()), unit_pad(hi.strip()))
            for n in range(a[1], b[1] + 1):
                num = f"{n:0{pad}d}" if pad else str(n)
                units.append(f"{a[0]}{num}{a[2]}")
        else:
            # A lone designator, parseable (`101`, `101A`, `LL01`) or not
            # (`A`, `B`, `REAR`). Either way it is one unit and it travels
            # verbatim; `compress_flats` carries the unparseable ones through
            # to the tail rather than guessing at them.
            units.append(part)

    if not units:
        return None
    seen: set[str] = set()
    ordered: list[str] = []
    for unit in units:
        if unit not in seen:
            seen.add(unit)
            ordered.append(unit)
    return ordered


def normalise(value: str | None) -> tuple[str | None, str]:
    """`(normalised value, "")`, or `(None, reason)` — the round-trip gate.

    Shaped like the engine's `flats_tag`: a value or a reason it was refused,
    never a half-answer. The reasons are the review buckets:

        unparsed     `parse_flats` could not read the value
        round-trip   it read, but re-reading the rendering named a different
                     set of units. The parser is wrong about this value and
                     must not be trusted with it
        too-long     the rendering is past OSM's 255-character tag limit, so
                     it cannot be uploaded at all

    The rendering is normally *shorter* than what it replaces, so `too-long`
    is a guard rather than an expectation: it is only reachable where a value
    compresses worse than it was written, e.g. a wide letter-suffixed range.
    """
    units = parse_flats(value)
    if units is None:
        return None, "unparsed"
    rendered = compress_flats(units)
    back = parse_flats(rendered)
    if back is None or set(back) != set(units):
        return None, "round-trip"
    if len(rendered) > OSM_TAG_VALUE_MAX:
        return None, "too-long"
    return rendered, ""
