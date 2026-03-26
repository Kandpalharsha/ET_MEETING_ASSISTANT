import json
from langchain_core.messages import SystemMessage, HumanMessage

from llm_client import llm
from state import WorkflowState, make_audit_entry


SYSTEM_PROMPT = """
Extract tasks from meeting transcript.
Return ONLY JSON.
"""


def extraction_agent(state: WorkflowState) -> WorkflowState:
    transcript = state["transcript_raw"]
    new_audit = list(state["audit_log"])

    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=transcript)
        ]

        response = llm.invoke(messages)
        data = json.loads(response.content)

        action_items = data.get("action_items", [])

        audit = make_audit_entry(
            agent="extraction_agent",
            action="llm_extraction",
            input_summary="Transcript",
            output_summary=f"{len(action_items)} tasks extracted",
            reasoning="LLM extraction successful"
        )

        return {
            **state,
            "action_items": action_items,
            "audit_log": new_audit + [audit],
            "current_error": None
        }

    except Exception as e:
        audit = make_audit_entry(
            agent="extraction_agent",
            action="extraction_failed",
            input_summary="Transcript",
            output_summary="LLM failed",
            reasoning=str(e),
            status="failure"
        )

        return {
            **state,
            "audit_log": new_audit + [audit],
            "current_error": "extraction_failed"
        }