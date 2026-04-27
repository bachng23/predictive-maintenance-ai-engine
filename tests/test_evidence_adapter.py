import pytest
from pydantic import ValidationError

from ai_engine.modeling.evidence_adapter import ModelEvidenceAdapter
from ai_engine.schemas.enums import DataQualityLevel, DriftStatus, FeatureDirection, SignalTrend


def build_payload() -> dict:
    return {
        "health_score": 0.42,
        "anomaly_score": 0.78,
        "failure_horizon_probability": 0.61,
        "rul_estimate_hours": 120.0,
        "prediction_confidence": 0.84,
        "signal_quality_score": 0.93,
        "data_completeness_score": 0.88,
        "drift_score": 0.17,
        "recent_signal_trend": "degrading",
        "data_quality_status": "ok",
        "drift_status": "warning",
        "top_feature_attributions": [
            {
                "feature_name": "vibration_rms",
                "importance": 0.31,
                "direction": "increase_risk",
            }
        ],
        "evidence_notes": ["Converted from model output."],
    }


def test_adapter_converts_model_payload_to_physical_evidence() -> None:
    adapter = ModelEvidenceAdapter()

    evidence = adapter.to_physical_evidence(build_payload())

    assert evidence.health_score == 0.42
    assert evidence.anomaly_score == 0.78
    assert evidence.recent_signal_trend == SignalTrend.DEGRADING
    assert evidence.data_quality_status == DataQualityLevel.OK
    assert evidence.drift_status == DriftStatus.WARNING
    assert evidence.top_feature_attributions[0].feature_name == "vibration_rms"
    assert evidence.top_feature_attributions[0].direction == FeatureDirection.INCREASE_RISK


def test_adapter_rejects_invalid_probability() -> None:
    adapter = ModelEvidenceAdapter()
    payload = build_payload()
    payload["failure_horizon_probability"] = 1.5

    with pytest.raises(ValidationError):
        adapter.to_physical_evidence(payload)


def test_adapter_rejects_unknown_trend() -> None:
    adapter = ModelEvidenceAdapter()
    payload = build_payload()
    payload["recent_signal_trend"] = "getting_weird"

    with pytest.raises(ValidationError):
        adapter.to_physical_evidence(payload)
