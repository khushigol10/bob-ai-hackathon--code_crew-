"""
/assistant  endpoint — receives a natural-language question, gathers
structured facts from the existing backend logic, and returns both the
structured facts and an AI-generated explanation.
"""

from __future__ import annotations

import json
import logging
import re

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .ai_provider import get_provider
from .data import DISRUPTIONS, FLEET, SHIPMENTS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["assistant"])

# Lazy-initialise the provider once per worker process.
_provider = None


def _get_provider():
    global _provider  # noqa: PLW0603
    if _provider is None:
        _provider = get_provider()
    return _provider


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class HistoryMessage(BaseModel):
    role: str   # "user" | "assistant"
    content: str


class AssistantRequest(BaseModel):
    question: str
    history: list[HistoryMessage] = []


class AssistantResponse(BaseModel):
    answer: str
    facts: dict
    provider: str


# ---------------------------------------------------------------------------
# Supply-chain fact gathering (delegates to the deterministic backend data)
# ---------------------------------------------------------------------------

# SHIPMENTS, DISRUPTIONS, FLEET are imported from .data (single source of truth)


def _simulate_disruption(disruption_id: str, additional_hours: int) -> dict:
    disruption = next((d for d in DISRUPTIONS if d["disruption_id"] == disruption_id), None)
    if disruption is None:
        return {"error": f"Disruption {disruption_id} not found"}

    location = disruption["location"].lower()
    impacted = [
        s for s in SHIPMENTS
        if location in s["origin"].lower() or location in s["destination"].lower()
    ]
    cold_chain = [s for s in impacted if s["cold_chain"]]
    total_value = sum(s["cargo_value"] for s in impacted)

    if additional_hours >= 48 and cold_chain:
        projected_risk = "Critical"
        recommendation = (
            "Prioritise cold-chain shipments and allocate refrigerated fleet capacity immediately."
        )
    elif additional_hours >= 24:
        projected_risk = "High"
        recommendation = "Monitor affected shipments and prepare alternative fleet capacity."
    else:
        projected_risk = "Medium"
        recommendation = "Monitor situation closely."

    return {
        "disruption": disruption,
        "additional_hours": additional_hours,
        "projected_total_duration_hours": disruption["expected_duration_hours"] + additional_hours,
        "impacted_shipments": impacted,
        "cold_chain_shipment_count": len(cold_chain),
        "total_cargo_value_at_risk": total_value,
        "projected_risk": projected_risk,
        "recommendation": recommendation,
    }


def _fleet_recommendation(shipment_id: str) -> dict:
    shipment = next((s for s in SHIPMENTS if s["shipment_id"] == shipment_id), None)
    if shipment is None:
        return {"error": f"Shipment {shipment_id} not found"}

    suitable = [
        a for a in FLEET
        if a["available"]
        and a["capacity_tons"] >= 15
        and (not shipment["cold_chain"] or a["refrigerated"])
    ]

    if not suitable:
        return {"shipment": shipment, "recommendation": None, "available_fleet": []}

    destination = shipment["destination"].lower()
    suitable.sort(
        key=lambda a: (0 if a["location"].lower() == destination else 1, a["utilisation_percent"])
    )

    return {
        "shipment": shipment,
        "recommendation": suitable[0],
        "all_suitable": suitable,
    }


# ---------------------------------------------------------------------------
# Intent detection helpers
# ---------------------------------------------------------------------------

_DISRUPTION_KEYWORDS = re.compile(
    r"\b(strike|disruption|rotterdam|weather|arabian|delay|port|impact|what.if|hours?)\b",
    re.IGNORECASE,
)
_RISK_KEYWORDS = re.compile(
    r"\b(risk|highest|danger|critical|cold.chain|temperature|at risk)\b",
    re.IGNORECASE,
)
_FLEET_KEYWORDS = re.compile(
    r"\b(fleet|truck|asset|allocat|assign|vehicle|refrigerat|recommend)\b",
    re.IGNORECASE,
)
_SHIPMENT_ID = re.compile(r"SHIP-\d+", re.IGNORECASE)
_HOURS = re.compile(r"(\d+)\s*hours?", re.IGNORECASE)


def _gather_facts(question: str) -> dict:
    """
    Map the question to structured backend facts without AI.
    Returns a dict that will be serialised and passed to the AI as context.
    """
    q = question.lower()

    facts: dict = {}

    # ── Disruption simulation ────────────────────────────────────────────────
    if _DISRUPTION_KEYWORDS.search(q):
        hours_match = _HOURS.search(q)
        extra = int(hours_match.group(1)) if hours_match else 48

        # Pick the most relevant disruption
        disruption_id = "DISR-001"
        if "arabian" in q or "weather" in q:
            disruption_id = "DISR-002"

        facts["simulation"] = _simulate_disruption(disruption_id, extra)

    # ── Shipment risk ────────────────────────────────────────────────────────
    if _RISK_KEYWORDS.search(q) or "shipment" in q:
        by_risk = sorted(
            SHIPMENTS,
            key=lambda s: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(
                s["risk_level"], 9
            ),
        )
        facts["shipments_by_risk"] = by_risk

    # ── Fleet recommendation ─────────────────────────────────────────────────
    if _FLEET_KEYWORDS.search(q):
        ship_id_match = _SHIPMENT_ID.search(question)
        if ship_id_match:
            ship_id = ship_id_match.group(0).upper()
        elif "vaccine" in q:
            ship_id = "SHIP-001"
        else:
            ship_id = "SHIP-001"  # default to highest-value cold-chain shipment

        facts["fleet_recommendation"] = _fleet_recommendation(ship_id)
        facts["all_fleet"] = FLEET

    # ── Always include a high-level summary ─────────────────────────────────
    facts["summary"] = {
        "total_shipments": len(SHIPMENTS),
        "active_disruptions": sum(1 for d in DISRUPTIONS if d["status"] == "Active"),
        "high_risk_shipments": sum(
            1 for s in SHIPMENTS if s["risk_level"] in ("Critical", "High")
        ),
        "available_fleet_count": sum(1 for a in FLEET if a["available"]),
    }

    return facts


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert supply-chain operations assistant embedded in a real-time \
control tower.  You receive structured data from a deterministic backend and \
must use ONLY that data to answer the user's question.

Rules:
- Never invent shipment IDs, cargo values, temperatures, fleet capacity, or \
  risk scores.  Every fact you state must come from the structured data.
- Be concise.  Use bullet points where helpful.
- If a cold-chain shipment is at risk, highlight it prominently.
- When recommending fleet assets, explain WHY that asset was chosen.
- End with a clear, actionable recommendation.
"""


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("", response_model=AssistantResponse)
async def ask_assistant(body: AssistantRequest):
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="question must not be empty")

    facts = _gather_facts(body.question)

    facts_text = json.dumps(facts, indent=2)
    user_message = (
        f"Structured backend data:\n```json\n{facts_text}\n```\n\n"
        f"User question: {body.question}"
    )

    # Build conversation history for multi-turn context (last 4 pairs max)
    history = [{"role": m.role, "content": m.content} for m in body.history[-8:]]

    provider = _get_provider()
    provider_name = type(provider).__name__

    try:
        answer = provider.generate(SYSTEM_PROMPT, user_message, history=history)
    except Exception as exc:  # noqa: BLE001
        logger.exception("AI provider error")
        raise HTTPException(status_code=502, detail=f"AI provider error: {exc}") from exc

    return AssistantResponse(answer=answer, facts=facts, provider=provider_name)
