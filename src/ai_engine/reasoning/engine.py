from __future__ import annotations

import json
from typing import Any

from ai_engine.reasoning.llm_client import build_openrouter_chat_model
from ai_engine.reasoning.prompts import build_system_prompt, build_user_prompt
from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import GuardrailResult, PolicyResult, ReasoningResult, RiskAssessment
from ai_engine.schemas.enums import ActionType, OperationalSeverity, RiskLevel


class ReasoningEngine:
    def __init__(self, model: Any | None = None) -> None:
        self.model = model or build_openrouter_chat_model()

    def generate(
        self,
        case: DecisionCase,
        risk: RiskAssessment,
        policy: PolicyResult,
        guardrail: GuardrailResult,
    ) -> ReasoningResult:
        if not guardrail.passed or self.model is None:
            return self._fallback(case=case, risk=risk, policy=policy, guardrail=guardrail)

        try:
            response = self.model.invoke(
                [
                    ("system", build_system_prompt()),
                    (
                        "human",
                        build_user_prompt(
                            case=case,
                            risk=risk,
                            policy=policy,
                            guardrail=guardrail,
                        ),
                    ),
                ]
            )
            payload = json.loads(response.content)
            result = ReasoningResult.model_validate(payload)
            self._ensure_action_allowed(result, policy)
            return result
        except Exception:
            return self._fallback(case=case, risk=risk, policy=policy, guardrail=guardrail)

    def _ensure_action_allowed(self, result: ReasoningResult, policy: PolicyResult) -> None:
        if result.recommended_action not in policy.allowed_actions:
            raise ValueError("Reasoning output recommended an action outside policy.allowed_actions.")

    def _fallback(
        self,
        case: DecisionCase,
        risk: RiskAssessment,
        policy: PolicyResult,
        guardrail: GuardrailResult,
    ) -> ReasoningResult:
        action = self._fallback_action(policy)
        rationale = self._fallback_rationale(risk=risk, policy=policy, guardrail=guardrail)
        evidence = self._fallback_evidence(case=case, guardrail=guardrail)

        return ReasoningResult(
            summary=self._fallback_summary(case=case, risk=risk, action=action),
            rationale=rationale,
            evidence=evidence,
            recommended_action=action,
            confidence=min(risk.confidence, case.physical_evidence.prediction_confidence),
            operational_severity=self._severity_for(risk.risk_level),
        )

    def _fallback_action(self, policy: PolicyResult) -> ActionType:
        if policy.allowed_actions:
            return policy.allowed_actions[0]
        return ActionType.ESCALATE

    def _fallback_rationale(
        self,
        risk: RiskAssessment,
        policy: PolicyResult,
        guardrail: GuardrailResult,
    ) -> list[str]:
        rationale = list(risk.contributing_factors[:3])
        if not rationale:
            rationale.append("Recommendation derived from risk level and policy constraints.")

        rationale.extend(policy.policy_notes[:2])

        if not guardrail.passed:
            rationale.extend(guardrail.blocking_reasons[:2])

        return rationale

    def _fallback_evidence(self, case: DecisionCase, guardrail: GuardrailResult) -> list[str]:
        evidence: list[str] = []

        failure_probability = case.physical_evidence.failure_horizon_probability
        if failure_probability is not None:
            evidence.append(f"failure_horizon_probability={failure_probability:.2f}")

        rul_hours = case.physical_evidence.rul_estimate_hours
        if rul_hours is not None:
            evidence.append(f"rul_estimate_hours={rul_hours:.1f}")

        evidence.extend(guardrail.warnings[:2])
        return evidence

    def _fallback_summary(self, case: DecisionCase, risk: RiskAssessment, action: ActionType) -> str:
        return (
            f"Risk is {risk.risk_level.value}; "
            f"asset criticality is {case.business_context.asset_criticality.value}; "
            f"recommended action is {action.value} within current policy constraints."
        )

    def _severity_for(self, risk_level: RiskLevel) -> OperationalSeverity:
        mapping = {
            RiskLevel.LOW: OperationalSeverity.LOW,
            RiskLevel.MEDIUM: OperationalSeverity.MEDIUM,
            RiskLevel.HIGH: OperationalSeverity.HIGH,
            RiskLevel.CRITICAL: OperationalSeverity.HIGH,
        }
        return mapping[risk_level]