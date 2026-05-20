"""
models/vehicle.py – SQLAlchemy Vehicle model.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    vehicle_id  = Column(String(50), unique=True, index=True, nullable=False)
    type        = Column(String(50), nullable=False)          # truck | van | bike | ev
    fuel_type   = Column(String(30), nullable=False)          # diesel | petrol | electric | hybrid
    capacity_kg = Column(Float, nullable=False)
    is_active   = Column(Boolean, default=True)
    driver_name = Column(String(100), nullable=True)
    current_location = Column(String(255), nullable=True)
