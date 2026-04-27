from pydantic import BaseModel, Field

from ai_engine.schemas.enums import DataQualityLevel, DriftStatus, FeatureDirection, SignalTrend
from ai_engine.schemas.evidence import FeatureAttribution, PhysicalEvidence


class ModelFeatureAttribution(BaseModel):
    feature_name: str = Field(..., description="Name of the model feature.")
    importance: float = Field(..., description="Relative feature contribution score.")
    direction: FeatureDirection = Field(..., description="Direction of feature contribution to risk.")


class ModelEvidencePayload(BaseModel):
    health_score: float | None = Field(None, ge=0.0, le=1.0, description="Model-derived health score.")
    anomaly_score: float | None = Field(None, ge=0.0, le=1.0, description="Model-derived anomaly score.")
    failure_horizon_probability: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Predicted probability of failure within the target horizon.",
    )
    rul_estimate_hours: float | None = Field(None, ge=0.0, description="Estimated remaining useful life in hours.")
    prediction_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the model output.")
    signal_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of input signals.")
    data_completeness_score: float = Field(..., ge=0.0, le=1.0, description="Completeness score of model inputs.")
    drift_score: float | None = Field(None, ge=0.0, le=1.0, description="Optional distribution drift score.")
    recent_signal_trend: SignalTrend = Field(..., description="Recent trend inferred from input signals.")
    data_quality_status: DataQualityLevel = Field(..., description="Data quality status used by guardrails.")
    drift_status: DriftStatus = Field(..., description="Drift status used by guardrails.")
    top_feature_attributions: list[ModelFeatureAttribution] = Field(
        default_factory=list,
        description="Top model feature attributions.",
    )
    evidence_notes: list[str] = Field(default_factory=list, description="Notes about model evidence.")


class ModelEvidenceAdapter:
    def to_physical_evidence(self, payload: ModelEvidencePayload | dict) -> PhysicalEvidence:
        model_payload = ModelEvidencePayload.model_validate(payload)

        return PhysicalEvidence(
            health_score=model_payload.health_score,
            anomaly_score=model_payload.anomaly_score,
            failure_horizon_probability=model_payload.failure_horizon_probability,
            rul_estimate_hours=model_payload.rul_estimate_hours,
            prediction_confidence=model_payload.prediction_confidence,
            signal_quality_score=model_payload.signal_quality_score,
            data_completeness_score=model_payload.data_completeness_score,
            drift_score=model_payload.drift_score,
            recent_signal_trend=model_payload.recent_signal_trend,
            data_quality_status=model_payload.data_quality_status,
            drift_status=model_payload.drift_status,
            top_feature_attributions=[
                FeatureAttribution(
                    feature_name=item.feature_name,
                    importance=item.importance,
                    direction=item.direction,
                )
                for item in model_payload.top_feature_attributions
            ],
            evidence_notes=model_payload.evidence_notes,
        )
