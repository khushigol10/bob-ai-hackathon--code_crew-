# Solution Overview

## What We Built

The **Supply Chain Control Tower** is a web application that gives logistics operations teams a single, real-time view of active disruptions, at-risk shipments, cold-chain exposure, and available fleet assets — with an embedded AI assistant that answers natural-language questions grounded entirely in live backend data.

The core design principle: **the deterministic backend is always the source of truth**. The AI layer (IBM watsonx.ai / Granite) receives structured facts computed by the backend and narrates them — it never invents numbers, shipment IDs, cargo values, or risk scores.

## How It Works

1. **The React dashboard** loads in the browser and displays the current state: active disruptions, shipments ranked by risk, fleet availability, and key metrics (active disruptions count, shipments at risk, cold-chain shipment count, available fleet).

2. **The FastAPI backend** exposes six deterministic REST endpoints:
   - `GET /shipments` — all shipments with status, risk level, cold-chain flag, and cargo value.
   - `GET /disruptions` — active and monitored disruptions with severity and expected duration.
   - `GET /impacted-shipments/{disruption_id}` — shipments affected by a given disruption (matched by location).
   - `GET /cold-chain-risk/{shipment_id}` — cold-chain temperature status and risk level for a shipment.
   - `GET /fleet` — all fleet assets with availability, refrigeration capability, and utilisation.
   - `GET /fleet-recommendation/{shipment_id}` — best available fleet asset for a shipment (proximity + utilisation ranked).
   - `GET /simulate-disruption/{disruption_id}?additional_hours=48` — projects total duration, impacted shipments, cold-chain exposure, cargo value at risk, and escalated risk level.

3. **The What-If Simulation panel** on the dashboard calls `simulate-disruption` with `additional_hours=48` for the Rotterdam port strike and displays the computed result: projected duration (96 h), 1 impacted cold-chain shipment (Vaccines, $520,000), projected risk: **Critical**.

4. **The Bob AI Assistant panel** (`POST /assistant`) accepts a natural-language question, runs `_gather_facts()` to collect relevant structured data from the backend logic, serialises it as JSON, and passes it to the AI provider alongside the question. The system prompt instructs the model to use only the provided facts.

5. **The AI provider layer** (`ai_provider.py`) automatically selects between:
   - **WatsonxProvider** — uses the `ibm-watsonx-ai` SDK to call `ibm/granite-3-8b-instruct` via the chat API, when `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` are configured.
   - **FallbackProvider** — returns a clear explanation that watsonx is not configured, while still returning the full structured `facts` dict so the frontend can display the backend data regardless.

6. **The frontend AssistantPanel** renders the AI answer, the provider name (with a watsonx badge if live), and a collapsible "Structured backend data" block showing the raw JSON facts — making the grounding transparent to judges and users.

## Architecture Diagram

See [`architecture.md`](architecture.md) for the full diagram.

```
[Browser]
   │
   ├──► [React Dashboard]  ──────────────────────────────────────────────┐
   │       • Disruptions panel                                            │
   │       • Shipment Risk Monitor                                        │
   │       • What-If Simulation                                           │
   │       • Fleet Availability                                           │
   │                                                                      │
   └──► [AssistantPanel]  ──► POST /assistant                            │
                                    │                                     │
                          [FastAPI Backend]  ◄───────────────────────────┘
                                    │         GET /shipments, /fleet, etc.
                          ┌─────────┴──────────┐
                          │                    │
                   [_gather_facts()]     [REST endpoints]
                          │              (deterministic)
                          │
                   [AI Provider]
                     ┌────┴────┐
              [Watsonx]   [Fallback]
           ibm/granite-3      (structured
           -8b-instruct        data only)
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Deterministic backend first, AI narrates | Eliminates hallucination risk; AI can only state what the backend calculated |
| Fallback provider | Application is fully functional without watsonx credentials — critical for demo resilience |
| Inline data in backend (no database) | Hackathon scope; keeps setup to zero dependencies beyond Python and Node |
| Facts passed as JSON in system context | Granite receives a structured prompt with explicit data — no retrieval augmentation needed at this scale |
| `max_new_tokens=600, temperature=0.2` | Keeps answers concise and deterministic; low temperature reduces creative deviation from the facts |
| Pydantic response models | Enforces `answer`, `facts`, `provider` contract between backend and frontend |

## IBM Technologies Used

- **IBM watsonx.ai (`ibm/granite-3-8b-instruct`):** Used via the `ibm-watsonx-ai` Python SDK's `ModelInference.chat()` API. The model receives a system prompt defining its role and constraints, then a user message containing the serialised JSON facts and the natural-language question. It returns a grounded, prose explanation. Model parameters: `max_new_tokens=600`, `temperature=0.2`.

- **IBM Bob:** Used as the AI coding assistant throughout development of this project — including the backend API design, frontend component architecture, assistant orchestration logic, and this documentation.
