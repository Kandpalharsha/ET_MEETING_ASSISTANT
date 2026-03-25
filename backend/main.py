from fastapi import FastAPI
from pydantic import BaseModel
from state import new_workflow
from agents.extraction import extraction_agent
from agents.escalation import escalation_agent
from agents.task_creation import task_creation_agent
from agents.tracker import tracker_agent

app = FastAPI()
class Input(BaseModel):
    transcript: str


@app.post("/run")
def run(data: Input):
    state = new_workflow(data.transcript)
    state = extraction_agent(state)
    state = escalation_agent(state)
    state = task_creation_agent(state)
    state = tracker_agent(state)

    return state