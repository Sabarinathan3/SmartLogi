"""
api/empty_mile_api.py – Empty Mile Intelligence endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.ai.empty_mile import detect_empty_miles, compute_route_absorption

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Shared sub-models
# ─────────────────────────────────────────────────────────────────────────────
class RouteIn(BaseModel):
    origin: str              = Field("Depot A")
    destination: str         = Field("Hub B")
    return_km: float         = Field(80.0, ge=0)
    capacity_used_pct: float = Field(20.0, ge=0, le=100)


class OrderIn(BaseModel):
    order_id: str
    pickup: str
    drop: str


# ─────────────────────────────────────────────────────────────────────────────
# GET /ai/empty-mile-status
# ─────────────────────────────────────────────────────────────────────────────
class EmptyMileStatusResponse(BaseModel):
    empty_mile_detected: bool
    unused_capacity_percentage: float
    potential_co2_saved: float
    trips_reduced_count: int


@router.get("/ai/empty-mile-status", response_model=EmptyMileStatusResponse,
            summary="Detect empty-mile scenarios across active fleet")
async def empty_mile_status():
    """
    Returns a snapshot of current empty-mile risk using simulated active routes.
    Replace the sample payload below with a live DB query in production.
    """
    # Demo payload — simulates fleet reality
    sample_routes = [
        {"origin": "Mumbai Central", "destination": "Pune Depot",
         "return_km": 148, "capacity_used_pct": 18},
        {"origin": "Nashik Hub",    "destination": "Aurangabad DC",
         "return_km": 110, "capacity_used_pct": 12},
        {"origin": "Nagpur DC",     "destination": "Raipur Hub",
         "return_km": 95,  "capacity_used_pct": 85},
    ]
    result = detect_empty_miles(active_routes=sample_routes)
    return EmptyMileStatusResponse(**result)


# ─────────────────────────────────────────────────────────────────────────────
# POST /ai/internal-route-absorption
# ─────────────────────────────────────────────────────────────────────────────
class AbsorptionRequest(BaseModel):
    active_routes: list[RouteIn]    = Field(..., min_length=1)
    internal_orders: list[OrderIn]  = Field(default=[])


class AbsorptionResponse(BaseModel):
    absorption_possible: bool
    merged_route: list[str]
    estimated_cost_savings: float
    estimated_co2_reduction: float


@router.post("/ai/internal-route-absorption", response_model=AbsorptionResponse,
             summary="Compute optimal internal route absorption to eliminate return trips")
async def internal_route_absorption(payload: AbsorptionRequest):
    """
    Given active routes and pending internal orders, determine whether
    two return-trip legs can be merged into a single vehicle journey.
    """
    routes_as_dicts = [r.model_dump() for r in payload.active_routes]
    orders_as_dicts = [o.model_dump() for o in payload.internal_orders]
    result = compute_route_absorption(
        active_routes=routes_as_dicts,
        internal_orders=orders_as_dicts,
    )
    return AbsorptionResponse(**result)
