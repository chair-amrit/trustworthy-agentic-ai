# Paper 02 — Can LLMs Explain Themselves Counterfactually?

## Paper Type

EMNLP 2025 — Empirical study of self-generated counterfactual explanations (SCEs).

## 1. Problem

The paper investigates whether LLMs can **reliably explain their own predictions using counterfactual explanations**.

The central question is:

> If an LLM claims that changing X would make it predict Y, does its actual behavior agree when X is changed?

This directly tests the reliability of model-generated counterfactual explanations.

## 2. Explanation Target

The target is a **Self-Generated Counterfactual Explanation (SCE)**.

Conceptually:

`Original Input → Prediction A`

Model explanation:

> "If factor X were changed, I would predict B."

The claimed counterfactual is then actually evaluated.

## 3. Experimental Approach

The study evaluates SCE generation across multiple:

- Model families
- Model sizes
- Temperatures
- Datasets / tasks

The general procedure is:

`Original input → Model prediction → Generate SCE → Modify according to SCE → Re-evaluate model`

The key question is whether the **actual counterfactual prediction matches the prediction claimed by the explanation**.

## 4. Evaluation

The paper uses several evaluation measures, including:

### Generation (Gen)

Can the model successfully generate a usable counterfactual explanation?

### Validity (Val)

Does the actual prediction on the generated counterfactual match the target prediction claimed by the explanation?

### Edit Distance (ED)

How much does the generated counterfactual differ from the original input?

Lower edit distance generally indicates a more minimal counterfactual change.

The most important measure for the faithfulness question is **counterfactual validity**.

## 5. Key Finding

Models can generate counterfactual explanations that appear coherent, but their actual predictions can **disagree with their own counterfactual reasoning**.

Therefore:

> **A plausible self-generated counterfactual does not automatically represent faithful evidence of model behavior.**

The study also shows that model capability alone does not guarantee reliable counterfactual self-explanation.

## 6. Important Research Insight

The paper provides empirical support for the principle:

`Self-explanation → Hypothesis`

rather than:

`Self-explanation → Ground truth`

A useful workflow is:

`Self-explanation`
→ `Claimed factor`
→ `Counterfactual intervention`
→ `Actual behavior`
→ `Faithfulness evaluation`

Therefore, self-explanations can be useful as **starting points for investigation**, but they should be validated behaviorally.

## 7. Limitation

The study mainly evaluates relatively structured classification and mathematical tasks.

Extending the same evaluation to open-ended generation and complex agentic systems is substantially harder.

This leaves open questions around:

- Long-horizon agent trajectories
- Tool use
- Planning
- Multi-step decisions
- Multi-agent interactions

## 8. Connection to Agent Explainability

This paper directly supports the faithfulness framework developed earlier:

`Agent behavior`
→ `Explanation claim`
→ `Intervention`
→ `Behavioral comparison`
→ `Faithfulness evidence`

Its main contribution to this learning path is **empirical evidence that self-explanations can fail to match actual behavior**.

## 9. Key Takeaway

> **Treat a model-generated counterfactual explanation as a hypothesis, not as ground truth; validate it through actual counterfactual behavior.**