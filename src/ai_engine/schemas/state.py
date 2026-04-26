from pydantic import BaseModel, Field

from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import FinalDecision, GuardrailResult, PolicyResult, ReasoningResult, RiskAssessment


class DecisionState(BaseModel):
    case: DecisionCase = Field(..., description="Canonical decision case snapshot.")
    risk: RiskAssessment | None = Field(None, description="Risk assessment produced for the case.")
    policy: PolicyResult | None = Field(None, description="Policy evaluation result for the case.")
    guardrail: GuardrailResult | None = Field(None, description="Guardrail evaluation result for the case.")
    reasoning: ReasoningResult | None = Field(None, description="Structured reasoning output for the case.")
    final_decision: FinalDecision | None = Field(None, description="Final decision produced for the case.")
