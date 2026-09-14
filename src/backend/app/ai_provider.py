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
    def generate(self, system_prompt: str, user_message: str) -> str:
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

    def generate(self, system_prompt: str, user_message: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ]
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
    Returns a structured plain-text answer built directly from the facts dict
    without calling any external API.  Useful for demo/development when
    watsonx credentials are not yet configured.
    """

    def generate(self, system_prompt: str, user_message: str) -> str:  # noqa: ARG002
        return (
            "IBM watsonx.ai is not yet configured.\n\n"
            "The structured data above contains the deterministic facts "
            "computed by the backend.  To enable AI-generated explanations, "
            "set the WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL "
            "environment variables and restart the server."
        )


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
