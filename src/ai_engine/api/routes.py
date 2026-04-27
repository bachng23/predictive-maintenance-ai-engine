from fastapi import APIRouter

from ai_engine.orchestration.graph import graph
from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.state import DecisionState

router = APIRouter(prefix="/decision-cases", tags=["decision-cases"])

@router.post("/run", response_model=DecisionState)
def run_decision_case(case: DecisionCase) -> DecisionState:
    initial_state = DecisionState(case=case)
    result = graph.invoke(initial_state)
    return DecisionState.model_validate(result)
