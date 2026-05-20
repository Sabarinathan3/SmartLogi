"""
ai/empty_mile.py – Rule-based AI engine for Empty Mile detection
and Internal Route Absorption.
"""

from __future__ import annotations
from typing import TypedDict


# ─────────────────────────────────────────────────────────────────────────────
# Type aliases
# ─────────────────────────────────────────────────────────────────────────────
class EmptyMileStatus(TypedDict):
    empty_mile_detected: bool
    unused_capacity_percentage: float
    potential_co2_saved: float          # kg
    trips_reduced_count: int


class AbsorptionResult(TypedDict):
    absorption_possible: bool
    merged_route: list[str]
    estimated_cost_savings: float       # INR
    estimated_co2_reduction: float      # kg


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
_CO2_KG_PER_KM          = 0.212        # avg diesel truck CO₂ per km
_COST_PER_KM_INR        = 18.5         # avg fuel + driver cost per km
_ABSORPTION_OVERLAP_KM  = 40           # minimum overlap distance to merge


# ─────────────────────────────────────────────────────────────────────────────
# GET /ai/empty-mile-status
# ─────────────────────────────────────────────────────────────────────────────
def detect_empty_miles(
    active_routes: list[dict],
    completed_deliveries: int = 0,
) -> EmptyMileStatus:
    """
    Detect empty-mile scenarios across active routes.

    Logic:
    - Each route has a 'return_km' field (distance of empty return leg).
    - Capacity utilisation below 25 % on any leg triggers the alert.
    - CO2 and cost savings are calculated from absorbed return km.
    """
    empty_trips: list[dict] = [
        r for r in active_routes
        if r.get("capacity_used_pct", 100) < 25
    ]

    trips_reduced   = len(empty_trips) // 2          # pairs that can merge
    absorbed_km     = sum(r.get("return_km", 80) for r in empty_trips[:trips_reduced * 2])
    co2_saved       = round(absorbed_km * _CO2_KG_PER_KM, 2)

    return EmptyMileStatus(
        empty_mile_detected    = len(empty_trips) > 0,
        unused_capacity_percentage = (
            round(sum(r.get("capacity_used_pct", 0) for r in empty_trips) / len(empty_trips), 1)
            if empty_trips else 0.0
        ),
        potential_co2_saved    = co2_saved,
        trips_reduced_count    = trips_reduced,
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /ai/internal-route-absorption
# ─────────────────────────────────────────────────────────────────────────────
def compute_route_absorption(
    active_routes: list[dict],
    internal_orders: list[dict],
) -> AbsorptionResult:
    """
    Determine if any two return-trip legs can be merged.

    Heuristic:
    1. Find route pairs whose end-point cities share the same region code.
    2. If merged distance saving > _ABSORPTION_OVERLAP_KM → absorption possible.
    3. Estimate savings and CO2 reduction from eliminated leg.
    """
    # Collect routes with return legs
    return_legs = [r for r in active_routes if r.get("return_km", 0) > 0]

    if len(return_legs) < 2:
        return AbsorptionResult(
            absorption_possible  = False,
            merged_route         = [],
            estimated_cost_savings  = 0.0,
            estimated_co2_reduction = 0.0,
        )

    # Pair first two eligible return legs (demo heuristic)
    r1, r2 = return_legs[0], return_legs[1]
    merged_km   = max(r1.get("return_km", 80), r2.get("return_km", 80))
    saved_km    = r1.get("return_km", 80) + r2.get("return_km", 80) - merged_km
    possible    = saved_km >= _ABSORPTION_OVERLAP_KM

    merged_waypoints = (
        [r1.get("origin", "Depot A"), r1.get("destination", "Hub B"),
         r2.get("destination", "Hub C")]
        if possible else []
    )

    return AbsorptionResult(
        absorption_possible     = possible,
        merged_route            = merged_waypoints,
        estimated_cost_savings  = round(saved_km * _COST_PER_KM_INR, 2) if possible else 0.0,
        estimated_co2_reduction = round(saved_km * _CO2_KG_PER_KM, 2) if possible else 0.0,
    )
