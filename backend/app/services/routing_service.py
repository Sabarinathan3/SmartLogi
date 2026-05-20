"""
services/routing_service.py – Route optimisation orchestration.
"""

from typing import List, Dict
from app.ai.route_optimizer import optimize_route


# Traffic multiplier on estimated time saving
_TRAFFIC_MULTIPLIER: Dict[str, float] = {
    "low":      0.5,
    "moderate": 1.0,
    "heavy":    1.8,
}


def get_optimised_route(
    waypoints: List[str],
    traffic_condition: str = "moderate",
) -> Dict:
    """
    Optimise waypoints and estimate time saved based on traffic.
    Returns the full optimisation payload expected by the API layer.
    """
    result = optimize_route(waypoints)

    multiplier = _TRAFFIC_MULTIPLIER.get(traffic_condition.lower(), 1.0)
    # Estimate: every percent improvement ≈ 0.3 min saving (scaled by traffic)
    time_saved = round(result["improvement_pct"] * 0.3 * multiplier, 1)

    return {
        "original_route":          result.get("original_route", waypoints),
        "optimised_route":         result["optimised_route"],
        "total_points":            result["total_points"],
        "improvement_pct":         result["improvement_pct"],
        "strategy":                result["strategy"],
        "estimated_time_saved_min": time_saved,
    }
