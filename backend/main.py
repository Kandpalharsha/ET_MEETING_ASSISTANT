from fastapi import FastAPI
from pydantic import BaseModel

from graph import workflow
from state import new_workflow, WorkflowState

app = FastAPI()

class Input(BaseModel):
    transcript: str


@app.post("/run")
def run(data: Input):
    state: WorkflowState = new_workflow(data.transcript)

    final_state = None

    for step in workflow.stream(state):
        for _, s in step.items():
            final_state = s

    return final_state