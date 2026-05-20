"""
api/optimize_route.py – Route optimisation endpoint.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
from app.services.routing_service import get_optimised_route

router = APIRouter()


class OptimiseRequest(BaseModel):
    route_id: str              = Field(None, description="Optional route reference ID")
    waypoints: List[str]       = Field(..., min_length=2, description="Ordered list of location names/coordinates")
    traffic_condition: str     = Field("moderate", description="Traffic level: low | moderate | heavy")


class OptimiseResponse(BaseModel):
    route_id: str | None
    original_route: List[str]
    optimised_route: List[str]
    total_points: int
    improvement_pct: float
    strategy: str
    estimated_time_saved_min: float


@router.post("/optimize-route", response_model=OptimiseResponse)
async def optimise_route_endpoint(payload: OptimiseRequest):
    """
    Optimise a delivery route given a list of waypoints.

    Returns the reordered route and estimated time/distance savings.
    """
    result = get_optimised_route(
        waypoints=payload.waypoints,
        traffic_condition=payload.traffic_condition,
    )
    return OptimiseResponse(
        route_id=payload.route_id,
        **result,
    )
