from langgraph.graph import StateGraph, END
from state import WorkflowState

from agents.extraction import extraction_agent
from agents.escalation import escalation_agent
from agents.task_creation import task_creation_agent
from agents.tracker import tracker_agent


def route_after_extraction(state: WorkflowState):
    # If no tasks → stop
    if not state["action_items"]:
        return END
    return "escalation"


def route_after_escalation(state: WorkflowState):
    return "task_creation"


def route_after_task_creation(state: WorkflowState):
    return "tracker"


def route_after_tracker(state: WorkflowState):
    return END

def route_after_extraction(state):
    return "escalation" if state.get("current_error") else "task_creation"


def route_after_escalation(state):
    if state.get("current_error") is None and state.get("recovery_attempts", 0) > 0:
        return "extraction"  
    return "task_creation"



def build_graph():
    g = StateGraph(WorkflowState)

    g.add_node("extraction", extraction_agent)
    g.add_node("escalation", escalation_agent)
    g.add_node("task_creation", task_creation_agent)
    g.add_node("tracker", tracker_agent)

    g.set_entry_point("extraction")

    g.add_conditional_edges(
        "extraction",
        route_after_extraction,
        {
            "escalation": "escalation",
            END: END
        }
    )

    g.add_conditional_edges(
        "escalation",
        route_after_escalation,
        {
            "task_creation": "task_creation"
        }
    )

    g.add_conditional_edges(
        "task_creation",
        route_after_task_creation,
        {
            "tracker": "tracker"
        }
    )

    g.add_conditional_edges(
        "tracker",
        route_after_tracker,
        {
            END: END
        }
    )
    
    
    
    
    
    
    
    
    
    
    

    return g.compile()


workflow = build_graph()