"""
Single source of truth for all demo supply-chain data.

Both main.py (REST endpoints) and assistant.py (AI fact-gathering) import
from here so the data is never duplicated or out of sync.
"""

from __future__ import annotations

SHIPMENTS: list[dict] = [
    {
        "shipment_id": "SHIP-001",
        "origin": "Mumbai",
        "destination": "Rotterdam",
        "cargo_type": "Vaccines",
        "cold_chain": True,
        "cargo_value": 520000,
        "status": "In Transit",
        "risk_level": "High",
    },
    {
        "shipment_id": "SHIP-002",
        "origin": "Chennai",
        "destination": "Singapore",
        "cargo_type": "Perishable Food",
        "cold_chain": True,
        "cargo_value": 180000,
        "status": "Delayed",
        "risk_level": "Critical",
    },
    {
        "shipment_id": "SHIP-003",
        "origin": "Delhi",
        "destination": "Dubai",
        "cargo_type": "Electronics",
        "cold_chain": False,
        "cargo_value": 250000,
        "status": "In Transit",
        "risk_level": "Medium",
    },
]

DISRUPTIONS: list[dict] = [
    {
        "disruption_id": "DISR-001",
        "type": "Port Strike",
        "location": "Rotterdam",
        "severity": "High",
        "status": "Active",
        "expected_duration_hours": 48,
        "description": "Labour strike affecting container handling and port operations.",
    },
    {
        "disruption_id": "DISR-002",
        "type": "Severe Weather",
        "location": "Arabian Sea",
        "severity": "Medium",
        "status": "Monitoring",
        "expected_duration_hours": 24,
        "description": "Severe weather may delay vessel movement and port arrivals.",
    },
]

FLEET: list[dict] = [
    {
        "asset_id": "TRUCK-017",
        "asset_type": "Refrigerated Truck",
        "location": "Rotterdam",
        "capacity_tons": 20,
        "available": True,
        "refrigerated": True,
        "utilisation_percent": 35,
    },
    {
        "asset_id": "TRUCK-021",
        "asset_type": "Standard Truck",
        "location": "Mumbai",
        "capacity_tons": 25,
        "available": True,
        "refrigerated": False,
        "utilisation_percent": 80,
    },
    {
        "asset_id": "TRUCK-034",
        "asset_type": "Refrigerated Truck",
        "location": "Dubai",
        "capacity_tons": 18,
        "available": False,
        "refrigerated": True,
        "utilisation_percent": 95,
    },
    {
        "asset_id": "TRUCK-042",
        "asset_type": "Standard Truck",
        "location": "Delhi",
        "capacity_tons": 22,
        "available": True,
        "refrigerated": False,
        "utilisation_percent": 25,
    },
]
