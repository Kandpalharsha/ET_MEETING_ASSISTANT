from typing import TypedDict, Optional, Literal
from datetime import datetime
import uuid


class ActionItem(TypedDict):
    id: str
    description: str
    owner: Optional[str]
    owner_confidence: float
    deadline: Optional[str]
    priority: Literal["high", "medium", "low"]
    category: str
    status: Literal["pending", "in_progress", "stalled", "done", "escalated"]
    created_at: str
    last_updated: str
    nudge_sent: bool


class AuditEntry(TypedDict):
    id: str
    timestamp: str
    agent: str
    action: str
    input_summary: str
    output_summary: str
    reasoning: str
    status: Literal["success", "failure", "recovery", "escalated"]


class EscalationRecord(TypedDict):
    id: str
    timestamp: str
    trigger: str
    attempted_recoveries: list[str]
    resolution: Optional[str]
    requires_human: bool


class WorkflowState(TypedDict):
    # Input
    transcript_raw: str
    workflow_id: str

    # Enrichment
    et_context: str

    # Extraction outputs
    decisions: list[str]
    action_items: list[ActionItem]
    extraction_complete: bool

    # Task creation
    tasks_created: list[str]
    failed_tasks: list[dict]

    # Tracker
    stalled_tasks: list[str]
    nudges_sent: list[str]

    # Error handling
    current_error: Optional[str]
    recovery_attempts: int
    escalations: list[EscalationRecord]

    # Audit trail
    audit_log: list[AuditEntry]

    # Status
    workflow_status: Literal["running", "completed", "failed", "awaiting_human"]


def new_workflow(transcript: str) -> WorkflowState:
    return WorkflowState(
        transcript_raw=transcript,
        workflow_id=str(uuid.uuid4())[:8],
        et_context="",
        decisions=[],
        action_items=[],
        extraction_complete=False,
        tasks_created=[],
        failed_tasks=[],
        stalled_tasks=[],
        nudges_sent=[],
        current_error=None,
        recovery_attempts=0,
        escalations=[],
        audit_log=[],
        workflow_status="running",
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
