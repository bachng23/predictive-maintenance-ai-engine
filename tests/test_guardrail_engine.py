from ai_engine.guardrails.engine import GuardrailEngine
from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.case import CaseMetadata, DecisionCase
from ai_engine.schemas.decision import ApprovalState, DecisionControl, DecisionRecommendation, PolicyResult
from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    AvailabilityStatus,
    CriticalityLevel,
    CustomerPriority,
    DataQualityLevel,
    DriftStatus,
    PressureLevel,
    SignalTrend,
)
from ai_engine.schemas.evidence import PhysicalEvidence


def build_case(
    *,
    data_quality_status: DataQualityLevel = DataQualityLevel.OK,
    drift_status: DriftStatus = DriftStatus.NONE,
    prediction_confidence: float = 0.90,
    maintenance_window_available: bool = True,
    shift_restriction: str | None = None,
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED,
) -> DecisionCase:
    return DecisionCase(
        metadata=CaseMetadata(
            case_id="case-guardrail-001",
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
            anomaly_score=0.75,
            failure_horizon_probability=0.68,
            rul_estimate_hours=72.0,
            prediction_confidence=prediction_confidence,
            signal_quality_score=0.91,
            data_completeness_score=0.96,
            drift_score=0.18,
            recent_signal_trend=SignalTrend.DEGRADING,
            data_quality_status=data_quality_status,
            drift_status=drift_status,
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
            maintenance_window_available=maintenance_window_available,
            current_load_pct=81.0,
            order_id="order-001",
            customer_priority=CustomerPriority.HIGH,
            shift_restriction=shift_restriction,
        ),
        decision_control=DecisionControl(
            allowed_actions=[],
            blocked_actions=[],
            approval_required=False,
            policy_flags=[],
        ),
        manager_recommendation=DecisionRecommendation(),
        approval_state=ApprovalState(status=approval_status),
    )


def build_policy_result(allowed_actions: list[ActionType]) -> PolicyResult:
    return PolicyResult(
        allowed_actions=allowed_actions,
        blocked_actions=[],
        requires_human_approval=ActionType.CONTROLLED_STOP in allowed_actions,
        policy_notes=[],
    )


def test_guardrail_passes_on_normal_case() -> None:
    engine = GuardrailEngine()
    case = build_case()
    policy_result = build_policy_result([ActionType.INSPECT, ActionType.ESCALATE])

    result = engine.evaluate(case, policy_result)

    assert result.passed is True
    assert result.blocking_reasons == []


def test_guardrail_blocks_severe_data_quality() -> None:
    engine = GuardrailEngine()
    case = build_case(data_quality_status=DataQualityLevel.SEVERE)
    policy_result = build_policy_result([ActionType.INSPECT])

    result = engine.evaluate(case, policy_result)

    assert result.passed is False
    assert "Data quality is severe; execution should not proceed." in result.blocking_reasons


def test_guardrail_blocks_unapproved_controlled_stop() -> None:
    engine = GuardrailEngine()
    case = build_case(approval_status=ApprovalStatus.PENDING)
    policy_result = build_policy_result([ActionType.CONTROLLED_STOP])

    result = engine.evaluate(case, policy_result)

    assert result.passed is False
    assert "Controlled stop requires explicit approval before execution." in result.blocking_reasons


def test_guardrail_emits_warning_for_shift_restriction() -> None:
    engine = GuardrailEngine()
    case = build_case(shift_restriction="night shift only", drift_status=DriftStatus.WARNING)
    policy_result = build_policy_result([ActionType.INSPECT])

    result = engine.evaluate(case, policy_result)

    assert result.passed is True
    assert "Warning-level drift detected in current input distribution." in result.warnings
    assert "Shift restriction in effect: night shift only" in result.warnings
