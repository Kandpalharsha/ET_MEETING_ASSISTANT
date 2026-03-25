from fastapi import FastAPI
from pydantic import BaseModel

from state import WorkflowState
from agents.extraction import extraction_agent
from agents.escalation import escalation_agent
from agents.task_creation import task_creation_agent

app = FastAPI()

class Input(BaseModel):
    transcript: str

@app.post("/run")
def run(data: Input):
    state: WorkflowState = {
        "transcript_raw": data.transcript,
        "decisions": [],
        "action_items": [],
        "audit_log": []
    }

    state = extraction_agent(state)
    state = escalation_agent(state)
    state = task_creation_agent(state)

    return state