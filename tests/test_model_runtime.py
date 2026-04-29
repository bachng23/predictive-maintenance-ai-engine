from ai_engine.modeling.contracts import ModelOutput
from ai_engine.modeling.evidence_adapter import ModelEvidenceAdapter
from ai_engine.modeling.runtime import MockModelRuntime, ModelInput, ModelPrediction, ModelRuntime
from ai_engine.schemas.evidence import PhysicalEvidence


def test_mock_model_runtime_returns_model_prediction() -> None:
    runtime: ModelRuntime = MockModelRuntime()

    prediction = runtime.predict(
        ModelInput(
            features={
                "vibration_rms": 6.0,
                "temperature_mean": 80.0,
            },
            metadata={
                "asset_id": "asset-001",
                "feature_set_version": "features-v1",
            },
        )
    )

    assert isinstance(prediction, ModelPrediction)
    assert isinstance(prediction, ModelOutput)
    assert prediction.anomaly_score is not None
    assert 0.0 <= prediction.anomaly_score <= 1.0
    assert prediction.failure_horizon_probability is not None
    assert 0.0 <= prediction.failure_horizon_probability <= 1.0
    assert prediction.inference_context.horizon_hours == 72.0
    assert prediction.inference_context.model_name == "mock_runtime"


def test_model_prediction_can_flow_through_evidence_adapter() -> None:
    runtime = MockModelRuntime()
    adapter = ModelEvidenceAdapter()

    prediction = runtime.predict(
        ModelInput(
            features={
                "vibration_rms": 7.5,
                "temperature_mean": 85.0,
            }
        )
    )

    evidence = adapter.to_physical_evidence(prediction.to_evidence_payload())

    assert isinstance(evidence, PhysicalEvidence)
    assert evidence.anomaly_score == prediction.anomaly_score
    assert evidence.failure_horizon_probability == prediction.failure_horizon_probability
    assert evidence.top_feature_attributions[0].feature_name == "vibration_rms"
