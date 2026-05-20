"""
api/vehicles.py – Vehicles API router.
"""

from fastapi import APIRouter
from app.schemas.vehicle_schema import VehicleSchema
from app.utils.data_generator import generate_mock_vehicles
from typing import List

router = APIRouter()

# ── Mock fleet data ───────────────────────────────────────────────────────────
_vehicles: List[dict] = generate_mock_vehicles(8)


@router.get("/vehicles", response_model=List[VehicleSchema])
async def get_vehicles():
    """Return the full vehicle fleet."""
    return _vehicles


@router.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    """Return a single vehicle by vehicle_id."""
    for v in _vehicles:
        if v["vehicle_id"] == vehicle_id:
            return v
    return {"error": f"Vehicle '{vehicle_id}' not found"}


@router.get("/vehicles/active/list")
async def get_active_vehicles():
    """Return only active vehicles."""
    return [v for v in _vehicles if v["is_active"]]


@router.patch("/vehicles/{vehicle_id}/status")
async def toggle_vehicle_status(vehicle_id: str, is_active: bool):
    """Activate or deactivate a vehicle."""
    for v in _vehicles:
        if v["vehicle_id"] == vehicle_id:
            v["is_active"] = is_active
            return {"message": "Status updated", "vehicle": v}
    return {"error": f"Vehicle '{vehicle_id}' not found"}
