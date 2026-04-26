from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.decision import ApprovalState, DecisionControl, DecisionRecommendation
from ai_engine.schemas.evidence import PhysicalEvidence


class CaseMetadata(BaseModel):
    case_id: str = Field(..., description="Unique identifier for the decision case.")
    asset_id: str = Field(..., description="Unique identifier for the monitored asset.")
    machine_id: str = Field(..., description="Identifier of the parent machine.")
    bearing_id: str | None = Field(None, description="Identifier of the bearing under evaluation.")
    site_id: str | None = Field(None, description="Identifier of the plant or site.")
    line_id: str | None = Field(None, description="Identifier of the production line.")
    window_start: datetime = Field(..., description="Start time of the evidence window.")
    window_end: datetime = Field(..., description="End time of the evidence window.")
    decision_time: datetime = Field(..., description="Timestamp when the decision snapshot was created.")
    signal_version: str | None = Field(None, description="Version of the raw signal dataset or extract.")
    feature_set_version: str = Field(..., description="Version of the feature set used for inference.")
    model_version: str = Field(..., description="Version of the predictive model used for evidence.")
    policy_version: str = Field(..., description="Version of the decision policy rules.")
    prompt_bundle_version: str | None = Field(None, description="Version of the prompt bundle used for reasoning.")
    schema_version: str = Field("1.0.0", description="Version of the decision case schema.")
    trace_id: str | None = Field(None, description="Trace identifier for workflow observability.")
    replay_id: str | None = Field(None, description="Identifier for replay or audit reconstruction.")


class DecisionCase(BaseModel):
    metadata: CaseMetadata = Field(..., description="Case metadata, identifiers, and version stamps.")
    physical_evidence: PhysicalEvidence = Field(..., description="Machine-health evidence for the current case.")
    business_context: BusinessContext = Field(..., description="Business constraints that shape the decision.")
    decision_control: DecisionControl = Field(..., description="Policy action boundaries and approval requirements.")
    manager_recommendation: DecisionRecommendation = Field(
        default_factory=DecisionRecommendation,
        description="Structured recommendation prepared for human review.",
    )
    approval_state: ApprovalState = Field(..., description="Current approval state for the case.")
