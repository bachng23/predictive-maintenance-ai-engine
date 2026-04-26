from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import PolicyResult
from ai_engine.schemas.enums import ActionType


def run_post_checks(case: DecisionCase, policy_result: PolicyResult) -> tuple[list[str], list[str]]:
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    business = case.business_context

    if (
        ActionType.PLAN_MAINTENANCE in policy_result.allowed_actions
        and business.maintenance_window_available is False
    ):
        blocking_reasons.append("Planned maintenance is allowed but no maintenance window is available.")

    if business.shift_restriction:
        warnings.append(f"Shift restriction in effect: {business.shift_restriction}")

    if not policy_result.allowed_actions:
        blocking_reasons.append("No policy-allowed actions remain after evaluation.")

    return blocking_reasons, warnings
