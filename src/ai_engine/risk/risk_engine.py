from __future__ import annotations

from dataclasses import dataclass, field

from ai_engine.schemas.case import NormalizedCase
from ai_engine.schemas.decision import RiskAssessment
from ai_engine.schemas.enums import RiskLevel, ActionType, OperationalSeverity

@dataclass(slots=True)
class RiskEngineConfig:
    signal_value_map: dict[str, float] = field(
        default_factory=lambda: {
            "stable": 0.05,
            "normal": 0.10,
            "good": 0.10,
            "slightly_increasing": 0.45,
            "slightly_high": 0.45,
            "abnormal": 0.55,
            "degrading": 0.50,
            "high": 0.85,
            "overheating": 0.95,
            "severe": 0.95,
            "poor": 0.85,
        }
    )

    severity_map: dict[OperationalSeverity, float] = field(
        default_factory=lambda: {
            OperationalSeverity.LOW: 0.15,
            OperationalSeverity.MEDIUM: 0.45,
            OperationalSeverity.HIGH: 0.80,
        }
    )
    
    low_threshold: float = 0.3
    medium_threshold: float = 0.6
    high_threshold: float = 0.8


class RiskEngine:
    def __init__(self, config: RiskEngineConfig | None = None):
        self.config = config or RiskEngineConfig()

    def assess(self, normalized_case: NormalizedCase) -> RiskAssessment:
        evidence = self._extract_evidence(normalized_case)
        score = self._score(evidence)
        risk_level = self._map_risk_level(score)
        confidence = self._calculate_confidence(score, normalized_case)
        contributing_factors = self.build_contributing_factors(evidence, normalized_case, score)
        recommended_actions = self._recommended_actions_for(risk_level)

        return RiskAssessment(
            risk_level=risk_level,
            confidence=confidence,
            contributing_factors=contributing_factors,
            recommended_actions=recommended_actions,
        )
    
    def _extract_evidence(self, normalized_case: NormalizedCase) -> dict[str, float]:
        signal_scores = []

        for value in normalized_case.detected_signals.values():
            signal_scores.append(self.config.signal_value_map.get(value.strip().lower(), 0.40))
        
        signal_score = sum(signal_scores) / len