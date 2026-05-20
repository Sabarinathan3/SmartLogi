"""
api/predictive_dispatch_api.py
Predictive Dispatch + Virtual Hubs endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.ai.predictive_dispatch import (
    TruckIn as TruckInDict,
    run_predictive_dispatch,
    generate_virtual_hub,
)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Shared Pydantic models
# ─────────────────────────────────────────────────────────────────────────────
class TruckPayload(BaseModel):
    truck_id: str         = Field(..., example="VH-001")
    current_lat: float    = Field(..., example=19.076)
    current_lng: float    = Field(..., example=72.877)
    dest_lat: float       = Field(..., example=18.520)
    dest_lng: float       = Field(..., example=73.856)
    current_speed_kmh: float = Field(60.0, ge=0, example=60.0)
    traffic_level: str    = Field("moderate", example="moderate")


class VirtualHubOut(BaseModel):
    hub_id: str
    name: str
    lat: float
    lng: float
    participating_trucks: list[str]
    synchronized_eta_min: float


class TruckSyncOut(BaseModel):
    truck_id: str
    recommended_speed_kmh: float
    current_speed_kmh: float
    speed_delta_kmh: float
    arrival_sync_status: str       # early | on-time | delayed
    idling_time_saved_min: float
    guidance_text: str


# ─────────────────────────────────────────────────────────────────────────────
# POST /ai/predictive-dispatch
# ─────────────────────────────────────────────────────────────────────────────
class DispatchRequest(BaseModel):
    trucks: list[TruckPayload] = Field(..., min_length=1)


class DispatchResponse(BaseModel):
    virtual_hubs: list[VirtualHubOut]
    sync_recommendations: list[TruckSyncOut]
    total_idling_saved_min: float
    estimated_co2_reduction_kg: float


@router.post(
    "/ai/predictive-dispatch",
    response_model=DispatchResponse,
    summary="Run JIT speed sync for active trucks toward virtual hubs",
)
async def predictive_dispatch(payload: DispatchRequest) -> DispatchResponse:
    """
    Given a list of active trucks, generates Virtual Hub coordinates and
    computes Just-in-Time speed adjustments so all trucks arrive simultaneously,
    eliminating engine idling and fuel waste.
    """
    trucks_in: list[TruckInDict] = [
        TruckInDict(
            truck_id=t.truck_id,
            current_lat=t.current_lat,
            current_lng=t.current_lng,
            dest_lat=t.dest_lat,
            dest_lng=t.dest_lng,
            current_speed_kmh=t.current_speed_kmh,
            traffic_level=t.traffic_level,
        )
        for t in payload.trucks
    ]
    result = run_predictive_dispatch(trucks_in)

    return DispatchResponse(
        virtual_hubs=[VirtualHubOut(**h) for h in result["virtual_hubs"]],
        sync_recommendations=[TruckSyncOut(**r) for r in result["sync_recommendations"]],
        total_idling_saved_min=result["total_idling_saved_min"],
        estimated_co2_reduction_kg=result["estimated_co2_reduction_kg"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /ai/virtual-hubs
# ─────────────────────────────────────────────────────────────────────────────
class HubStatusOut(BaseModel):
    hub_id: str
    name: str
    lat: float
    lng: float
    participating_trucks: list[str]
    synchronized_eta_min: float
    sync_status: str               # active | standby


class VirtualHubsResponse(BaseModel):
    active_hubs: list[HubStatusOut]
    total_trucks_synced: int
    total_idling_saved_min: float
    estimated_co2_reduction_kg: float


@router.get(
    "/ai/virtual-hubs",
    response_model=VirtualHubsResponse,
    summary="Get currently active Virtual Hubs and synchronization status",
)
async def get_virtual_hubs() -> VirtualHubsResponse:
    """
    Returns a snapshot of Virtual Hubs currently active across the fleet.
    In production, replace the demo payload with live DB / telemetry queries.
    """
    # Demo payload — simulates live telemetry
    demo_trucks: list[TruckInDict] = [
        TruckInDict(truck_id="VH-001", current_lat=19.076, current_lng=72.877,
                    dest_lat=18.520, dest_lng=73.856, current_speed_kmh=68,
                    traffic_level="moderate"),
        TruckInDict(truck_id="VH-002", current_lat=18.650, current_lng=73.500,
                    dest_lat=18.520, dest_lng=73.856, current_speed_kmh=55,
                    traffic_level="heavy"),
        TruckInDict(truck_id="VH-003", current_lat=17.385, current_lng=78.486,
                    dest_lat=15.364, dest_lng=75.124, current_speed_kmh=72,
                    traffic_level="low"),
        TruckInDict(truck_id="VH-004", current_lat=16.500, current_lng=77.200,
                    dest_lat=15.364, dest_lng=75.124, current_speed_kmh=60,
                    traffic_level="moderate"),
    ]

    result = run_predictive_dispatch(demo_trucks)

    hubs_out = [
        HubStatusOut(**h, sync_status="active")
        for h in result["virtual_hubs"]
    ]

    return VirtualHubsResponse(
        active_hubs=hubs_out,
        total_trucks_synced=len(demo_trucks),
        total_idling_saved_min=result["total_idling_saved_min"],
        estimated_co2_reduction_kg=result["estimated_co2_reduction_kg"],
    )
