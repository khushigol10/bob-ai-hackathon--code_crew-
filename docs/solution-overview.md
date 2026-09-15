# Solution Overview

## What We Built

**L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer** is a real-time supply chain control tower with an embedded AI assistant.

The application has two layers:

1. **A deterministic operations dashboard** that gives operations teams instant visibility into active disruptions, cold-chain cargo risk, fleet utilisation, and shipment status — all in a single screen.

2. **An AI conversational assistant** (powered by IBM watsonx.ai, Granite 3 8B Instruct) that answers natural-language questions about the live operational state, grounding every answer in verified backend data.

## How It Solves the Problem

| Problem | Our Solution |
|---|---|
| Which shipments are affected by a disruption? | `GET /impacted-shipments/{id}` — instant location-match across all active routes |
| How bad will it get if the disruption extends? | "Run Simulation" button calls `GET /simulate-disruption/DISR-001?additional_hours=48` and projects cold-chain count, cargo value at risk, and risk level |
| Which fleet asset should be reallocated? | `GET /fleet-recommendation/{shipment_id}` — filters by availability, capacity, and refrigeration requirement |
| I want to ask a follow-up question in plain English | `POST /assistant` — natural-language query answered with structured backend facts, multi-turn context preserved |

## Key Design Decisions

### Fact-grounded AI
Every AI response is built from a structured `facts` dict computed deterministically by the backend before any AI model is called. The model receives the facts as context and can only explain/elaborate — it cannot invent shipment IDs, cargo values, temperatures, or risk scores. This is a deliberate architectural choice for reliability in operational settings.

### Graceful degradation
The `FallbackProvider` ensures the assistant remains fully functional even without watsonx credentials. It parses the same `facts` dict and generates structured, readable answers using Python string templates. The dashboard also uses hardcoded fallback data if the backend is unreachable.

### Single source of truth
All three copies of the supply-chain data (previously duplicated across `main.py`, `assistant.py`, and `App.jsx`) were consolidated. The backend reads from a single `data.py` module; the frontend fetches from the backend at runtime.

## Features Implemented

- **Live dashboard**: KPI cards (active disruptions, shipments at risk, cold-chain count, available fleet) computed from backend data
- **Disruption monitoring**: Active and monitoring-status disruptions with severity badges
- **Fleet panel**: Asset availability, type, location, and utilisation percentage
- **Shipment risk table**: All shipments with origin→destination route, cargo type, cargo value, and risk level
- **What-if simulation**: 48-hour extension simulation with projected duration, impacted count, cold-chain exposure, cargo value at risk, and risk level
- **AI assistant**: Three suggested questions + free-form input, multi-turn conversation, structured facts collapsible debug view, inline markdown rendering
- **watsonx.ai integration**: IBM Granite 3 8B Instruct via `ibm-watsonx-ai` chat API, with automatic fallback to structured template answers
