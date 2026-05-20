"""
schemas/order_schema.py – Pydantic models for Order API.
"""

from typing import Optional
from pydantic import BaseModel


class OrderBase(BaseModel):
    pickup_location: str
    drop_location: str
    status: str = "pending"
    eta: Optional[str] = None
    distance_km: Optional[float] = None
    delay_risk: Optional[str] = None


class OrderCreate(OrderBase):
    order_id: str


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    eta: Optional[str] = None
    delay_risk: Optional[str] = None


class OrderSchema(OrderBase):
    id: int
    order_id: str

    class Config:
        from_attributes = True
