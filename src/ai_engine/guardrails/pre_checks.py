from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import PolicyResult
from ai_engine.schemas.enums import ActionType, ApprovalStatus, DataQualityLevel, DriftStatus


def run_pre_checks(case: DecisionCase, policy_result: PolicyResult) -> tuple[list[str], list[str]]:
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    evidence = case.physical_evidence
    approval = case.approval_state

    if evidence.data_quality_status is DataQualityLevel.SEVERE:
        blocking_reasons.append("Data quality is severe; execution should not proceed.")

    if evidence.prediction_confidence < 0.50:
        blocking_reasons.append("Prediction confidence is below the hard execution threshold.")
    elif evidence.prediction_confidence < 0.65:
        warnings.append("Prediction confidence is low; human review is strongly recommended.")

    if evidence.drift_status is DriftStatus.SEVERE:
        blocking_reasons.append("Severe drift detected; execution should pause pending review.")
    elif evidence.drift_status is DriftStatus.WARNING:
        warnings.append("Warning-level drift detected in current input distribution.")

    if (
        ActionType.CONTROLLED_STOP in policy_result.allowed_actions
        and approval.status is not ApprovalStatus.APPROVED
    ):
        blocking_reasons.append("Controlled stop requires explicit approval before execution.")

    return blocking_reasons, warnings
