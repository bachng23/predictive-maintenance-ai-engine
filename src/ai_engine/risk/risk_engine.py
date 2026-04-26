from __future__ import annotations

from dataclasses import dataclass

from ai_engine.schemas.decision import RiskAssessment
from ai_engine.schemas.enums import ActionType, RiskLevel
from ai_engine.schemas.evidence import PhysicalEvidence


@dataclass(slots=True)
class RiskEngineConfig:
    low_threshold: float = 0.30
    medium_threshold: float = 0.60
    high_threshold: float = 0.80


class RiskEngine:
    def __init__(self, config: RiskEngineConfig | None = None) -> None:
        self.config = config or RiskEngineConfig()

    def assess(self, evidence: PhysicalEvidence) -> RiskAssessment:
        score = self._score(evidence)
        risk_level = self._map_risk_level(score)
        return RiskAssessment(
            risk_level=risk_level,
            confidence=evidence.prediction_confidence,
            contributing_factors=self._build_contributing_factors(evidence),
            recommended_actions=self._recommended_actions_for(risk_level),
        )

    def _score(self, evidence: PhysicalEvidence) -> float:
        weighted_values = [
            evidence.anomaly_score or 0.0,
            evidence.failure_horizon_probability or 0.0,
            1.0 - (evidence.health_score or 1.0),
        ]
        return sum(weighted_values) / len(weighted_values)

    def _map_risk_level(self, score: float) -> RiskLevel:
        if score >= self.config.high_threshold:
            return RiskLevel.CRITICAL
        if score >= self.config.medium_threshold:
            return RiskLevel.HIGH
        if score >= self.config.low_threshold:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _build_contributing_factors(self, evidence: PhysicalEvidence) -> list[str]:
        factors: list[str] = []
        if evidence.anomaly_score is not None and evidence.anomaly_score >= self.config.medium_threshold:
            factors.append("Anomaly score exceeds the medium-risk threshold.")
        if (
            evidence.failure_horizon_probability is not None
            and evidence.failure_horizon_probability >= self.config.medium_threshold
        ):
            factors.append("Failure horizon probability indicates elevated near-term risk.")
        if evidence.rul_estimate_hours is not None and evidence.rul_estimate_hours <= 72.0:
            factors.append("Estimated remaining useful life is below 72 hours.")
        if evidence.drift_status.value != "none":
            factors.append("Input distribution shows measurable drift.")
        return factors

    def _recommended_actions_for(self, risk_level: RiskLevel) -> list[ActionType]:
        action_map = {
            RiskLevel.LOW: [ActionType.RUN],
            RiskLevel.MEDIUM: [ActionType.RUN_WITH_MONITORING, ActionType.INSPECT],
            RiskLevel.HIGH: [ActionType.INSPECT, ActionType.PLAN_MAINTENANCE, ActionType.ESCALATE],
            RiskLevel.CRITICAL: [ActionType.ESCALATE, ActionType.CONTROLLED_STOP],
        }
        return action_map[risk_level]
