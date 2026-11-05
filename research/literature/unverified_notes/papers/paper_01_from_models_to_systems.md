# Paper 01 — From Models to Systems: A Survey of Explainability for Tool-Augmented Language Models and AI Agents

## Paper Type

Survey / Research Overview

## 1. Problem

Traditional XAI is largely model-centric and often assumes a relatively self-contained model:

`Input → Model → Output`

Tool-augmented and agentic systems instead involve:

`Input → LLM → Tool Selection → Tool Execution → Observation → New Decision → ...`

Therefore, conventional model-level explanations may not adequately explain the behavior of the complete system.

## 2. Explanation Object

The explanation target expands from a single model prediction to **tool-augmented system behavior**, including:

- Tool/action selection
- Tool invocation
- Tool results
- Execution traces
- Subsequent decisions
- Overall system trajectory

The key shift is:

> **Explain not only the model, but how the model + tools + execution process produce behavior.**

## 3. Explanation Levels

The survey motivates thinking about explanations at multiple levels:

`Model-level → Tool-level → Tool-result/evidence → System/trajectory-level`

### Tool-level

Explains a local event:

> Why did the agent select or invoke this tool?

### System/trajectory-level

Explains relationships across events:

> How did tool use, observations, decisions, and subsequent actions collectively produce the outcome?

Trajectory-level explanation is therefore not simply a collection of local explanations; it also concerns **dependencies between events across the execution**.

## 4. Main Difficulty

Agentic systems contain multiple interacting factors:

`Model state + Prompt + History + Tools + Tool outputs + Retrieved evidence + External environment`

These factors can influence later decisions across multiple execution steps.

Therefore, the challenge is not only identifying individual factors, but understanding how they **interact across the trajectory**.

## 5. Evaluation Challenge

A generated explanation may be coherent or plausible without faithfully representing the factors that influenced system behavior.

Therefore:

> **Explanation generation ≠ explanation validation**

Evaluation should consider the actual system behavior and execution trajectory rather than relying only on self-generated rationales or final-answer correctness.

## 6. Main Research Gaps

Important unresolved problems include:

- Faithful explanation of tool-augmented systems
- System/trajectory-level explanation
- Causal attribution across multiple execution steps
- Evaluation of explanation faithfulness
- Standardized evaluation protocols and benchmarks
- Explanation of complex or long-horizon agent behavior

## 7. Key Takeaway

The main conceptual shift from this survey is:

`Traditional XAI: Model → Prediction → Explanation`

`Agent Explainability: System → Trajectory → Explanation → Evidence → Evaluation`

The core research challenge is:

> **How can we produce and systematically evaluate faithful explanations for the behavior of complex tool-augmented and agentic systems?**

## 8. Connection to My Learning

This paper reinforces the concepts already learned:

- **Trajectory:** the primary behavioral record
- **Explanation target:** must be explicitly defined
- **Tool-level vs system-level:** different explanation granularity
- **Faithfulness:** plausible explanations are not automatically trustworthy
- **Counterfactual evaluation:** behavior can be tested through intervention

### Final takeaway

> **Agent Explainability is not simply XAI applied to an LLM; it is explainability of a larger interactive system whose behavior emerges from model decisions, tools, observations, and execution history.**