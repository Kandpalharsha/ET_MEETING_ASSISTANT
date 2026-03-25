from datetime import datetime
from state import WorkflowState
from mock.task_board import task_board

STALL_HOURS = 48


def tracker_agent(state: WorkflowState) -> WorkflowState:
    """
    Detects stalled tasks AND escalates automatically
    """

    new_audit = list(state["audit_log"])
    now = datetime.now()

    for task in task_board.get_all():
        last_updated = datetime.fromisoformat(task["last_updated"])
        hours = (now - last_updated).total_seconds() / 3600

        if hours >= STALL_HOURS and task.get("status") != "stalled":

            # mark stalled
            task_board.update_status(task["id"], "stalled")

            # 🔥 escalation entry
            escalation_entry = {
                "agent": "tracker_agent",
                "action": "stall_detected",
                "output": f"Task '{task['description']}' stalled",
            }

            new_audit.append(escalation_entry)

            # 🔥 manager escalation
            manager_entry = {
                "agent": "escalation_agent",
                "action": "task_escalated",
                "output": f"Escalated to manager for task '{task['description']}'",
            }

            new_audit.append(manager_entry)

    return {
        **state,
        "audit_log": new_audit
    }