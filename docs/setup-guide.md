# Setup Guide

## Prerequisites

- Python 3.11 or later
- Node.js 18 or later
- An IBM Cloud account with watsonx.ai access *(optional — the app runs fully without it using the built-in FallbackProvider)*

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp src/.env.example src/backend/.env
```

| Variable | Description | Required |
|---|---|---|
| `WATSONX_API_KEY` | IBM Cloud API key | For AI prose answers |
| `WATSONX_PROJECT_ID` | watsonx.ai project ID | For AI prose answers |
| `WATSONX_URL` | watsonx.ai endpoint URL | For AI prose answers |
| `WATSONX_MODEL_ID` | Model ID (default: `ibm/granite-3-8b-instruct`) | No |

> Without watsonx credentials the assistant still returns fully structured, data-grounded answers via the built-in `FallbackProvider`.

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd bob-ai-hackathon--code_crew-

# 2. Create and activate a Python virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install backend dependencies
pip install -r src/backend/requirements.txt

# Optional: install IBM watsonx.ai SDK for AI-generated answers
pip install ibm-watsonx-ai

# 4. Install frontend dependencies
cd frontend
npm install
cd ..
```

## Running the Application

Open **two terminals**:

**Terminal 1 — Backend (FastAPI)**
```bash
# From repo root, with venv activated:
cd src/backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend (Vite dev server)**
```bash
cd frontend
npm run dev
```

The application will be available at: **http://localhost:5173**

The API will be running at: **http://localhost:8000**

API docs (Swagger UI): **http://localhost:8000/docs**

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/shipments` | All shipments with risk levels |
| GET | `/disruptions` | Active and monitored disruptions |
| GET | `/fleet` | Fleet asset availability and utilisation |
| GET | `/cold-chain-risk/{shipment_id}` | Cold-chain temperature risk for a shipment |
| GET | `/fleet-recommendation/{shipment_id}` | Best available fleet asset for a shipment |
| GET | `/impacted-shipments/{disruption_id}` | Shipments affected by a disruption |
| GET | `/simulate-disruption/{disruption_id}` | 48-hour what-if simulation |
| POST | `/assistant` | AI conversational assistant |

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: fastapi` | Run `pip install -r src/backend/requirements.txt` |
| `CORS error in browser` | Ensure the backend is running on port 8000 |
| `watsonx.ai 401 Unauthorized` | Check `WATSONX_API_KEY` and `WATSONX_PROJECT_ID` in your `.env` file |
| Assistant returns "not configured" message | watsonx credentials not set — this is expected; the FallbackProvider will still return structured answers |
| Frontend shows fallback data | Backend is not running — start `uvicorn app.main:app --reload` |
