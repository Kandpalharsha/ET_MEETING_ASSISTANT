# ET Editorial Workflow Agent
## PS 2 — Agentic AI for Autonomous Enterprise Workflows
### Stack: 100% open source · Groq (free) · Llama 3.3 70B · LangGraph · DuckDuckGo

---

## Setup (10 minutes)

### Step 1 — Groq API key (free, no credit card)
1. Go to https://console.groq.com
2. Sign up with email
3. Click "API Keys" → "Create API Key"
4. Copy the key (starts with `gsk_`)

### Step 2 — Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Open .env and set: GROQ_API_KEY=gsk_your_key_here
uvicorn main:app --reload --port 8000
```

### Step 3 — Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Step 4 — Test
Open http://localhost:5173 → click "load demo transcript" → click "Run workflow"
Watch agents work in real time on the left panel. Tasks appear on the right.

---

## File Structure
```
backend/
├── main.py                  # FastAPI + WebSocket server
├── graph.py                 # LangGraph agent pipeline
├── llm_client.py            # Groq/Llama client (one file to rule them all)
├── state.py                 # Shared TypedDict state
├── demo_data.py             # ET transcript + demo script
├── agents/
│   ├── extraction.py        # Transcript → structured tasks + DuckDuckGo enrichment
│   ├── escalation.py        # Self-correction + owner resolution (DEMO CENTERPIECE)
│   ├── task_creation.py     # Creates tasks on mock board
│   └── tracker.py           # Stall detection + deadline nudges
├── audit/
│   └── logger.py            # SQLite audit persistence
└── mock/
    └── task_board.py        # In-memory mock task board

frontend/
└── src/
    ├── App.jsx              # Main app + upload panel + stats
    ├── index.css            # Dark ET theme
    ├── components/
    │   ├── AuditStream.jsx  # Live audit log (WebSocket)
    │   └── TaskBoard.jsx    # Task cards with stall button
    └── hooks/
        └── useWebSocket.js  # Auto-reconnecting WS client
```

---

## Open Source APIs Used
| Tool              | Purpose                          | Cost          |
|-------------------|----------------------------------|---------------|
| Groq API          | LLM inference (Llama 3.3 70B)    | Free tier     |
| LangGraph         | Agent orchestration              | Free (Apache) |
| DuckDuckGo Search | ET news context enrichment       | Free, no key  |
| FastAPI           | Backend + WebSockets             | Free (MIT)    |
| SQLite            | Audit log                        | Free (builtin)|
| React + Vite      | Frontend                         | Free (MIT)    |

---

## Live Demo Steps
1. Paste ET transcript → Run workflow
2. Watch extraction agent parse 8 tasks
3. Watch escalation agent resolve ambiguous "email delivery" owner → Vikram Iyer
4. Click "simulate stall →" on any pending task
5. Watch tracker detect stall → escalation agent notifies manager
6. Scroll audit trail → show every decision with reasoning
7. Point to stats: "7 autonomous steps. 1 human escalation. Full audit trail."

---

## Architecture (for submission doc)
```
Transcript Input
     ↓
[Extraction Agent] — Groq Llama 3.3 70B + DuckDuckGo
     ↓ (ambiguous owners?)
[Escalation Agent] — Org chart → LLM context → Human
     ↓
[Task Creation Agent] — Mock board + duplicate check
     ↓ (stalls?)
[Tracker Agent] — Deadline nudges + stall detection
     ↓ (stalled tasks?)
[Escalation Agent] — Manager notification
     ↓
Audit Log (SQLite) → WebSocket → React UI
```

Every arrow is a conditional edge in LangGraph.
Self-correction happens at escalation nodes.
