# 03 — Explanation Targets

## 1. Why "Explain the Agent" Is Too Vague

An agent trajectory contains many decisions, actions, observations, and interactions.

Therefore, a research study should first define:

> **What exactly are we trying to explain?**

The main explanation targets learned so far are:

1. Action
2. Decision
3. Plan
4. Evidence
5. Outcome
6. Trajectory / Process

---

## 2. Action / Tool-Choice Explanation

Question:

> **Why did the agent perform this particular action or call this tool?**

Example:

    Action:
    retrieve(Document A)

    Question:
    Why did the agent choose to retrieve Document A?

This focuses on the **specific operation executed**.

Examples of actions include:

    retrieve()
    search()
    calculate()
    ask_user()
    delegate_to_agent()
    terminate()

---

## 3. Decision Explanation

Question:

> **Why did the agent decide that this action was appropriate?**

Example:

    State:
    Current context lacks required information

      ↓

    Decision:
    "Retrieve another document"

The explanation concerns the **choice itself**, rather than only the execution of the chosen action.

Important distinction:

> **Decision = what the agent chooses to do**

> **Action = what the agent actually executes**

---

## 4. Plan Explanation

Question:

> **Why did the agent follow this sequence or strategy?**

Example:

    Retrieve A
      ↓
    Check sufficiency
      ↓
    Retrieve B
      ↓
    Answer

A plan explanation asks why the agent followed this sequence instead of a simpler or different strategy, such as:

    Retrieve A
      ↓
    Answer

Plan explanations therefore operate at a **multi-step level**.

---

## 5. Evidence Explanation

Question:

> **What information or observation influenced the agent's decision?**

Example:

    Document A:
    Contains disease information
    Does not contain tribe information

      ↓

    Decision:
    Document A is insufficient

The evidence explanation focuses on the information that contributed to this decision.

Important distinction:

    Action explanation:
    "Why did the agent retrieve Document B?"

    Evidence explanation:
    "What information in Document A contributed to
    the conclusion that Document A was insufficient?"

---

## 6. Outcome Explanation

Question:

> **Why did the agent produce this final result?**

Example:

    Search
      ↓
    Compare
      ↓
    Verify
      ↓
    Select B
      ↓
    Final answer

An outcome explanation focuses on the factors that led to the final result.

This is closer to traditional model explainability, but the outcome may depend on an entire agent trajectory rather than a single prediction step.

---

## 7. Trajectory / Process Explanation

Question:

> **How did the complete sequence of states, actions, observations, and decisions lead to the outcome?**

Example:

    Initial question
      ↓
    Retrieve A
      ↓
    A lacks required information
      ↓
    Retrieve B
      ↓
    B provides the missing information
      ↓
    Final answer

A trajectory explanation describes the **overall process**, rather than focusing on one isolated action.

---

## 8. Same Trajectory, Different Explanation Questions

Consider:

    State₀
      ↓
    Retrieve A
      ↓
    A is insufficient
      ↓
    Retrieve B
      ↓
    Answer

The same trajectory can support different explanation questions:

    Action:
    Why did the agent retrieve A or B?

    Decision:
    Why did the agent decide that A was insufficient?

    Plan:
    Why did it use Retrieve → Check → Retrieve?

    Evidence:
    What information made A appear insufficient?

    Outcome:
    Why did the agent produce the final answer?

    Trajectory:
    How did the complete process lead from the question
    to the final answer?

Therefore:

> **The explanation target must be explicitly defined before selecting an explanation method.**

---

## 9. Explanation Granularity

Explanation targets can also differ in scale:

### Micro-level

A single action or decision.

Example:

> Why did the agent call Tool A?

### Meso-level

A short sequence or plan.

Example:

> Why did the agent Search → Retrieve → Verify?

### Macro-level

The complete execution or system process.

Example:

> How did the full trajectory produce the final outcome?

---

## 10. Connection to Existing VLM Explainability

The same general idea transfers from VLM explainability.

For a VLM:

    Prediction
        ↑
    Important visual/text evidence

For an agent:

    Decision / Action / Outcome
        ↑
    Important trajectory evidence

In other words, the explanatory object changes from evidence surrounding a model prediction to **states, observations, actions, history, and interactions across time**.

---

## 11. Core Principle

Do not ask only:

> "How do I explain the agent?"

Ask:

> **"What exactly am I trying to explain in the agent's trajectory?"**

That choice determines:

    Explanation Target
          ↓
    Explanation Method
          ↓
    Evaluation Strategy
          ↓
    Evidence for the Explanation

This is a fundamental step in designing Agent Explainability research.