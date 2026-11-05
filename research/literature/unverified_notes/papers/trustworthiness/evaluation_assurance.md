# Literature Cluster — Evaluation, Monitoring & Assurance

## Purpose

Map the **Evaluation, Monitoring & Assurance** dimension of Trustworthy Agentic AI.

## Paper 1 — A Survey on Evaluation of LLM-based Agents

**Focus:** Overall evaluation landscape for agentic systems.

### Core contribution

The survey organizes agent evaluation across multiple dimensions rather than relying only on task success:

- Capability
- Reliability
- Safety
- Robustness
- Cost
- Evaluation methodology

### Key insight

> **Agent evaluation cannot be reduced to a single success-rate metric.**

Agents need evaluation of both outcomes and the process that produced them.

### Key gap

> How can agent evaluation become more realistic, fine-grained, scalable, and continuously relevant to deployed systems?

**Priority:** Very High

---

## Paper 2 — A Unified Framework for the Evaluation of LLM Agentic Capabilities

**Focus:** Controlled and standardized evaluation of agent capabilities.

### Core contribution

The framework separates:

`Model capability`

from

`Agent scaffold / framework`

and

`Environment effects`

This helps determine whether performance differences come from the underlying model or from the surrounding agent system.

It also supports fine-grained analysis of decision/execution failures.

### Key insight

> **A benchmark result may measure the interaction between the model, agent framework, and environment rather than the model alone.**

The paper evaluates large numbers of rollouts across multiple models and domains to improve comparability.

### Key gap

> How can agent benchmarks isolate the true source of performance and failure while remaining scalable and realistic?

**Priority:** Very High

---

## Paper 3 — AgenticEval

**Focus:** Continuous and adaptive safety evaluation.

### Core contribution

Instead of treating evaluation as a one-time benchmark, AgenticEval creates an iterative loop:

`Evaluate`
→ `Identify weaknesses`
→ `Generate harder/adaptive tests`
→ `Evaluate again`

This supports continuously evolving safety evaluation as agents and risks change.

### Key insight

> **Static benchmarks can become outdated as agent behavior and threat patterns evolve.**

### Key gap

> How can evaluation continuously adapt to newly discovered failure modes without becoming excessively expensive or unstable?

**Priority:** High — reference paper.

---

## Comparison

| Paper | Main Question | Contribution | Priority |
|---|---|---|---|
| Evaluation Survey | What should be evaluated? | Broad evaluation taxonomy | Very High |
| Unified Evaluation Framework | How can evaluation be standardized? | Model/scaffold/environment separation | Very High |
| AgenticEval | How can evaluation stay current? | Adaptive safety evaluation loop | High |

## Combined Insight

Trustworthiness evaluation can be viewed as:

`Measure`
→ `Localize Failure`
→ `Monitor`
→ `Adapt Tests`
→ `Re-evaluate`

This moves evaluation from a one-time benchmark toward **continuous assurance**.

## Key Research Questions

- How should trustworthy agents be evaluated across multiple dimensions simultaneously?
- How can benchmark results separate model capability from scaffold/environment effects?
- How can failures be localized to specific decisions, tools, or trajectory stages?
- How can benchmarks adapt to newly discovered risks?
- How can continuous monitoring remain computationally practical?

## Relevance to Trustworthy Agentic AI

Evaluation connects all other trustworthiness dimensions:

`Explainability`
→ Is behavior understandable?

`UQ`
→ Is confidence calibrated?

`Reliability`
→ Does behavior remain stable?

`Safety`
→ Are actions compliant and safe?

`Multi-Agent Trust`
→ Does coordination remain reliable?

`Security`
→ Can threats be detected?

`Evaluation`
→ Can we demonstrate and continuously monitor all of the above?

Therefore:

> **Evaluation and assurance form the evidence layer for Trustworthy Agentic AI.**