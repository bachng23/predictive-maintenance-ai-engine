from ai_engine.policy.engine import PolicyEngine
from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.case import CaseMetadata, DecisionCase
from ai_engine.schemas.decision import ApprovalState, DecisionControl, DecisionRecommendation
from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    AvailabilityStatus,
    CriticalityLevel,
    CustomerPriority,
    DataQualityLevel,
    DriftStatus,
    PressureLevel,
    RiskLevel,
    SignalTrend,
)
from ai_engine.schemas.evidence import PhysicalEvidence


def build_case(
    *,
    data_quality_status: DataQualityLevel = DataQualityLevel.OK,
    drift_status: DriftStatus = DriftStatus.NONE,
    prediction_confidence: float = 0.90,
    maintenance_window_available: bool = True,
    technician_availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE,
    spare_availability: AvailabilityStatus = AvailabilityStatus.AVAILABLE,
    asset_criticality: CriticalityLevel = CriticalityLevel.MEDIUM,
) -> DecisionCase:
    return DecisionCase(
        metadata=CaseMetadata(
            case_id="case-001",
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
            health_score=0.45,
            anomaly_score=0.70,
            failure_horizon_probability=0.62,
            rul_estimate_hours=96.0,
            prediction_confidence=prediction_confidence,
            signal_quality_score=0.92,
            data_completeness_score=0.95,
            drift_score=0.12,
            recent_signal_trend=SignalTrend.DEGRADING,
            data_quality_status=data_quality_status,
            drift_status=drift_status,
        ),
        business_context=BusinessContext(
            asset_criticality=asset_criticality,
            due_date_pressure=PressureLevel.HIGH,
            queue_length=5,
            production_backlog_level=PressureLevel.MEDIUM,
            downtime_cost_per_hour=1200.0,
            lateness_penalty_estimate=3000.0,
            maintenance_cost_estimate=800.0,
            emergency_failure_cost_estimate=12000.0,
            spare_availability=spare_availability,
            technician_availability=technician_availability,
            maintenance_window_available=maintenance_window_available,
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


def test_high_risk_case_returns_expected_base_actions() -> None:
    engine = PolicyEngine()
    case = build_case()

    result = engine.evaluate(case=case, risk_level=RiskLevel.HIGH)

    assert result.allowed_actions == [
        ActionType.INSPECT,
        ActionType.PLAN_MAINTENANCE,
        ActionType.ESCALATE,
    ]
    assert result.requires_human_approval is True


def test_severe_data_quality_blocks_run_and_high_impact_actions() -> None:
    engine = PolicyEngine()
    case = build_case(data_quality_status=DataQualityLevel.SEVERE)

    result = engine.evaluate(case=case, risk_level=RiskLevel.MEDIUM)

    assert ActionType.RUN_WITH_MONITORING not in result.allowed_actions
    assert ActionType.PLAN_MAINTENANCE in result.blocked_actions
    assert ActionType.CONTROLLED_STOP in result.blocked_actions


def test_low_confidence_blocks_stronger_actions() -> None:
    engine = PolicyEngine()
    case = build_case(prediction_confidence=0.40)

    result = engine.evaluate(case=case, risk_level=RiskLevel.HIGH)

    assert ActionType.PLAN_MAINTENANCE in result.blocked_actions
    assert ActionType.INSPECT in result.allowed_actions
    assert ActionType.ESCALATE in result.allowed_actions


def test_no_maintenance_window_blocks_plan_maintenance() -> None:
    engine = PolicyEngine()
    case = build_case(maintenance_window_available=False)

    result = engine.evaluate(case=case, risk_level=RiskLevel.HIGH)

    assert ActionType.PLAN_MAINTENANCE in result.blocked_actions
    assert ActionType.ESCALATE in result.allowed_actions
