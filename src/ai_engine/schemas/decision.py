from datetime import datetime

from pydantic import BaseModel, Field

from ai_engine.schemas.enums import ActionType, ApprovalStatus, OperationalSeverity, PriorityLevel, RiskLevel


class DecisionControl(BaseModel):
    allowed_actions: list[ActionType] = Field(..., description="Actions currently allowed by policy.")
    blocked_actions: list[ActionType] = Field(
        default_factory=list,
        description="Actions currently blocked by policy or guardrails.",
    )
    approval_required: bool = Field(..., description="Whether the case requires human approval before execution.")
    policy_flags: list[str] = Field(default_factory=list, description="Policy flags or rule references for the case.")


class DecisionRecommendation(BaseModel):
    recommended_action: ActionType | None = Field(None, description="Action recommended for the current case.")
    rationale: list[str] = Field(default_factory=list, description="Structured rationale supporting the recommendation.")
    evidence_used: list[str] = Field(default_factory=list, description="Evidence references used in the recommendation.")
    unresolved_assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions that still need human review or confirmation.",
    )


class ApprovalState(BaseModel):
    status: ApprovalStatus = Field(..., description="Current approval status of the case.")
    decided_by: str | None = Field(None, description="Identifier of the actor who made the approval decision.")
    decided_at: datetime | None = Field(None, description="Timestamp when the approval decision was recorded.")
    comments: str | None = Field(None, description="Optional comment attached to the approval decision.")


class RiskAssessment(BaseModel):
    risk_level: RiskLevel = Field(..., description="Overall risk level for the case.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the risk assessment.")
    contributing_factors: list[str] = Field(
        default_factory=list,
        description="Key factors contributing to the risk assessment.",
    )
    recommended_actions: list[ActionType] = Field(
        default_factory=list,
        description="Action candidates suggested by the risk assessment.",
    )


class PolicyResult(BaseModel):
    allowed_actions: list[ActionType] = Field(default_factory=list, description="Actions allowed by policy.")
    blocked_actions: list[ActionType] = Field(default_factory=list, description="Actions blocked by policy.")
    requires_human_approval: bool = Field(..., description="Whether policy requires human approval.")
    policy_notes: list[str] = Field(default_factory=list, description="Additional policy notes or rule references.")


class GuardrailResult(BaseModel):
    passed: bool = Field(..., description="Whether guardrail checks passed.")
    blocking_reasons: list[str] = Field(default_factory=list, description="Reasons that caused the case to be blocked.")
    warnings: list[str] = Field(default_factory=list, description="Non-blocking guardrail warnings for the case.")


class ReasoningResult(BaseModel):
    summary: str = Field(..., description="High-level explanation of the case.")
    rationale: list[str] = Field(default_factory=list, description="Structured reasons supporting the proposed action.")
    evidence: list[str] = Field(default_factory=list, description="Evidence items referenced by the reasoning layer.")
    recommended_action: ActionType = Field(..., description="Action proposed by the reasoning layer.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the reasoning output.")
    operational_severity: OperationalSeverity = Field(
        ...,
        description="Operational severity inferred from the overall context.",
    )


class FinalDecision(BaseModel):
    risk_level: RiskLevel = Field(..., description="Final risk level for the case.")
    action: ActionType = Field(..., description="Final selected action for the case.")
    priority: PriorityLevel = Field(..., description="Priority assigned to the final action.")
    approval_status: ApprovalStatus = Field(..., description="Approval status of the final decision.")
    decision_notes: list[str] = Field(default_factory=list, description="Additional notes attached to the decision.")
    rationale: list[str] = Field(default_factory=list, description="Short rationale statements for the final decision.")
    evidence: list[str] = Field(default_factory=list, description="Supporting evidence used for the final decision.")
    next_steps: list[str] = Field(default_factory=list, description="Recommended next steps after the decision.")
