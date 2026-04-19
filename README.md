# Risk-Aware AI Decision Engine for Predictive Maintenance

A decision-centric AI engine for predictive maintenance that combines risk scoring, policy enforcement, guardrails, and LLM-based reasoning to generate structured maintenance recommendations for industrial environments.

## Overview

Modern predictive maintenance systems are good at detecting anomalies, but they often stop at alerts, scores, or dashboards. In practice, engineers and operators need more than anomaly signals — they need actionable, explainable, and policy-aware recommendations.

This project focuses on the AI core of that problem.

It implements a **risk-aware decision engine** that takes an industrial maintenance case, normalizes it into a structured state, evaluates risk, applies business and safety policies, runs guardrails, and produces a final recommendation with reasoning.

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

1. deterministic logic
2. policy and safety constraints
3. AI reasoning
4. orchestration of the end-to-end workflow

## Project Goal

The goal of this project is to build a modular AI decision engine for predictive maintenance that can:

- ingest and normalize maintenance cases
- assess risk using mock, rule-based, or future ML-based adapters
- apply deterministic policy rules
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
- replace mock risk engine with a real ML model adapter
- add human-in-the-loop approval flow
- add specialized safety / maintenance / operations agents
- add observability dashboard
- add API and web integration

## Architecture

The system is intentionally designed in three layers.

### 1. Deterministic Core
Responsible for the stable decision backbone:
- input normalization
- risk assessment
- policy checks
- safety and output guardrails

### 2. AI Reasoning Layer
Responsible for:
- case interpretation
- explanation generation
- rationale synthesis
- translating technical state into human-readable recommendations

### 3. Orchestration Layer
Responsible for:
- state flow
- node execution
- routing
- blocked vs. pass paths
- finalization of output

The orchestration layer uses **LangGraph** as a state machine for the decision workflow.

## Design Principles

This project follows a few core engineering principles:

- **Decision-centric, not chatbot-centric**
- **Deterministic core before AI reasoning**
- **LLM as reasoning layer, not sole source of truth**
- **Policies must be explicit and auditable**
- **Guardrails must exist from the beginning**
- **Vertical slice first, platform later**
- **Mock/demo stability before production complexity**

## High-Level Workflow

```text
START
-> ingest_case
-> normalize_case
-> assess_risk
-> evaluate_policy
-> run_guardrails
   -> if blocked: finalize_blocked
   -> else: generate_reasoning
-> compose_decision
-> finalize
-> END
