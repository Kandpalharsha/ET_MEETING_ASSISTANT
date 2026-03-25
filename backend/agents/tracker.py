from datetime import datetime
from state import WorkflowState
from mock.task_board import task_board

STALL_HOURS = 48


def tracker_agent(state: WorkflowState) -> WorkflowState:
    """
    Detects stalled tasks and logs it.
    (First version: detection only — escalation comes next step)
    """

    new_audit = list(state["audit_log"])
    now = datetime.now()

    stalled_count = 0

    for task in task_board.get_all():
        last_updated = datetime.fromisoformat(task["last_updated"])
        hours = (now - last_updated).total_seconds() / 3600

        if hours >= STALL_HOURS and task.get("status") != "stalled":
            task_board.update_status(task["id"], "stalled")
            stalled_count += 1

    audit_entry = {
        "agent": "tracker_agent",
        "action": "stall_check",
        "output": f"{stalled_count} stalled tasks detected"
    }

    return {
        **state,
        "audit_log": new_audit + [audit_entry]
    }