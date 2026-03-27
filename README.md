# ET Editorial Workflow Agent
## Agentic AI for Autonomous Enterprise Workflows 

## The Problem

Every enterprise meeting ends with decisions that never get executed.

Ownership is unclear. Deadlines are missed. Nobody follows up. Tasks fall through the cracks — not because people are lazy, but because there is no system that takes responsibility for execution after the meeting ends.

For a newsroom like Economic Times, this is not a productivity problem. It is a **business-critical** problem. A missed compliance review means a regulatory article goes live with unverified RBI citations. A stalled websocket fix means the Markets live feed crashes during Budget day coverage. A lost sponsorship approval means advertiser revenue delayed by a week.

---

## The Solution

A **multi-agent autonomous workflow system** that attends your meeting, extracts every decision and action item, assigns verified owners, creates tracked tasks, monitors progress in real time, attempts autonomous recovery when tasks stall, and escalates to a human **only when it has genuinely exhausted all recovery options**.

The system does not just generate a to-do list. It owns the execution.

---

## Live Demo

```
Input:  15-minute ET editorial planning meeting transcript
Output: 8 tracked tasks, owners verified, deadlines set,
        1 autonomous owner resolution, 1 escalation with full context
Time:   ~45 seconds end-to-end
Human involvement: 0 steps (until escalation fires)
```

**Demo flow:**
1. Paste meeting transcript → click Run Workflow
2. Watch agents reason through the transcript in real time (audit stream)
3. Watch tasks appear on the board with verified owners and deadlines
4. Click "simulate stall" on any task → watch tracker detect it → escalation fires → manager notified
5. Scroll the audit trail → every agent decision visible with reasoning and timestamp

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MEETING TRANSCRIPT                        │
│         (ET Editorial Planning Meeting — 15 minutes)         │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EXTRACTION AGENT                           │
│                                                              │
│  • Sends transcript to Llama 3.3 70B via Groq               │
│  • Forces structured JSON output (decisions + action items)  │
│  • Scores each owner assignment with confidence (0.0–1.0)    │
│  • Enriches context with DuckDuckGo ET headline search       │
│  • Flags ambiguous owners for resolution                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │    Ambiguous owners?        │
              │    API failure?             │
              └──────┬──────────┬──────────┘
                     │ YES      │ NO
                     ▼          ▼
┌──────────────────────────┐   ┌──────────────────────────────┐
│    ESCALATION AGENT      │   │    TASK CREATION AGENT        │
│                          │   │                               │
│  Pass 1: Org chart       │   │  • Creates task for each      │
│  fuzzy match (instant)   │   │    confirmed action item       │
│                          │   │  • Skips escalated tasks       │
│  Pass 2: LLM reads       │   │  • Detects and skips          │
│  transcript context      │   │    duplicates                  │
│                          │   │  • Logs mock Slack alert       │
│  Pass 3: Escalate to     │   │    per owner                   │
│  human (last resort)     │   │                               │
│                          │   │  Output: tasks_created[]       │
│  Also handles:           │   └──────────────┬────────────────┘
│  • API retry (2x max)    │                  │
│  • Workflow failures      │◄─────────────────┘
└──────────────────────────┘         │
                                      ▼
                    ┌─────────────────────────────────────────┐
                    │            TRACKER AGENT                 │
                    │                                          │
                    │  • Scans all created tasks               │
                    │  • Stall detection: 48h no update        │
                    │  • Deadline nudge: 24h warning           │
                    │  • Sends autonomous Slack nudges         │
                    │  • Logs final workflow summary           │
                    │  • Marks workflow "completed"            │
                    └──────────────┬──────────────────────────┘
                                   │
                     ┌─────────────▼──────────────┐
                     │      Stalls detected?        │
                     └──────┬──────────┬───────────┘
                            │ YES      │ NO
                            ▼          ▼
              ┌─────────────────┐   ┌──────────────────┐
              │ ESCALATION      │   │   WORKFLOW         │
              │ AGENT (again)   │   │   COMPLETED ✓      │
              │                 │   │                    │
              │ Notifies manager│   │ Audit trail saved  │
              │ with full       │   │ to SQLite          │
              │ context         │   │                    │
              └─────────────────┘   └──────────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │     AUDIT LOG (SQLite)        │
         │     ↓ WebSocket stream        │
         │     ↓ React UI (live)         │
         └──────────────────────────────┘
```

---

## Agent Roles

### Agent 1 — Extraction Agent
**Purpose:** Convert unstructured meeting audio/text into structured, actionable data.

**How it works:**
- Sends transcript to Llama 3.3 70B with a strict JSON schema prompt
- Extracts: decisions made, action items, owner names, deadlines, priorities, and categories (editorial / compliance / technical / finance / events)
- Assigns `owner_confidence` score to every task (0.0–1.0)
- Runs DuckDuckGo search on key decisions to pull real ET headlines for context grounding
- On failure: sets `current_error` in state, triggering escalation to retry

**Confidence scoring rules:**
| Score | Meaning |
|---|---|
| 0.95 | Explicitly named ("Arjun, you handle this") |
| 0.80 | Strongly implied by role |
| 0.60 | Mentioned nearby, not clearly assigned |
| 0.40 | Vague ("the team", "someone") |
| null | Completely unresolvable |

---

### Agent 2 — Escalation Agent
**Purpose:** Self-correction engine. Resolve ambiguities before they become blockers.

**3-pass owner resolution:**

```
Pass 1: ET Org Chart fuzzy match
        "email delivery" → matches "tech" → Vikram Iyer
        Instant. No LLM call. Logged to audit.
              ↓ (if no match)
Pass 2: Llama 3.3 70B reads transcript context
        Sends task + transcript → LLM reasons about ownership
        Confidence ≥ 65% → resolved. Logged with reasoning.
              ↓ (if still below threshold)
Pass 3: Escalate to human
        Status = "escalated". Manager notified.
        Full reasoning logged: "Tried X and Y. Best guess was Z at 58%."
```

**Also handles:**
- Groq API failures: retries extraction up to 2 times with backoff
- Unrecoverable errors: escalates entire workflow with full audit context

---

### Agent 3 — Task Creation Agent
**Purpose:** Write confirmed tasks to the editorial task board.

**Logic:**
- Skips tasks with `status = "escalated"` (no owner confirmed)
- Checks for duplicate tasks before creating
- Creates task with: title, owner, deadline, priority, category
- Logs mock Slack notification per owner in audit trail
- On creation failure: logs with reasoning, adds to `failed_tasks`

---

### Agent 4 — Tracker Agent
**Purpose:** Monitor execution. Detect stalls. Act autonomously before things break.

**Detection thresholds:**
- **Stall:** No task update for 48+ hours → mark stalled → trigger escalation
- **Deadline warning:** Task still pending within 24h of deadline → send autonomous nudge
- **Completion:** All tasks healthy → mark workflow `completed`

**Final summary audit entry** (visible to judges):
```
Completed 14 autonomous agent decisions across extraction → resolution
→ creation → tracking. Human involvement: 1 escalation, triggered only
when all autonomous recovery options were exhausted.
```

---

## Self-Correction Flow (The Core Innovation)

Most systems fail silently or crash. This system fails **visibly and recovers autonomously.**

```
Failure detected
      ↓
What type of failure?
      ↓
├── Ambiguous owner
│     ├── Try org chart (0ms, no LLM)
│     ├── Try LLM context reading (2-3s)
│     └── Escalate to human (last resort)
│
├── API failure
│     ├── Retry 1 (logged)
│     ├── Retry 2 (logged)
│     └── Escalate to human operator
│
└── Task stall (48h)
      ├── Send owner nudge (autonomous)
      └── Escalate to manager with full context
```

Every attempt is logged with reasoning. Judges can trace exactly what the system tried and why it escalated.

---

## Audit Trail

Every agent decision is captured with:

| Field | Example |
|---|---|
| `agent` | `escalation_agent` |
| `action` | `owner_resolved_org_chart` |
| `input_summary` | `Fix email delivery pipeline` |
| `output_summary` | `Resolved → Vikram Iyer (85% confidence)` |
| `reasoning` | `Keyword 'email' matched ET org chart entry → 'tech' → Vikram Iyer. No LLM call needed.` |
| `status` | `recovery` |
| `timestamp` | `2026-03-23T17:41:38.421` |

Persisted to **SQLite**. Streamed live to browser via **WebSocket**. Visible in the UI audit panel during demo.

---

## Tech Stack

### Backend
| Tool | Purpose | Cost |
|---|---|---|
| **LangGraph** | Agent orchestration with conditional edges | Free (Apache 2.0) |
| **Groq API** | Llama 3.3 70B inference | Free tier |
| **LangChain-Groq** | LLM client with retry handling | Free |
| **DuckDuckGo Search** | ET news context enrichment | Free, no key needed |
| **FastAPI** | REST API + WebSocket server | Free (MIT) |
| **SQLite** | Audit log persistence | Free (built-in) |
| **Python 3.10+** | Runtime | Free |

### Frontend
| Tool | Purpose |
|---|---|
| **React 18** | UI framework |
| **Vite** | Build tool |
| **Tailwind CSS** | Styling |
| **WebSocket (native)** | Live audit stream with auto-reconnect |

**Total external API cost: ₹0**

---

## File Structure

```
et_workflow/
├── backend/
│   ├── main.py                  # FastAPI server + WebSocket streaming
│   ├── graph.py                 # LangGraph workflow (agents + routing)
│   ├── llm_client.py            # Groq/Llama client (single config point)
│   ├── state.py                 # Shared TypedDict state schema
│   ├── demo_data.py             # ET transcript + demo script
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── extraction.py        # Transcript → structured tasks
│   │   ├── escalation.py        # Self-correction + owner resolution
│   │   ├── task_creation.py     # Task board writer
│   │   └── tracker.py           # Stall detection + deadline nudges
│   ├── audit/
│   │   └── logger.py            # SQLite audit persistence
│   └── mock/
│       └── task_board.py        # In-memory mock task board
│
└── frontend/
    └── src/
        ├── App.jsx              # Main app + upload + stats
        ├── components/
        │   ├── AuditStream.jsx  # Live audit log panel (WebSocket)
        │   └── TaskBoard.jsx    # Task cards with stall simulation
        └── hooks/
            └── useWebSocket.js  # Auto-reconnecting WS client
```

---

## Setup & Run

### Prerequisites
- Python 3.10+
- Node.js 18+
- Free Groq API key from [console.groq.com](https://console.groq.com)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GROQ_API_KEY to .env
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`

### .env configuration
```env
LLM_BACKEND=groq
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
FRONTEND_ORIGIN=http://localhost:5173
DEMO_MODE=true
```

---

## Evaluation Criteria Mapping

| PS 2 Criterion | Implementation | Evidence |
|---|---|---|
| **Depth of autonomy** | 7 of 8 workflow steps are fully autonomous | Final audit entry explicitly states autonomous step count |
| **Quality of error recovery** | 3-pass recovery with logged reasoning at each attempt | Live demo: ambiguous owner resolved via org chart without LLM |
| **Auditability of decisions** | Every agent action logged: who, what, why, when, status | SQLite audit.db + live WebSocket stream in UI |
| **Real-world applicability** | ET editorial domain: Budget coverage, RBI compliance, Wealth Summit | Demo transcript uses real ET workflow scenarios |

---

## Impact Model

### Assumptions
- ET runs 10+ editorial planning meetings per day
- Average meeting generates 6–10 action items
- Without tracking: 30% of action items are delayed or lost
- Average cost of a missed editorial deadline: 2–4 hours of rework

### Without this system
| Metric | Value |
|---|---|
| Tasks lost or delayed per day | ~24 |
| Manual follow-up time | 3–4 hours/day per team |
| Accountability gaps | No audit trail |

### With this system
| Metric | Value |
|---|---|
| Tasks auto-managed | ~90% |
| Reduction in manual tracking | ~70% |
| Time saved per team per day | 3–4 hours |
| Human escalations required | <10% of tasks |

### Business impact estimate
- **Time saved:** 3–4 hours/day/editorial team → ~₹15,000/day in productivity (at ₹50/min knowledge worker rate)
- **Missed deadline reduction:** 70% → fewer article corrections, fewer advertiser delays
- **Audit compliance:** 100% of decisions traceable → supports regulatory and editorial governance

*Assumptions stated. Back-of-envelope. Logic holds at scale.*

---

## Why This Wins

| Generic "AI Workflow" Demo | This System |
|---|---|
| Single LLM call, clean data only | Multi-agent pipeline, handles messy real data |
| No failure handling | 3-pass autonomous recovery |
| Console logs as "audit trail" | Structured SQLite log + live UI stream |
| Generic business scenario | ET-specific editorial domain |
| Human asked at every step | Human contacted only when recovery exhausted |
| Static output shown at end | Live agent reasoning visible in real time |

---

## Future Enhancements

- **Whisper integration** — accept audio recordings directly, auto-transcribe before extraction
- **Real Slack/Teams API** — send actual notifications instead of mocks
- **Jira/Notion sync** — push tasks to real project management tools
- **Multi-meeting memory** — track recurring action items across meetings
- **Continuous background polling** — tracker runs every 60 seconds autonomously
- **Human approval UI** — inline owner assignment for escalated tasks
- **ML priority prediction** — learn from historical completion rates to auto-adjust priorities

---

## Team

Built for **ET AI Hackathon 2026** — PS 2: Agentic AI for Autonomous Enterprise Workflows

---

## License

MIT License — open source, free to use and extend.
