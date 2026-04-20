# Risk-Aware AI Decision Engine for Predictive Maintenance

A decision-centric AI engine for predictive maintenance that combines model-driven risk interpretation, policy enforcement, guardrails, and LLM reasoning to generate structured maintenance recommendations for industrial environments.

## Overview

Modern predictive maintenance systems are good at detecting anomalies, but they often stop at alerts, scores, or dashboards. In practice, engineers and operators need more than anomaly signals — they need actionable, explainable, and policy-aware recommendations.

This project focuses on the AI core of that problem.

It implements a **risk-aware decision engine** that takes an industrial maintenance case, normalizes it into a structured state, evaluates risk, generates reasoning, applies business and safety constraints, and produces a final recommendation with traceable rationale.

The system is designed as an **AI engineering project**, not as a generic chatbot. Its center is a structured decision workflow rather than conversational prompting.

## Problem Statement

In industrial environments, predictive maintenance signals alone are often not enough to support reliable operational decisions.

Typical challenges include:

- anomaly outputs that do not map clearly to recommended actions
- inconsistent decision-making across different cases
- lack of explainability for maintenance recommendations
- no explicit enforcement of business, safety, or approval policies
- difficulty integrating AI reasoning with deterministic constraints

This project addresses those issues by building a structured decision engine that separates:

1. input and state contracts
2. intelligence and reasoning
3. policy and safety constraints
4. orchestration of the end-to-end workflow

## Project Goal

The goal of this project is to build a modular AI decision engine for predictive maintenance that can:

- ingest and normalize maintenance cases
- assess risk through replaceable model-oriented adapters
- apply deterministic policy rules as constraints
- enforce safety and output guardrails
- generate explainable reasoning with an LLM
- produce a structured final decision

## Scope

### Current scope
- decision-centric AI engine
- CLI-based MVP
- LangGraph orchestration
- mock/demo scenarios
- policy engine
- guardrail layer
- structured reasoning output
- final decision composer
- evaluation-ready architecture

### Planned extensions
- replace baseline risk adapter with a stronger ML or external model adapter
- add human-in-the-loop approval flow
- add specialized safety / maintenance / operations agents
- add observability dashboard
- add API and web integration

Implementation planning lives in [docs/phase0_doc.md](/Users/bachng/Coding/predictive-maintenance-ai-engine/docs/phase0_doc.md) and [docs/implementation_roadmap.md](/Users/bachng/Coding/predictive-maintenance-ai-engine/docs/implementation_roadmap.md).

## Architecture

The system is intentionally designed in four layers.

### 1. Contract Layer
Responsible for:
- input validation
- normalized state contracts
- typed output schemas

### 2. Intelligence Layer
Responsible for:
- risk interpretation
- recommendation candidate generation
- explainable reasoning

### 3. Constraint Layer
Responsible for:
- policy checks
- safety and output guardrails
- approval constraints

### 4. Orchestration Layer
Responsible for:
- state flow
- node execution
- routing
- trace generation
- finalization of output

The orchestration layer uses **LangGraph** as a state machine for the decision workflow.

## Design Principles

This project follows a few core engineering principles:

- **Decision-centric, not chatbot-centric**
- **Typed contracts before orchestration complexity**
- **Model-driven intelligence, not rule tables as the core engine**
- **LLM as reasoning layer, not sole source of truth**
- **Policies must be explicit and auditable**
- **Guardrails must exist from the beginning**
- **Vertical slice first, platform later**
- **MVP scope can be small, but architecture quality should stay high**

## High-Level Workflow

```text
START
-> ingest_case
-> normalize_case
-> assess_risk
-> generate_reasoning
-> evaluate_policy
-> run_guardrails
   -> if blocked: finalize_blocked
   -> else: compose_decision
-> finalize
-> END
