# DABStep Research Notes

## Paper

**DABStep: Data Agent Benchmark for Multi-step Reasoning**

DABStep is a benchmark designed to evaluate data-analysis agents on multi-step reasoning tasks involving real-world data.

Reference:

Egg, Alex, et al. "DABStep: Data Agent Benchmark for Multi-step Reasoning." arXiv preprint arXiv:2506.23719, 2025.

## Why DABStep Is Relevant

DABStep is relevant to this project because it provides a setting where an LLM-based agent must perform a sequence of data-analysis operations rather than simply answer a single question.

This makes it useful for studying the relationship between:

- intermediate agent behavior
- tool execution
- uncertainty
- correctness
- accumulated errors
- final task performance

The benchmark can therefore provide the task environment on top of which the project's uncertainty–correctness analysis can be developed.

## Task Structure

DABStep focuses on multi-step data-analysis problems.

The agent is expected to reason over data and perform analysis through executable operations rather than producing an answer entirely from language-model knowledge.

The benchmark contains:

- **450 tasks**
- **72 Easy tasks**
- **378 Hard tasks**

Tasks have verifiable final outcomes, allowing final-answer correctness to be evaluated objectively.

## Important Observation for This Project

DABStep provides a strong basis for evaluating **final correctness**, but the project's research question requires more than final-answer evaluation.

Our analysis needs to examine the agent's execution trajectory:

`State → Action → Tool Execution → Observation → Next State`

Therefore, intermediate correctness cannot simply be assumed to be available from the benchmark.

For our experiments, intermediate correctness will need to be defined using observable and testable artifacts where objective verification is possible.

Examples include:

- whether a tool call is valid
- whether code executes successfully
- whether an intermediate computation is correct
- whether an intermediate result satisfies a known condition
- whether the final answer is correct

## Difficulty

The benchmark contains a substantially larger number of Hard tasks than Easy tasks.

The reported distribution is:

| Difficulty | Tasks |
|---|---:|
| Easy | 72 |
| Hard | 378 |
| Total | 450 |

This is important for our research because task difficulty can potentially act as an observable factor when analyzing uncertainty–correctness relationships.

However, difficulty should not automatically be treated as a causal explanation. It should first be measured and then tested as a candidate factor.

## Relevance to Our Research Question

The benchmark gives us a suitable environment for asking questions such as:

- Does uncertainty increase before an incorrect action?
- Can an agent remain confident after an earlier error?
- Are high-uncertainty decisions necessarily incorrect?
- Does uncertainty change after successful or unsuccessful tool execution?
- Do accumulated errors affect later uncertainty?
- Does task difficulty influence uncertainty–correctness mismatch?
- Which trajectory factors are associated with high uncertainty + correct and low uncertainty + incorrect cases?

These questions connect DABStep's multi-step data-analysis setting to the project's central research problem.

## Limitation for Our Use

DABStep should be treated primarily as a **task and evaluation environment**, not as the complete experimental methodology for this project.

The benchmark's final correctness signal does not by itself provide the per-step labels required for trajectory-level uncertainty–correctness analysis.

Therefore, our implementation will need an additional trajectory logging and correctness-evaluation layer.

## Planned Use

The current plan is:

`DABStep Tasks`
→ `Our Multi-step Data-analysis Agent`
→ `Tool Execution`
→ `Trajectory Logging`
→ `Uncertainty Estimation`
→ `Correctness Evaluation`
→ `Mismatch Analysis`
→ `Factor Identification`
→ `Controlled Intervention`

The agent itself will be implemented separately so that the execution process and research instrumentation remain under our control.

## Current Status

This document records the role of DABStep in the research design.

The exact subset of tasks, tool configuration, agent architecture, intermediate correctness protocol, and uncertainty estimator are **not yet locked**.

Those decisions should be made after studying the benchmark in greater detail and testing the feasibility of obtaining reliable intermediate correctness signals.