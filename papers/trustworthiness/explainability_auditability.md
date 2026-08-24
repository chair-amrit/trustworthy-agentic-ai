# Literature Cluster — Explainability & Auditability

## Purpose

Map the **Explainability & Auditability** dimension of Trustworthy Agentic AI using representative 2026 work.

## Paper 1 — From Models to Systems

**Focus:** System-level explainability for tool-augmented LLMs.

Core idea:

`Traditional XAI: Model → Output → Explanation`

becomes:

`Agent → Tool Use → Execution Trace → System Behavior → Explanation`

### Main contribution

Argues that agentic systems require explanations covering:

- Tool selection and usage
- External execution traces
- Tool results
- System-level behavior
- Causal influence across the trajectory

### Key gap

> How can faithful explanations be produced for complex LLM-based systems whose behavior depends on multiple interacting internal and external factors?

**Priority:** High — foundational for understanding agent explainability.

---

## Paper 2 — Auditable Agents

**Focus:** Operational auditability and accountability for agents that can act in the world.

### Key distinction

**Accountability:** ability to determine compliance and assign responsibility.

**Auditability:** system property that makes accountability possible.

**Auditing:** process of reconstructing behavior from trustworthy evidence.

### Five auditability dimensions

1. Action recoverability
2. Lifecycle coverage
3. Policy checkability
4. Responsibility attribution
5. Evidence integrity

### Mechanism classes

`Detect → Enforce → Recover`

The paper argues that no single mechanism is sufficient for complete auditability.

### Practical contribution

The study combines:

- Ecosystem security measurements
- Runtime feasibility experiments
- Responsibility-recovery experiments
- An **Auditability Card** for agent systems

### Key gap

> How can agent behavior remain reconstructable and responsibility-attributable after deployment, including when conventional logs are incomplete?

**Priority:** Very High — strong connection between trustworthy agents, evidence, accountability, and practical deployment.

---

## Paper 3 — Transparency in Agentic AI

**Focus:** Lifecycle transparency and governance.

The paper studies transparency across:

- Plans
- Tool interactions
- Memory events
- Coordination signals
- Agent lifecycle stages

It connects transparency with:

`Faithfulness + Auditability + Compliance + Robustness + Governance`

### Proposed artifact

**Minimal Explanation Packet**

A standardized outcome artifact intended to bundle important lifecycle evidence into an audit-ready record.

### Key gaps

The paper highlights limited treatment of:

- Trajectory-level accountability
- Tool-mediated provenance
- Multi-agent coordination transparency
- Verification of recorded evidence

**Priority:** Medium–High — useful as a broad reference for transparency and governance.

---

## Comparison

| Paper | Primary Question | Contribution | Priority |
|---|---|---|---|
| From Models to Systems | How should agent behavior be explained? | System/trajectory-level XAI | High |
| Auditable Agents | Can agent behavior be reconstructed and responsibility assigned? | Operational auditability | Very High |
| Transparency in Agentic AI | What should be recorded and exposed across the lifecycle? | Transparency + governance framework | Medium–High |

## Combined Insight

The three papers cover complementary trustworthiness layers:

`Explainability`
→ understand behavior

`Auditability`
→ reconstruct and verify behavior

`Transparency`
→ make relevant lifecycle evidence available for oversight

This suggests a broader trustworthiness chain:

`Agent Action → Evidence → Explanation → Verification → Accountability`

## Literature Direction

For deeper study:

**Deep read**
- From Models to Systems
- Auditable Agents

**Reference / skim**
- Transparency in Agentic AI

The major open space is not simply "more explanations," but **reliable evidence, reconstruction, and validation of agent behavior across long-running and multi-component systems.**