from typing import TypedDict, List

class WorkflowState(TypedDict):
    transcript_raw: str
    decisions: List[str]
    action_items: List[dict]
    audit_log: List[dict]