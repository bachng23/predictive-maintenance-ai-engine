from datetime import datetime, timezone

import pytest

from ai_engine.schemas.case import DecisionCase, NormalizedCase
from ai_engine.schemas.decision import FinalDecision, GuardrailResult, ReasoningResult
from ai_engine.schemas.enums import (
    ActionType,
    ApprovalStatus,
    OperationalSeverity,
    PriorityLevel,
    RiskLevel,
    ScenarioType,
)


def test_decision_case_accepts_locked_demo_scenarios() -> None:
    case = DecisionCase(
        case_id="case-1",
        asset_type="bearing",
        scenario_type=ScenarioType.BEARING_WARNING,
        telemetry_summary={"vibration": "elevated"},
        operating_context={"load": "normal"},
        timestamp="2026-04-20T12:00:00Z",
    )

    assert case.scenario_type is ScenarioType.BEARING_WARNING
    assert case.timestamp == datetime(2026, 4, 20, 12, 0, tzinfo=timezone.utc)


def test_normalized_case_requires_known_operational_severity() -> None:
    with pytest.raises(ValueError):
        NormalizedCase(
            asset_type="bearing",
            detected_signals={"vibration": "elevated"},
            signal_quality=0.9,
            data_completeness=0.85,
            symptom_summary="Minor wear signs",
            operational_severity="critical",
        )


def test_guardrail_result_defaults_empty_lists() -> None:
    result = GuardrailResult(passed=True)

    assert result.blocking_reasons == []
    assert result.warnings == []


def test_reasoning_and_final_decision_contracts_are_instantiable() -> None:
    reasoning = ReasoningResult(
        summary="Signals indicate elevated wear risk.",
        rationale=["Vibration trend is increasing."],
        evidence=["Abnormal noise has been reported."],
        recommended_action=ActionType.SCHEDULE_MAINTENANCE,
        confidence=0.81,
        operational_severity=OperationalSeverity.MEDIUM,
    )
    final_decision = FinalDecision(
        risk_level=RiskLevel.MEDIUM,
        action=ActionType.SCHEDULE_MAINTENANCE,
        priority=PriorityLevel.MEDIUM,
        approval_status=ApprovalStatus.REQUIRED,
        rationale=["Plan a maintenance window soon."],
        next_steps=["Create maintenance ticket."],
    )

    assert reasoning.recommended_action is ActionType.SCHEDULE_MAINTENANCE
    assert final_decision.risk_level is RiskLevel.MEDIUM
    assert final_decision.next_steps == ["Create maintenance ticket."]
