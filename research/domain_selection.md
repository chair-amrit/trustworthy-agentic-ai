# Domain Selection Analysis

## Purpose

Select an application domain that supports the locked research direction:

> Explainable Analysis of Uncertainty–Correctness Mismatch in Multi-Step Tool-Using Agents

The domain must provide controlled sequential decisions, measurable correctness, reproducible trajectories, and feasible counterfactual intervention.

## Selection Criteria

A suitable domain should provide:

- Multi-step decision-making
- Observable state/action trajectories
- Clear correctness or failure criteria
- Controlled interventions
- Reproducible experiments
- Available simulators/benchmarks
- Feasible computation for a 4-month solo project
- Sufficient research space without unnecessarily narrowing the contribution

## Candidate: Edge–Cloud Task Offloading

A natural formulation is:

`Environment State → Agent Decision → Offloading Action → Execution → Observation → Next State`

Possible state variables include:

- Network bandwidth
- Edge/cloud resource utilization
- Task size
- Queue length
- Latency
- Energy constraints
- Deadline requirements

Correctness can be defined using objective criteria such as:

- Deadline satisfaction
- Constraint satisfaction
- Task completion
- Utility/regret relative to an oracle or reference policy

This makes uncertainty–correctness mismatch measurable.

## Potential Four Cases

| Uncertainty | Outcome | Example |
|---|---|---|
| High | Error | Uncertain offloading decision violates deadline |
| High | Correct | Uncertain decision still satisfies constraints |
| Low | Error | Confident decision causes deadline/resource failure |
| Low | Correct | Confident decision satisfies constraints |

## Explainability and Intervention

A decision can be explained using state variables such as:

`Bandwidth + CPU load + queue + task size + latency`

A candidate mechanism can then be tested by intervention.

Example:

`Original bandwidth → Offload to Cloud → Deadline violation`

`Modified bandwidth → Re-run → Different decision / outcome`

This provides a controlled environment for behavioral validation.

## Agent Architecture Decision

Two main options exist.

### Conventional RL Agent

`State → RL Policy → Action → Environment → Reward`

Advantages:

- Natural fit for edge-cloud offloading
- Efficient execution
- Established simulation literature

Challenges:

- Requires additional RL/UQ methodology
- Explanation is less directly connected to the tool-using-agent framework
- Project becomes more focused on trustworthy RL decision-making

### LLM / Tool-Using Agent

`State → LLM Decision → Tool → Observation → Next Decision`

Advantages:

- Directly matches the current agent-explainability framework
- Explicit multi-step trajectories
- Natural tool interactions
- Easier integration of explanation and counterfactual reasoning

Challenges:

- Higher compute cost
- More stochastic behavior
- More difficult uncertainty estimation/calibration
- Requires a constrained action/tool interface

## Current Assessment

Edge-cloud offloading is a **strong candidate domain** because it offers:

`Controlled Environment + Measurable Outcomes + Sequential Decisions + Reproducible Intervention`

However, the final choice depends on whether the research should use a conventional RL agent or an LLM-based tool-using agent.

## Domain Decision Status

**Not yet finalized.**

The domain will be selected only after comparing edge-cloud offloading with alternative domains using the same criteria and verifying that the chosen agent architecture is feasible within the project constraints.