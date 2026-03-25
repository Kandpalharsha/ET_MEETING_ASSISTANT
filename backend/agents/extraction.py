from datetime import datetime
from state import WorkflowState, make_audit_entry


def extraction_agent(state: WorkflowState) -> WorkflowState:
    transcript = state["transcript_raw"]

    decisions = ["Budget analysis scheduled"]

    action_items = [{
        "id": "1",
        "description": "Prepare budget report",
        "owner": "Arjun Mehta",
        "deadline": "2026-03-29",
        "priority": "high",
        "status": "pending"
    }]

    audit = make_audit_entry(
        agent="extraction_agent",
        action="task_extraction",
        input_summary="Transcript processed",
        output_summary="1 task extracted",
        reasoning="Basic parsing logic used",
    )

    return {
        **state,
        "decisions": decisions,
        "action_items": action_items,
        "audit_log": state["audit_log"] + [audit],
    }