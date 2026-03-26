from datetime import datetime, timedelta
from state import WorkflowState, make_audit_entry
from mock.task_board import task_board

STALL_HOURS   = 48
DEADLINE_WARN = 24


def tracker_agent(state: WorkflowState) -> WorkflowState:
    """
    Monitors tasks for:
    - stalls
    - deadlines
    - completion

    Includes auto-recovery (reassignment) before escalation.
    """
    new_audit     = list(state["audit_log"])
    stalled_tasks = list(state["stalled_tasks"])
    nudges_sent   = list(state["nudges_sent"])
    now           = datetime.now()

    # 🔥 NEW: agent thinking
    new_audit.append(make_audit_entry(
        agent="tracker_agent",
        action="monitoring_started",
        input_summary=f"{len(state['tasks_created'])} tasks",
        output_summary="Monitoring task health, deadlines, and progress",
        reasoning="[STEP] Scan all tasks → detect stalls → trigger recovery if needed",
        status="success",
    ))

    for task_id in state["tasks_created"]:
        task = task_board.get(task_id)
        if not task:
            continue

        # Skip completed
        if task.get("status") == "done":
            continue

        deadline      = datetime.fromisoformat(task["deadline"])
        last_updated  = datetime.fromisoformat(task["last_updated"])
        hours_stalled = (now - last_updated).total_seconds() / 3600
        hours_to_dl   = (deadline - now).total_seconds() / 3600

        # ── STALL DETECTION ───────────────────────────────────────────
        if hours_stalled >= STALL_HOURS and task_id not in stalled_tasks:

            # 🔥 NEW: Auto-reassignment before escalation
            fallback_owner = "Rakesh Sharma"
            original_owner = task.get("owner")

            task_board.update_status(task_id, "pending")
            task["owner"] = fallback_owner

            new_audit.append(make_audit_entry(
                agent="tracker_agent",
                action="auto_reassignment",
                input_summary=f"{task['title'][:55]}",
                output_summary=f"Reassigned → {fallback_owner}",
                reasoning=(
                    f"[DECISION] Task stalled for {hours_stalled:.0f}h → "
                    f"[ACTION] Reassign from {original_owner} → {fallback_owner} → "
                    f"[RESULT] Attempt recovery before escalation"
                ),
                status="recovery",
            ))

            # Mark as stalled AFTER reassignment
            stalled_tasks.append(task_id)
            task_board.update_status(task_id, "stalled")

            new_audit.append(make_audit_entry(
                agent="tracker_agent",
                action="stall_detected",
                input_summary=f"{task['title'][:55]}",
                output_summary=(
                    f"STALLED — {hours_stalled:.0f}h no progress · "
                    f"Deadline in {max(hours_to_dl,0):.0f}h"
                ),
                reasoning=(
                    f"[DECISION] No updates for {hours_stalled:.0f}h → "
                    f"[ACTION] Mark as stalled → escalate if still unresolved"
                ),
                status="failure",
            ))

            continue

        # ── DEADLINE NUDGE ────────────────────────────────────────────
        if (
            0 < hours_to_dl <= DEADLINE_WARN
            and task.get("status") == "pending"
            and not task.get("nudge_sent")
        ):
            task_board.send_nudge(task_id)
            nudges_sent.append(task["owner"])

            new_audit.append(make_audit_entry(
                agent="tracker_agent",
                action="deadline_nudge_sent",
                input_summary=f"{task['title'][:55]}",
                output_summary=f"Nudge → {task['owner']} ({hours_to_dl:.0f}h left)",
                reasoning=(
                    f"[DECISION] Deadline approaching → "
                    f"[ACTION] Send automated reminder → "
                    f"[RESULT] No human intervention needed"
                ),
                status="success",
            ))

    # ── COMPLETION CHECK ──────────────────────────────────────────────
    all_done = all(
        task_board.get(tid) and task_board.get(tid).get("status") == "done"
        for tid in state["tasks_created"]
    )

    new_status = state["workflow_status"]

    if all_done and state["tasks_created"]:
        new_status = "completed"

        new_audit.append(make_audit_entry(
            agent="tracker_agent",
            action="workflow_completed",
            input_summary=f"{len(state['tasks_created'])} tasks",
            output_summary="All tasks completed successfully",
            reasoning=(
                f"[RESULT] All tasks marked done → "
                f"[SYSTEM] Workflow completed autonomously"
            ),
            status="success",
        ))

    return {
        **state,
        "stalled_tasks":   stalled_tasks,
        "nudges_sent":     nudges_sent,
        "audit_log":       new_audit,
        "workflow_status": new_status,
    }