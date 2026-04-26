from pydantic import BaseModel, Field

from ai_engine.schemas.enums import DataQualityLevel, DriftStatus, FeatureDirection, SignalTrend


class FeatureAttribution(BaseModel):
    feature_name: str = Field(..., description="Name of the feature contributing to the prediction.")
    importance: float = Field(..., description="Relative contribution score for the feature.")
    direction: FeatureDirection = Field(..., description="Direction of the feature's effect on risk.")


class PhysicalEvidence(BaseModel):
    health_score: float | None = Field(None, ge=0.0, le=1.0, description="Normalized health score for the asset.")
    anomaly_score: float | None = Field(None, ge=0.0, le=1.0, description="Normalized anomaly score for the asset.")
    failure_horizon_probability: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Probability of failure within the configured prediction horizon.",
    )
    rul_estimate_hours: float | None = Field(
        None,
        ge=0.0,
        description="Estimated remaining useful life expressed in hours.",
    )
    prediction_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the model output.")
    signal_quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score of the input signals.")
    data_completeness_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Completeness score of the required input data.",
    )
    drift_score: float | None = Field(None, ge=0.0, le=1.0, description="Distribution shift score for the case.")
    recent_signal_trend: SignalTrend = Field(..., description="Recent trend of the monitored signals.")
    data_quality_status: DataQualityLevel = Field(..., description="Overall quality label for the input data.")
    drift_status: DriftStatus = Field(..., description="Overall drift label for the input data.")
    top_feature_attributions: list[FeatureAttribution] = Field(
        default_factory=list,
        description="Top feature attributions supporting the model output.",
    )
    evidence_notes: list[str] = Field(
        default_factory=list,
        description="Additional notes about the evidence or inference context.",
    )
