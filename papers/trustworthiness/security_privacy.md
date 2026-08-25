# Literature Cluster — Security, Privacy & Tool/Environment Safety

## Purpose

Map the **Security, Privacy & Tool/Environment Safety** dimension of Trustworthy Agentic AI.

## Paper 1 — Agent Security Bench (ASB)

**Focus:** Comprehensive security evaluation of LLM-based agents.

### Core contribution

ASB evaluates agent security across multiple:

- Attack scenarios
- Agent architectures
- Tools
- Attack categories
- Defense strategies
- Security metrics

The benchmark covers vulnerabilities across different stages of agent execution, including:

`Prompt / Context → Memory → Decision → Tool Use → Environment`

### Key insight

> **Agent security is a system-level problem, not only an LLM prompt-security problem.**

Security weaknesses can emerge from interactions between the model, memory, tools, and external environment.

**Priority:** Very High

---

## Paper 2 — VIGIL: Defending LLM Agents Against Tool-Stream Injection

**Focus:** Runtime defense against malicious manipulation of tool outputs/streams.

### Core contribution

VIGIL uses a **verify-before-commit** approach to inspect tool-stream information before allowing it to affect downstream agent behavior.

Conceptually:

`Tool Output → Verification → Commit / Reject → Agent Continues`

### Key insight

> **Security mechanisms must protect the agent while preserving useful autonomous behavior.**

This creates a practical tradeoff:

`Security ↑`

versus

`Utility / Task Performance`

### Key gap

> How can agents detect and block malicious tool-mediated information without excessively degrading normal task performance?

**Priority:** Very High

---

## Paper 3 — Security of LLM-based Agents Regarding Attacks, Defenses, and Applications

**Focus:** Broad survey of the security landscape for LLM-based agents.

The survey covers threats such as:

- Context / prompt manipulation
- Privacy attacks
- Action induction
- Availability attacks
- Reconnaissance
- Tool-related threats

and defensive approaches including:

- Input sanitization
- Training
- Architectural safeguards
- Monitoring
- Provenance mechanisms

### Key insight

Security must be considered across the **full agent lifecycle and interaction pipeline**, not only at the input layer.

**Priority:** High — reference paper.

---

## Comparison

| Paper | Main Question | Contribution | Priority |
|---|---|---|---|
| Agent Security Bench | How vulnerable are agents across the system? | Comprehensive security benchmark | Very High |
| VIGIL | How can tool-stream attacks be blocked? | Runtime verify-before-commit defense | Very High |
| Security Survey | What is the overall agent-security landscape? | Threat/defense taxonomy | High |

## Combined Insight

A trustworthy agent security pipeline can be viewed as:

`Untrusted Input / Environment`
→ `Detection`
→ `Verification`
→ `Controlled Action`
→ `Monitoring`
→ `Recovery`

## Key Research Questions

- Can security threats be detected across the complete agent trajectory?
- How can malicious tool outputs be distinguished from legitimate evidence?
- How much security intervention can an agent tolerate before utility degrades?
- Can provenance and verification help establish where an attack entered the trajectory?
- How should security and autonomy be balanced?

## Relevance to Trustworthy Agentic AI

Security is tightly connected to the other trustworthiness dimensions:

`Security`
→ protects the agent's information and actions

`UQ`
→ can identify uncertainty caused by suspicious or conflicting information

`Explainability`
→ can help reconstruct suspicious behavior

`Auditability`
→ preserves evidence of what happened

`Verification`
→ can prevent unsafe actions

Therefore:

> **Trustworthy Agentic AI requires security mechanisms that protect the full agent pipeline while preserving useful autonomous behavior.**