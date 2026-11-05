# Uncertainty–Correctness Mismatch

## Problem

Uncertainty and correctness are related, but they are not equivalent.

An agent can be:

| Uncertainty | Correctness | Case |
|---|---|---|
| High | Error | High-U + Error |
| High | Correct | High-U + Correct |
| Low | Error | Low-U + Error |
| Low | Correct | Low-U + Correct |

Therefore:

> **High uncertainty does not necessarily mean failure, and low uncertainty does not guarantee correctness.**

## Research Question

The important question is not simply:

> Can uncertainty predict agent errors?

Instead:

> **When is uncertainty informative about correctness, when is it misleading, and what mechanisms explain the mismatch?**

## Why This Matters

Consider:

### High-U + Error

The agent recognized difficulty but still failed.

Possible mechanisms:
- Conflicting evidence
- Tool failure
- Insufficient information
- Poor planning
- Incorrect action selection

### High-U + Correct

The agent was uncertain but still succeeded.

Possible mechanisms:
- Effective verification
- Redundant evidence
- Safe decision-making
- Recovery after uncertainty

### Low-U + Error

The agent was confidently wrong.

Possible mechanisms:
- Misleading evidence
- Overconfidence
- Retrieval failure
- Incorrect assumptions
- Tool misuse

### Low-U + Correct

The agent was confident and successful.

Possible mechanisms:
- Strong evidence
- Reliable tool result
- Well-grounded decision
- Stable state

## Proposed Analysis

For each agent trajectory:

`Step → Uncertainty → Action → Outcome`

Classify individual steps into the four uncertainty–correctness cases.

Then compare:

- Frequency of each case
- Error rates
- Trajectory position
- Tool/action types
- Evidence conditions
- Failure mechanisms

## Explainability Layer

Use trajectory/explainability methods to generate candidate mechanisms for each case.

Example:

`Low-U + Error`

→ explanation suggests misleading retrieval

→ intervene on retrieved evidence

→ re-run agent

→ compare behavior

This allows the explanation to be treated as a **testable hypothesis** rather than ground truth.

## Validation

The proposed mechanism is tested using:

`Candidate factor → Controlled intervention → Re-execution → Behavioral comparison`

Relevant outcomes include:

- Action change
- Error reduction
- Trajectory divergence
- Final outcome change

## Research Objective

> **Characterize uncertainty–correctness mismatch across multi-step tool-using agent trajectories and investigate the mechanisms responsible for each mismatch pattern using explainability and controlled intervention.**

## Core Pipeline

`Per-step UQ`
→ `Four uncertainty–correctness cases`
→ `Mechanism identification`
→ `Controlled intervention`
→ `Behavioral validation`

## Important Boundary

The objective is **not** to prove a single true causal mechanism.

The objective is to:

> **Identify and validate behaviorally relevant mechanisms that help explain why uncertainty is informative in some cases and misleading in others.**