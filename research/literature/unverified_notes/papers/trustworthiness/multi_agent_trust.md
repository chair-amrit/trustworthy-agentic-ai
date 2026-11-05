# Literature Cluster — Multi-Agent Coordination & Trust

## Purpose

Map the **Multi-Agent Coordination & Trust** dimension of Trustworthy Agentic AI.

## Paper 1 — Explicit Trait Inference for Multi-Agent Coordination

**Focus:** Trust and competence modeling for agent coordination.

### Core contribution

Agents infer partner traits such as:

- Trust / warmth
- Competence

from interaction history and use these estimates in future coordination decisions.

Conceptually:

`Interaction History → Partner Model → Trust-Aware Coordination`

### Key insight

> **Trust can be treated as a dynamic state that influences future coordination rather than assuming all agents are equally reliable.**

### Key gap

> How can agents reliably infer and update the trustworthiness of other agents during long-running interactions?

**Priority:** Very High

---

## Paper 2 — Rethinking the Reliability of Multi-Agent System: A Perspective from Byzantine Fault Tolerance

**Focus:** Coordination when some agents are unreliable or potentially faulty.

### Core contribution

The paper applies ideas from **Byzantine Fault Tolerance (BFT)** to LLM-agent networks and uses confidence-aware weighting / consensus mechanisms to reduce the influence of unreliable agents.

Conceptually:

`Unreliable Agents → Detect / Reweight → Fault-Tolerant Consensus`

### Key insight

> **Multi-agent trust is not only about cooperation; systems must remain reliable when some participants provide incorrect or adversarial information.**

### Key gap

> How can multi-agent systems maintain reliable decisions when a subset of agents behaves unreliably or provides misleading information?

**Priority:** Very High

---

## Paper 3 — SILO-BENCH

**Focus:** Benchmarking distributed coordination under information silos.

### Core contribution

Agents have access to different portions of information and must coordinate through communication.

The benchmark evaluates:

- Task success
- Communication behavior
- Communication efficiency
- Agent scale
- Different communication protocols

### Key finding

The paper identifies a **communication–reasoning gap**:

> More communication does not necessarily produce better distributed reasoning or coordination.

### Key insight

`More messages ≠ Better coordination`

Effective coordination depends on whether communication actually improves distributed decision-making.

**Priority:** High — useful benchmark/reference paper.

---

## Comparison

| Paper | Main Question | Contribution | Priority |
|---|---|---|---|
| Explicit Trait Inference | How should agents model partner trust/competence? | Dynamic trust/trait inference | Very High |
| Byzantine Fault Tolerance | How should systems handle unreliable agents? | Fault-tolerant coordination | Very High |
| SILO-BENCH | Can agents coordinate effectively with partial information? | Distributed coordination benchmark | High |

## Combined Insight

Multi-agent trust can be viewed as:

`Partner Modeling`
→ `Trust Estimation`
→ `Communication`
→ `Coordination`
→ `Fault Tolerance`
→ `System Outcome`

## Key Research Questions

- How should agent trust be updated over time?
- How should unreliable agents be detected?
- How much should one agent trust another's information?
- Can coordination remain reliable under faulty or adversarial agents?
- Does increased communication actually improve system performance?

## Relevance to Trustworthy Agentic AI

A trustworthy multi-agent system must not assume that every participating agent is correct.

It should be able to:

`Assess → Trust / Down-weight → Verify → Coordinate → Recover`

The major open challenge is **maintaining reliable collective behavior when individual agents or communication channels are imperfect.**