from state import WorkflowState

# simple org mapping
ORG = {
    "tech": "Vikram Iyer",
    "legal": "Sunita Rao",
    "finance": "Ravi Krishnan",
    "events": "Meera Joshi",
    "editorial": "Rakesh Sharma"
}

def escalation_agent(state: WorkflowState) -> WorkflowState:
    updated_items = []

    for task in state["action_items"]:
        owner = task.get("owner")

        # if no owner → try to resolve
        if not owner:
            desc = task["description"].lower()

            resolved = None
            for key, person in ORG.items():
                if key in desc:
                    resolved = person
                    break

            task["owner"] = resolved if resolved else "Rakesh Sharma"

        updated_items.append(task)

    audit_entry = {
        "agent": "escalation_agent",
        "action": "owner_resolution",
        "output": f"{len(updated_items)} tasks processed"
    }

    return {
        **state,
        "action_items": updated_items,
        "audit_log": state["audit_log"] + [audit_entry]
    }