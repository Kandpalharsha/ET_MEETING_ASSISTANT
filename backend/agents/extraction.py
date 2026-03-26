import json
from langchain_core.messages import SystemMessage, HumanMessage

from llm_client import llm
from state import WorkflowState, make_audit_entry

SYSTEM_PROMPT = """
You are an expert system that extracts tasks from meeting transcripts.

Return ONLY JSON:

{
  "decisions": ["..."],
  "action_items": [
    {
      "description": "...",
      "owner": "name or null",
      "deadline": "YYYY-MM-DD",
      "priority": "high"
    }
  ]
}
"""


def extraction_agent(state: WorkflowState) -> WorkflowState:
    transcript = state["transcript_raw"]

    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=transcript)
    ]

    response = llm.invoke(messages)
    text = response.content.strip()

    try:
        data = json.loads(text)
    except:
        data = {"decisions": [], "action_items": []}

    decisions = data.get("decisions", [])
    raw_items = data.get("action_items", [])

    action_items = []
    for i, item in enumerate(raw_items):
        action_items.append({
            "id": str(i + 1),
            "description": item.get("description", ""),
            "owner": item.get("owner"),
            "deadline": item.get("deadline"),
            "priority": item.get("priority", "medium"),
            "status": "pending"
        })

    audit = make_audit_entry(
        agent="extraction_agent",
        action="llm_extraction",
        input_summary="Transcript processed",
        output_summary=f"{len(action_items)} tasks extracted",
        reasoning="Used Groq Llama 3.3 for extraction"
    )

    return {
        **state,
        "decisions": decisions,
        "action_items": action_items,
        "audit_log": state["audit_log"] + [audit]
    }