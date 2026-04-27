from ai_engine.decision.composer import DecisionComposer
from ai_engine.schemas.business import BusinessContext
from ai_engine.schemas.case import CaseMetadata, DecisionCase
from ai_engine.schemas.decision import (
    ApprovalState,
    DecisionControl,
    DecisionRecommendation,
    FinalDecision,
    GuardrailResult,
    PolicyResult,
    ReasoningResult,
    RiskAssessment,
)
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
    PriorityLevel,
    RiskLevel,
    SignalTrend,
)
from ai_engine.schemas.evidence import PhysicalEvidence


def build_case(*, approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED) -> DecisionCase:
    return DecisionCase(
        metadata=CaseMetadata(
            case_id="case-compose-001",
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
            prediction_confidence=0.90,
            signal_quality_score=0.92,
            data_completeness_score=0.95,
            drift_score=0.12,
            recent_signal_trend=SignalTrend.DEGRADING,
            data_quality_status=DataQualityLevel.OK,
            drift_status=DriftStatus.NONE,
        ),
        business_context=BusinessContext(
            asset_criticality=CriticalityLevel.MEDIUM,
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
        approval_state=ApprovalState(status=approval_status),
    )


def build_risk(risk_level: RiskLevel = RiskLevel.HIGH) -> RiskAssessment:
    return RiskAssessment(
        risk_level=risk_level,
        confidence=0.87,
        contributing_factors=["Failure probability is elevated."],
        recommended_actions=[ActionType.INSPECT, ActionType.PLAN_MAINTENANCE],
    )


def test_composer_uses_reasoning_action_when_allowed() -> None:
    composer = DecisionComposer()
    case = build_case()
    risk = build_risk(RiskLevel.HIGH)
    policy = PolicyResult(
        allowed_actions=[ActionType.INSPECT, ActionType.PLAN_MAINTENANCE],
        blocked_actions=[],
        requires_human_approval=True,
        policy_notes=["High-risk case requires approval before execution."],
    )
    guardrail = GuardrailResult(passed=True, warnings=["Shift restriction in effect: night shift only"])
    reasoning = ReasoningResult(
        summary="Planned maintenance best balances risk and disruption.",
        rationale=["Maintenance can be planned before failure risk becomes critical."],
        evidence=["Failure horizon probability is elevated."],
        recommended_action=ActionType.PLAN_MAINTENANCE,
        confidence=0.82,
        operational_severity=OperationalSeverity.HIGH,
    )

    recommendation, final_decision = composer.compose(case, risk, policy, guardrail, reasoning)

    assert recommendation.recommended_action == ActionType.PLAN_MAINTENANCE
    assert "Human approval is required before execution." in recommendation.unresolved_assumptions
    assert "Shift restriction in effect: night shift only" in recommendation.unresolved_assumptions
    assert final_decision.action == ActionType.PLAN_MAINTENANCE
    assert final_decision.approval_status == ApprovalStatus.PENDING
    assert final_decision.priority == PriorityLevel.HIGH
    assert final_decision.next_steps[0] == "Obtain required human approval before execution."


def test_composer_falls_back_to_first_policy_action_without_reasoning() -> None:
    composer = DecisionComposer()
    case = build_case()
    risk = build_risk(RiskLevel.MEDIUM)
    policy = PolicyResult(
        allowed_actions=[ActionType.RUN_WITH_MONITORING, ActionType.INSPECT],
        blocked_actions=[],
        requires_human_approval=False,
        policy_notes=["Medium-risk case supports continued operation with tighter monitoring."],
    )
    guardrail = GuardrailResult(passed=True)

    recommendation, final_decision = composer.compose(case, risk, policy, guardrail, reasoning=None)

    assert recommendation.recommended_action == ActionType.RUN_WITH_MONITORING
    assert recommendation.rationale == ["Recommendation derived from policy-ranked allowed actions."]
    assert final_decision.action == ActionType.RUN_WITH_MONITORING
    assert final_decision.approval_status == ApprovalStatus.NOT_REQUIRED
    assert final_decision.priority == PriorityLevel.MEDIUM


def test_composer_escalates_blocked_case() -> None:
    composer = DecisionComposer()
    case = build_case(approval_status=ApprovalStatus.PENDING)
    risk = build_risk(RiskLevel.CRITICAL)
    policy = PolicyResult(
        allowed_actions=[ActionType.CONTROLLED_STOP],
        blocked_actions=[ActionType.RUN, ActionType.RUN_WITH_MONITORING],
        requires_human_approval=True,
        policy_notes=["Critical case would normally require controlled stop."],
    )
    guardrail = GuardrailResult(
        passed=False,
        blocking_reasons=["Controlled stop requires explicit approval before execution."],
        warnings=[],
    )

    recommendation, final_decision = composer.compose(case, risk, policy, guardrail, reasoning=None)

    assert recommendation.recommended_action == ActionType.ESCALATE
    assert final_decision.action == ActionType.ESCALATE
    assert final_decision.approval_status == ApprovalStatus.BLOCKED
    assert final_decision.priority == PriorityLevel.URGENT
    assert "Controlled stop requires explicit approval before execution." in final_decision.decision_notes
