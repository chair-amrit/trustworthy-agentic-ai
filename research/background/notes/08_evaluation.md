# 08 — Evaluation of Agent Explanations

## Objective

Determine whether an explanation is **trustworthy and useful**, rather than merely well-written.

`Explanation → Evidence → Evaluation`

## 1. Core Evaluation Dimensions

### Faithfulness
Does the explanation reflect factors that actually influence the agent's behavior?

`Claim → Intervention → Behavioral comparison`

### Plausibility
Does the explanation sound reasonable to humans?

> Plausible ≠ Faithful

### Human Usefulness
Does the explanation help users understand, evaluate, predict, or act on the agent's behavior?

### Counterfactual Validity
Does changing the claimed factor change behavior as the explanation predicts?

### Consistency
Does the explanation remain reasonably stable under equivalent conditions?

## 2. Task Performance ≠ Explanation Quality

These must be evaluated separately.

Example:

`Task accuracy = 95%`

`Explanation faithfulness = 40%`

The agent performs well but may not explain its behavior faithfully.

Therefore:

> **Good task performance does not imply good explanations.**

## 3. Practical Evaluation Methods

**Behavioral perturbation:** change a factor and observe behavior.

**Ablation:** remove a component and observe what changes.

**Counterfactual intervention:** change the factor claimed by the explanation and re-run.

**Trajectory comparison:** compare original and counterfactual execution paths, including the first divergence point.

**Human evaluation:** measure understandability, plausibility, usefulness, or related user outcomes.

## 4. Match Evaluation to Explanation Target

The test must target the factor being explained.

`Tool-choice explanation → tool-related intervention`

`Plan explanation → sequence/planning intervention`

`Communication explanation → message intervention`

`Delegation explanation → agent capability/selection intervention`

`Outcome explanation → factors affecting final outcome`

Testing an unrelated variable does not properly validate the explanation.

## 5. Example

Claim:

> "Supervisor selected Agent A because A had database access."

Baseline:

`A has access, B does not → A selected`

Counterfactual:

`A has access, B also has access → observe selection`

If delegation changes substantially, the claim gains behavioral support.

If delegation barely changes, the explanation is weakly supported.

## 6. Explanation Quality Is Multidimensional

An explanation can be:

`High plausibility + Low faithfulness`

→ convincing but potentially misleading.

Or:

`High faithfulness + Low usefulness`

→ behaviorally informative but difficult for users to understand.

Therefore:

> **No single evaluation dimension completely defines explanation quality.**

## 7. Research Evaluation Pipeline

`Agent Behavior`

`↓`

`Explanation`

`↓`

`Claimed Factor`

`↓`

`Intervention / Human Evaluation`

`↓`

`Behavioral + User Evidence`

`↓`

`Explanation Evaluation`

## Key Takeaway

> **A serious Agent Explainability system does not stop at generating an explanation; it provides evidence for whether that explanation should be trusted.**