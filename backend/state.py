from typing import TypedDict, Optional, List
from datetime import datetime
import uuid


class ActionItem(TypedDict):
    id: str
    description: str
    owner: Optional[str]
    deadline: Optional[str]
    priority: str
    status: str


class AuditEntry(TypedDict):
    id: str
    timestamp: str
    agent: str
    action: str
    input_summary: str
    output_summary: str
    reasoning: str
    status: str


class WorkflowState(TypedDict):
    transcript_raw: str
    workflow_id: str

    decisions: List[str]
    action_items: List[ActionItem]

    audit_log: List[AuditEntry]

    # 🔥 NEW
    current_error: Optional[str]
    recovery_attempts: int


def new_workflow(transcript: str) -> WorkflowState:
    return WorkflowState(
        transcript_raw=transcript,
        workflow_id=str(uuid.uuid4())[:8],
        decisions=[],
        action_items=[],
        audit_log=[],
        current_error=None,
        recovery_attempts=0,
    )


def make_audit_entry(
    agent: str,
    action: str,
    input_summary: str,
    output_summary: str,
    reasoning: str,
    status: str = "success",
) -> AuditEntry:
    return AuditEntry(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        agent=agent,
        action=action,
        input_summary=input_summary,
        output_summary=output_summary,
        reasoning=reasoning,
        status=status,
    )