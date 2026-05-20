"""
ai/route_optimizer.py – Mock route optimisation logic.
"""

from typing import List, Dict


def optimize_route(waypoints: List[str]) -> Dict:
    """
    Simple route optimisation heuristic:
    - If there are 2 or fewer points, return as-is.
    - Otherwise, sort alphabetically (mocks shortest-path ordering for hackathon).
    - Returns the optimised list and an estimated improvement percentage.
    """
    if not waypoints:
        return {
            "optimised_route": [],
            "total_points": 0,
            "improvement_pct": 0,
            "strategy": "none",
        }

    if len(waypoints) <= 2:
        return {
            "optimised_route": waypoints,
            "total_points": len(waypoints),
            "improvement_pct": 0,
            "strategy": "direct",
        }

    # Keep first (origin) and last (destination) fixed; optimise middle stops
    origin      = waypoints[0]
    destination = waypoints[-1]
    middle      = sorted(waypoints[1:-1])  # alphabetical proxy for shortest path

    optimised = [origin] + middle + [destination]
    improvement = round(len(middle) * 3.5, 1)  # mock: each reordered stop saves 3.5%

    return {
        "optimised_route":  optimised,
        "original_route":   waypoints,
        "total_points":     len(optimised),
        "improvement_pct":  min(improvement, 40.0),   # cap at 40%
        "strategy":         "nearest-neighbour-proxy",
    }
