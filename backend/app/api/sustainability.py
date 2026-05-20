"""
api/sustainability.py – Carbon footprint and ESG endpoint.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.services.sustainability_service import get_carbon_footprint

router = APIRouter()


class SustainabilityRequest(BaseModel):
    distance_km:    float = Field(..., gt=0,  description="Journey distance in km")
    fuel_type:      str   = Field(...,         description="diesel | petrol | hybrid | electric | cng")
    num_deliveries: int   = Field(1,  ge=1,   description="Number of deliveries on this trip")


class SustainabilityResponse(BaseModel):
    distance_km:       float
    fuel_type:         str
    fuel_factor:       float
    co2_kg:            float
    co2_grams:         float
    rating:            str          # Green | Moderate | High
    num_deliveries:    int
    per_delivery_co2:  float
    trees_to_offset:   float
    sustainability_tip: str


@router.post("/sustainability", response_model=SustainabilityResponse)
async def sustainability_endpoint(payload: SustainabilityRequest):
    """
    Calculate CO₂ footprint for a delivery journey.

    Returns full emission report with per-delivery breakdown,
    tree-offset equivalent, and a sustainability tip.
    """
    report = get_carbon_footprint(
        distance_km=payload.distance_km,
        fuel_type=payload.fuel_type,
        num_deliveries=payload.num_deliveries,
    )
    return SustainabilityResponse(**report)
