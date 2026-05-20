"""
ai/delay_model.py – Extended rule-based delay prediction model.
Now returns speed guidance, reroute flag, and AI explanation.
"""

from typing import Literal, TypedDict


DelayRisk = Literal["Low", "Medium", "High"]


class DelayPrediction(TypedDict):
    delay_risk: DelayRisk
    recommendation: str
    recommended_speed_adjustment: str   # "increase" | "decrease" | "maintain"
    reroute_required: bool
    ai_explanation: str


# Speed guidance per risk × traffic matrix
_SPEED_GUIDANCE: dict[tuple[str, str], str] = {
    ("Low",    "low"):      "Maintain current speed — no disruptions detected.",
    ("Low",    "moderate"): "Maintain current speed — minor delays possible.",
    ("Low",    "heavy"):    "Reduce speed slightly; heavy traffic, but risk is low.",
    ("Medium", "low"):      "Maintain 60 km/h — moderate risk from weather.",
    ("Medium", "moderate"): "Maintain 45 km/h for synchronized arrival at handover.",
    ("Medium", "heavy"):    "Reduce to 40 km/h; traffic corridors are congested.",
    ("High",   "low"):      "Increase speed where safe — storm risk demands early arrival.",
    ("High",   "moderate"): "Maintain 45 km/h; AI reroute recommended to avoid idling.",
    ("High",   "heavy"):    "Reduce speed; rerouting is mandatory — congestion + weather.",
}

_EXPLANATIONS: dict[tuple[str, str, str], str] = {
    ("High",   "heavy", "storm"):    "Severe storm + heavy traffic: congestion ahead. Speed synchronization prevents idling at handover point. Rerouting via bypass saves ~42 min.",
    ("High",   "heavy", "fog"):      "Dense fog reducing visibility + heavy traffic: high collision risk. Maintain reduced speed and take bypass route.",
    ("High",   "heavy", "rain"):     "Rain-induced surface delays compound heavy traffic. AI recommends interim depot stop to reduce risk.",
    ("High",   "moderate", "storm"): "Storm conditions with moderate traffic: primary route unsafe. Alternate highway corridor recommended.",
    ("Medium", "moderate", "rain"):  "Rain + moderate traffic: 30 % probability of 1-hr delay. No reroute needed; maintain steady 45 km/h.",
    ("Medium", "heavy", "clear"):    "Heavy traffic alone causes medium risk. Consider timed departure to avoid peak congestion window.",
}


def predict_delay(
    distance_km: float,
    traffic: str,        # "low" | "moderate" | "heavy"
    weather: str,        # "clear" | "rain" | "fog" | "storm"
) -> DelayPrediction:
    """
    Extended rule-based delay predictor.

    Scoring:
      Distance → 1-3 pts  |  Traffic → 0-3 pts  |  Weather → 0-4 pts
      ≤3 → Low  |  4-6 → Medium  |  >6 → High
    """
    score = 0

    if distance_km > 200:
        score += 3
    elif distance_km > 100:
        score += 2
    else:
        score += 1

    traffic_map = {"low": 0, "moderate": 2, "heavy": 3}
    score += traffic_map.get(traffic.lower(), 1)

    weather_map = {"clear": 0, "rain": 2, "fog": 3, "storm": 4}
    score += weather_map.get(weather.lower(), 1)

    if score <= 3:
        risk: DelayRisk = "Low"
    elif score <= 6:
        risk = "Medium"
    else:
        risk = "High"

    # Reroute required for High risk with heavy traffic or extreme weather
    reroute_required = risk == "High" and (
        traffic.lower() == "heavy" or weather.lower() in {"storm", "fog"}
    )

    # Speed adjustment
    speed_key = (risk, traffic.lower())
    speed_text = _SPEED_GUIDANCE.get(speed_key, "Maintain current speed.")
    if risk == "High":
        speed_adj = "decrease" if traffic.lower() == "heavy" else "maintain"
    elif risk == "Low":
        speed_adj = "maintain"
    else:
        speed_adj = "maintain"

    # AI explanation
    explanation_key = (risk, traffic.lower(), weather.lower())
    ai_explanation = _EXPLANATIONS.get(
        explanation_key,
        f"Risk level {risk} based on {traffic} traffic and {weather} weather "
        f"over {distance_km:.0f} km. {'Rerouting recommended.' if reroute_required else 'Current route is viable.'}",
    )

    # Recommendation (legacy field kept for UI compatibility)
    rec_map = {
        "Low":    "Proceed on current route. No significant delays expected.",
        "Medium": "Monitor route conditions. Consider 15–30 min buffer at pickup.",
        "High":   "High delay risk detected! AI recommends immediate rerouting.",
    }

    return DelayPrediction(
        delay_risk                   = risk,
        recommendation               = rec_map[risk],
        recommended_speed_adjustment = speed_adj,
        reroute_required             = reroute_required,
        ai_explanation               = ai_explanation,
    )
