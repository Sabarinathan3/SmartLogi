"""
services/delay_service.py – Orchestrates delay risk prediction.
Now passes through extended fields from the updated delay model.
"""

from app.ai.delay_model import predict_delay


def get_delay_prediction(
    distance_km: float,
    traffic: str,
    weather: str,
) -> dict:
    """
    Call the AI delay model and return the full prediction dictionary,
    including the three new fields: recommended_speed_adjustment,
    reroute_required, and ai_explanation.
    """
    return predict_delay(
        distance_km=distance_km,
        traffic=traffic,
        weather=weather,
    )
