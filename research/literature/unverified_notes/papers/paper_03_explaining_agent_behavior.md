# Paper 03 — Explaining Agent Behavior with Large Language Models

## Paper Type

Research paper on explaining agent behavior using an external LLM rather than relying on the original agent's self-explanation.

## 1. Problem

Self-explanations can be unreliable because an agent may generate plausible rationales that do not accurately reflect the factors behind its behavior.

The paper investigates whether **observed agent behavior can instead be provided to an external LLM to generate natural-language explanations**.

## 2. Core Approach

The paper represents the agent's observed behavior using a structured **decision-tree representation**.

The representation captures information about:

- Agent state / situation
- Available choices
- Actions taken
- Relevant behavioral context

The external LLM is then given this representation and generates a natural-language explanation.

Conceptually:

`Agent → Observed State/Action Behavior → Structured Representation → External LLM → Explanation`

The original agent does not need to explain itself.

## 3. Important Insight

This differs from self-explanation:

`Agent → Self-explanation`

versus:

`Agent → Observed behavior → External explainer → Explanation`

The second approach provides an explanation based on **externally observed evidence** rather than the agent's own rationale.

## 4. Evaluation

The paper uses participant studies to evaluate generated explanations.

Evaluation includes aspects such as:

- Human judgments of explanations
- Comparison with human-generated explanations
- Plausibility / interpretability
- Usefulness
- Hallucination-related behavior

The focus is mainly on whether people find the generated explanations understandable and useful.

## 5. Limitation

Observed behavior tells the explainer **what happened**, but does not necessarily reveal **why it happened**.

An external LLM can therefore still infer an unsupported reason or hallucinate a causal explanation.

Therefore:

> **External explanation is not automatically faithful simply because it uses observed behavior.**

## 6. Connection to Previous Papers

### Paper 1

Agent explainability should consider:

`Tools + Observations + Decisions + Execution Trajectory`

### Paper 2

Self-generated explanations can disagree with actual model behavior.

### Paper 3

Observed behavior can instead be provided to an **external explainer** to generate explanations.

Together:

`System behavior → External explanation`

but the resulting explanation still requires **faithfulness validation**.

## 7. Key Takeaway

> **Observed state/action behavior provides a stronger evidence base than relying only on self-explanation, but an external explainer can still infer unsupported causes.**

Therefore:

`Observed behavior → Explanation → Counterfactual / behavioral validation`

is a stronger research direction than treating either internal or external explanations as ground truth.