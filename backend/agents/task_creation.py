from state import WorkflowState
from mock.task_board import task_board

def task_creation_agent(state: WorkflowState) -> WorkflowState:
    created = []

    for item in state["action_items"]:

        # skip duplicates
        if task_board.exists(item["description"]):
            continue

        task_id = task_board.create(item)
        created.append(task_id)

    audit_entry = {
        "agent": "task_creation_agent",
        "action": "tasks_created",
        "output": f"{len(created)} tasks created"
    }

    return {
        **state,
        "audit_log": state["audit_log"] + [audit_entry]
    }