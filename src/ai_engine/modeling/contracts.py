from __future__ import annotations

from pydantic import BaseModel, Field

from ai_engine.schemas.enums import DataQualityLevel, DriftStatus, FeatureDirection, SignalTrend


class ModelFeatureAttribution(BaseModel):
    feature_name: str = Field(..., description="Name of the model feature.")
    importance: float = Field(..., description="Relative feature contribution score.")
    direction: FeatureDirection = Field(..., description="Direction of feature contribution to risk.")


class InferenceContext(BaseModel):
    horizon_hours: float | None = Field(
        None,
        ge=0.0,
        description="Prediction horizon in hours used for failure probability output.",
    )
    model_name: str | None = Field(None, description="Logical model family or experiment name.")
    model_version: str | None = Field(None, description="Version of the model artifact used for inference.")
    feature_set_version: str | None = Field(None, description="Version of the feature set used for inference.")
    inference_notes: list[str] = Field(
        default_factory=list,
        description="Additional notes about how this inference was produced.",
    )


class ModelOutput(BaseModel):
    health_score: float | None = Field(None, ge=0.0, le=1.0, description="Model-derived health score.")
    anomaly_score: float | None = Field(None, ge=0.0, le=1.0, description="Model-derived anomaly score.")
    failure_horizon_probability: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Predicted probability of failure within the configured horizon.",
    )
    rul_estimate_hours: float | None = Field(
        None,
        ge=0.0,
        description="Estimated remaining useful life in hours.",
    )
    prediction_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence of the model output.")
    signal_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of input signals.")
    data_completeness_score: float = Field(..., ge=0.0, le=1.0, description="Completeness score of model inputs.")
    drift_score: float | None = Field(None, ge=0.0, le=1.0, description="Optional distribution drift score.")
    recent_signal_trend: SignalTrend = Field(..., description="Recent trend inferred from input signals.")
    data_quality_status: DataQualityLevel = Field(..., description="Data quality status used by decision logic.")
    drift_status: DriftStatus = Field(..., description="Drift status used by decision logic.")
    top_feature_attributions: list[ModelFeatureAttribution] = Field(
        default_factory=list,
        description="Top feature attributions explaining the prediction.",
    )
    evidence_notes: list[str] = Field(
        default_factory=list,
        description="Short notes describing evidence or model behavior.",
    )
    inference_context: InferenceContext = Field(
        default_factory=InferenceContext,
        description="Inference metadata that helps trace how the output was produced.",
    )
