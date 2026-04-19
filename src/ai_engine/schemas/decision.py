from pydantic import BaseModel, Field
from typing import Dict

from ai_engine.schemas.enums import (\
    ActionType,
    ApprovalStatus,
    PriorityLevel,
    RiskLevel
)


class RiskAssessment(BaseModel):
    risk_level: RiskLevel = Field(..., description="Overall risk level for the case")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    contributing_factors: list[str] = Field(
        default_factory=list, 
        description="Key factors contributing to the risk assessment"
    )
    recommended_actions: list[ActionType] = Field(
        default_factory=list,
        description="Recommended actions based on the risk assessment"
    )

class PolicyResult(BaseModel):
    allowed_actions: list[ActionType] = Field(
        default_factory=list,
        description="Actions allowed by the policy"
    )
    blocked_actions: list[ActionType] = Field(
        default_factory=list,
        description="Actions blocked by the policy"
    )
    requires_human_approval: bool = Field(..., description="Whether human review is required")
    policy_notes: list[str] = Field(
        default_factory=list,
        description="Additional policy notes or constraints"
    )

class GuardrailResult(BaseModel):
    passed: bool = Field(..., description="Whether guardrails checks passed")
    blocking_reasons: list[str] = Field(
        decimal_places=list,
        description="Reasons for blocking if guardrails checks failed"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking warnings raised during guardrails checks"
    )

class FinalDecision(BaseModel):
    action: ActionType = Field(..., description="Final recommended action")
    priority: PriorityLevel = Field(..., description="Priority level for the action")
    approval_status: ApprovalStatus = Field(..., description="Approval status of the final decision")
    decision_notes: list[str] = Field(
        default_factory=list,
        description="Additional notes explaining the final decision"
    )
    rationales: list[str] = Field(
        default_factory=list,
        description="Short explanation for the final decision"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Supporting evidence that influenced the final decision"
    )
    next_steps: list[str] = Field(
        default_factory=list,
        description="Recommended next steps after the final decision"
    )
