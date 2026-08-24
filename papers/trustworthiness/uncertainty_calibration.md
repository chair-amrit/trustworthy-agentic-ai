# Literature Cluster — Uncertainty & Calibration

## Purpose

Map the **Uncertainty Quantification & Calibration** dimension of Trustworthy Agentic AI using representative 2026 agent-specific research.

## Paper 1 — Uncertainty Quantification in LLM Agents

**Focus:** Foundations and open challenges for uncertainty quantification in interactive LLM agents.

### Core contribution

The paper argues that most UQ research focuses on single-turn LLM tasks, while agents require uncertainty analysis across **interactive, multi-step trajectories**.

It proposes a general formulation of agent UQ and identifies four agent-specific challenges:

1. **Selection of uncertainty estimator**
2. **Uncertainty of heterogeneous entities**
3. **Uncertainty dynamics in interactive systems**
4. **Lack of fine-grained benchmarks**

### Key insight

Agent uncertainty is not necessarily static.

`State₀ → Action → Observation → State₁`

can change the agent's uncertainty throughout execution.

### Key gap

> How should uncertainty be represented, propagated, and evaluated across dynamic agent trajectories?

**Priority:** Very High — foundational paper for agent-specific UQ.

---

## Paper 2 — The Confidence Dichotomy

**Focus:** Calibration in tool-use agents.

### Core finding

Tool type can systematically affect agent confidence.

The study identifies a difference between:

- **Evidence tools** such as web search, which can introduce noisy information and increase overconfidence.
- **Verification tools** such as code interpreters, which can provide deterministic feedback and improve calibration.

### Contribution

The paper proposes an RL-based fine-tuning framework that jointly considers:

`Task Accuracy + Calibration`

It evaluates different reward designs and reports improved calibration and transfer across environments/domains.

### Key insight

Tool use does not merely provide information; it can **change the reliability of the agent's confidence**.

Conceptually:

`Tool → Evidence quality → Confidence → Decision`

### Key gap

> Calibration strategies may need to account for the characteristics and reliability of different tools and environments.

**Priority:** Very High — strong practical connection to trustworthy tool-using agents.

---

## Paper 3 — Structured Uncertainty Guided Clarification for LLM Agents

**Focus:** Using structured uncertainty to control agent interaction and clarification.

### Core idea

The paper separates:

**Specification uncertainty**
> What exactly does the user want?

from:

**Model uncertainty**
> What does the agent predict?

It uses structured uncertainty over tool parameters and **Expected Value of Perfect Information (EVPI)** to decide:

- Which clarification question is worth asking
- When clarification should stop

### Practical contribution

The framework improves:

- Ambiguous-task coverage
- Clarification efficiency
- Tool-calling accuracy
- Training efficiency

It also introduces **ClarifyBench**, a multi-turn tool-calling disambiguation benchmark.

### Key insight

Uncertainty can become an **action-selection signal**:

`Uncertainty → Clarification decision → Better tool call`

### Key gap

> How can uncertainty be integrated into agent decision policies while controlling interaction cost and avoiding unnecessary clarification?

**Priority:** High — valuable example of uncertainty-aware agent behavior.

---

## Comparison

| Paper | Primary Question | Contribution | Priority |
|---|---|---|---|
| Uncertainty Quantification in LLM Agents | How should agent uncertainty be defined/evaluated? | Agent-specific UQ framework + challenges | Very High |
| Confidence Dichotomy | Is agent confidence reliable during tool use? | Tool-aware calibration + mitigation | Very High |
| Structured Uncertainty Guided Clarification | How should agents act under ambiguity? | Uncertainty-guided clarification | High |

## Combined Insight

These papers show three increasingly practical levels:

`UQ`
→ How uncertain is the agent?

`Calibration`
→ Does confidence match actual reliability?

`Uncertainty-aware behavior`
→ Does the agent change its actions appropriately when uncertain?

This suggests a trustworthiness chain:

`Uncertainty Estimation → Calibration → Safe/Adaptive Agent Behavior`

## Literature Direction

For deeper study:

**Deep read**
- Uncertainty Quantification in LLM Agents
- The Confidence Dichotomy

**Reference / skim**
- Structured Uncertainty Guided Clarification

## Relevance to Trustworthy Agentic AI

UQ becomes particularly valuable when uncertainty is not merely reported but **used to influence agent behavior**.

Potential trustworthiness questions include:

- Should high uncertainty trigger verification?
- Should uncertainty trigger clarification?
- Should uncertainty prevent an external action?
- How should uncertainty propagate across long trajectories?
- How should confidence be calibrated when different tools have different reliability?