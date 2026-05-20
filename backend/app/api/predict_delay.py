"""
api/predict_delay.py – AI delay prediction endpoint (extended).
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.delay_service import get_delay_prediction

router = APIRouter()


class DelayRequest(BaseModel):
    distance_km: float = Field(..., gt=0, description="Journey distance in kilometres")
    traffic: str       = Field(..., description="Traffic level: low | moderate | heavy")
    weather: str       = Field(..., description="Weather condition: clear | rain | fog | storm")
    order_id: str | None = Field(None, description="Optional order reference")


class DelayResponse(BaseModel):
    order_id: str | None
    distance_km: float
    traffic: str
    weather: str
    delay_risk: str                      # Low | Medium | High
    recommendation: str
    # ── Extended AI fields ──────────────────────────────────────────────────
    recommended_speed_adjustment: str    # "increase" | "decrease" | "maintain"
    reroute_required: bool
    ai_explanation: str


@router.post("/predict-delay", response_model=DelayResponse)
async def predict_delay_endpoint(payload: DelayRequest):
    """
    Predict delivery delay risk using AI model.

    Returns delay_risk (Low / Medium / High), speed guidance,
    reroute decision, and a human-readable AI explanation.
    """
    result = get_delay_prediction(
        distance_km=payload.distance_km,
        traffic=payload.traffic,
        weather=payload.weather,
    )
    return DelayResponse(
        order_id=payload.order_id,
        distance_km=payload.distance_km,
        traffic=payload.traffic,
        weather=payload.weather,
        delay_risk=result["delay_risk"],
        recommendation=result["recommendation"],
        recommended_speed_adjustment=result["recommended_speed_adjustment"],
        reroute_required=result["reroute_required"],
        ai_explanation=result["ai_explanation"],
    )
