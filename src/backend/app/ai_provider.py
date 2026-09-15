"""
AI provider abstraction for the supply-chain assistant.

Supports IBM watsonx.ai (ibm-watsonx-ai SDK) when credentials are present,
and falls back to a deterministic template-based responder so the application
is fully functional without credentials — you just won't get free-form prose.

Required environment variables (watsonx path):
  WATSONX_API_KEY      – IBM Cloud API key
  WATSONX_PROJECT_ID   – watsonx.ai project ID
  WATSONX_URL          – e.g. https://us-south.ml.cloud.ibm.com
  WATSONX_MODEL_ID     – optional, defaults to ibm/granite-3-8b-instruct
"""

from __future__ import annotations

import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class AIProvider(ABC):
    """Minimal interface that every AI backend must satisfy."""

    @abstractmethod
    def generate(self, system_prompt: str, user_message: str, history: list[dict] | None = None) -> str:
        """Return a plain-text response string."""


# ---------------------------------------------------------------------------
# watsonx.ai provider
# ---------------------------------------------------------------------------

class WatsonxProvider(AIProvider):
    """Uses ibm-watsonx-ai SDK to call an IBM foundation model."""

    def __init__(self) -> None:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        api_key = os.environ["WATSONX_API_KEY"]
        project_id = os.environ["WATSONX_PROJECT_ID"]
        url = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        model_id = os.environ.get("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct")

        credentials = Credentials(url=url, api_key=api_key)
        client = APIClient(credentials)

        self._model = ModelInference(
            model_id=model_id,
            api_client=client,
            params={"max_new_tokens": 600, "temperature": 0.2},
            project_id=project_id,
        )
        logger.info("WatsonxProvider initialised with model %s", model_id)

    def generate(self, system_prompt: str, user_message: str, history: list[dict] | None = None) -> str:
        messages = [{"role": "system", "content": system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})
        response = self._model.chat(messages=messages)
        # chat() returns a dict with choices[0].message.content
        try:
            return response["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            # Fallback: try generate_text path
            return str(response)


# ---------------------------------------------------------------------------
# Fallback provider (no credentials needed)
# ---------------------------------------------------------------------------

class FallbackProvider(AIProvider):
    """
    Generates a useful structured answer from the facts dict without any
    external API call.  Used when watsonx credentials are not configured.
    """

    def generate(self, system_prompt: str, user_message: str, history: list[dict] | None = None) -> str:  # noqa: ARG002
        import json as _json
        import re as _re

        # Extract the JSON block embedded in user_message by assistant.py
        json_match = _re.search(r"```json\n(.*?)```", user_message, _re.DOTALL)
        if not json_match:
            return "No structured data available to answer this question."

        try:
            facts = _json.loads(json_match.group(1))
        except _json.JSONDecodeError:
            return "Could not parse structured backend data."

        lines: list[str] = []

        # ── Summary ─────────────────────────────────────────────────────────
        summary = facts.get("summary", {})
        if summary:
            lines.append(
                f"**Current status:** {summary.get('total_shipments', '?')} shipments tracked, "
                f"{summary.get('active_disruptions', 0)} active disruption(s), "
                f"{summary.get('high_risk_shipments', 0)} at high/critical risk, "
                f"{summary.get('available_fleet_count', 0)} fleet assets available."
            )

        # ── Simulation ───────────────────────────────────────────────────────
        sim = facts.get("simulation")
        if sim and "error" not in sim:
            d = sim.get("disruption", {})
            lines.append(
                f"\n**What-if simulation — {d.get('type', 'disruption')} at {d.get('location', '?')}:**"
            )
            lines.append(
                f"- Original duration: {d.get('expected_duration_hours', '?')}h  "
                f"→ projected total: {sim.get('projected_total_duration_hours', '?')}h "
                f"(+{sim.get('additional_hours', '?')}h added)"
            )
            lines.append(f"- Shipments impacted: {len(sim.get('impacted_shipments', []))}")
            lines.append(f"- Cold-chain shipments at risk: {sim.get('cold_chain_shipment_count', 0)}")
            lines.append(
                f"- Total cargo value at risk: "
                f"${sim.get('total_cargo_value_at_risk', 0):,.0f}"
            )
            lines.append(f"- **Projected risk: {sim.get('projected_risk', '?').upper()}**")
            lines.append(f"- Recommendation: {sim.get('recommendation', '')}")

        # ── Shipments by risk ────────────────────────────────────────────────
        by_risk = facts.get("shipments_by_risk")
        if by_risk:
            lines.append("\n**Shipments ranked by risk:**")
            for s in by_risk:
                cold = " ❄️" if s.get("cold_chain") else ""
                lines.append(
                    f"- {s['shipment_id']}: {s['origin']} -> {s['destination']}  "
                    f"{s['cargo_type']}{cold}  |  ${s['cargo_value']:,}  |  "
                    f"**{s['risk_level']}** ({s['status']})"
                )

        # ── Fleet recommendation ─────────────────────────────────────────────
        fleet_rec = facts.get("fleet_recommendation")
        if fleet_rec and "error" not in fleet_rec:
            rec = fleet_rec.get("recommendation")
            shipment = fleet_rec.get("shipment", {})
            if rec:
                lines.append(
                    f"\n**Fleet recommendation for {shipment.get('shipment_id', '?')} "
                    f"({shipment.get('cargo_type', '?')}):**"
                )
                lines.append(
                    f"- Recommended asset: **{rec['asset_id']}** "
                    f"({rec['asset_type']}, {rec['location']})"
                )
                lines.append(
                    f"- Capacity: {rec['capacity_tons']}t  |  "
                    f"Utilisation: {rec['utilisation_percent']}%  |  "
                    f"Refrigerated: {'Yes' if rec['refrigerated'] else 'No'}"
                )
                lines.append(
                    "- Reason: asset is available, has sufficient capacity"
                    + (", and supports cold-chain refrigeration." if shipment.get("cold_chain") else ".")
                )

        if not lines:
            return (
                "I have the backend data but could not identify a specific answer. "
                "Try asking about shipment risk, the Rotterdam disruption, or fleet allocation."
            )

        lines.append(
            "\n_(Note: AI-generated prose is disabled — set WATSONX_API_KEY to enable "
            "watsonx.ai explanations.)_"
        )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def _try_watsonx() -> AIProvider | None:
    if not os.environ.get("WATSONX_API_KEY"):
        return None
    if not os.environ.get("WATSONX_PROJECT_ID"):
        logger.warning("WATSONX_API_KEY set but WATSONX_PROJECT_ID missing — using fallback.")
        return None
    try:
        import importlib
        importlib.import_module("ibm_watsonx_ai")
    except ModuleNotFoundError:
        logger.warning(
            "ibm-watsonx-ai package not installed — using fallback provider. "
            "Install with: pip install ibm-watsonx-ai"
        )
        return None
    try:
        return WatsonxProvider()
    except Exception as exc:  # noqa: BLE001
        logger.warning("WatsonxProvider init failed (%s) — using fallback.", exc)
        return None


def get_provider() -> AIProvider:
    """Return the best available AI provider."""
    provider = _try_watsonx()
    if provider is not None:
        return provider
    logger.info("Using FallbackProvider (no watsonx credentials configured).")
    return FallbackProvider()
