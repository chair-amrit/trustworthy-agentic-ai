# 07 — Multi-Agent Explainability

## Objective

Understand how explainability changes when behavior is distributed across multiple interacting agents.

`Agent A ↔ Agent B ↔ Agent C → System Outcome`

## 1. Main Explanation Targets

### Delegation
Why was a task assigned to this particular agent?

`Supervisor → Research Agent`

Focus: **why this agent was selected**.

### Communication
Why did one agent send a particular message or information to another?

`Research Agent → "Evidence A is reliable" → Verifier`

Focus: **why the communication occurred and whether it influenced the receiver**.

### Coordination
Why did agents follow this collaborative sequence?

`Research → Verify → Write`

Focus: **why this strategy was used instead of another**.

### System-Level Explanation
How did multiple agents, actions, messages, and decisions collectively produce the final outcome?

`Supervisor → Research → Verifier → Writer → Outcome`

---

## 2. Levels of Explanation

`Agent-level → Interaction-level → System-level`

- **Agent-level:** Why did Agent A call Tool X?
- **Interaction-level:** Why did A send information to B?
- **System-level:** How did A, B, and C collectively produce the outcome?

Explaining each agent independently may not fully explain system behavior.

## 3. Credit Assignment

A major challenge is determining:

> **Which agent, action, message, or interaction contributed to the outcome?**

Example:

`Agent A → bad evidence → Agent B trusts it → Agent C gives wrong answer`

Possible contributors:

- A produced the bad evidence
- B failed to verify it
- C propagated the error
- An interaction between agents caused the failure

This is a **credit-assignment problem**.

## 4. Distributed Causality

In a single agent:

`State → Decision → Action`

In a multi-agent system:

`Agent A → Message → Agent B → Decision → Agent C → Outcome`

The cause of an outcome may therefore be distributed across several agents and interactions.

## 5. Communication as a Causal Variable

A message can itself influence another agent.

Example:

`Agent A: "Evidence A is reliable" → Agent B accepts A`

To test whether the message mattered:

`Original: "reliable"`

vs.

`Counterfactual: "unreliable" / no message`

Then compare Agent B's behavior.

This connects multi-agent explainability with the **counterfactual testing** framework from Module 6.

## 6. Other Counterfactual Tests

### Remove an agent

`A → B → C`

vs.

`B → C`

Question: Does removing A change the system behavior?

### Replace an agent

`A → B → C`

vs.

`A → D → C`

Question: Does replacing an agent change the outcome?

### Change a message

`A → Message X → B`

vs.

`A → Message Y → B`

Question: Does B's decision change?

## 7. Emergent Behavior

A multi-agent system can exhibit behavior that is not obvious from any single agent.

`Agent A tendency + Agent B tendency + Interaction → System behavior`

Therefore:

> **Individual explanations may be insufficient for explaining collective behavior.**

System-level and interaction-level explanations are necessary when behavior emerges from coordination.

## 8. Connection to Single-Agent Explainability

Single agent:

`State → Decision → Action → Observation`

Multi-agent:

`Agent State → Decision → Action/Message → Other Agent → New State → Decision → ... → Outcome`

The explanatory object therefore becomes a **distributed trajectory**.

## 9. Research Questions

Useful questions include:

- Why was this agent delegated the task?
- Why was this message sent?
- Did the receiver's decision depend on that message?
- Which agent or interaction contributed most to the outcome?
- What happens if an agent, message, or interaction is removed or changed?

## Key Takeaway

> **Multi-Agent Explainability extends single-agent explainability from individual decisions to delegation, communication, coordination, and distributed causal contribution across the system.**