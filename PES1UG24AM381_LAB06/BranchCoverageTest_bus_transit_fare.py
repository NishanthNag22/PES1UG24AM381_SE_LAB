"""Lab 6: decision outcomes, loop exits, defaults and boundary cases."""

import pytest
from bus_transit_fare import process_commute_manifest, inspect_smartcard_turnstiles


@pytest.mark.parametrize("manifests, fee", [(None, 0), ({}, 0), ([], -0.01)])
def test_invalid_inputs(manifests, fee):
    with pytest.raises(ValueError, match="Invalid manifests list or booking fee"):
        process_commute_manifest(manifests, fee)


@pytest.mark.parametrize("route, passenger, expected", [
    ("local", "regular", 4.5), ("shuttle", "regular", 6.0),
    ("express", "regular", 8.0), ("local", "student", 1.75),
    ("shuttle", "student", 2.5), ("express", "student", 3.5),
    ("local", "senior", 2.45), ("shuttle", "senior", 3.5),
    ("express", "senior", 4.9), ("local", "other", 4.5),
])
def test_fare_categories(route, passenger, expected):
    manifest = {"route_active": True, "route_type": route,
                "commuters": [{"zones": 2, "type": passenger}]}
    assert process_commute_manifest([manifest], 0) == {
        "total_fare": expected, "status": "COMPLETED"}


@pytest.mark.parametrize("manifests", [[], [{}], [{"route_active": False}],
    [{"route_active": True}], [{"route_active": True, "commuters": []}]])
def test_zero_ridership_and_inactive_routes(manifests):
    assert process_commute_manifest(manifests, 0) == {
        "total_fare": 0.0, "status": "ZERO_RIDERSHIP"}


def test_defaults_and_multiple_manifests():
    assert process_commute_manifest([
        {"route_active": True, "commuters": [{}]},
        {"route_active": True, "route_type": "express", "commuters": [{}]},
    ], 0) == {"total_fare": 10.5, "status": "COMPLETED"}


@pytest.mark.parametrize("fee, expected", [(0, 3.5), (2, 5.5)])
def test_priority_fee(fee, expected):
    assert process_commute_manifest([{
        "route_active": True, "priority_boarding": True, "commuters": [{}]}], fee
    ) == {"total_fare": expected, "status": "COMPLETED"}


def test_priority_fee_without_commuters():
    assert process_commute_manifest([{
        "route_active": True, "priority_boarding": True}], 2
    ) == {"total_fare": 2.0, "status": "COMPLETED"}


@pytest.mark.parametrize("zones", [0, -1])
def test_invalid_zones_skip_only_invalid_commuter(zones):
    assert process_commute_manifest([{
        "route_active": True, "commuters": [{"zones": zones}, {}]}], 0
    ) == {"total_fare": 3.5, "status": "COMPLETED"}


@pytest.mark.parametrize("route, expected", [("local", 7.0), ("shuttle", 10.0)])
def test_nonexpress_blacklist_does_not_cancel_other_riders(route, expected):
    assert process_commute_manifest([{
        "route_active": True, "route_type": route,
        "commuters": [{}, {"blacklisted": True}, {}]}], 0
    ) == {"total_fare": expected, "status": "COMPLETED"}


@pytest.mark.parametrize("priority, expected, status", [
    (False, 0.0, "ZERO_RIDERSHIP"), (True, 2.0, "COMPLETED")])
def test_express_blacklist_resets_fare_and_breaks_loop(priority, expected, status):
    assert process_commute_manifest([{
        "route_active": True, "route_type": "express", "priority_boarding": priority,
        "commuters": [{}, {"blacklisted": True}, {"zones": 100}]}], 2
    ) == {"total_fare": expected, "status": status}


@pytest.mark.parametrize("count, status", [(4, "COMPLETED"), (5, "AUDIT_REJECTED")])
def test_audit_threshold_with_valid_fare(count, status):
    manifests = [{"route_active": True, "route_type": "invalid"}] * count
    manifests += [{"route_active": True, "commuters": [{}]}]
    assert process_commute_manifest(manifests, 0) == {
        "total_fare": 3.5, "status": status}


def test_audit_takes_precedence_over_zero_fare():
    assert process_commute_manifest([{
        "route_active": True, "commuters": [{"zones": 0}] * 5}], 0
    ) == {"total_fare": 0.0, "status": "AUDIT_REJECTED"}


@pytest.mark.parametrize("matrix, expected", [
    ([], "NO_DATA"), (None, "NO_DATA"), ([[]], "OPERATIONAL"),
    ([[0, 1, 2, 3]], "OPERATIONAL"), ([[4]], "OPERATIONAL"),
    ([[4, 4]], "TURNSTILE_JAM"), ([[4, 3, 4]], "OPERATIONAL"),
    ([[4], [4]], "OPERATIONAL"), ([[], [4, 5]], "TURNSTILE_JAM"),
    ([[4, 0, 4, 4]], "TURNSTILE_JAM"),
])
def test_turnstile_decisions(matrix, expected):
    assert inspect_smartcard_turnstiles(matrix) == expected
