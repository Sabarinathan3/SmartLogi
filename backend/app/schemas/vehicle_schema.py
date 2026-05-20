"""
schemas/vehicle_schema.py – Pydantic models for Vehicle API.
"""

from typing import Optional
from pydantic import BaseModel


class VehicleBase(BaseModel):
    vehicle_id: str
    type: str
    fuel_type: str
    capacity_kg: float
    is_active: bool = True
    driver_name: Optional[str] = None
    current_location: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass


class VehicleSchema(VehicleBase):
    id: int

    class Config:
        from_attributes = True
