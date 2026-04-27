from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from ai_engine.orchestration.nodes import (
    assess_risk_node,
    compose_decision_node,
    evaluate_policy_node,
    reasoning_node,
    run_guardrails_node,
)
from ai_engine.schemas.state import DecisionState

builder = StateGraph(DecisionState)

builder.add_node("assess_risk", assess_risk_node)
builder.add_node("evaluate_policy", evaluate_policy_node)
builder.add_node("run_guardrails", run_guardrails_node)
builder.add_node("generate_reasoning", reasoning_node)
builder.add_node("compose_decision", compose_decision_node)

builder.add_edge(START, "assess_risk")
builder.add_edge("assess_risk", "evaluate_policy")
builder.add_edge("evaluate_policy", "run_guardrails")
builder.add_edge("run_guardrails", "generate_reasoning")
builder.add_edge("generate_reasoning", "compose_decision")
builder.add_edge("compose_decision", END)

graph = builder.compile()


