# 07 — Multi-Agent Explainability

## 1. Why Multi-Agent Explainability Is Harder

A single agent can be represented as:

    Goal
      ↓
    State
      ↓
    Decision
      ↓
    Action
      ↓
    Observation
      ↓
    New State

A multi-agent system introduces multiple decision-makers and interactions:

    Supervisor
       ↓
    Research Agent
       ↓
    Verifier
       ↓
    Writer
       ↓
    Final Outcome

Now the behavior may depend not only on individual agent decisions, but also on:

- Delegation
- Communication
- Coordination
- Shared information
- Previous agent outputs
- Inter-agent dependencies

Therefore, explaining each agent independently may not be enough to explain the overall system.

---

## 2. Main Explanation Targets

Multi-agent explainability introduces several additional targets.

### A. Delegation Explanation

Question:

> **Why was a task assigned to this particular agent?**

Example:

    Supervisor
       ↓
    Assigns verification task
       ↓
    Research Agent

Possible explanation:

> "The Supervisor assigned the task to the Research Agent because it had the required retrieval and evidence-analysis capability."

The key question is not only **who received the task**, but **why that agent was selected**.

---

## 3. Communication Explanation

Question:

> **Why did one agent send a particular message or information to another agent?**

Example:

    Research Agent
       ↓
    "Evidence A is reliable"
       ↓
    Verifier

Possible explanation:

> "The Research Agent sent the assessment because the Verifier needed the evidence evaluation to perform validation."

Communication itself becomes an explainable event.

---

## 4. Coordination Explanation

Question:

> **Why did the agents follow this particular collaborative strategy?**

Example:

    Research Agent
       ↓
    Gather evidence
       ↓
    Verifier
       ↓
    Validate evidence
       ↓
    Writer
       ↓
    Produce answer

A coordination explanation asks why the system used:

    Research → Verify → Write

instead of:

    Research → Write

This is a multi-step, system-level explanation target.

---

## 5. System-Level Explanation

Question:

> **How did the interactions between multiple agents collectively produce the final outcome?**

Example:

    Supervisor
       ↓
    Delegates task
       ↓
    Research Agent
       ↓
    Produces evidence
       ↓
    Verifier
       ↓
    Validates evidence
       ↓
    Writer
       ↓
    Final answer

A system-level explanation describes the chain of decisions, actions, communications, and observations that produced the final result.

---

## 6. Levels of Explanation

Multi-agent explanations can be viewed at three levels.

### Agent-Level

Explain one agent's behavior.

> Why did Agent A call Tool X?

### Interaction-Level

Explain behavior between agents.

> Why did Agent A send this information to Agent B?

### System-Level

Explain collective behavior.

> How did coordination between A, B, and C produce the final outcome?

Conceptually:

    Individual behavior
          ↓
      Interactions
          ↓
    Collective behavior
          ↓
      System outcome

---

## 7. Credit Assignment

A major challenge is determining:

> **Which agent, action, message, or interaction contributed to the final outcome?**

Example:

    Agent A
       ↓
    Produces incorrect evidence
       ↓
    Agent B
       ↓
    Trusts the evidence
       ↓
    Agent C
       ↓
    Produces incorrect answer

Who caused the failure?

Possibilities include:

- Agent A directly caused it
- Agent B amplified the error
- Agent C produced the final failure
- The interaction between agents caused the failure

This is a **credit assignment** problem.

The goal is to determine how different agents and events contributed to the final behavior.

---

## 8. Distributed Causality

In a single-agent system, a simplified causal chain may be:

    State
      ↓
    Decision
      ↓
    Action

In a multi-agent system:

    Agent A
       ↓
    Message
       ↓
    Agent B
       ↓
    Decision
       ↓
    Agent C
       ↓
    Outcome

The cause of an outcome may therefore be distributed across several agents and interactions.

This creates a core research question:

> **Which agents, actions, messages, and interactions actually contributed to the system's behavior?**

---

## 9. Communication as an Explanation Variable

In multi-agent systems, messages themselves can influence downstream decisions.

Example:

    Agent A
       ↓
    "Document A is unreliable."
       ↓
    Agent B
       ↓
    Rejects Document A

A useful question is:

> Did Agent B reject the document because of the document's actual evidence, or because Agent A told it that the document was unreliable?

This can be investigated using controlled interventions.

---

## 10. Counterfactual Multi-Agent Explainability

Counterfactual methods from Module 6 can be extended to multi-agent systems.

### Message Intervention

Original:

    Agent A
       ↓
    "Evidence A is reliable."
       ↓
    Agent B
       ↓
    Accepts A

Counterfactual:

    Agent A
       ↓
    "Evidence A is unreliable."
       ↓
    Agent B
       ↓
    Observe decision

If B's behavior changes substantially, this provides evidence that A's message influenced B.

---

## 11. Other Useful Counterfactuals

### Remove an Agent

    Original:
    A → B → C → Outcome

    Counterfactual:
    A removed
      ↓
    B → C → Outcome?

Question:

> Does the system still behave similarly?

### Replace an Agent

    Original:
    A → B → C

    Counterfactual:
    A → D → C

Question:

> Does replacing A or B change the system behavior?

### Change a Message

    Original:
    A → Message X → B

    Counterfactual:
    A → Message Y → B

Question:

> Does B's behavior change?

These experiments help identify which agents and interactions are behaviorally important.

---

## 12. Emergent Behavior

A multi-agent system can sometimes exhibit behavior that is not obvious from inspecting one agent alone.

Example:

    Agent A has tendency X
    Agent B has tendency Y

            ↓

      Interaction

            ↓

    System exhibits behavior Z

Neither A nor B may individually explain Z.

Therefore:

> **Explaining each agent independently may not fully explain the behavior of the collective system.**

This is one reason system-level and interaction-level explanations are important.

---

## 13. Example

Consider:

    Supervisor
       ↓
    Research Agent
       ↓
    "Evidence A is reliable"
       ↓
    Verifier
       ↓
    Accepts A
       ↓
    Writer
       ↓
    Wrong final answer

Possible explanation targets:

### Delegation

> Why did the Supervisor assign the task to the Research Agent?

### Communication

> Why did the Research Agent send the reliability assessment to the Verifier?

### Verifier Decision

> Why did the Verifier accept Evidence A?

### System-Level

> How did the Supervisor's delegation, Research Agent's assessment, Verifier's decision, and Writer's use of A collectively produce the wrong outcome?

### Counterfactual

> What happens if the Research Agent sends "Evidence A is unreliable" instead?

---

## 14. Connection to Single-Agent Explainability

The concepts can be extended directly:

    Single Agent:

    State
      ↓
    Decision
      ↓
    Action
      ↓
    Observation

    Multi-Agent:

    Agent State
      ↓
    Agent Decision
      ↓
    Action / Communication
      ↓
    Other Agent
      ↓
    New Agent State
      ↓
    New Decision
      ↓
    System Outcome

The explanatory object therefore becomes a **distributed trajectory** rather than only one agent's trajectory.

---

## 15. Connection to Existing VLM Explainability

In VLM explainability, the question may be:

> Which image patches or tokens contributed to the prediction?

For multi-agent explainability, an analogous question is:

> Which agents, states, actions, messages, observations, and interactions contributed to the system decision?

Conceptually:

    VLM:
    Prediction ← visual/text evidence

    Single Agent:
    Decision ← state/evidence/history

    Multi-Agent:
    Outcome ← agents + actions + messages + interactions + evidence

The explanatory object becomes increasingly distributed.

---

## 16. Key Takeaways

1. Multi-agent systems require explanations at **agent, interaction, and system levels**.
2. Important targets include:
   - Delegation
   - Communication
   - Coordination
   - Individual decisions
   - System outcomes
3. **Credit assignment** asks which agents or events contributed to an outcome.
4. **Distributed causality** makes system-level explanations harder than single-agent explanations.
5. Communication can itself become an important causal/explanatory variable.
6. Counterfactual interventions can test whether an agent's message or interaction actually influenced another agent.
7. Removing or replacing agents can help identify their contribution to system behavior.
8. Explaining every individual agent separately may not fully explain **emergent collective behavior**.
9. The core question becomes:

> **Which agents and interactions contributed to the behavior, and why?**