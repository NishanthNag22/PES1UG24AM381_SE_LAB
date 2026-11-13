"""The same Hypothesis tests run against the original and fixed processors."""

import math
from decimal import Decimal

import pytest
from hypothesis import given, settings, strategies as st
from processor import (
    parse_transit_corridor,
    lookup_concession_discount,
    compute_passenger_density,
)


# Deterministic generation makes the before/after evidence reproducible.
FUZZ = settings(max_examples=300, derandomize=True, database=None, deadline=None)
scalars = st.one_of(st.none(), st.booleans(), st.integers(), st.floats(),
                    st.text(max_size=300), st.binary(max_size=40))
unexpected = st.one_of(scalars, st.lists(scalars, max_size=8),
                      st.dictionaries(st.text(max_size=12), scalars, max_size=5))


@FUZZ
@given(unexpected)
def test_parse_transit_corridor_no_crash(value):
    try:
        result = parse_transit_corridor(value)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {value!r}: {exc}")
    assert result is None or isinstance(result, str)


@FUZZ
@given(unexpected)
def test_lookup_concession_discount_safe(value):
    try:
        result = lookup_concession_discount(value)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {value!r}: {exc}")
    assert result is None or result in {1.0, 0.5, 0.35, 0.2, 0.0}


@FUZZ
@given(unexpected)
def test_compute_passenger_density_safe(value):
    try:
        result = compute_passenger_density(value)
    except Exception as exc:
        pytest.fail(f"Unexpected {type(exc).__name__} for {value!r}: {exc}")
    assert result is None or (isinstance(result, float)
                              and math.isfinite(result) and result >= 0)


@pytest.mark.parametrize("value", [None, 42, True, [], {}, b"DT-UP-3", "",
    "DT", "DT-UP", "DT-UP-3-X", "-UP-3", "DT--3", "DT-UP-zero",
    "DT-UP-0", "DT-UP--1", "DT-UP-2.5", "DT-UP-+3", "DT-UP-\u00b2",
    "D T-UP-3", "DT-UP-" + "9" * 257])
def test_invalid_corridors_return_none(value):
    assert parse_transit_corridor(value) is None


@pytest.mark.parametrize("value, expected", [
    ("DT-UP-3", "Route DT->UP: 3 Zones, Fare $4.75"),
    (" dt - up - 003 ", "Route DT->UP: 3 Zones, Fare $4.75"),
    ("A1-B2-1", "Route A1->B2: 1 Zones, Fare $3.25"),
])
def test_corridor_regressions(value, expected):
    assert parse_transit_corridor(value) == expected


@FUZZ
@given(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=8),
       st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=8),
       st.integers(min_value=1, max_value=1000000))
def test_valid_corridor_fares(origin, destination, zones):
    fare = Decimal("2.50") + Decimal("0.75") * zones
    assert parse_transit_corridor(f"{origin}-{destination}-{zones}") == (
        f"Route {origin}->{destination}: {zones} Zones, Fare ${fare:.2f}")


@pytest.mark.parametrize("value", [None, 0, True, [], {}, b"STUDENT", "",
    "TEACHER", "STUDENT/SENIOR", "S" * 257])
def test_unknown_categories_return_none(value):
    assert lookup_concession_discount(value) is None


@FUZZ
@given(st.sampled_from([("STANDARD", 1.0), ("STUDENT", 0.5),
                       ("SENIOR", 0.35), ("MILITARY", 0.2), ("CHILD", 0.0)]),
       st.sampled_from(["", " ", "\t", "\n"]), st.booleans())
def test_known_concessions(category, space, lowercase):
    label, expected = category
    if lowercase:
        label = label.lower()
    assert lookup_concession_discount(space + label + space) == expected


@pytest.mark.parametrize("value", [None, 20, True, [], {}, b"50/10", "", "5",
    "1/2/3", "/2", "1/", "one/2", "1/two", "1/0", "0/0", "1/-0.0",
    "-1/2", "1/-2", "nan/2", "2/nan", "inf/2", "2/inf", "-inf/2",
    "1e309/1", "1/1e-999", "1e308/1e-308", "9" * 257 + "/1"])
def test_invalid_densities_return_none(value):
    assert compute_passenger_density(value) is None


@pytest.mark.parametrize("value, expected", [
    ("50/10.0", 5.0), ("0/10", 0.0), (" 15 / 2 ", 7.5),
    ("1/3", 0.33), ("2/3", 0.67), ("1e2/2.5e1", 4.0),
    ("1/1e308", 0.0), ("1e308/1", 1e308),
])
def test_density_regressions(value, expected):
    assert compute_passenger_density(value) == expected


@FUZZ
@given(st.integers(min_value=0, max_value=1000000),
       st.integers(min_value=1, max_value=10000))
def test_valid_density_is_finite_and_within_rounding_error(passengers, km):
    result = compute_passenger_density(f"{passengers}/{km}")
    exact = Decimal(passengers) / Decimal(km)
    assert math.isfinite(result) and result >= 0
    assert abs(Decimal(str(result)) - exact) <= Decimal("0.00500001")
