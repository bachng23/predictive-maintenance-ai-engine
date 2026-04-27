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

graph = StateGraph(DecisionState)

graph.add_node("assess_risk", assess_risk_node)
graph.add_node("evaluate_policy", evaluate_policy_node)
graph.add_node("run_guardrails", run_guardrails_node)
graph.add_node("generate_reasoning", reasoning_node)
graph.add_node("compose_decision", compose_decision_node)

graph.add_edge(START, "assess_risk")
graph.add_edge("assess_risk", "evaluate_policy")
graph.add_edge("evaluate_policy", "run_guardrails")
graph.add_edge("run_guardrails", "generate_reasoning")
graph.add_edge("generate_reasoning", "compose_decision")
graph.add_edge("run_guardrails", "compose_decision")
graph.add_edge("compose_decision", END)

graph.compile()



