# 01 — Agent Explainability Foundations

## 1. Why Agent Explainability Is Different

A conventional ML/LLM system can often be viewed as:

`Input → Model → Prediction/Answer`

Its explanation usually asks:

> Why did the model produce this prediction or answer?

An AI agent is different because it operates over multiple sequential steps:

`Goal → State → Decision → Action → Observation → New State → ... → Outcome`

The agent may call tools, retrieve information, update its state, change decisions, and continue until it reaches an outcome.

Therefore, agent explainability is not limited to explaining the final answer. It focuses on explaining the **relevant decisions, actions, evidence, and trajectory** that produced the outcome.

---

## 2. Core Mental Model

An agent can be viewed as a repeated transition process:

`State → Decision → Action → Environment/Tool → Observation → New State`

Possible explanation questions include:

- Why did the agent make this decision?
- Why did it choose this tool/action?
- What information influenced the decision?
- Why did it follow this sequence of steps?
- How did the overall trajectory lead to the final outcome?

---

## 3. Trajectory as the Explanation Object

A **trajectory** is the sequence of states, decisions/actions, and observations generated during one execution.

Example:

    State₀
      ↓
    Decision: need external information
      ↓
    Action: search tool
      ↓
    Observation: search results
      ↓
    State₁
      ↓
    Decision: compare results
      ↓
    Action: select candidate
      ↓
    Outcome

The trajectory gives us the sequence of **what happened** during execution.

However:

> **Trajectory ≠ Explanation**

The trajectory describes **what happened**. Explainability attempts to establish **why it happened**.

---

## 4. What Makes an Agent Explanation Different?

For a normal LLM:

`Input → Answer`

A typical explanation asks:

> Why did the model produce this answer?

For an agent:

`Goal → State → Decision → Action → Observation → New State → ... → Outcome`

We may need to ask:

> Why did the agent make this decision?

> Why did it choose this tool?

> What information influenced the decision?

> Why did it follow this sequence?

> How did the complete trajectory lead to the final outcome?

Therefore:

> **Ordinary XAI focuses mainly on explaining a prediction or output, while Agent Explainability focuses on explaining relevant aspects of sequential agent behavior and its trajectory.**

---

## 5. Explanations Do Not Necessarily Need to Cover Everything

It is not always necessary to explain the agent's entire internal process.

The explanation target should depend on the research question or user's need.

For example:

> "Why did the agent call the web-search tool?"

may require only an explanation of a particular action.

It may not require an explanation of every previous and subsequent event.

Therefore:

> **Agent Explainability should target the relevant parts of the agent's decision process or trajectory.**

---

## 6. A Critical Trustworthiness Problem

An agent, especially an LLM-based agent, can generate a convincing natural-language rationale for its own behavior.

Example:

> "I selected Tool A because it provided the most relevant information."

This explanation may sound reasonable, but the statement itself does not prove that the claimed reason actually caused or influenced the decision.

Therefore:

> **Good language ≠ faithful explanation.**

A plausible explanation and a faithful explanation are not necessarily the same thing.

This motivates later study of:

- Faithfulness
- Counterfactual testing
- Behavioral interventions
- Explanation evaluation

---

## 7. Core Mental Model for Agent Explainability

The overall research structure is:

`Agent → Trajectory → Explanation Target → Explanation Method → Evaluation`

Where:

- **Agent** = the decision-making system
- **Trajectory** = what happened during execution
- **Explanation target** = what part of the behavior we want to explain
- **Explanation method** = how the explanation is produced
- **Evaluation** = how we determine whether the explanation is good/trustworthy

---

## 8. Key Takeaways

1. An agent is not simply `Input → Answer`; it repeatedly processes information, makes decisions, takes actions, observes results, updates its state, and continues.
2. Therefore, explaining only the final answer is often insufficient.
3. The **trajectory** is an important object for understanding and explaining agent behavior.
4. The first question in an explainability study should be:

> **What exactly are we trying to explain in the agent's trajectory?**

5. A convincing explanation is not automatically a faithful explanation.
6. Agent Explainability is ultimately about connecting **behavior → explanation → evidence → evaluation**.