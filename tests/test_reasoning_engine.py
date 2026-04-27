from dataclasses import dataclass
import json

from ai_engine.reasoning.engine import ReasoningEngine
from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.case import CaseMetadata, DecisionCase
from ai_engine.schemas.decision import ApprovalState, DecisionControl, DecisionRecommendation
from ai_engine.schemas.decision import GuardrailResult, PolicyResult, RiskAssessment
from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    AvailabilityStatus,
    CriticalityLevel,
    CustomerPriority,
    DataQualityLevel,
    DriftStatus,
    OperationalSeverity,
    PressureLevel,
    RiskLevel,
    SignalTrend,
)
from ai_engine.schemas.evidence import PhysicalEvidence


@dataclass
class FakeResponse:
    content: str


class FakeModel:
    def __init__(self, payload: dict | None = None, should_fail: bool = False) -> None:
        self.payload = payload or {}
        self.should_fail = should_fail

    def invoke(self, messages: list[tuple[str, str]]) -> FakeResponse:
        if self.should_fail:
            raise RuntimeError("fake model failure")
        return FakeResponse(content=json.dumps(self.payload))


def build_case() -> DecisionCase:
    return DecisionCase(
        metadata=CaseMetadata(
            case_id="case-reasoning-001",
            asset_id="asset-001",
            machine_id="machine-001",
            window_start="2026-04-20T10:00:00Z",
            window_end="2026-04-20T11:00:00Z",
            decision_time="2026-04-20T11:05:00Z",
            feature_set_version="features-v1",
            model_version="model-v1",
            policy_version="policy-v1",
        ),
        physical_evidence=PhysicalEvidence(
            health_score=0.40,
            anomaly_score=0.74,
            failure_horizon_probability=0.68,
            rul_estimate_hours=60.0,
            prediction_confidence=0.88,
            signal_quality_score=0.93,
            data_completeness_score=0.96,
            drift_score=0.14,
            recent_signal_trend=SignalTrend.DEGRADING,
            data_quality_status=DataQualityLevel.OK,
            drift_status=DriftStatus.WARNING,
        ),
        business_context=BusinessContext(
            asset_criticality=CriticalityLevel.HIGH,
            due_date_pressure=PressureLevel.HIGH,
            queue_length=5,
            production_backlog_level=PressureLevel.MEDIUM,
            downtime_cost_per_hour=1200.0,
            lateness_penalty_estimate=3000.0,
            maintenance_cost_estimate=800.0,
            emergency_failure_cost_estimate=12000.0,
            spare_availability=AvailabilityStatus.AVAILABLE,
            technician_availability=AvailabilityStatus.AVAILABLE,
            maintenance_window_available=True,
            current_load_pct=81.0,
            order_id="order-001",
            customer_priority=CustomerPriority.HIGH,
        ),
        decision_control=DecisionControl(
            allowed_actions=[],
            blocked_actions=[],
            approval_required=False,
            policy_flags=[],
        ),
        manager_recommendation=DecisionRecommendation(),
        approval_state=ApprovalState(status=ApprovalStatus.NOT_REQUIRED),
    )


def build_risk() -> RiskAssessment:
    return RiskAssessment(
        risk_level=RiskLevel.HIGH,
        confidence=0.84,
        contributing_factors=["Failure horizon probability is elevated."],
        recommended_actions=[ActionType.INSPECT, ActionType.PLAN_MAINTENANCE],
    )


def test_reasoning_engine_uses_valid_model_output() -> None:
    engine = ReasoningEngine(
        model=FakeModel(
            payload={
                "summary": "Planned maintenance best fits the case.",
                "rationale": ["Failure risk is elevated but action remains schedulable."],
                "evidence": ["failure_horizon_probability=0.68"],
                "recommended_action": "PLAN_MAINTENANCE",
                "confidence": 0.79,
                "operational_severity": "high",
            }
        )
    )

    result = engine.generate(
        case=build_case(),
        risk=build_risk(),
        policy=PolicyResult(
            allowed_actions=[ActionType.INSPECT, ActionType.PLAN_MAINTENANCE],
            blocked_actions=[],
            requires_human_approval=True,
            policy_notes=[],
        ),
        guardrail=GuardrailResult(passed=True),
    )

    assert result.recommended_action == ActionType.PLAN_MAINTENANCE
    assert result.operational_severity == OperationalSeverity.HIGH
    assert result.summary == "Planned maintenance best fits the case."


def test_reasoning_engine_falls_back_when_model_fails() -> None:
    engine = ReasoningEngine(model=FakeModel(should_fail=True))

    result = engine.generate(
        case=build_case(),
        risk=build_risk(),
        policy=PolicyResult(
            allowed_actions=[ActionType.INSPECT],
            blocked_actions=[],
            requires_human_approval=False,
            policy_notes=["Inspection remains the safest allowed action."],
        ),
        guardrail=GuardrailResult(passed=True, warnings=["Warning-level drift detected."]),
    )

    assert result.recommended_action == ActionType.INSPECT
    assert "Inspection remains the safest allowed action." in result.rationale
    assert "Warning-level drift detected." in result.evidence


def test_reasoning_engine_falls_back_when_action_is_outside_policy() -> None:
    engine = ReasoningEngine(
        model=FakeModel(
            payload={
                "summary": "Stop now.",
                "rationale": ["This looks critical."],
                "evidence": ["anomaly_score=0.74"],
                "recommended_action": "CONTROLLED_STOP",
                "confidence": 0.85,
                "operational_severity": "high",
            }
        )
    )

    result = engine.generate(
        case=build_case(),
        risk=build_risk(),
        policy=PolicyResult(
            allowed_actions=[ActionType.INSPECT, ActionType.PLAN_MAINTENANCE],
            blocked_actions=[],
            requires_human_approval=False,
            policy_notes=[],
        ),
        guardrail=GuardrailResult(passed=True),
    )

    assert result.recommended_action == ActionType.INSPECT
