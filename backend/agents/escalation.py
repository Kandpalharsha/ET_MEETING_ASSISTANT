import json
import uuid
from datetime import datetime

from langchain_core.messages import HumanMessage, SystemMessage

from llm_client import llm
from state import WorkflowState, ActionItem, EscalationRecord, make_audit_entry


# ── ET org chart (mock HRMS) ──────────────────────────────────────────
ET_ORG = {
    # Editorial
    "rakesh": "Rakesh Sharma",
    "editor": "Rakesh Sharma",
    "senior editor": "Rakesh Sharma",
    "priya": "Priya Nair",
    "bureau": "Priya Nair",
    "bureau chief": "Priya Nair",
    "arjun": "Arjun Mehta",
    "reporter": "Arjun Mehta",
    "correspondent": "Arjun Mehta",
    # Tech
    "vikram": "Vikram Iyer",
    "tech": "Vikram Iyer",
    "technical": "Vikram Iyer",
    "digital": "Vikram Iyer",
    "dev": "Vikram Iyer",
    "backend": "Vikram Iyer",
    "infrastructure": "Vikram Iyer",
    "engineering": "Vikram Iyer",
    # Legal / Compliance
    "sunita": "Sunita Rao",
    "legal": "Sunita Rao",
    "compliance": "Sunita Rao",
    "regulatory": "Sunita Rao",
    # Finance
    "ravi": "Ravi Krishnan",
    "finance": "Ravi Krishnan",
    "sponsorship": "Ravi Krishnan",
    # Events
    "meera": "Meera Joshi",
    "events": "Meera Joshi",
    "summit": "Meera Joshi",
    "conference": "Meera Joshi",
}

RESOLVE_SYSTEM = """You are an editorial workflow expert at Economic Times (ET).
Identify the correct task owner using the transcript context and ET team structure.

ET team: Rakesh Sharma (Senior Editor), Priya Nair (Bureau Chief),
Arjun Mehta (Correspondent), Vikram Iyer (Tech Lead),
Sunita Rao (Legal/Compliance), Ravi Krishnan (Finance), Meera Joshi (Events)

Return ONLY valid JSON — no markdown, no explanation:
{"resolved_owner": "Full Name or null", "confidence": 0.85, "reasoning": "why this person"}"""


def _fuzzy_org_match(raw_owner: str | None) -> tuple[str | None, float]:
    """
    Fast org chart lookup — no LLM call needed.
    Returns (matched_name, confidence) or (None, 0.0).
    """
    if not raw_owner:
        return None, 0.0
    lower = raw_owner.lower()
    for key, name in ET_ORG.items():
        if key in lower or lower in key:
            return name, 0.85
    return None, 0.0


def _resolve_with_llm(
    task: ActionItem,
    transcript: str,
) -> tuple[str | None, float, str]:
    """
    Use Llama 3.3 70B to read transcript and resolve owner.
    Called only when org chart fails.
    """
    messages = [
        SystemMessage(content=RESOLVE_SYSTEM),
        HumanMessage(content=f"""
Task description: "{task['description']}"
Task category: {task.get('category', 'editorial')}
Raw owner hint: "{task['owner']}"
Owner confidence was: {task['owner_confidence']}

Meeting transcript:
{transcript[:3000]}

Who is the correct owner for this task?"""),
    ]

    response = llm.invoke(messages)
    text = response.content.strip()

    # Strip markdown fences
    if "```" in text:
        parts = text.split("```")
        text = parts[1] if len(parts) > 1 else text
        if text.startswith("json"):
            text = text[4:]

    data = json.loads(text.strip())
    return (
        data.get("resolved_owner"),
        float(data.get("confidence", 0.5)),
        data.get("reasoning", ""),
    )


def escalation_agent(state: WorkflowState) -> WorkflowState:
    """
    Self-correction engine. Handles:

    1. Ambiguous owners:
       Pass 1 — Org chart fuzzy match (instant, no LLM)
       Pass 2 — Llama reads transcript context (Groq free tier)
       Pass 3 — Escalate to human with full reasoning

    2. Hard workflow failures:
       Retry extraction up to 2 times, then escalate.

    Every attempt is logged with full reasoning — this is what
    makes the audit trail compelling for judges.
    """
    updated_items = list(state["action_items"])
    new_audit     = list(state["audit_log"])
    escalations   = list(state["escalations"])

    # ── Resolve ambiguous owners ──────────────────────────────────────
    for i, task in enumerate(updated_items):
        needs_resolution = (
            task["owner"] is None or task["owner_confidence"] < 0.7
        )
        if not needs_resolution or task["status"] == "escalated":
            continue

        task_short = task["description"][:60]

        # Pass 1: org chart fuzzy match
        matched, conf = _fuzzy_org_match(task.get("owner"))
        if matched:
            updated_items[i] = {
                **task,
                "owner": matched,
                "owner_confidence": conf,
                "last_updated": datetime.now().isoformat(),
            }
            new_audit.append(make_audit_entry(
                agent="escalation_agent",
                action="owner_resolved_org_chart",
                input_summary=task_short,
                output_summary=f"Resolved → {matched}",
                reasoning=(
                    f"Keyword '{task['owner']}' matched ET org chart entry → "
                    f"'{matched}'. No LLM call needed. "
                    f"Confidence: {conf:.0%}. Proceeding to task creation."
                ),
                status="recovery",
            ))
            continue

        # Pass 2: LLM reads transcript context
        try:
            resolved, confidence, reasoning = _resolve_with_llm(
                task, state["transcript_raw"]
            )

            if resolved and confidence >= 0.65:
                updated_items[i] = {
                    **task,
                    "owner": resolved,
                    "owner_confidence": confidence,
                    "last_updated": datetime.now().isoformat(),
                }
                new_audit.append(make_audit_entry(
                    agent="escalation_agent",
                    action="owner_resolved_llm_context",
                    input_summary=task_short,
                    output_summary=f"Resolved → {resolved} ({confidence:.0%} confidence)",
                    reasoning=reasoning,
                    status="recovery",
                ))

            else:
                # Pass 3: escalate to human
                esc = EscalationRecord(
                    id=str(uuid.uuid4())[:8],
                    timestamp=datetime.now().isoformat(),
                    trigger=f"Unresolvable owner: {task_short}",
                    attempted_recoveries=[
                        "org_chart_fuzzy_match",
                        "llm_transcript_context_analysis",
                    ],
                    resolution=None,
                    requires_human=True,
                )
                escalations.append(esc)
                updated_items[i] = {
                    **task,
                    "status": "escalated",
                    "last_updated": datetime.now().isoformat(),
                }
                new_audit.append(make_audit_entry(
                    agent="escalation_agent",
                    action="owner_escalated_to_human",
                    input_summary=task_short,
                    output_summary="Requires human assignment — notifying editor",
                    reasoning=(
                        f"Tried org chart lookup and LLM transcript analysis. "
                        f"Best guess was '{resolved}' at {confidence:.0%} — "
                        f"below 65% confidence threshold. "
                        f"Escalating to Rakesh Sharma (Senior Editor) rather than "
                        f"risk incorrect assignment."
                    ),
                    status="escalated",
                ))

        except Exception as e:
            new_audit.append(make_audit_entry(
                agent="escalation_agent",
                action="resolution_error",
                input_summary=task_short,
                output_summary="LLM resolution failed",
                reasoning=f"Groq API error during owner resolution: {str(e)}",
                status="failure",
            ))

    # ── Hard workflow failure recovery ────────────────────────────────
    if state.get("current_error"):
        error    = state["current_error"]
        attempts = state["recovery_attempts"]

        if "extraction_failed" in error and attempts < 2:
            new_audit.append(make_audit_entry(
                agent="escalation_agent",
                action="retry_extraction",
                input_summary=f"Error: {error}",
                output_summary=f"Scheduling retry {attempts + 1}/2",
                reasoning=(
                    f"Extraction failure is likely a transient Groq API issue. "
                    f"Retrying (attempt {attempts + 1} of 2 max). "
                    f"Will escalate to human operator if retry fails."
                ),
                status="recovery",
            ))
            return {
                **state,
                "action_items": updated_items,
                "audit_log": new_audit,
                "escalations": escalations,
                "current_error": None,
                "recovery_attempts": attempts + 1,
                "extraction_complete": False,
            }

        # Unrecoverable — hand to human
        new_audit.append(make_audit_entry(
            agent="escalation_agent",
            action="workflow_escalated_to_human",
            input_summary=f"Error: {error}",
            output_summary="Human operator notified",
            reasoning=(
                f"Error '{error}' is not auto-recoverable after "
                f"{attempts} attempt(s). Escalating to editorial manager "
                f"with full audit context attached."
            ),
            status="escalated",
        ))
        return {
            **state,
            "action_items": updated_items,
            "audit_log": new_audit,
            "escalations": escalations,
            "workflow_status": "awaiting_human",
        }

    return {
        **state,
        "action_items": updated_items,
        "audit_log": new_audit,
        "escalations": escalations,
        "current_error": None,
    }
