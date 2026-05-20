"""
ai/emission_calc.py – CO₂ emission calculator.
"""

from typing import Dict

# kg CO₂ emitted per km for each fuel type
FUEL_FACTORS: Dict[str, float] = {
    "diesel":   0.27,
    "petrol":   0.21,
    "hybrid":   0.12,
    "electric": 0.05,   # indirect emissions from power grid
    "cng":      0.18,
}

DEFAULT_FACTOR = 0.25   # fallback for unknown fuel types


def calculate_emission(distance_km: float, fuel_type: str) -> Dict:
    """
    Calculate CO₂ emission for a journey.

    Formula: CO₂ (kg) = distance_km × fuel_factor

    Returns a dict with:
      - co2_kg       total kg of CO₂
      - co2_grams    total grams of CO₂
      - fuel_factor  factor used
      - rating       Green | Moderate | High
    """
    factor  = FUEL_FACTORS.get(fuel_type.lower(), DEFAULT_FACTOR)
    co2_kg  = round(distance_km * factor, 3)
    co2_g   = round(co2_kg * 1000, 1)

    # Environmental rating
    if co2_kg < 10:
        rating = "Green"
    elif co2_kg < 50:
        rating = "Moderate"
    else:
        rating = "High"

    return {
        "co2_kg":      co2_kg,
        "co2_grams":   co2_g,
        "fuel_factor": factor,
        "fuel_type":   fuel_type,
        "distance_km": distance_km,
        "rating":      rating,
    }
