from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import PolicyResult
from ai_engine.schemas.enums import (
    ActionType,
    AvailabilityStatus,
    CriticalityLevel,
    DataQualityLevel,
    DriftStatus,
    RiskLevel,
)


class PolicyEngine:
    def __init__(self, policy_path: str | Path | None = None) -> None:
        default_path = Path(__file__).resolve().parent / "policies.yaml"
        self.policy_path = Path(policy_path) if policy_path is not None else default_path
        self.config = self._load_config()

    def evaluate(self, case: DecisionCase, risk_level: RiskLevel) -> PolicyResult:
        base_allowed = self._base_actions_for_risk(risk_level)
        blocked_actions: set[ActionType] = set()
        policy_notes: list[str] = []

        evidence = case.physical_evidence
        business = case.business_context

        if evidence.data_quality_status is DataQualityLevel.SEVERE:
            blocked_actions.update(self._actions_from_config("severe_data_quality_blocks"))
            policy_notes.append("Severe data quality blocks run and high-impact actions.")

        if evidence.drift_status is DriftStatus.SEVERE:
            blocked_actions.update(self._actions_from_config("severe_drift_blocks"))
            policy_notes.append("Severe drift reduces trust in continued running or stop actions.")

        low_confidence_threshold = float(self.config["thresholds"]["low_confidence"])
        if evidence.prediction_confidence < low_confidence_threshold:
            blocked_actions.update(self._actions_from_config("low_confidence_blocks"))
            policy_notes.append("Low model confidence blocks stronger maintenance actions.")

        if not business.maintenance_window_available:
            blocked_actions.add(ActionType.PLAN_MAINTENANCE)
            policy_notes.append("No maintenance window is currently available.")

        if business.technician_availability is AvailabilityStatus.UNAVAILABLE:
            blocked_actions.add(ActionType.PLAN_MAINTENANCE)
            policy_notes.append("Technician availability does not support planned maintenance now.")

        if business.spare_availability is AvailabilityStatus.UNAVAILABLE:
            blocked_actions.add(ActionType.PLAN_MAINTENANCE)
            policy_notes.append("Spare availability does not support planned maintenance now.")

        allowed_actions = [action for action in base_allowed if action not in blocked_actions]

        if not allowed_actions:
            allowed_actions = [ActionType.ESCALATE]
            policy_notes.append("All candidate actions were blocked; escalated for human review.")

        requires_human_approval = self._requires_human_approval(case, allowed_actions)

        return PolicyResult(
            allowed_actions=allowed_actions,
            blocked_actions=sorted(blocked_actions, key=lambda item: item.value),
            requires_human_approval=requires_human_approval,
            policy_notes=policy_notes,
        )

    def _load_config(self) -> dict[str, Any]:
        with self.policy_path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file)

    def _base_actions_for_risk(self, risk_level: RiskLevel) -> list[ActionType]:
        action_names = self.config["action_matrix"][risk_level.value]
        return [ActionType(name) for name in action_names]

    def _actions_from_config(self, key: str) -> set[ActionType]:
        action_names = self.config["blocking_rules"][key]
        return {ActionType(name) for name in action_names}

    def _requires_human_approval(
        self,
        case: DecisionCase,
        allowed_actions: list[ActionType],
    ) -> bool:
        approval_config = self.config["approval"]

        criticality_requires_approval = {
            CriticalityLevel(value)
            for value in approval_config["criticality_requires_approval"]
        }
        actions_require_approval = {
            ActionType(value)
            for value in approval_config["actions_require_approval"]
        }

        if case.business_context.asset_criticality in criticality_requires_approval:
            return True

        return any(action in actions_require_approval for action in allowed_actions)
