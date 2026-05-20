"""
schemas/route_schema.py – Pydantic models for Route API.
"""

from typing import Optional, List
from pydantic import BaseModel


class RouteBase(BaseModel):
    route_id: str
    origin: str
    destination: str
    waypoints: Optional[List[str]] = None
    distance_km: float
    duration_min: float
    optimised: str = "false"


class RouteCreate(RouteBase):
    pass


class RouteSchema(RouteBase):
    id: int

    class Config:
        from_attributes = True
