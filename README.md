# 🚀 L2 Supply Chain Disruption Assistant & Fleet Utilisation Optimizer

> A real-time supply chain control tower with an IBM watsonx.ai conversational assistant.

---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | code-crew |
| **Track** | AI |
| **Team Lead** | Khushi Gol — khushigol88@gmail.com |
| **Members** | Yana Savaliya, Esha Halani, Shukti Rabadiya |

---

## 🎯 Problem Statement

Supply chain operations teams face three urgent questions the moment a disruption hits: which shipments are affected, how bad it will get if the disruption extends, and which fleet assets should be redeployed. Manual cross-referencing of routes, cargo types, and fleet availability is too slow when cold-chain spoilage windows are measured in hours.

---

## 💡 Solution

We built a real-time Supply Chain Control Tower — a single-page dashboard backed by a FastAPI service — that monitors active disruptions, cold-chain risk, and fleet utilisation. An embedded AI assistant powered by IBM watsonx.ai (Granite 3 8B Instruct) answers natural-language questions about the live operational state, grounding every answer in deterministic backend facts so no values are ever invented.

---

## ✨ Key Features

- **Live disruption monitoring** — port strikes and weather events with severity badges and expected duration
- **Cold-chain risk assessment** — temperature range validation and spoilage alerts for vaccine and perishable cargo
- **48-hour what-if simulation** — projects total duration, impacted shipment count, cold-chain exposure, and cargo value at risk
- **Fleet utilisation optimiser** — matches available refrigerated/standard assets to shipment requirements
- **IBM watsonx.ai conversational assistant** — multi-turn context, structured fact grounding, inline markdown rendering

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.11+, JavaScript |
| **Frameworks** | FastAPI, React 19, Vite 8 |
| **IBM Technologies** | watsonx.ai, ibm/granite-3-8b-instruct |
| **Other** | uvicorn, pydantic, CORS middleware |

---

## 📁 Repository Structure

```
├── src/
│   └── backend/
│       ├── app/
│       │   ├── main.py          ← FastAPI app + all REST endpoints
│       │   ├── assistant.py     ← POST /assistant endpoint + intent/fact logic
│       │   ├── ai_provider.py   ← WatsonxProvider + FallbackProvider
│       │   └── data.py          ← Single source of truth for demo data
│       └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx              ← Dashboard UI (live backend data)
│   │   └── AssistantPanel.jsx   ← AI chat panel with markdown rendering
│   ├── vite.config.js
│   └── package.json
├── docs/
│   ├── problem-statement.md
│   ├── solution-overview.md
│   ├── architecture.md
│   └── setup-guide.md
└── submission.yaml
```

---

## ⚡ How to Run

```bash
# 1. Clone the repo and create a Python virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# 2. Install backend dependencies
pip install -r src/backend/requirements.txt

# Optional: enable AI-generated answers
pip install ibm-watsonx-ai

# 3. Configure watsonx credentials (optional)
cp src/.env.example src/backend/.env
# Edit src/backend/.env with WATSONX_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL

# 4. Start the backend (Terminal 1)
cd src/backend
uvicorn app.main:app --reload --port 8000

# 5. Install and start the frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

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

- All shipment, disruption, and fleet data is hardcoded demo data — not connected to a live database
- Cold-chain temperature readings are simulated (static sensor value)
- The what-if simulation UI only supports extending DISR-001 by 48 hours; the API supports any disruption and any duration
- No authentication or authorisation

---

## 🏅 What We're Most Proud Of

The AI assistant's **grounding architecture**: every answer is built from a structured `facts` dict computed deterministically by the backend before any AI model is called. The model cannot invent shipment IDs, cargo values, or risk scores — it can only explain and elaborate on verified data. The `FallbackProvider` ensures the full application gives real, useful answers even without watsonx credentials, making the demo reliable in any environment.
