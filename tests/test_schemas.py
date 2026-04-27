from datetime import datetime, timezone

import pytest

from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.case import CaseMetadata, DecisionCase
from ai_engine.schemas.decision import (
    ApprovalState,
    DecisionControl,
    DecisionRecommendation,
    FinalDecision,
    GuardrailResult,
    ReasoningResult,
)
from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    AvailabilityStatus,
    CriticalityLevel,
    CustomerPriority,
    DataQualityLevel,
    DriftStatus,
    FeatureDirection,
    OperationalSeverity,
    PressureLevel,
    PriorityLevel,
    RiskLevel,
    SignalTrend,
)
from ai_engine.schemas.evidence import FeatureAttribution, PhysicalEvidence


def build_case() -> DecisionCase:
    return DecisionCase(
        metadata=CaseMetadata(
            case_id="case-1",
            asset_id="asset-7",
            machine_id="machine-2",
            bearing_id="bearing-a",
            window_start="2026-04-20T10:00:00Z",
            window_end="2026-04-20T11:00:00Z",
            decision_time="2026-04-20T11:05:00Z",
            feature_set_version="features-v1",
            model_version="model-v1",
            policy_version="policy-v1",
        ),
        physical_evidence=PhysicalEvidence(
            health_score=0.42,
            anomaly_score=0.78,
            failure_horizon_probability=0.61,
            rul_estimate_hours=120.0,
            prediction_confidence=0.84,
            signal_quality_score=0.93,
            data_completeness_score=0.88,
            drift_score=0.17,
            recent_signal_trend=SignalTrend.DEGRADING,
            data_quality_status=DataQualityLevel.OK,
            drift_status=DriftStatus.WARNING,
            top_feature_attributions=[
                FeatureAttribution(
                    feature_name="vibration_rms",
                    importance=0.31,
                    direction=FeatureDirection.INCREASE_RISK,
                )
            ],
        ),
        business_context=BusinessContext(
            asset_criticality=CriticalityLevel.HIGH,
            due_date_pressure=PressureLevel.HIGH,
            queue_length=6,
            production_backlog_level=PressureLevel.MEDIUM,
            downtime_cost_per_hour=1500.0,
            lateness_penalty_estimate=3000.0,
            maintenance_cost_estimate=800.0,
            emergency_failure_cost_estimate=15000.0,
            spare_availability=AvailabilityStatus.LIMITED,
            technician_availability=AvailabilityStatus.AVAILABLE,
            maintenance_window_available=False,
            current_load_pct=82.0,
            order_id="order-9",
            customer_priority=CustomerPriority.CRITICAL,
        ),
        decision_control=DecisionControl(
            allowed_actions=[ActionType.INSPECT, ActionType.ESCALATE],
            blocked_actions=[ActionType.RUN],
            approval_required=True,
            policy_flags=["critical_asset", "tight_due_dates"],
        ),
        manager_recommendation=DecisionRecommendation(
            recommended_action=ActionType.ESCALATE,
            rationale=["Failure risk is rising while order pressure remains high."],
        ),
        approval_state=ApprovalState(status=ApprovalStatus.PENDING),
    )


def test_decision_case_accepts_structured_snapshot() -> None:
    case = build_case()

    assert case.metadata.case_id == "case-1"
    assert case.metadata.decision_time == datetime(2026, 4, 20, 11, 5, tzinfo=timezone.utc)
    assert case.physical_evidence.recent_signal_trend == SignalTrend.DEGRADING
    assert case.business_context.customer_priority == CustomerPriority.CRITICAL


def test_physical_evidence_rejects_invalid_probability() -> None:
    with pytest.raises(ValueError):
        PhysicalEvidence(
            prediction_confidence=0.9,
            signal_quality_score=0.8,
            data_completeness_score=0.85,
            failure_horizon_probability=1.3,
            recent_signal_trend=SignalTrend.STABLE,
            data_quality_status=DataQualityLevel.OK,
            drift_status=DriftStatus.NONE,
        )


def test_guardrail_result_defaults_empty_lists() -> None:
    result = GuardrailResult(passed=True)

    assert result.blocking_reasons == []
    assert result.warnings == []


def test_reasoning_and_final_decision_contracts_are_instantiable() -> None:
    reasoning = ReasoningResult(
        summary="Signals indicate elevated wear risk.",
        rationale=["Vibration trend is increasing."],
        evidence=["RMS vibration and temperature both increased."],
        recommended_action=ActionType.PLAN_MAINTENANCE,
        confidence=0.81,
        operational_severity=OperationalSeverity.MEDIUM,
    )
    final_decision = FinalDecision(
        risk_level=RiskLevel.MEDIUM,
        action=ActionType.PLAN_MAINTENANCE,
        priority=PriorityLevel.HIGH,
        approval_status=ApprovalStatus.PENDING,
        rationale=["Plan a maintenance window soon."],
        next_steps=["Prepare parts and technician schedule."],
    )

    assert reasoning.recommended_action == ActionType.PLAN_MAINTENANCE
    assert final_decision.risk_level == RiskLevel.MEDIUM
    assert final_decision.next_steps == ["Prepare parts and technician schedule."]
