# 05 — Faithfulness vs Plausibility

## 1. The Core Question

After generating an explanation, we need to ask:

> **Should we trust the explanation?**

An agent can generate an explanation that sounds correct without that explanation actually reflecting the factors that caused or influenced its behavior.

This creates two important concepts:

- **Plausibility**
- **Faithfulness**

---

## 2. Plausibility

**Plausibility** asks:

> **Does the explanation sound reasonable or make sense to a human?**

Example:

    Agent:
    retrieve(Document B)

    Explanation:
    "I retrieved Document B because Document A
    did not contain the required information."

This sounds reasonable.

Therefore, the explanation is **plausible**.

However, this does not prove that the stated reason actually caused the agent's behavior.

---

## 3. Faithfulness

**Faithfulness** asks:

> **Does the explanation accurately reflect the factors that actually caused or influenced the agent's behavior?**

Suppose the explanation is:

> "I retrieved Document B because Document A lacked tribe information."

We now perform an intervention:

    Original:
    Document A lacks tribe information
      ↓
    Agent retrieves Document B

    Counterfactual:
    Document A now contains tribe information
      ↓
    Agent still retrieves Document B

If changing the claimed cause does not significantly change the behavior, the explanation is not well supported.

Therefore:

> **Faithfulness is about behavioral evidence, not merely whether an explanation sounds convincing.**

---

## 4. Plausible Does Not Mean Faithful

This is one of the most important ideas in Agent Explainability.

An explanation can be:

    Plausible + Faithful
    → Good explanation

    Plausible + Unfaithful
    → Convincing but potentially misleading

    Implausible + Faithful
    → Behaviorally accurate but poorly communicated

    Implausible + Unfaithful
    → Poor explanation

The most dangerous case is:

> **Plausible but unfaithful.**

A convincing explanation can create trust even when it does not describe the actual decision factors.

---

## 5. Why This Problem Is Important for LLM Agents

LLMs are very good at producing coherent natural-language rationales.

For example:

> "I selected Tool A because the question required current information."

This sounds reasonable.

However, the actual decision may have been influenced by other factors, such as:

- Previous context
- Tool descriptions
- Prompt structure
- State/history
- Learned behavioral patterns
- Tool ordering
- Retrieved information
- Stochastic generation

The generated explanation alone does not establish which factor actually influenced the behavior.

Therefore:

> **Reasoning text or rationale ≠ causal evidence**

---

## 6. A Simple Faithfulness Test

Suppose the agent says:

> "I selected Tool A because the question required current information."

We can test the claim.

### Original condition

    Question requires current information
      ↓
    Agent selects Tool A

### Counterfactual condition

    Question does not require current information
      ↓
    Run the agent again

Then compare the behavior.

If the agent switches to another tool, this provides evidence that the claimed factor influenced the decision.

If the agent continues selecting Tool A, the explanation becomes questionable.

---

## 7. Example

Agent explanation:

> "I chose Tool B because Tool A lacked the required information."

Experiment:

    Original:
    A incomplete
      ↓
    B selected

    Intervention:
    A made complete
      ↓
    B still selected in 95/100 runs

Interpretation:

The result does **not** prove that the agent is random or that its decision-making is broken.

Instead, it suggests:

> **The incompleteness of A is probably not the primary factor determining the selection of B.**

Other factors may be influencing the decision.

---

## 8. Faithfulness Is Different from Task Performance

An agent can perform a task correctly while giving an unfaithful explanation.

Example:

    Task accuracy = 95%
    Explanation faithfulness = low

The agent performs well but may not accurately explain its behavior.

The reverse is also possible:

    Task accuracy = low
    Explanation faithfulness = high

The explanation may accurately describe why the agent made a poor decision.

Therefore:

> **Task performance and explanation quality should be evaluated separately.**

---

## 9. Counterfactual Testing as Evidence

A useful faithfulness workflow is:

    Explanation claim
          ↓
    Identify claimed factor
          ↓
    Intervene on that factor
          ↓
    Re-run the agent
          ↓
    Compare original and counterfactual behavior
          ↓
    Evaluate whether the behavior changed as predicted

For example:

    Claim:
    "B was selected because A lacked tribe information."

    Intervention:
    Add tribe information to A.

    Observation:
    Does the agent stop selecting B?

If yes, the claim gains behavioral support.

If no, the claim is weakly supported.

---

## 10. Repeated Runs Matter

LLM-based agents can be stochastic.

Therefore, a single execution is often insufficient.

Example:

    Original:
    B selected = 96/100 runs

    Counterfactual:
    B selected = 8/100 runs

This indicates a strong behavioral difference.

Instead:

    Original:
    B selected = 96/100 runs

    Counterfactual:
    B selected = 93/100 runs

The intervention had little effect, so the proposed explanation is weakly supported.

Repeated trials help distinguish a consistent behavioral effect from occasional variation.

---

## 11. Do Not Immediately Call Variation "Randomness"

Suppose:

    Original:
    B selected = 93%

    Counterfactual:
    B selected = 88%

We should not immediately conclude:

> "The remaining behavior is random."

The variation could result from:

- Stochastic generation
- Other untested factors
- Interactions between variables
- Experimental noise
- Hidden state/history

More controlled experiments are needed.

---

## 12. Important Research Distinction

There are two different claims:

### Claim A

> "The agent says X caused its decision."

This is a **self-reported rationale**.

### Claim B

> "Changing X causes the agent's decision to change."

This is **behavioral evidence supporting a causal relationship**.

Agent Explainability research is interested in moving from Claim A toward evidence for Claim B.

---

## 13. Faithfulness and Explanation Quality

A useful conceptual structure is:

    Explanation
        │
        ├── Plausibility
        │      "Does it make sense?"
        │
        └── Faithfulness
               "Is it supported by behavior?"

Faithfulness can then be investigated using:

    Intervention
       ↓
    Behavioral change
       ↓
    Counterfactual comparison

This is why faithfulness is central to trustworthy agent explanations.

---

## 14. Key Takeaways

1. **Plausibility** asks whether an explanation sounds reasonable.
2. **Faithfulness** asks whether the explanation reflects factors that actually influenced behavior.
3. A plausible explanation can still be unfaithful.
4. LLM-generated rationales should not automatically be treated as causal explanations.
5. Counterfactual interventions provide behavioral evidence for testing explanation claims.
6. Repeated trials are useful because agent behavior can be stochastic.
7. Do not interpret unexplained variation as randomness without further evidence.
8. **Task performance and explanation faithfulness are separate properties.**
9. The central principle is:

> **A convincing explanation is not automatically a faithful explanation.**