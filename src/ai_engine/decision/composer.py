from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import (
    ApprovalState,
    DecisionRecommendation,
    FinalDecision,
    GuardrailResult,
    PolicyResult,
    ReasoningResult,
    RiskAssessment,
)
from ai_engine.schemas.enums import ActionType, ApprovalStatus, PriorityLevel, RiskLevel


class DecisionComposer:
    def compose(
        self,
        case: DecisionCase,
        risk: RiskAssessment,
        policy: PolicyResult,
        guardrail: GuardrailResult,
        reasoning: ReasoningResult | None = None,
    ) -> tuple[DecisionRecommendation, FinalDecision]:
        if not guardrail.passed:
            return self._compose_blocked_decision(case, risk, policy, guardrail)

        recommended_action = self._select_action(policy, reasoning)
        recommendation = self._build_recommendation(
            recommended_action=recommended_action,
            policy=policy,
            guardrail=guardrail,
            reasoning=reasoning,
        )
        final_decision = self._build_final_decision(
            risk=risk,
            recommended_action=recommended_action,
            case=case,
            policy=policy,
            recommendation=recommendation,
            guardrail=guardrail,
        )
        return recommendation, final_decision

    def _compose_blocked_decision(
        self,
        case: DecisionCase,
        risk: RiskAssessment,
        policy: PolicyResult,
        guardrail: GuardrailResult,
    ) -> tuple[DecisionRecommendation, FinalDecision]:
        recommendation = DecisionRecommendation(
            recommended_action=ActionType.ESCALATE,
            rationale=["Guardrails blocked direct execution for this case."],
            evidence_used=guardrail.blocking_reasons,
            unresolved_assumptions=["Human review is required before any action is taken."],
        )

        final_decision = FinalDecision(
            risk_level=risk.risk_level,
            action=ActionType.ESCALATE,
            priority=self._priority_for(risk.risk_level),
            approval_status=ApprovalStatus.BLOCKED,
            decision_notes=policy.policy_notes + guardrail.blocking_reasons,
            rationale=recommendation.rationale,
            evidence=guardrail.blocking_reasons,
            next_steps=[
                "Review blocking reasons.",
                "Escalate to supervisor or reliability engineer.",
            ],
        )
        return recommendation, final_decision

    def _select_action(
        self,
        policy: PolicyResult,
        reasoning: ReasoningResult | None,
    ) -> ActionType:
        if reasoning is not None and reasoning.recommended_action in policy.allowed_actions:
            return reasoning.recommended_action

        if policy.allowed_actions:
            return policy.allowed_actions[0]

        return ActionType.ESCALATE

    def _build_recommendation(
        self,
        recommended_action: ActionType,
        policy: PolicyResult,
        guardrail: GuardrailResult,
        reasoning: ReasoningResult | None,
    ) -> DecisionRecommendation:
        if reasoning is not None:
            rationale = list(reasoning.rationale)
            evidence_used = list(reasoning.evidence)
        else:
            rationale = ["Recommendation derived from policy-ranked allowed actions."]
            evidence_used = []

        unresolved_assumptions = []
        if policy.requires_human_approval:
            unresolved_assumptions.append("Human approval is required before execution.")
        if guardrail.warnings:
            unresolved_assumptions.extend(guardrail.warnings)

        return DecisionRecommendation(
            recommended_action=recommended_action,
            rationale=rationale,
            evidence_used=evidence_used,
            unresolved_assumptions=unresolved_assumptions,
        )

    def _build_final_decision(
        self,
        risk: RiskAssessment,
        recommended_action: ActionType,
        case: DecisionCase,
        policy: PolicyResult,
        recommendation: DecisionRecommendation,
        guardrail: GuardrailResult,
    ) -> FinalDecision:
        approval_status = self._approval_status_for(case.approval_state, policy)

        decision_notes = list(policy.policy_notes)
        if guardrail.warnings:
            decision_notes.extend(guardrail.warnings)

        next_steps = self._next_steps_for(recommended_action, approval_status)

        return FinalDecision(
            risk_level=risk.risk_level,
            action=recommended_action,
            priority=self._priority_for(risk.risk_level),
            approval_status=approval_status,
            decision_notes=decision_notes,
            rationale=recommendation.rationale,
            evidence=recommendation.evidence_used,
            next_steps=next_steps,
        )

    def _approval_status_for(
        self,
        approval_state: ApprovalState,
        policy: PolicyResult,
    ) -> ApprovalStatus:
        if approval_state.status == ApprovalStatus.APPROVED:
            return ApprovalStatus.APPROVED
        if approval_state.status == ApprovalStatus.REJECTED:
            return ApprovalStatus.REJECTED
        if approval_state.status == ApprovalStatus.BLOCKED:
            return ApprovalStatus.BLOCKED
        if policy.requires_human_approval:
            return ApprovalStatus.PENDING
        return ApprovalStatus.NOT_REQUIRED

    def _priority_for(self, risk_level: RiskLevel) -> PriorityLevel:
        mapping = {
            RiskLevel.LOW: PriorityLevel.LOW,
            RiskLevel.MEDIUM: PriorityLevel.MEDIUM,
            RiskLevel.HIGH: PriorityLevel.HIGH,
            RiskLevel.CRITICAL: PriorityLevel.URGENT,
        }
        return mapping[risk_level]

    def _next_steps_for(
        self,
        action: ActionType,
        approval_status: ApprovalStatus,
    ) -> list[str]:
        steps_by_action = {
            ActionType.RUN: [
                "Continue normal operation.",
                "Monitor on the next scheduled cycle.",
            ],
            ActionType.RUN_WITH_MONITORING: [
                "Continue operation with increased monitoring frequency.",
                "Re-evaluate the case after the next data window.",
            ],
            ActionType.INSPECT: [
                "Schedule an inspection at the earliest feasible slot.",
                "Record findings in the maintenance log.",
            ],
            ActionType.PLAN_MAINTENANCE: [
                "Prepare planned maintenance work order.",
                "Confirm spare parts and technician availability.",
            ],
            ActionType.ESCALATE: [
                "Escalate the case to a supervisor or reliability engineer.",
                "Review business and safety constraints before execution.",
            ],
            ActionType.CONTROLLED_STOP: [
                "Prepare controlled stop procedure.",
                "Coordinate operations, maintenance, and supervision teams.",
            ],
        }

        steps = list(steps_by_action[action])

        if approval_status == ApprovalStatus.PENDING:
            steps.insert(0, "Obtain required human approval before execution.")
        if approval_status == ApprovalStatus.REJECTED:
            steps.insert(0, "Reassess the case after rejection and provide an alternative action.")

        return steps
