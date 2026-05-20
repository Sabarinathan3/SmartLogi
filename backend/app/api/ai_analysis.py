"""
api/ai_analysis.py – Combined AI analysis endpoint.

Demonstrates the full end-to-end AI pipeline in a single call:
  1. Predict delay risk
  2. Optimise route
  3. Calculate CO₂ savings

This is the key "judge demo" endpoint.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from app.services.delay_service        import get_delay_prediction
from app.services.routing_service      import get_optimised_route
from app.services.sustainability_service import get_carbon_footprint

router = APIRouter()


# ─── Request ──────────────────────────────────────────────────────────────────
class AIAnalysisRequest(BaseModel):
    order_id:          Optional[str]   = Field(None, description="Optional order reference")
    distance_km:       float           = Field(..., gt=0,       description="Journey distance in km")
    traffic:           str             = Field(...,             description="low | moderate | heavy")
    weather:           str             = Field("clear",         description="clear | rain | fog | storm")
    fuel_type:         str             = Field("diesel",        description="diesel | petrol | hybrid | electric | cng")
    waypoints:         List[str]       = Field(..., min_length=2, description="Route waypoints, first=origin last=destination")
    num_deliveries:    int             = Field(1, ge=1,         description="Deliveries consolidated in this trip")


# ─── Response ─────────────────────────────────────────────────────────────────
class AIAnalysisResponse(BaseModel):
    order_id:                Optional[str]

    # Layer 1 – Delay prediction
    delay_risk:              str          # Low | Medium | High
    recommendation:          str

    # Layer 2 – Route optimisation
    original_route:          List[str]
    optimised_route:         List[str]
    improvement_pct:         float
    eta_improved:            str          # human-readable e.g. "14%"
    estimated_time_saved_min: float
    strategy:                str

    # Layer 3 – Sustainability
    co2_kg:                  float
    co2_reduced:             str          # human-readable e.g. "18%"
    rating:                  str          # Green | Moderate | High
    trees_to_offset:         float
    per_delivery_co2:        float
    sustainability_tip:      str


@router.post("/ai-analysis", response_model=AIAnalysisResponse, tags=["AI – Full Analysis"])
async def ai_analysis_endpoint(payload: AIAnalysisRequest):
    """
    **Full AI Pipeline — Judge Demo Endpoint** 🔥

    Runs all three AI layers in sequence and returns a combined decision:

    ```
    Admin triggers → AI predicts delay → Route re-optimised →
    CO₂ recalculated → Unified decision returned → UI updates.
    ```

    This single call demonstrates the complete SmartLogi intelligence pipeline.
    """

    # Step 1 – Delay Intelligence
    delay = get_delay_prediction(
        distance_km=payload.distance_km,
        traffic=payload.traffic,
        weather=payload.weather,
    )

    # Step 2 – Route Optimisation
    route = get_optimised_route(
        waypoints=payload.waypoints,
        traffic_condition=payload.traffic,
    )

    # Step 3 – Sustainability Impact
    sustainability = get_carbon_footprint(
        distance_km=payload.distance_km,
        fuel_type=payload.fuel_type,
        num_deliveries=payload.num_deliveries,
    )

    # Estimate CO₂ saved (optimised distance is improvement_pct shorter)
    co2_saved_pct   = round(route["improvement_pct"], 1)
    eta_improvement = f"{round(route['improvement_pct'], 0):.0f}%"
    co2_reduction   = f"{co2_saved_pct:.0f}%"

    return AIAnalysisResponse(
        order_id=payload.order_id,

        # Delay
        delay_risk=delay["delay_risk"],
        recommendation=delay["recommendation"],

        # Route
        original_route=route["original_route"],
        optimised_route=route["optimised_route"],
        improvement_pct=route["improvement_pct"],
        eta_improved=eta_improvement,
        estimated_time_saved_min=route["estimated_time_saved_min"],
        strategy=route["strategy"],

        # Sustainability
        co2_kg=sustainability["co2_kg"],
        co2_reduced=co2_reduction,
        rating=sustainability["rating"],
        trees_to_offset=sustainability["trees_to_offset"],
        per_delivery_co2=sustainability["per_delivery_co2"],
        sustainability_tip=sustainability["sustainability_tip"],
    )
