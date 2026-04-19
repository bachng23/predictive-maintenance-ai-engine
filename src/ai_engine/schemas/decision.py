from pydantic import BaseModel, Field

from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    OperationalSeverity,
    PriorityLevel,
    RiskLevel,
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
        default_factory=list,
        description="Reasons for blocking if guardrails checks failed"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-blocking warnings raised during guardrails checks"
    )


class ReasoningResult(BaseModel):
    summary: str = Field(..., description="High-level explanation of the case")
    rationale: list[str] = Field(
        default_factory=list,
        description="Structured reasons supporting the proposed decision"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Signals and facts referenced by the reasoning layer"
    )
    recommended_action: ActionType = Field(
        ...,
        description="Action proposed by the reasoning layer before final composition"
    )
    confidence: float = Field(..., ge=0.0, le=1.0, description="Reasoning confidence (0-1)")
    operational_severity: OperationalSeverity = Field(
        ...,
        description="Operational severity inferred from the case context"
    )


class FinalDecision(BaseModel):
    risk_level: RiskLevel = Field(..., description="Final risk level for the case")
    action: ActionType = Field(..., description="Final recommended action")
    priority: PriorityLevel = Field(..., description="Priority level for the action")
    approval_status: ApprovalStatus = Field(..., description="Approval status of the final decision")
    decision_notes: list[str] = Field(
        default_factory=list,
        description="Additional notes explaining the final decision"
    )
    rationale: list[str] = Field(
        default_factory=list,
        description="Short explanations for the final decision"
    )
    evidence: list[str] = Field(
        default_factory=list,
        description="Supporting evidence that influenced the final decision"
    )
    next_steps: list[str] = Field(
        default_factory=list,
        description="Recommended next steps after the final decision"
    )
