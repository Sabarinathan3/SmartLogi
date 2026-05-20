"""
models/order.py – SQLAlchemy Order model.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.core.database import Base


class Order(Base):
    __tablename__ = "orders"

    id               = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id         = Column(String(50), unique=True, index=True, nullable=False)
    pickup_location  = Column(String(255), nullable=False)
    drop_location    = Column(String(255), nullable=False)
    status           = Column(String(50), default="pending")   # pending | in_transit | delivered | delayed
    eta              = Column(String(50), nullable=True)        # ISO timestamp or human-readable duration
    distance_km      = Column(Float, nullable=True)
    delay_risk       = Column(String(20), nullable=True)        # Low | Medium | High
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    updated_at       = Column(DateTime(timezone=True), onupdate=func.now())
