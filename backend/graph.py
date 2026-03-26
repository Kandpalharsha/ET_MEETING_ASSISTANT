from langgraph.graph import StateGraph, END
from state import WorkflowState
from agents.extraction   import extraction_agent
from agents.escalation   import escalation_agent
from agents.task_creation import task_creation_agent
from agents.tracker      import tracker_agent


# ── Routing functions (conditional edges = self-correction) ───────────

def route_after_extraction(state: WorkflowState) -> str:
    """After extraction: error → escalation, ambiguous owners → escalation, clean → task_creation"""
    if state.get("current_error"):
        return "escalation"
    ambiguous = [
        t for t in state["action_items"]
        if t["owner"] is None or t["owner_confidence"] < 0.7
    ]
    if ambiguous:
        return "escalation"
    return "task_creation"


def route_after_escalation(state: WorkflowState) -> str:
    """After escalation: retry extraction, proceed to tasks, or await human"""
    if state["workflow_status"] == "awaiting_human":
        return END
    if not state["extraction_complete"]:
        return "extraction"        # retry after recovery
    return "task_creation"


def route_after_task_creation(state: WorkflowState) -> str:
    """After task creation: escalate failures or proceed to tracking"""
    if state.get("failed_tasks"):
        # Only escalate if failures are non-duplicate errors
        real_failures = [
            f for f in state["failed_tasks"]
            if f.get("reason") != "duplicate_task"
        ]
        if real_failures:
            return "escalation"
    return "tracker"


def route_after_tracker(state: WorkflowState) -> str:
    """After tracker: escalate stalled tasks or complete"""
    if state.get("stalled_tasks"):
        return "escalation"
    return END


# ── Build and compile the graph ───────────────────────────────────────

def build_graph() -> StateGraph:
    g = StateGraph(WorkflowState)

    g.add_node("extraction",    extraction_agent)
    g.add_node("escalation",    escalation_agent)
    g.add_node("task_creation", task_creation_agent)
    g.add_node("tracker",       tracker_agent)

    g.set_entry_point("extraction")

    g.add_conditional_edges(
        "extraction",
        route_after_extraction,
        {"escalation": "escalation", "task_creation": "task_creation"},
    )
    g.add_conditional_edges(
        "escalation",
        route_after_escalation,
        {"extraction": "extraction", "task_creation": "task_creation", END: END},
    )
    g.add_conditional_edges(
        "task_creation",
        route_after_task_creation,
        {"escalation": "escalation", "tracker": "tracker"},
    )
    g.add_conditional_edges(
        "tracker",
        route_after_tracker,
        {"escalation": "escalation", END: END},
    )

    return g.compile()


# Compiled workflow singleton
workflow = build_graph()
