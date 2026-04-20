from typing import Optional

from pydantic import BaseModel, Field

from src.ai_engine.schemas.case import DecisionCase, NormalizedCase
from src.ai_engine.schemas.decision import (
    FinalDecision,
    GuardrailResult,
    PolicyResult,
    ReasoningResult,
    RiskAssessment,
)


class DecisionState(BaseModel):
    case: DecisionCase = Field(..., description="Original case data")
    normalized_case: Optional[NormalizedCase] = Field(None, description="Normalized case data")

    risk: Optional[RiskAssessment] = Field(None, description="Risk assessment for the case")
    policy: Optional[PolicyResult] = Field(None, description="Policy result for the case")
    guardrail: Optional[GuardrailResult] = Field(None, description="Guardrail result for the case")
    reasoning: Optional[ReasoningResult] = Field(None, description="Reasoning output for the case")

    final_decision: Optional[FinalDecision] = Field(None, description="Final decision for the case")
