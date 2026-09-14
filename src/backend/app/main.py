from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .assistant import router as assistant_router

app = FastAPI(
    title="L2 Supply Chain Disruption Assistant",
    description="Backend API for supply chain disruption analysis and fleet utilisation optimisation.",
    version="0.1.0",
)

# Allow the Vite dev server (and any deployed frontend origin) to call the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assistant_router)


@app.get("/")
async def root():
    return {
        "message": "L2 Supply Chain Disruption Assistant API is running",
        "status": "ok",
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "supply-chain-backend",
    }


@app.get("/shipments")
async def get_shipments():
    return [
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

@app.get("/disruptions")
async def get_disruptions():
    return [
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
@app.get("/impacted-shipments/{disruption_id}")
async def get_impacted_shipments(disruption_id: str):
    disruptions = await get_disruptions()
    shipments = await get_shipments()

    disruption = next(
        (d for d in disruptions if d["disruption_id"] == disruption_id),
        None,
    )

    if disruption is None:
        return {
            "error": "Disruption not found",
            "disruption_id": disruption_id,
        }

    location = disruption["location"].lower()

    impacted_shipments = [
        shipment
        for shipment in shipments
        if location in shipment["origin"].lower()
        or location in shipment["destination"].lower()
    ]

    return {
        "disruption": disruption,
        "impacted_shipments": impacted_shipments,
        "impacted_count": len(impacted_shipments),
    }
@app.get("/cold-chain-risk/{shipment_id}")
async def get_cold_chain_risk(shipment_id: str):
    shipments = await get_shipments()

    shipment = next(
        (s for s in shipments if s["shipment_id"] == shipment_id),
        None,
    )

    if shipment is None:
        return {
            "error": "Shipment not found",
            "shipment_id": shipment_id,
        }

    if not shipment["cold_chain"]:
        return {
            "shipment_id": shipment_id,
            "cold_chain": False,
            "risk_level": "Not Applicable",
            "message": "This shipment does not require cold-chain monitoring.",
        }

    # Demo sensor reading.
    # Vaccines are assumed to require 2°C to 8°C.
    current_temperature = 7.5
    minimum_temperature = 2.0
    maximum_temperature = 8.0

    if current_temperature < minimum_temperature:
        risk_level = "Critical"
        message = "Temperature is below the safe cold-chain range."
    elif current_temperature > maximum_temperature:
        risk_level = "Critical"
        message = "Temperature is above the safe cold-chain range."
    elif current_temperature >= 7.0:
        risk_level = "High"
        message = "Temperature is approaching the upper safe limit."
    else:
        risk_level = "Low"
        message = "Temperature is within the safe cold-chain range."

    return {
        "shipment_id": shipment_id,
        "cargo_type": shipment["cargo_type"],
        "cargo_value": shipment["cargo_value"],
        "cold_chain": True,
        "current_temperature_c": current_temperature,
        "safe_range_c": {
            "minimum": minimum_temperature,
            "maximum": maximum_temperature,
        },
        "risk_level": risk_level,
        "message": message,
    }
@app.get("/fleet")
async def get_fleet():
    return [
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
@app.get("/fleet-recommendation/{shipment_id}")
async def get_fleet_recommendation(shipment_id: str):
    shipments = await get_shipments()
    fleet = await get_fleet()

    shipment = next(
        (s for s in shipments if s["shipment_id"] == shipment_id),
        None,
    )

    if shipment is None:
        return {
            "error": "Shipment not found",
            "shipment_id": shipment_id,
        }

    suitable_assets = [
        asset
        for asset in fleet
        if asset["available"]
        and asset["capacity_tons"] >= 15
        and (not shipment["cold_chain"] or asset["refrigerated"])
    ]

    if not suitable_assets:
        return {
            "shipment_id": shipment_id,
            "recommendation": None,
            "message": "No suitable fleet asset is currently available.",
        }

    # Prefer assets that are already closest to the shipment destination.
    destination = shipment["destination"].lower()

    suitable_assets.sort(
        key=lambda asset: (
            0 if asset["location"].lower() == destination else 1,
            asset["utilisation_percent"],
        )
    )

    recommended_asset = suitable_assets[0]

    return {
        "shipment_id": shipment_id,
        "cargo_type": shipment["cargo_type"],
        "cargo_value": shipment["cargo_value"],
        "cold_chain_required": shipment["cold_chain"],
        "recommended_asset": recommended_asset,
        "reason": (
            "The asset is available, has sufficient capacity, "
            "and supports refrigeration required for this cold-chain shipment."
            if shipment["cold_chain"]
            else "The asset is available and has sufficient capacity."
        ),
    }
@app.get("/simulate-disruption/{disruption_id}")
async def simulate_disruption(
    disruption_id: str,
    additional_hours: int = 48,
):
    disruptions = await get_disruptions()
    shipments = await get_shipments()

    disruption = next(
        (d for d in disruptions if d["disruption_id"] == disruption_id),
        None,
    )

    if disruption is None:
        return {
            "error": "Disruption not found",
            "disruption_id": disruption_id,
        }

    location = disruption["location"].lower()

    impacted_shipments = [
        shipment
        for shipment in shipments
        if location in shipment["origin"].lower()
        or location in shipment["destination"].lower()
    ]

    total_cargo_value = sum(
        shipment["cargo_value"]
        for shipment in impacted_shipments
    )

    cold_chain_shipments = [
        shipment
        for shipment in impacted_shipments
        if shipment["cold_chain"]
    ]

    projected_risk = "Medium"

    if additional_hours >= 48 and cold_chain_shipments:
        projected_risk = "Critical"
    elif additional_hours >= 24:
        projected_risk = "High"

    return {
        "disruption_id": disruption_id,
        "disruption_type": disruption["type"],
        "location": disruption["location"],
        "original_duration_hours": disruption["expected_duration_hours"],
        "additional_hours": additional_hours,
        "projected_total_duration_hours": (
            disruption["expected_duration_hours"] + additional_hours
        ),
        "impacted_shipment_count": len(impacted_shipments),
        "cold_chain_shipment_count": len(cold_chain_shipments),
        "total_cargo_value_at_risk": total_cargo_value,
        "projected_risk": projected_risk,
        "recommendation": (
            "Prioritise cold-chain shipments and allocate refrigerated "
            "fleet capacity immediately."
            if projected_risk == "Critical"
            else "Monitor affected shipments and prepare alternative fleet capacity."
        ),
    }