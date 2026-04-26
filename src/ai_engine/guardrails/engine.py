from ai_engine.schemas.case import DecisionCase
from ai_engine.schemas.decision import GuardrailResult, PolicyResult
from ai_engine.guardrails.post_checks import run_post_checks
from ai_engine.guardrails.pre_checks import run_pre_checks


class GuardrailEngine:
    def evaluate(self, case: DecisionCase, policy_result: PolicyResult) -> GuardrailResult:
        pre_blocking, pre_warnings = run_pre_checks(case, policy_result)
        post_blocking, post_warnings = run_post_checks(case, policy_result)

        blocking_reasons = pre_blocking + post_blocking
        warnings = pre_warnings + post_warnings

        return GuardrailResult(
            passed=len(blocking_reasons) == 0,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
        )
