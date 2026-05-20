"""
ai/predictive_dispatch.py
Just-in-Time Predictive Dispatch + Virtual Hub Engine.

Three sub-engines:
  1. ETA Predictor    – haversine distance + traffic penalty → minutes
  2. Virtual Hub Gen  – geometric centroid of converging routes,
                        snapped to nearest named waypoint
  3. JIT Sync Engine  – speed delta to align all ETAs within ±5 minutes
"""

from __future__ import annotations
import math
from typing import TypedDict

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
_EARTH_RADIUS_KM   = 6371.0
_CO2_KG_PER_KM     = 0.212          # diesel truck
_IDLE_CO2_KG_MIN   = 0.031          # idling emission per minute
_SYNC_WINDOW_MIN   = 5              # acceptable ETA spread (minutes)
_MIN_SPEED_KMH     = 35
_MAX_SPEED_KMH     = 90

# Named waypoints across India (lat, lng, name)
_WAYPOINTS: list[tuple[float, float, str]] = [
    (19.0760,  72.8777, "Mumbai Central"),
    (18.5204,  73.8567, "Pune Depot"),
    (17.3850,  78.4867, "Hyderabad Hub"),
    (12.9716,  77.5946, "Bangalore Yard"),
    (28.6139,  77.2090, "Delhi Gate"),
    (22.5726,  88.3639, "Kolkata Port"),
    (21.1458,  79.0882, "Nagpur Centre"),
    (23.0225,  72.5714, "Ahmedabad Logistics Park"),
    (15.3647,  75.1240, "Hubli Transfer Point"),
    (20.4625,  85.8828, "Bhubaneswar Hub"),
]


# ─────────────────────────────────────────────────────────────────────────────
# TypedDicts
# ─────────────────────────────────────────────────────────────────────────────
class TruckIn(TypedDict):
    truck_id: str
    current_lat: float
    current_lng: float
    dest_lat: float
    dest_lng: float
    current_speed_kmh: float   # km/h
    traffic_level: str         # low | moderate | heavy


class VirtualHub(TypedDict):
    hub_id: str
    name: str
    lat: float
    lng: float
    participating_trucks: list[str]
    synchronized_eta_min: float


class TruckSyncRec(TypedDict):
    truck_id: str
    recommended_speed_kmh: float
    current_speed_kmh: float
    speed_delta_kmh: float      # negative = slow down
    arrival_sync_status: str    # early | on-time | delayed
    idling_time_saved_min: float
    guidance_text: str


class DispatchResult(TypedDict):
    virtual_hubs: list[VirtualHub]
    sync_recommendations: list[TruckSyncRec]
    total_idling_saved_min: float
    estimated_co2_reduction_kg: float


# ─────────────────────────────────────────────────────────────────────────────
# 1. Haversine ETA Predictor
# ─────────────────────────────────────────────────────────────────────────────
def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lng2 - lng1)
    a = math.sin(Δφ / 2) ** 2 + math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def predict_eta_minutes(
    current_lat: float, current_lng: float,
    dest_lat: float, dest_lng: float,
    speed_kmh: float,
    traffic: str,
) -> float:
    dist = _haversine_km(current_lat, current_lng, dest_lat, dest_lng)
    traffic_penalty = {"low": 1.0, "moderate": 1.25, "heavy": 1.6}.get(
        traffic.lower(), 1.15
    )
    effective_speed = max(speed_kmh / traffic_penalty, _MIN_SPEED_KMH)
    return (dist / effective_speed) * 60.0   # → minutes


# ─────────────────────────────────────────────────────────────────────────────
# 2. Virtual Hub Generator
# ─────────────────────────────────────────────────────────────────────────────
def _nearest_waypoint(lat: float, lng: float) -> tuple[float, float, str]:
    return min(
        _WAYPOINTS,
        key=lambda w: _haversine_km(lat, lng, w[0], w[1]),
    )


def generate_virtual_hub(trucks: list[TruckIn], hub_index: int) -> VirtualHub:
    """
    Compute a virtual meeting point as the centroid of truck destinations,
    then snap to the nearest named waypoint for a realistic hub name.
    """
    centroid_lat = sum(t["dest_lat"] for t in trucks) / len(trucks)
    centroid_lng = sum(t["dest_lng"] for t in trucks) / len(trucks)
    hub_lat, hub_lng, hub_name = _nearest_waypoint(centroid_lat, centroid_lng)

    # ETA of each truck to the hub (using their current params)
    etas = [
        predict_eta_minutes(
            t["current_lat"], t["current_lng"],
            hub_lat, hub_lng,
            t["current_speed_kmh"],
            t.get("traffic_level", "moderate"),
        )
        for t in trucks
    ]
    sync_eta = round(sum(etas) / len(etas), 1)   # average = target

    return VirtualHub(
        hub_id            = f"HUB-{hub_index:02d}",
        name              = hub_name,
        lat               = hub_lat,
        lng               = hub_lng,
        participating_trucks = [t["truck_id"] for t in trucks],
        synchronized_eta_min = sync_eta,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. JIT Speed Synchronization
# ─────────────────────────────────────────────────────────────────────────────
def _sync_status(delta_min: float) -> str:
    if delta_min < -_SYNC_WINDOW_MIN:
        return "early"
    if delta_min > _SYNC_WINDOW_MIN:
        return "delayed"
    return "on-time"


def _guidance(delta_kmh: float, status: str) -> str:
    if status == "on-time":
        return "Maintain current speed for synchronized arrival"
    if delta_kmh < 0:
        reduction = abs(round(delta_kmh, 1))
        return f"Reduce speed by {reduction} km/h to avoid early arrival and idling"
    increase = round(delta_kmh, 1)
    return f"Increase speed by {increase} km/h to stay on schedule"


def compute_sync_recommendation(
    truck: TruckIn,
    target_hub: VirtualHub,
    target_eta_min: float,
) -> TruckSyncRec:
    hub = target_hub
    current_eta = predict_eta_minutes(
        truck["current_lat"], truck["current_lng"],
        hub["lat"], hub["lng"],
        truck["current_speed_kmh"],
        truck.get("traffic_level", "moderate"),
    )

    dist_to_hub = _haversine_km(
        truck["current_lat"], truck["current_lng"],
        hub["lat"], hub["lng"],
    )

    # Required speed to hit target ETA
    if target_eta_min > 0:
        required_speed = (dist_to_hub / target_eta_min) * 60.0
    else:
        required_speed = truck["current_speed_kmh"]

    recommended = round(
        max(_MIN_SPEED_KMH, min(_MAX_SPEED_KMH, required_speed)), 1
    )
    delta_speed = round(recommended - truck["current_speed_kmh"], 1)
    delta_eta   = round(current_eta - target_eta_min, 1)
    status      = _sync_status(delta_eta)

    # Idling time saved = time truck would have waited if arriving early
    idling_saved = max(0.0, round(-delta_eta if delta_eta < 0 else 0.0, 1))

    return TruckSyncRec(
        truck_id                = truck["truck_id"],
        recommended_speed_kmh   = recommended,
        current_speed_kmh       = truck["current_speed_kmh"],
        speed_delta_kmh         = delta_speed,
        arrival_sync_status     = status,
        idling_time_saved_min   = idling_saved,
        guidance_text           = _guidance(delta_speed, status),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ─────────────────────────────────────────────────────────────────────────────
def run_predictive_dispatch(trucks: list[TruckIn]) -> DispatchResult:
    """
    Full pipeline:
      1. Pair trucks into groups of 2 (expandable to N).
      2. Generate a Virtual Hub per group.
      3. Compute JIT speed recommendations.
      4. Aggregate savings.
    """
    if not trucks:
        return DispatchResult(
            virtual_hubs=[], sync_recommendations=[],
            total_idling_saved_min=0.0, estimated_co2_reduction_kg=0.0,
        )

    # Group trucks in pairs (simple heuristic for demo)
    groups: list[list[TruckIn]] = []
    for i in range(0, len(trucks), 2):
        group = trucks[i : i + 2]
        if group:
            groups.append(group)

    hubs: list[VirtualHub]         = []
    recs: list[TruckSyncRec]       = []
    total_idling   = 0.0

    for idx, group in enumerate(groups, start=1):
        hub = generate_virtual_hub(group, idx)
        hubs.append(hub)
        for truck in group:
            rec = compute_sync_recommendation(truck, hub, hub["synchronized_eta_min"])
            recs.append(rec)
            total_idling += rec["idling_time_saved_min"]

    co2_reduction = round(total_idling * _IDLE_CO2_KG_MIN, 2)

    return DispatchResult(
        virtual_hubs               = hubs,
        sync_recommendations       = recs,
        total_idling_saved_min     = round(total_idling, 1),
        estimated_co2_reduction_kg = co2_reduction,
    )
