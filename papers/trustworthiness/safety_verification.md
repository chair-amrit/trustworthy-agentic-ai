# Literature Cluster — Safety, Verification & Constraint Satisfaction

## Purpose

Map the **Safety, Verification & Constraint Satisfaction** dimension of Trustworthy Agentic AI.

## Paper 1 — Towards Verifiably Safe Tool Use for LLM Agents

**Focus:** Formal safety specifications for tool-using agents.

### Core contribution

The paper proposes:

`Hazard Analysis → Safety Requirements → Formal Specifications → Enforceable Tool Constraints`

It uses **System-Theoretic Process Analysis (STPA)** to identify hazards and derive safety requirements, then applies capability-aware labels to tool interactions.

### Key insight

Safety should not depend only on an LLM deciding whether an action is safe.

> **Safety requirements should be explicitly specified and enforced at the system level.**

### Key gap

> How can formal safety guarantees be achieved for autonomous tool use without excessive manual specification or user confirmation?

**Priority:** Very High

---

## Paper 2 — The Verifier Tax

**Focus:** Runtime safety enforcement in multi-step tool-using agents.

### Core contribution

The paper evaluates:

`Baseline Tool Calling → Planning → Policy-Mediated Safety`

and separates:

- Overall Success Rate (SR)
- Safe Success Rate (SSR)
- Unsafe Success Rate (USR)

### Key finding

Blocking unsafe actions does not necessarily produce safe task completion.

The study identifies a **Safety-Capability Gap**:

`Unsafe actions intercepted ↑`

but

`Safe task completion remains very low`

Agents may fail to recover after intervention or find alternative unsafe paths.

### Key insight

> **Safety is not simply blocking unsafe actions; safe recovery and continued task completion also matter.**

### Key gap

> How can agents recover safely after an unsafe action is blocked while still completing the user's task?

**Priority:** Very High

---

## Paper 3 — Toward Safe LLM Agents

**Focus:** Systematic review of agent safety across specification, verification, and enforcement.

### Main findings

The survey highlights a **specification bottleneck**:

`Natural-language requirement → Formal specification`

can introduce semantic errors before verification even begins.

It also finds that runtime monitoring is comparatively mature, but does not provide complete task-level safety guarantees.

### Core challenge

Current approaches struggle to simultaneously achieve:

`Soundness + Scalability + Semantic Correctness + Task-Level Safety`

### Key gap

> **How can safety specifications be correctly defined and verified while remaining scalable for realistic agentic tasks?**

**Priority:** High — useful as a field-level reference.

---

## Comparison

| Paper | Main Question | Contribution | Priority |
|---|---|---|---|
| Towards Verifiably Safe Tool Use | Can tool behavior be formally constrained? | Hazard analysis + formal safety specifications | Very High |
| The Verifier Tax | Does runtime blocking actually produce safe completion? | Empirical safety/capability tradeoff | Very High |
| Toward Safe LLM Agents | What remains unsolved across safety research? | Systematic review + research agenda | High |

## Combined Insight

A trustworthy safety pipeline is:

`Hazard Identification`
→ `Safety Specification`
→ `Verification`
→ `Runtime Enforcement`
→ `Safe Recovery`
→ `Task Completion`

## Relevance to Trustworthy Agentic AI

This dimension shifts the question from:

> **"Why did the agent do this?"**

to:

> **"Was the action allowed, safe, and recoverable?"**

The most interesting unresolved issue is that **blocking unsafe behavior alone is insufficient**; trustworthy agents also need correct specifications and effective post-intervention recovery.