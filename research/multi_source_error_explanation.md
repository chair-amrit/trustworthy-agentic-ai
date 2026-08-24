# Research Insight — Multi-Source Agent Error Explanation

## Motivation

Current literature suggests two complementary limitations:

- **Self-explanations** can be plausible but may not faithfully reflect the factors behind an agent's behavior.
- **External behavior-based explanations** use observable state/action traces but can still infer unsupported causes or hallucinate explanations.

Therefore, neither explanation source should be treated as ground truth.

## Proposed Idea

Use **internal and external explanations as hypothesis sources** for explaining agent errors.

`Agent Error`
→ `Internal Explanation`
→ Candidate Factors

`Agent Error`
→ `External Explanation`
→ Candidate Factors

Combine the candidate factors and test them experimentally.

## Proposed Workflow

`Agent Error`
→ `Internal + External Explanations`
→ `Candidate Error Factors`
→ `Prioritize Candidates`
→ `Counterfactual Intervention`
→ `Re-run Agent`
→ `Measure Behavioral Change`
→ `Evidence-Supported Error Explanation`

## Important Principle

The objective is **not** to recover the single true causal mechanism with certainty.

Instead:

> **Identify and validate behaviorally relevant factors that provide evidence for why the agent made an error.**

## Candidate-Factor Testing

Example:

`Internal explanation → X, Z`

`External explanation → X, Y`

Candidate set:

`{X, Y, Z}`

Test each candidate under controlled conditions.

Example:

`X → ΔBehavior = 0.42`

`Y → ΔBehavior = 0.05`

`Z → ΔBehavior = 0.18`

This provides evidence about the relative behavioral influence of the tested factors.

## Important Caveat

Agreement between internal and external explanations does **not** prove causality.

For example:

`Internal → X`

`External → X`

only makes X a stronger candidate for testing.

The actual behavioral evidence comes from intervention.

## Error-Explanation Goal

The refined research objective is:

> **Explain why an agent made an erroneous decision by using multiple explanation sources to generate candidate factors and validating those factors through controlled behavioral interventions.**

## Research Principle

> **Explanations are hypothesis sources, not truth sources. Behavioral intervention provides the evidence.**

## Potential Research Question

> Can combining internal self-explanations and external behavior-based explanations improve the identification of behaviorally relevant factors underlying agent errors when those factors are subsequently validated through counterfactual intervention?