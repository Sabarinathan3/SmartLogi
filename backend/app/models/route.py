"""
models/route.py – SQLAlchemy Route model.
"""

from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Route(Base):
    __tablename__ = "routes"

    id           = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id     = Column(String(50), unique=True, index=True, nullable=False)
    origin       = Column(String(255), nullable=False)
    destination  = Column(String(255), nullable=False)
    waypoints    = Column(JSON, nullable=True)          # list of intermediate points
    distance_km  = Column(Float, nullable=False)
    duration_min = Column(Float, nullable=False)
    optimised    = Column(String(5), default="false")   # "true" | "false"
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
