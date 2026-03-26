import asyncio
import os
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from graph import workflow
from state import new_workflow, WorkflowState
from audit.logger import AuditLogger
from mock.task_board import task_board

app = FastAPI(title="ET Editorial Workflow Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)

audit_logger = AuditLogger()
ws_connections: list[WebSocket] = []

DEMO_DELAY = 0.3  # smoother UI streaming


# ── SAFE BROADCAST ─────────────────────────────

async def _broadcast(msg: dict):
    dead = []
    for ws in ws_connections:
        try:
            await ws.send_json(msg)
        except Exception:
            dead.append(ws)

    for ws in dead:
        if ws in ws_connections:
            ws_connections.remove(ws)


# ── WebSocket (FIXED CLEAN VERSION) ────────────

@app.websocket("/ws/audit")
async def audit_ws(websocket: WebSocket):
    await websocket.accept()
    ws_connections.append(websocket)

    try:
        while True:
            await asyncio.sleep(20)
            # prevent crash on closed socket
            if websocket.client_state.name != "CONNECTED":
                break
            await websocket.send_json({"type": "ping"})
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        if websocket in ws_connections:
            ws_connections.remove(websocket)


# ── RUN WORKFLOW ───────────────────────────────

class TranscriptRequest(BaseModel):
    transcript: str


@app.post("/api/run")
async def run_workflow(req: TranscriptRequest):
    # reset everything (IMPORTANT FIX)
    task_board.clear()
    audit_logger.clear()

    await _broadcast({"type": "reset"})  # frontend clear

    initial_state = new_workflow(req.transcript.strip())
    prev_len = 0
    final_state: WorkflowState = initial_state

    for step in workflow.stream(initial_state):
        for _, state in step.items():
            final_state = state

            # stream audit entries
            new_entries = state["audit_log"][prev_len:]
            for entry in new_entries:
                audit_logger.save(entry)
                await _broadcast({"type": "audit", "data": entry})
                await asyncio.sleep(DEMO_DELAY)

            prev_len = len(state["audit_log"])

            # stream tasks
            await _broadcast({
                "type": "tasks_full",
                "data": task_board.get_all(),
            })

    # FINAL RESULT (IMPORTANT FOR UI)
    await _broadcast({
        "type": "workflow_complete",
        "data": {
            "workflow_id": final_state["workflow_id"],
            "status": final_state["workflow_status"],
            "tasks_created": len(final_state["tasks_created"]),
            "escalations": len(final_state["escalations"]),
            "audit_count": len(final_state["audit_log"]),
            "decisions": final_state["decisions"],
            "et_context": final_state["et_context"],
        },
    })

    return {"status": final_state["workflow_status"]}


# ── STALL → TRACKER → ESCALATION ───────────────

@app.post("/api/demo/stall/{task_id}")
async def inject_stall(task_id: str):
    task = task_board.get(task_id)

    if not task:
        return {"ok": False, "error": "task not found"}

    # simulate stall
    task_board.simulate_stall(task_id)

    stall_entry = {
        "id": f"stall-{task_id}",
        "timestamp": datetime.now().isoformat(),
        "agent": "demo_control",
        "action": "stall_injected",
        "input_summary": task["title"][:50],
        "output_summary": "48h stall simulated",
        "reasoning": "Triggering tracker for demo",
        "status": "failure",
    }

    audit_logger.save(stall_entry)
    await _broadcast({"type": "audit", "data": stall_entry})
    await asyncio.sleep(DEMO_DELAY)

    # rebuild minimal state
    from agents.tracker import tracker_agent

    mini_state = {
        "transcript_raw": "",
        "workflow_id": "demo",
        "et_context": "",
        "decisions": [],
        "action_items": [],
        "extraction_complete": True,
        "tasks_created": [t["id"] for t in task_board.get_all()],
        "failed_tasks": [],
        "stalled_tasks": [],
        "nudges_sent": [],
        "current_error": None,
        "recovery_attempts": 0,
        "escalations": [],
        "audit_log": [],
        "workflow_status": "running",
    }

    # run tracker
    after_tracker = tracker_agent(mini_state)

    for entry in after_tracker["audit_log"]:
        audit_logger.save(entry)
        await _broadcast({"type": "audit", "data": entry})
        await asyncio.sleep(DEMO_DELAY)

    # escalation (if needed)
    if after_tracker["stalled_tasks"]:
        stalled_id = after_tracker["stalled_tasks"][0]
        stalled_task = task_board.get(stalled_id)

        escalation_entry = {
            "id": f"escalation-{stalled_id}",
            "timestamp": datetime.now().isoformat(),
            "agent": "escalation_agent",
            "action": "task_escalated_due_to_stall",
            "input_summary": stalled_task["title"][:50],
            "output_summary": "Escalated to manager (Rakesh Sharma)",
            "reasoning": "Task stalled >48h, auto-recovery exhausted",
            "status": "escalated",
        }

        audit_logger.save(escalation_entry)
        await _broadcast({"type": "audit", "data": escalation_entry})

        # popup trigger
        await _broadcast({
            "type": "escalation_notification",
            "data": {
                "task_id": stalled_id,
                "task_title": stalled_task["title"],
                "owner": stalled_task["owner"],
                "manager": "Rakesh Sharma",
                "message": "Task stalled for 48h. Manager notified.",
            },
        })

    await _broadcast({
        "type": "tasks_full",
        "data": task_board.get_all(),
    })

    return {"ok": True}


# ── MARK TASK DONE ─────────────────────────────

@app.post("/api/tasks/{task_id}/done")
async def mark_done(task_id: str):
    task = task_board.get(task_id)

    if not task:
        return {"ok": False}

    # FIX: correct method
    task_board.update_status(task_id, "done")

    entry = {
        "id": f"done-{task_id}",
        "timestamp": datetime.now().isoformat(),
        "agent": "human",
        "action": "task_completed",
        "input_summary": task["title"][:50],
        "output_summary": "Task marked done",
        "reasoning": "User completed task",
        "status": "success",
    }

    audit_logger.save(entry)
    await _broadcast({"type": "audit", "data": entry})
    await _broadcast({"type": "tasks_full", "data": task_board.get_all()})

    return {"ok": True}


# ── BASIC ENDPOINTS ───────────────────────────

@app.get("/api/tasks")
async def get_tasks():
    return task_board.get_all()


@app.get("/api/audit")
async def get_audit():
    return audit_logger.get_all()


@app.get("/health")
async def health():
    return {"status": "ok"}