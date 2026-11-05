# 04 — Explanation Types & Methods

## 1. From "What to Explain?" to "How to Explain It?"

After identifying the explanation target, the next question is:

> **How can the explanation be generated or obtained?**

Different methods provide different kinds and strengths of evidence.

The main approaches learned are:

1. Intrinsic explanations
2. Post-hoc explanations
3. Self-explanations
4. Trace-based explanations
5. Attribution-based explanations
6. Counterfactual explanations

These approaches can also be combined in a single explainability system.

---

## 2. Intrinsic Explanations

An **intrinsic explanation** is built into the agent's decision process or architecture.

The system is designed so that its decision process contains interpretable structure.

Example:

    State
      ↓
    Explicit rule:
    "If retrieval confidence < threshold,
    retrieve another document"
      ↓
    Action

Explanation:

> "The agent retrieved another document because retrieval confidence was below the defined threshold."

The explanation comes directly from an interpretable decision mechanism.

### Key idea

> **The decision process is interpretable by design.**

---

## 3. Post-hoc Explanations

A **post-hoc explanation** is generated after the agent has already produced its behavior.

Conceptually:

    Agent
      ↓
    Decision / Action
      ↓
    Post-hoc Explainer
      ↓
    Explanation

Example:

    Agent:
    retrieve(Document B)

    Explainer:
    "Document B was selected because Document A
    did not contain the required information."

The explanation process is separate from the original decision process.

### Key idea

> **Behavior happens first; explanation is produced afterward.**

---

## 4. Self-Explanation

In a self-explanation approach, the agent or underlying LLM is asked to explain its own behavior.

Example:

> "Why did you choose Tool A?"

Agent:

> "I chose Tool A because the question required current information."

This is convenient and easy to implement, but it creates an important trustworthiness problem:

> **The decision-maker is also acting as the explainer.**

The generated rationale may be plausible without accurately representing the actual factors that influenced the decision.

Therefore:

> **A self-generated explanation should not automatically be treated as evidence of causality or faithfulness.**

---

## 5. Trace-Based Explanation

A **trace-based explanation** uses the actual execution trace of the agent as evidence.

Example:

    Step 1:
    User asks question

    Step 2:
    Agent retrieves Document A

    Step 3:
    Document A contains disease information
    but lacks tribe information

    Step 4:
    Agent retrieves Document B

    Step 5:
    Document B contains tribe information

    Step 6:
    Agent produces the answer

An explanation can then be constructed from the observed trace:

> "Document A was insufficient because it lacked information about the tribe, so the agent retrieved Document B."

The important advantage is that the explanation can reference **observable execution events** rather than relying only on the agent's self-report.

---

## 6. Attribution-Based Explanation

An attribution-based approach attempts to identify:

> **Which inputs, observations, state variables, or previous events contributed to the agent's behavior?**

Example:

    Agent chooses:
    retrieve(Document B)

    Potential influencing factors:

    - User query
    - Current state
    - Document A
    - Previous tool result
    - Memory
    - Retrieval score

The goal is to estimate which factors were important to the decision.

### Connection to VLM Explainability

For a VLM:

    Prediction
       ↑
    Important image patches / tokens

For an agent:

    Decision / Action
       ↑
    Important state variables / observations / events

The underlying idea of identifying influential information is similar, but the explanatory object changes from model inputs around a prediction to **information distributed across an agent trajectory**.

---

## 7. Counterfactual Explanation

A **counterfactual explanation** asks:

> **What would have happened if an important condition had been different?**

Example:

    Original:
    Document A is insufficient
      ↓
    Agent retrieves Document B

    Counterfactual:
    Document A now contains the missing information
      ↓
    Agent is executed again

If the agent no longer retrieves Document B, this provides behavioral evidence that the changed information influenced the decision.

The basic process is:

    Claim
      ↓
    Identify claimed factor
      ↓
    Intervene on the factor
      ↓
    Re-run the agent
      ↓
    Compare behavior
      ↓
    Evaluate the explanation

---

## 8. Counterfactuals Should Be Actual Interventions

There is an important distinction between:

    "What would you do if Document A
    contained the missing information?"

and:

    Modify Document A
      ↓
    Actually execute the agent
      ↓
    Observe the new behavior

The first produces a **generated hypothetical**.

The second provides **behavioral evidence**.

For faithfulness research, actual interventions are generally more informative than simply asking the LLM to imagine a counterfactual.

---

## 9. These Methods Can Be Combined

Real research systems do not necessarily use only one method.

A possible pipeline is:

    Agent
      ↓
    Execution Trace
      ↓
    Attribution Analysis
      ↓
    Counterfactual Intervention
      ↓
    Explanation Generator
      ↓
    Final Explanation

For example:

- The trace records what happened.
- Attribution identifies potentially influential factors.
- Counterfactual testing investigates whether those factors actually affect behavior.
- An explanation generator converts the evidence into understandable language.

---

## 10. Different Methods Provide Different Evidence

Consider:

    Agent:
    retrieve(Document B)

### Self-explanation

> "I retrieved B because A was insufficient."

This is a **rationale** generated by the agent.

### Trace-based evidence

    Document A retrieved
      ↓
    A lacks required information
      ↓
    Document B retrieved

This provides **observational evidence**.

### Counterfactual evidence

    Modify A so it contains the missing information
      ↓
    Agent no longer retrieves B

This provides stronger **behavioral evidence** that the proposed factor influenced the decision.

Therefore:

> **Not all explanations have the same evidential strength.**

---

## 11. Explanation vs Rationale

An important distinction:

**Rationale**

> A stated reason or justification, often generated by the model.

**Explanation**

> An account of why a behavior occurred, ideally supported by evidence.

A model-generated rationale can be useful, but it should not automatically be interpreted as the true causal explanation.

This is why later evaluation focuses on:

- Faithfulness
- Behavioral testing
- Counterfactual validity
- Evidence quality

---

## 12. Quick Comparison

| Method | Main idea | Main strength | Main concern |
|---|---|---|---|
| Intrinsic | Interpretable by design | Decision process is explicit | May restrict system design |
| Post-hoc | Explain after behavior | Flexible | Explanation may not reflect actual cause |
| Self-explanation | Agent explains itself | Simple and natural | Can produce plausible but unfaithful rationales |
| Trace-based | Use execution trace | Observable behavioral evidence | Trace may not reveal true causal factors |
| Attribution-based | Identify influential factors | Highlights relevant evidence | Influence may be correlational |
| Counterfactual | Change a factor and observe behavior | Stronger behavioral/causal evidence | Requires controlled interventions |

---

## 13. Core Framework

The connection between the previous and current module is:

    What do we explain?
            ↓
    Action / Decision / Plan / Evidence / Outcome / Trajectory
            ↓
    How do we explain it?
            ↓
    Intrinsic / Post-hoc / Trace / Attribution /
    Self-explanation / Counterfactual
            ↓
    How do we know it is good?
            ↓
    Faithfulness / Plausibility / Usefulness / Evaluation

---

## 14. Key Takeaways

1. There is no single explanation method suitable for every agent behavior.
2. **Intrinsic** explanations come from interpretable decision mechanisms.
3. **Post-hoc** explanations are generated after behavior occurs.
4. **Self-explanations** are convenient but can be unfaithful.
5. **Trace-based explanations** use observable execution history.
6. **Attribution-based explanations** identify potentially influential factors.
7. **Counterfactual explanations** test behavior under changed conditions.
8. Methods can be combined to obtain stronger explanations and stronger evidence.
9. The distinction between a **plausible rationale** and a **faithful explanation** is fundamental to trustworthy Agent Explainability.