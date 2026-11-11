"""Lab 6: tests designed to execute every application statement."""

import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


def test_invalid_input():
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest(None, 0)


def test_route_fares_and_concessions():
    manifests = [
        {"route_active": False},
        {"route_active": True, "route_type": "unknown"},
        {"route_active": True, "route_type": "express", "commuters": [
            {"zones": 2}, {"blacklisted": True}, {"zones": 100}]},
        {"route_active": True, "route_type": "shuttle", "commuters": [
            {"zones": 2, "type": "student"}, {"zones": 2, "type": "senior"}]},
        {"route_active": True, "route_type": "local", "priority_boarding": True,
         "commuters": [{"zones": 0}, {"blacklisted": True}, {"zones": 2}]},
    ]
    # Express fare is reset by the blacklist; shuttle=2.50+3.50; local=4.50+2.
    assert process_commute_manifest(manifests, 2) == {
        "total_fare": 12.5, "status": "COMPLETED"}


def test_audit_rejected():
    manifests = [{"route_active": True, "route_type": "invalid"}] * 5
    assert process_commute_manifest(manifests, 0) == {
        "total_fare": 0.0, "status": "AUDIT_REJECTED"}


def test_empty_manifest():
    assert process_commute_manifest([], 0) == {
        "total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


@pytest.mark.parametrize("matrix, expected", [
    ([], "NO_DATA"),
    ([[0, 4, 3]], "OPERATIONAL"),
    ([[4, 5]], "TURNSTILE_JAM"),
])
def test_turnstiles(matrix, expected):
    assert inspect_smartcard_turnstiles(matrix) == expected
