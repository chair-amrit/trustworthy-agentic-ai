# Literature Cluster — Reliability & Robustness

## Purpose

Map the **Reliability & Robustness** dimension of Trustworthy Agentic AI using representative 2026 research.

## Paper 1 — ReliabilityBench

**Focus:** Evaluating agent reliability under production-like stress.

### Core contribution

Reliability is treated as more than single-run success through three dimensions:

`Consistency + Robustness + Fault Tolerance`

The paper introduces:

- **Reliability Surface R(k, ε, λ)**
- **Action Metamorphic Relations**
- **Chaos engineering for agents**
- Systematic fault injection

Faults include:

- Timeouts
- Rate limits
- Partial responses
- Schema drift

### Key finding

Agents that perform strongly under clean conditions can degrade significantly under perturbations and infrastructure failures.

The study also shows that simpler agent architectures can sometimes outperform more complex ones under stress.

### Key gap

> How can reliability of long-running agents be measured consistently across repeated execution, environmental perturbations, and infrastructure failures?

**Priority:** Very High

---

## Paper 2 — AgentNoiseBench

**Focus:** Robustness of tool-using agents in noisy environments.

### Core contribution

Separates environmental noise into:

- **User noise**
- **Tool noise**

The framework injects controlled noise into agent benchmarks while preserving task solvability.

### Key insight

`Clean benchmark performance ≠ real-world robustness`

Agents can be highly capable under idealized conditions but become sensitive when users, tools, or environments behave imperfectly.

### Key gap

> How can agent robustness be systematically evaluated under realistic environmental uncertainty and noise?

**Priority:** Very High

---

## Paper 3 — Why Do LLM-based Web Agents Fail?

**Focus:** Process-level diagnosis of web-agent failures.

The paper decomposes execution into:

`High-level planning → Low-level execution → Replanning`

### Key finding

Low-level execution remains a major bottleneck even when high-level planning is strong.

This shows that end-to-end success rate alone is insufficient to identify where an agent fails.

### Key insight

> **Reliability evaluation should localize failures within the agent trajectory rather than only measure final task success.**

**Priority:** High — strong connection to error diagnosis.

---

## Comparison

| Paper | Main Question | Contribution | Priority |
|---|---|---|---|
| ReliabilityBench | Does the agent remain dependable under stress? | Unified reliability surface + fault injection | Very High |
| AgentNoiseBench | How robust is the agent to environmental noise? | Controlled user/tool noise evaluation | Very High |
| Why Do Web Agents Fail? | Where does the trajectory fail? | Hierarchical process-level diagnosis | High |

## Combined Insight

Reliability can be viewed as:

`Repeated consistency`
→ `Perturbation robustness`
→ `Fault tolerance`
→ `Failure localization`

This extends the simple notion of agent accuracy into **production-oriented reliability**.

## Literature Direction

**Deep-read later:**
- ReliabilityBench
- AgentNoiseBench

**Reference:**
- Why Do LLM-based Web Agents Fail?

## Relevance to Trustworthy Agentic AI

The important distinction is:

> **Reliability asks whether the agent continues to behave dependably; robustness asks whether it remains dependable when conditions change or components fail.**