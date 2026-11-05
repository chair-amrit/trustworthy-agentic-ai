# Agent Architecture Trade-off

## Decision Context

The locked research direction is:

> Explainable Analysis of Uncertainty–Correctness Mismatch in Multi-Step Tool-Using Agents

For an edge-cloud offloading domain, two main agent architectures are possible:

`Conventional RL Agent`

or

`LLM / Tool-Using Agent`

## 1. Conventional RL Agent

Architecture:

`State → RL Policy → Action → Environment → Reward`

### Advantages

- Natural fit for sequential offloading decisions
- Efficient inference
- Mature edge-cloud/RL literature
- Easy integration with simulation environments
- Straightforward state/action/reward formulation

### Challenges for This Project

- Agent uncertainty requires additional UQ methodology
- Policy confidence/Q-values do not automatically represent trustworthy uncertainty
- Explainability must be adapted to policy behavior
- Less direct alignment with the tool-using trajectory framework already developed
- Requires additional RL-specific learning and experimentation

## 2. LLM / Tool-Using Agent

Architecture:

`State → LLM Decision → Tool → Observation → Next State`

Possible tools:

- Network-state query
- Edge-capacity query
- Latency estimation
- Resource-status query
- Offloading action

### Advantages

- Naturally produces multi-step trajectories
- Explicit decisions and tool interactions
- Directly compatible with trajectory-based explainability
- Natural integration of self/external explanations
- Counterfactual intervention can target tool outputs or state information

### Challenges

- Higher inference cost
- Stochastic behavior
- More difficult uncertainty estimation/calibration
- Requires constrained tools/actions
- More experimental runs may be needed

## 3. Practical Comparison

| Factor | RL Agent | LLM Agent |
|---|---|---|
| Edge-cloud fit | Very High | Medium |
| Multi-step trajectory | High | Very High |
| Tool interaction | Low/Medium | Very High |
| UQ complexity | Medium/High | High |
| Explainability alignment | Medium | Very High |
| Compute efficiency | Very High | Medium/Low |
| Experimental control | Very High | High |
| Existing project knowledge | Medium | High |

## 4. Current Interpretation

Neither architecture is automatically superior.

The choice depends on what should be the **research object**:

### RL-centered

The project becomes:

> Trustworthy uncertainty and error analysis of RL-based offloading decisions.

### LLM-centered

The project becomes:

> Uncertainty–correctness analysis of a tool-using LLM agent operating in an edge-cloud environment.

The second option aligns more directly with the Agent Explainability and tool-using-agent research already studied.

## 5. Constraint for Final Selection

Before locking the architecture, verify:

- Available compute
- Inference cost
- Simulator integration
- Action-space constraints
- Reliable uncertainty estimation
- Number of trajectories required
- Reproducibility
- Availability of suitable baselines

## Current Status

**Architecture:** Not finalized

**Domain:** Edge-cloud offloading remains a candidate, not yet locked.

The final architecture should be selected only after confirming that it supports reliable per-step uncertainty measurement and controlled uncertainty–correctness experiments within the project timeline.