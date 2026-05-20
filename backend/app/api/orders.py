"""
api/orders.py – Orders API router.
"""

from fastapi import APIRouter
from app.schemas.order_schema import OrderSchema, OrderCreate
from app.utils.data_generator import generate_mock_orders
from typing import List
import uuid

router = APIRouter()

# ── In-memory store (hackathon) ───────────────────────────────────────────────
_orders: List[dict] = generate_mock_orders(10)


@router.get("/orders", response_model=List[OrderSchema])
async def get_orders():
    """Return all orders."""
    return _orders


@router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Return a single order by order_id."""
    for order in _orders:
        if order["order_id"] == order_id:
            return order
    return {"error": f"Order '{order_id}' not found"}


@router.post("/orders", response_model=OrderSchema, status_code=201)
async def create_order(order: OrderCreate):
    """Create a new order."""
    new_order = order.model_dump()
    new_order["id"] = len(_orders) + 1
    _orders.append(new_order)
    return new_order


@router.put("/orders/{order_id}")
async def update_order_status(order_id: str, status: str):
    """Update the status of an existing order."""
    for order in _orders:
        if order["order_id"] == order_id:
            order["status"] = status
            return {"message": "Order updated", "order": order}
    return {"error": f"Order '{order_id}' not found"}


@router.delete("/orders/{order_id}")
async def delete_order(order_id: str):
    """Delete an order by order_id."""
    global _orders
    before = len(_orders)
    _orders = [o for o in _orders if o["order_id"] != order_id]
    if len(_orders) < before:
        return {"message": f"Order '{order_id}' deleted"}
    return {"error": f"Order '{order_id}' not found"}
