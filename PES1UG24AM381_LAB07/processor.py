"""Validated transit helpers. Invalid input returns None instead of crashing.

Only strings up to 256 characters are accepted. Corridors have two ASCII
alphanumeric stop codes (starting with a letter) and a positive zone count.
Density requires finite, nonnegative passengers and finite, positive km.
"""

import math
import re


MAX_INPUT_LENGTH = 256
DISCOUNTS = {
    "STANDARD": 1.00,
    "STUDENT": 0.50,
    "SENIOR": 0.35,
    "MILITARY": 0.20,
    "CHILD": 0.00,
}


def _valid_text(value):
    return isinstance(value, str) and len(value) <= MAX_INPUT_LENGTH


def parse_transit_corridor(corridor_code):
    """Return the original formatted fare for valid codes, otherwise None."""
    if not _valid_text(corridor_code):
        return None
    parts = [part.strip() for part in corridor_code.strip().split("-")]
    if len(parts) != 3:
        return None
    orig, dest, zones_str = parts
    if not all(re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", stop)
               for stop in (orig, dest)):
        return None
    if not re.fullmatch(r"[0-9]+", zones_str):
        return None
    zones = int(zones_str)
    if zones <= 0:
        return None
    base_fare = 2.50 + zones * 0.75
    return (f"Route {orig.upper()}->{dest.upper()}: {zones} Zones, "
            f"Fare ${base_fare:.2f}")


def lookup_concession_discount(category_name):
    """Return the specified multiplier, or None for an unknown category."""
    if not _valid_text(category_name):
        return None
    return DISCOUNTS.get(category_name.strip().upper())


def compute_passenger_density(occupancy_ratio_str):
    """Return finite passengers/km rounded to 2 decimals, otherwise None."""
    if not _valid_text(occupancy_ratio_str):
        return None
    parts = occupancy_ratio_str.strip().split("/")
    if len(parts) != 2:
        return None
    try:
        passengers, km = (float(part.strip()) for part in parts)
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(passengers) or not math.isfinite(km):
        return None
    if passengers < 0 or km <= 0:
        return None
    density = passengers / km
    if not math.isfinite(density):
        return None
    return round(density, 2)


def main():
    print("==== Running parse_transit_corridor ====")
    c_input = input("Enter corridor (e.g. DT-UP-3): ")
    route = parse_transit_corridor(c_input)
    print(route if route is not None else "Invalid corridor code")

    print("\n==== Running lookup_concession_discount ====")
    cat_input = input("Enter concession category (e.g. STUDENT, SENIOR): ")
    multiplier = lookup_concession_discount(cat_input)
    print("Multiplier:", multiplier if multiplier is not None
          else "Invalid concession category")

    print("\n==== Running compute_passenger_density ====")
    d_input = input("Enter passengers/km (e.g. 50/10.0): ")
    density = compute_passenger_density(d_input)
    print("Density:", density if density is not None else "Invalid density input")


if __name__ == "__main__":
    try:
        main()
    except EOFError:
        print("Input ended before all three values were supplied.")
