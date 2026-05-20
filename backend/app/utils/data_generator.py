"""
utils/data_generator.py – Random mock logistics data generator.
"""

import random
import uuid
from typing import List, Dict

# ── Location pool ─────────────────────────────────────────────────────────────
LOCATIONS = [
    "Mumbai Central", "Delhi Gate", "Bangalore Tech Park",
    "Chennai Port", "Hyderabad Hub", "Pune Depot",
    "Kolkata Warehouse", "Ahmedabad Yard", "Jaipur Sorting",
    "Surat Distribution Center", "Lucknow Station", "Kochi Docks",
]

STATUSES    = ["pending", "in_transit", "delivered", "delayed"]
RISK_LEVELS = ["Low", "Medium", "High"]
VEHICLE_TYPES = ["truck", "van", "bike", "ev_van", "mini_truck"]
FUEL_TYPES  = ["diesel", "petrol", "electric", "hybrid", "cng"]
DRIVER_NAMES = [
    "Ravi Kumar", "Suresh Yadav", "Anita Singh", "Priya Sharma",
    "Mohammed Ali", "Deepak Verma", "Neha Gupta", "Sanjay Patil",
]


def generate_mock_orders(n: int = 10) -> List[Dict]:
    """Generate `n` random logistics orders."""
    orders = []
    for i in range(1, n + 1):
        pickup, drop = random.sample(LOCATIONS, 2)
        orders.append({
            "id":              i,
            "order_id":        f"ORD-{str(uuid.uuid4())[:8].upper()}",
            "pickup_location": pickup,
            "drop_location":   drop,
            "status":          random.choice(STATUSES),
            "eta":             f"{random.randint(1, 72)} hrs",
            "distance_km":     round(random.uniform(10, 800), 1),
            "delay_risk":      random.choice(RISK_LEVELS),
        })
    return orders


def generate_mock_vehicles(n: int = 8) -> List[Dict]:
    """Generate `n` random fleet vehicles."""
    vehicles = []
    for i in range(1, n + 1):
        vehicles.append({
            "id":               i,
            "vehicle_id":       f"VH-{str(uuid.uuid4())[:6].upper()}",
            "type":             random.choice(VEHICLE_TYPES),
            "fuel_type":        random.choice(FUEL_TYPES),
            "capacity_kg":      round(random.uniform(200, 5000), 0),
            "is_active":        random.choice([True, True, True, False]),  # 75% active
            "driver_name":      random.choice(DRIVER_NAMES),
            "current_location": random.choice(LOCATIONS),
        })
    return vehicles


def generate_mock_routes(n: int = 5) -> List[Dict]:
    """Generate `n` random routes with waypoints."""
    routes = []
    for i in range(1, n + 1):
        num_stops = random.randint(2, 5)
        stops = random.sample(LOCATIONS, num_stops)
        routes.append({
            "id":           i,
            "route_id":     f"RT-{str(uuid.uuid4())[:6].upper()}",
            "origin":       stops[0],
            "destination":  stops[-1],
            "waypoints":    stops[1:-1] if len(stops) > 2 else [],
            "distance_km":  round(random.uniform(20, 600), 1),
            "duration_min": round(random.uniform(30, 600), 0),
            "optimised":    random.choice(["true", "false"]),
        })
    return routes
