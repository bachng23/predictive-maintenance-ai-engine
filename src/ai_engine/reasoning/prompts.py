from __future__ import annotations

import json

from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import GuardrailResult, PolicyResult, RiskAssessment


def build_system_prompt() -> str:
    return (
        "You are a bounded reasoning engine for predictive maintenance decisions. "
        "Use only the facts provided by the system. "
        "Do not invent evidence, actions, costs, or operational constraints. "
        "You must choose recommended_action only from allowed_actions. "
        "If the facts are uncertain, prefer a conservative allowed action. "
        "Return JSON only with these keys: "
        "summary, rationale, evidence, recommended_action, confidence, operational_severity."
    )


def build_user_prompt(
    case: DecisionCase,
    risk: RiskAssessment,
    policy: PolicyResult,
    guardrail: GuardrailResult,
) -> str:
    facts = {
        "case": {
            "case_id": case.metadata.case_id,
            "asset_id": case.metadata.asset_id,
            "machine_id": case.metadata.machine_id,
        },
        "physical_evidence": {
            "health_score": case.physical_evidence.health_score,
            "anomaly_score": case.physical_evidence.anomaly_score,
            "failure_horizon_probability": case.physical_evidence.failure_horizon_probability,
            "rul_estimate_hours": case.physical_evidence.rul_estimate_hours,
            "prediction_confidence": case.physical_evidence.prediction_confidence,
            "data_quality_status": case.physical_evidence.data_quality_status.value,
            "drift_status": case.physical_evidence.drift_status.value,
            "recent_signal_trend": case.physical_evidence.recent_signal_trend.value,
        },
        "business_context": {
            "asset_criticality": case.business_context.asset_criticality.value,
            "due_date_pressure": case.business_context.due_date_pressure.value,
            "production_backlog_level": case.business_context.production_backlog_level.value,
            "maintenance_window_available": case.business_context.maintenance_window_available,
            "technician_availability": case.business_context.technician_availability.value,
            "spare_availability": case.business_context.spare_availability.value,
            "shift_restriction": case.business_context.shift_restriction,
        },
        "risk": {
            "risk_level": risk.risk_level.value,
            "confidence": risk.confidence,
            "contributing_factors": risk.contributing_factors,
            "recommended_actions": [action.value for action in risk.recommended_actions],
        },
        "policy": {
            "allowed_actions": [action.value for action in policy.allowed_actions],
            "blocked_actions": [action.value for action in policy.blocked_actions],
            "requires_human_approval": policy.requires_human_approval,
            "policy_notes": policy.policy_notes,
        },
        "guardrails": {
            "passed": guardrail.passed,
            "blocking_reasons": guardrail.blocking_reasons,
            "warnings": guardrail.warnings,
        },
        "output_contract": {
            "summary": "string",
            "rationale": "list of short strings",
            "evidence": "list of facts used from the input",
            "recommended_action": "one value from policy.allowed_actions",
            "confidence": "float from 0.0 to 1.0",
            "operational_severity": "low, medium, or high",
        },
    }

    facts_json = json.dumps(facts, indent=2)

    return (
        "Reason over the following maintenance decision facts.\n"
        "Return JSON only. Do not wrap the JSON in markdown.\n\n"
        + facts_json
    )
