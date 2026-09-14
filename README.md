# Supply Chain Control Tower

> AI-powered disruption monitoring, cold-chain risk management, and fleet optimisation — built for the IBM Bob AI Hackathon.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | Code Crew |
| **Track** | AI |
| **Team Lead** | *(see submission.yaml)* |
| **Members** | *(see submission.yaml)* |

---

## 🎯 Problem Statement

Global supply chain operations teams are caught flat-footed when port strikes, severe weather, or logistics failures strike.
Responding to a disruption means manually cross-referencing shipment lists, cold-chain alerts, and fleet availability across multiple disconnected systems — taking 30–60 minutes at the exact moment speed matters most.
Cold-chain cargo (vaccines, perishables) is particularly exposed: every hour of uncertainty is a financial and safety risk.

---

## 💡 Solution

We built a **Supply Chain Control Tower** — a real-time dashboard backed by a FastAPI intelligence layer that detects disruptions, identifies at-risk shipments, and recommends fleet reallocation in seconds.
An embedded **Bob AI Assistant** (powered by IBM watsonx.ai / Granite) takes natural-language questions ("What if the Rotterdam strike lasts another 48 hours?") and responds with structured, grounded answers derived entirely from the deterministic backend — no hallucinated values, ever.
When watsonx credentials are not configured, the assistant runs in **fallback mode**, still returning all structured backend facts.

---

## ✨ Key Features

- **Real-time Disruption Dashboard** — live view of active disruptions, their severity, affected locations, and expected duration.
- **Shipment Risk Monitor** — all shipments ranked by risk level (Critical → High → Medium), with cold-chain flag, cargo value, and status.
- **What-If Simulation** — one-click simulation of the Rotterdam port strike extending 48 hours, computing projected risk escalation, impacted shipment count, and cargo value at risk from the deterministic backend.
- **Fleet Optimisation Recommendation** — automatically identifies the best available refrigerated or standard truck asset for any shipment, prioritising proximity to destination and lowest utilisation.
- **Bob AI Assistant** — natural-language Q&A grounded in live backend data via IBM watsonx.ai (Granite 3 8B Instruct); degrades gracefully to structured-data fallback mode when credentials are absent.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.11+, JavaScript (ES2022) |
| **Frameworks** | FastAPI 0.141, React 19, Vite 8 |
| **IBM Technologies** | IBM watsonx.ai (ibm/granite-3-8b-instruct), IBM Bob |
| **Databases** | None — in-memory data (hackathon scope) |
| **Other** | Uvicorn, python-dotenv, Pydantic v2, oxlint |

---

## 📁 Repository Structure

```
├── src/
│   ├── .env.example              # Environment variable template
│   └── backend/
│       └── app/
│           ├── main.py           # FastAPI app + all REST endpoints
│           ├── assistant.py      # /assistant endpoint + AI orchestration
│           └── ai_provider.py    # watsonx.ai provider + fallback
├── frontend/
│   └── src/
│       ├── App.jsx               # Main dashboard
│       └── AssistantPanel.jsx    # Bob AI chat panel
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
├── demo/
│   ├── screenshots/
│   ├── demo-video-link.txt
│   └── live-demo-url.txt
├── presentation/
└── submission.yaml
```

---

## ⚡ How to Run

Full instructions with troubleshooting are in [`docs/setup-guide.md`](docs/setup-guide.md).

**Quick start (Windows — fallback mode, no credentials needed):**

```powershell
# 1. Clone
git clone https://github.com/<your-org>/bob-ai-hackathon--code_crew-.git
cd bob-ai-hackathon--code_crew-

# 2. Backend
python -m venv .venv
.\.venv\Scripts\activate
pip install fastapi uvicorn python-dotenv pydantic

# 3. Frontend
cd frontend
npm install
cd ..

# 4. Run backend (terminal 1)
cd src
uvicorn backend.app.main:app --reload --port 8000

# 5. Run frontend (terminal 2)
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

To enable AI-generated answers, copy `src/.env.example` to `src/.env` and fill in `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, and `WATSONX_URL` before starting the backend.

---

## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](demo/live-demo-url.txt) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/](presentation/) |

---

## ⚠️ Known Limitations

- **Static data** — shipment, fleet, and disruption data is hardcoded in the backend for hackathon scope; a production version would connect to real logistics APIs or a database.
- **Cold-chain temperature** — the `/cold-chain-risk/{shipment_id}` endpoint uses a fixed demo sensor reading (7.5 °C) rather than a live IoT feed.
- **Single disruption simulation** — the What-If panel is fixed to the Rotterdam port strike (+48 h); the assistant endpoint supports arbitrary disruption IDs and durations via natural language.
- **No authentication** — API endpoints are open; production would require auth.
- **ibm-watsonx-ai package not bundled** — must be installed separately (see setup guide); the app runs fully without it in fallback mode.

---

## 🏅 What We're Most Proud Of

The **grounded AI assistant** architecture: the backend computes all facts deterministically first, then passes them as structured JSON context to IBM Granite. The model can only cite values that the backend calculated — it cannot hallucinate shipment IDs, cargo values, or risk scores. This "deterministic core + AI narration" pattern makes the assistant both trustworthy and demo-safe. The fallback mode ensures the entire application works end-to-end even without watsonx credentials, which made development and judging significantly easier.

---
