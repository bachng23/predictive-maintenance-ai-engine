from ai_engine.modeling.contracts import ModelFeatureAttribution, ModelOutput
from ai_engine.schemas.evidence import FeatureAttribution, PhysicalEvidence


class ModelEvidencePayload(ModelOutput):
    """Backward-compatible alias for the model-to-evidence contract."""


class ModelEvidenceAdapter:
    def to_model_output(self, payload: ModelOutput | dict) -> ModelOutput:
        return ModelOutput.model_validate(payload)

    def to_physical_evidence(self, payload: ModelOutput | dict) -> PhysicalEvidence:
        model_payload = self.to_model_output(payload)

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
