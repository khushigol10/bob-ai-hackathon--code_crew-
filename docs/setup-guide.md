# Setup Guide

> **This file is read by the automated evaluation pipeline. Follow every step exactly.**

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11 or later** — [Download](https://www.python.org/downloads/)
  - Verify: `python --version` (Windows) or `python3 --version` (macOS/Linux)
- **Node.js 18 or later** — [Download](https://nodejs.org/)
  - Verify: `node --version`
- **Git** — [Download](https://git-scm.com/)

> **IBM watsonx.ai credentials are optional.** The application runs fully in fallback mode without them. See [Enabling IBM watsonx.ai](#enabling-ibm-watsonxai-optional) below.

---

## 1 — Clone the Repository

```powershell
# Windows PowerShell
git clone https://github.com/<your-org>/bob-ai-hackathon--code_crew-.git
cd bob-ai-hackathon--code_crew-
```

```bash
# macOS / Linux
git clone https://github.com/<your-org>/bob-ai-hackathon--code_crew-.git
cd bob-ai-hackathon--code_crew-
```

---

## 2 — Set Up the Python Backend

### 2a — Create a virtual environment

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\activate
```

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your prompt.

### 2b — Install backend dependencies

```bash
pip install fastapi uvicorn python-dotenv pydantic
```

> The `ibm-watsonx-ai` package is **not** required for basic operation. See [Enabling IBM watsonx.ai](#enabling-ibm-watsonxai-optional) if you want live AI responses.

---

## 3 — Set Up the Frontend

```bash
cd frontend
npm install
cd ..
```

---

## 4 — Configure Environment Variables

The backend reads credentials from a `.env` file inside `src/`. **This file must never be committed to git** (it is already in `.gitignore`).

### 4a — Copy the example file

```powershell
# Windows
Copy-Item src\.env.example src\.env
```

```bash
# macOS / Linux
cp src/.env.example src/.env
```

### 4b — Edit `src/.env`

Open `src/.env` in any text editor.

**For fallback mode (no credentials needed):** you can leave the file as-is. The backend detects that `WATSONX_API_KEY` is not set and uses the `FallbackProvider` automatically.

**For live watsonx.ai responses:** fill in the three required values:

```dotenv
WATSONX_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
# Optional — defaults to ibm/granite-3-8b-instruct
# WATSONX_MODEL_ID=ibm/granite-3-8b-instruct
```

> **Where to find these values:**
> - `WATSONX_API_KEY` — IBM Cloud console → Manage → Access (IAM) → API keys
> - `WATSONX_PROJECT_ID` — watsonx.ai platform → your project → Manage → General → Project ID
> - `WATSONX_URL` — depends on your IBM Cloud region; `https://us-south.ml.cloud.ibm.com` is the US South default

---

## 5 — Run the Application

You need **two terminal windows** (or tabs).

### Terminal 1 — Backend

```powershell
# Windows — from the repo root, with (.venv) active
cd src
uvicorn backend.app.main:app --reload --port 8000
```

```bash
# macOS / Linux
cd src
uvicorn backend.app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### Terminal 2 — Frontend

```bash
# From the repo root
cd frontend
npm run dev
```

You should see:

```
  VITE v8.x.x  ready in Xms

  ➜  Local:   http://localhost:5173/
```

### Open the application

Navigate to **http://localhost:5173** in your browser.

---

## 6 — Verify It Works

1. **Dashboard loads** — you should see the header "Supply Chain Control Tower", metrics cards, the disruption panel, shipment risk table, and fleet panel.
2. **What-If Simulation** — click "Run Simulation" in the simulation panel. It should expand to show: Projected Duration 96 hours, Shipments Impacted 1, Cargo Value at Risk $520,000, Projected Risk CRITICAL.
3. **Bob AI Assistant** — scroll down to the assistant panel. Click the suggested question "Which shipments are at highest risk?" — you should receive a response within a few seconds.
   - In fallback mode: the response will explain that watsonx is not configured and show the structured facts JSON.
   - With credentials: IBM Granite will return a prose answer grounded in the backend data.
4. **API health check** — open http://localhost:8000/health in a browser or run:
   ```bash
   curl http://localhost:8000/health
   ```
   Expected: `{"status":"healthy","service":"supply-chain-backend"}`

---

## Enabling IBM watsonx.ai (Optional)

To enable live AI-generated answers using IBM Granite:

1. Ensure `src/.env` has valid values for `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, and `WATSONX_URL`.
2. Install the watsonx SDK:
   ```bash
   pip install ibm-watsonx-ai
   ```
3. Restart the backend server (CTRL+C, then re-run the `uvicorn` command).
4. The backend log will show: `INFO: WatsonxProvider initialised with model ibm/granite-3-8b-instruct`
5. The AssistantPanel will show a **POWERED BY WATSONX** badge and a provider label of `WatsonxProvider`.

---

## Running Checks

### Backend syntax check

```bash
python -m py_compile src/backend/app/main.py src/backend/app/assistant.py src/backend/app/ai_provider.py
```

No output = all OK.

### Frontend lint

```bash
cd frontend
npm run lint
```

Expected: `Found 0 warnings and 0 errors.`

### Frontend production build

```bash
cd frontend
npm run build
```

Expected: build completes with no errors, output in `frontend/dist/`.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install fastapi uvicorn python-dotenv pydantic` inside the activated virtual environment |
| `(.venv)` not showing in prompt | Re-run `.\.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (macOS/Linux) |
| `Error: Cannot find module` (npm) | Run `npm install` inside the `frontend/` directory |
| Backend starts but returns 502 on `/assistant` | Check the backend terminal for the error; most likely `WATSONX_API_KEY` is set but invalid — remove it from `.env` to use fallback mode |
| `ModuleNotFoundError: No module named 'ibm_watsonx_ai'` | Run `pip install ibm-watsonx-ai` or remove `WATSONX_API_KEY` from `.env` to use fallback |
| Port 8000 already in use | Stop the existing process or use `uvicorn backend.app.main:app --reload --port 8001` and update `API_BASE` in `frontend/src/AssistantPanel.jsx` to match |
| CORS error in browser console | Ensure the backend is running on port 8000 and the frontend on port 5173; other ports require updating the CORS `allow_origins` list in `src/backend/app/main.py` |
| Frontend shows wrong data | The frontend data is hardcoded to match the backend; if you modified the backend data, update `App.jsx` to match |
