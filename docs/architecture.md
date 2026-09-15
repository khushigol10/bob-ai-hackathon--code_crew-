# Architecture

## System Architecture

```mermaid
graph TD
    Browser["User / Browser\nhttp://localhost:5173"] -->|renders| React["React 19 + Vite\nfrontend/"]
    React -->|GET /shipments\nGET /disruptions\nGET /fleet| FastAPI["FastAPI\nsrc/backend/app/main.py\nport 8000"]
    React -->|GET /simulate-disruption/DISR-001| FastAPI
    React -->|POST /assistant| AssistantRouter["assistant.py\n/assistant endpoint"]
    AssistantRouter -->|imports| DataModule["data.py\nSingle source of truth\nSHIPMENTS · DISRUPTIONS · FLEET"]
    FastAPI -->|imports| DataModule
    AssistantRouter -->|_gather_facts()| FactEngine["Intent detection\n+ Fact gathering\n(regex + deterministic logic)"]
    FactEngine -->|structured facts JSON| AssistantRouter
    AssistantRouter -->|system prompt + facts + question + history| AIProvider["ai_provider.py\nget_provider()"]
    AIProvider -->|if creds set| WatsonxProvider["WatsonxProvider\nibm-watsonx-ai SDK\nGranite 3 8B Instruct"]
    AIProvider -->|if no creds| FallbackProvider["FallbackProvider\nTemplate-based answer\nfrom facts dict"]
    WatsonxProvider -->|chat API| Watsonx["IBM watsonx.ai\nus-south.ml.cloud.ibm.com"]
    Watsonx -->|answer text| AssistantRouter
    FallbackProvider -->|answer text| AssistantRouter
    AssistantRouter -->|answer + facts + provider| React
```

## Components

| Component | Technology | Responsibility |
|---|---|---|
| Frontend | React 19, Vite 8 | Dashboard UI, live data display, what-if simulation, AI chat panel |
| Backend API | FastAPI, Python 3.11+ | REST endpoints, business logic, disruption simulation, fleet optimisation |
| AI Assistant | IBM watsonx.ai (Granite 3 8B Instruct) | Natural-language answers grounded in deterministic backend facts |
| FallbackProvider | Python (built-in) | Structured template answers when watsonx credentials are absent |
| Data layer | `data.py` module | Single source of truth for all demo shipment, disruption, and fleet data |

## Data Flow

### Dashboard data flow
1. React mounts → fires `GET /shipments`, `GET /disruptions`, `GET /fleet` in parallel
2. FastAPI returns data from the shared `data.py` module
3. React renders live KPI cards, disruptions panel, fleet panel, shipment risk table
4. KPI counters (active disruptions, shipments at risk, cold-chain count, available fleet) are computed dynamically from the fetched data

### What-if simulation data flow
1. User clicks "Run Simulation" → React fires `GET /simulate-disruption/DISR-001?additional_hours=48`
2. FastAPI runs the deterministic projection: finds impacted shipments by location match, counts cold-chain shipments, sums cargo values, applies risk thresholds
3. Result is rendered in the simulation panel below the button

### AI assistant data flow
1. User submits a question (typed or from suggested buttons)
2. React sends `POST /assistant` with `{ question, history: [...last 8 messages] }`
3. `assistant.py` runs `_gather_facts()` — regex intent detection maps question to relevant data (simulation / risk ranking / fleet recommendation)
4. Facts are serialised to JSON and embedded in the user message alongside the question
5. `get_provider()` returns `WatsonxProvider` (if credentials set) or `FallbackProvider`
6. Provider receives: system prompt + conversation history + facts-augmented user message
7. Answer is returned to the frontend as `{ answer, facts, provider }`
8. React renders the answer with inline markdown formatting; facts are available as a collapsible debug panel

## Security Considerations

- API keys are stored in environment variables only — never committed to git
- `.env` is listed in `.gitignore`
- CORS is restricted to `localhost:5173` and `localhost:3000` in development
- No authentication on API endpoints (acceptable for hackathon demo scope)

## Scalability Notes

The FastAPI backend is stateless and could be horizontally scaled behind a load balancer.
Switching from hardcoded `data.py` to a PostgreSQL database requires only changing the three
list constants to async DB queries — the rest of the logic is unchanged.
The watsonx.ai calls are the latency bottleneck and would benefit from response caching for
repeated identical questions.
