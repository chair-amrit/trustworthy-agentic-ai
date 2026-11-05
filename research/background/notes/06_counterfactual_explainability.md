# 06 — Counterfactual Agent Explainability

## Objective

Test agent explanations by changing a claimed factor and observing whether the agent's behavior changes.

`Explanation Claim → Intervention → Re-run → Behavioral Comparison → Evidence`

## 1. Counterfactual

A counterfactual asks:

> **What would the agent have done if an important condition had been different?**

Example:

`Original: A incomplete → Agent retrieves B`

`Counterfactual: A complete → Re-run agent`

The key is to **actually modify the condition and execute the agent**, not merely ask the LLM to imagine the alternative.

## 2. Intervention

An intervention deliberately changes one relevant factor.

Possible targets:

- User input
- State
- Retrieved evidence
- Memory
- Tool availability
- Tool output
- Previous observation
- Agent message

Example:

`Tool A available → Agent selects A`

vs.

`Tool A unavailable → Agent selects B`

## 3. Controlled Counterfactuals

Change as little as possible.

Keep constant where possible:

- Model
- Prompt
- Query
- Tools
- Initial state
- Other context
- Sampling/settings

Otherwise, it becomes difficult to determine what caused the behavioral change.

## 4. Counterfactual Trajectories

Compare the complete trajectories, not only final outputs.

Original:

`State₀ → Search A → Observation X → Search B → Answer`

Counterfactual:

`State₀' → Search A → Observation Y → Answer`

Important questions:

- Where did the trajectories first diverge?
- Which decision changed?
- Which action changed?
- Did the final outcome change?

## 5. Different Counterfactual Targets

### Action
What change would make the agent choose another action?

### Plan
What change would make the agent follow a different sequence?

### Evidence
What happens when the information influencing the decision changes?

### Outcome
What happens to the final result when an earlier condition changes?

### Multi-Agent
What happens if an agent, message, or interaction is changed or removed?

## 6. Example: Testing an Explanation

Claim:

> "The agent retrieved B because A lacked tribe information."

Experiment:

`A incomplete → B selected`

vs.

`A contains tribe information → re-run`

If B selection drops substantially, the explanation gains behavioral support.

If B is still selected in most runs, the claimed factor is probably not the primary determinant.

This does not prove randomness; other factors may be influencing the behavior.

## 7. Multi-Agent Counterfactual

To test whether Agent A's message influenced Agent B:

Original:

`A → "Evidence A is reliable" → B → Accept`

Counterfactual:

`A → "Evidence A is unreliable" → B → Observe`

or:

`A → No message → B → Observe`

A behavioral change supports the claim that A's communication influenced B.

## 8. Limitations

Changing a factor can unintentionally change other properties.

For example, modifying a document may alter:

- Retrieval score
- Semantic similarity
- Length
- Wording
- Token distribution

Therefore, counterfactual experiments require careful controls and repeated trials.

## Key Takeaway

> **A counterfactual explanation becomes scientifically useful when a claimed cause is actually intervened on and the resulting behavioral/trajectory change is measured.**