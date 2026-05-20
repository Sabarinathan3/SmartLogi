"""
services/sustainability_service.py – Carbon footprint calculation service.
"""

from typing import Dict
from app.ai.emission_calc import calculate_emission


def get_carbon_footprint(
    distance_km: float,
    fuel_type: str,
    num_deliveries: int = 1,
) -> Dict:
    """
    Calculate the total CO₂ footprint for a journey (or batch of deliveries).

    Args:
        distance_km:    total distance of the journey in km
        fuel_type:      vehicle fuel type (diesel | petrol | hybrid | electric | cng)
        num_deliveries: number of deliveries consolidated in this trip

    Returns:
        Enriched emission report with per-delivery statistics and tree-equivalent offset.
    """
    report = calculate_emission(distance_km, fuel_type)

    # Per-delivery split
    per_delivery_co2 = round(report["co2_kg"] / max(num_deliveries, 1), 3)

    # A mature tree absorbs ~21 kg CO₂/year → equivalent trees to offset
    trees_to_offset = round(report["co2_kg"] / 21, 2)

    return {
        **report,
        "num_deliveries":    num_deliveries,
        "per_delivery_co2":  per_delivery_co2,
        "trees_to_offset":   trees_to_offset,
        "sustainability_tip": _get_tip(report["rating"], fuel_type),
    }


def _get_tip(rating: str, fuel_type: str) -> str:
    if fuel_type.lower() == "electric":
        return "🌱 Great choice! Electric vehicles produce the lowest emissions."
    if rating == "Green":
        return "🟢 This route has a low carbon footprint. Keep it up!"
    if rating == "Moderate":
        return "🟡 Consider switching to a hybrid/EV vehicle for this route."
    return "🔴 High emissions detected. Consolidate deliveries or switch to EV."
