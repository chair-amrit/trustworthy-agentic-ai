# 09 — Faithfulness Testing & Experimental Design

## Objective

Test whether an explanation reflects factors that actually influence agent behavior.

`Explanation Claim → Claimed Factor → Intervention → Re-run → Behavioral Comparison`

## 1. Baseline

First measure the original behavior under fixed conditions.

Example:

`Document A incomplete → Agent retrieves Document B`

Use repeated runs rather than a single execution because LLM agents can be stochastic.

## 2. Intervention

Change the factor claimed by the explanation while keeping other relevant variables controlled.

Example:

`Document A incomplete → B selected`

vs.

`Document A complete → observe whether B is still selected`

## 3. Experimental Controls

Change **one relevant factor at a time**.

Keep constant where possible:

- Model
- Prompt
- User query
- Tools
- Initial state
- Other context
- Sampling/settings

Otherwise, behavioral differences cannot be attributed reliably to the tested factor.

## 4. Repeated Trials

Compare behavioral frequencies rather than individual runs.

Example:

`Baseline: B = 96/100`

`Intervention: B = 8/100`

This indicates a substantial behavioral effect.

If:

`Baseline: B = 96/100`

`Intervention: B = 93/100`

the claimed factor has little observed influence.

## 5. Quantifying Behavioral Effect

A simple measure:

`ΔP = P(action | baseline) − P(action | intervention)`

Example:

`P(B | baseline) = 0.96`

`P(B | intervention) = 0.08`

`ΔP = 0.88`

The effect can be reported as an 88-percentage-point reduction in B selection.

More advanced statistical tests can be added when needed.

## 6. Perturbation vs Ablation

**Perturbation:** change a factor.

`A incomplete → A complete`

**Ablation:** remove a factor/component.

`Tool A available → Tool A removed`

Both test behavioral dependence, but neither automatically proves a complete causal explanation.

## 7. Trajectory Comparison

Compare complete executions, not only final outputs.

Example:

`Original: State → Retrieve A → Verify → Retrieve B → Answer`

`Counterfactual: State → Retrieve A → Answer`

Identify the **first divergence point** to determine where the intervention changed the trajectory.

## 8. Multiple Candidate Factors

A decision may depend on several variables:

`Query + State + Memory + Tool availability + Evidence → Decision`

Test plausible factors individually under the same baseline.

Example:

`Database access → ΔP = 0.03`

`Tool availability → ΔP = 0.41`

`Previous state → ΔP = 0.27`

This provides evidence about **relative influence**, not proof that the largest factor is the sole cause.

## 9. Experimental Record

For each explanation claim, record:

- Explanation claim
- Explanation target
- Claimed factor
- Baseline condition
- Intervention
- Controlled variables
- Number of runs
- Behavioral result
- Trajectory divergence
- Quantified effect
- Interpretation
- Limitations

## 10. Research Principle

A weak approach is:

`Agent → "Why did you do this?" → Accept rationale`

A stronger approach is:

`Agent behavior → Explanation claim → Intervention → Repeated runs → Behavioral/trajectory comparison → Evidence`

> **Ask not only what explanation the agent gives, but what experiment could falsify that explanation.**

## Key Takeaway

> **Faithfulness testing converts an explanation from a plausible statement into a testable behavioral hypothesis.**