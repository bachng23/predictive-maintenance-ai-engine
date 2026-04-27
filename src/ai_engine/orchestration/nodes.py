from __future__ import annotations

from ai_engine.decision.composer import DecisionComposer
from ai_engine.policy.engine import PolicyEngine
from ai_engine.risk.risk_engine import RiskEngine
from ai_engine.guardrails.engine import GuardrailEngine
from ai_engine.reasoning.engine import ReasoningEngine
from ai_engine.schemas.state import DecisionState

risk_engine = RiskEngine()
policy_engine = PolicyEngine()
guardrails_engine = GuardrailEngine()
reasoning_engine = ReasoningEngine()
composer = DecisionComposer()

def assess_risk_node(state: DecisionState) -> dict:
    risk = risk_engine.assess(state.case.physical_evidence)
    return {"risk": risk}
    
def evaluate_policy_node(state: DecisionState) -> dict:
    if state.risk is None:
        raise ValueError("Risk assessment is required before policy evaluation.")

    policy = policy_engine.evaluate(state.case, state.risk.risk_level)
    return {"policy": policy}

def run_guardrails_node(state: DecisionState) -> dict:
    if state.policy is None:
        raise ValueError("Policy result is required before guardrail evaluation.")

    guardrail = guardrails_engine.evaluate(state.case, state.policy)
    return {"guardrail": guardrail}

def reasoning_node(state: DecisionState) -> dict:
    if state.risk is None or state.policy is None or state.guardrail is None:
        raise ValueError("Risk assessment, policy result, and guardrail result are all required before reasoning.")

    reasoning = reasoning_engine.generate(
        case=state.case,
        risk=state.risk,
        policy=state.policy,
        guardrail=state.guardrail,
    )
    return {"reasoning": reasoning}

def compose_decision_node(state: DecisionState) -> dict:
    if state.risk is None or state.policy is None or state.guardrail is None:
        raise ValueError("Risk assessment, policy result, and guardrail result are all required before composing final decision.")

    recommendation, final_decision = composer.compose(
        case=state.case,
        risk=state.risk,
        policy=state.policy,
        guardrail=state.guardrail,
        reasoning=state.reasoning
    )

    updated_case = state.case.model_copy(
        update={"manager_recommendation": recommendation}
    )

    return {
        "case": updated_case,
        "final_decision": final_decision,
    }
