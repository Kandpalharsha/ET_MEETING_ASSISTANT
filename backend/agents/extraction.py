from state import WorkflowState

def extraction_agent(state: WorkflowState) -> WorkflowState:
    transcript = state["transcript_raw"]

    # dummy extraction for now
    decisions = ["Budget analysis scheduled"]
    action_items = [
        {
            "id": "1",
            "description": "Prepare budget report",
            "owner": "Arjun Mehta",
            "deadline": "2026-03-29",
            "priority": "high",
            "status": "pending"
        }
    ]

    audit_entry = {
        "agent": "extraction_agent",
        "action": "basic_extraction",
        "output": "1 decision, 1 task extracted"
    }

    return {
        **state,
        "decisions": decisions,
        "action_items": action_items,
        "audit_log": state["audit_log"] + [audit_entry]
    }