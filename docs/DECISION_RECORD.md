# Decision record (written by Amrit, 4 November 2026)

I want to clarify the decisions we have reached so that we can move forward without repeatedly reopening the same questions.

Please treat the following as our current research direction and decision record. I do not want another general literature audit or another round of questioning whether we should pursue this direction. I want you to understand the conclusions, identify genuine methodological gaps, and help us develop the research rigorously.

# 1. Our research priority is settled

The December deadline is no longer relevant. I am willing to extend the project timeline substantially.

My priority is to develop a genuine, rigorous research contribution that could eventually be competitive for a prestigious ML venue such as ICML, ICLR, or NeurIPS.

I understand that no one can guarantee acceptance. I am not asking you to promise that this project will reach ICML. I want to maximize its research quality, originality, methodological rigor, and empirical strength.

We will not sacrifice research quality to finish quickly.

# 2. Our research direction

Our current overarching research question is:

"What observable intermediate factors contribute to failures in multi-step AI agents, and how are those factors related to uncertainty and correctness throughout execution?"

The project is about understanding failures inside multi-step agent execution, not merely evaluating final-answer accuracy.

We want to investigate:
- Where and how failures emerge during execution.
- What observable factors are associated with those failures.
- How factual correctness and process validity relate to each other.
- Whether uncertainty reflects actual intermediate correctness.
- How intermediate errors affect subsequent execution.
- Whether agents recover from errors or allow them to propagate.
- Whether controlled interventions can establish the contribution of suspected failure factors.

This is our current research direction, not an immutable title. The final title and narrower hypotheses can evolve after the methodology is established.

# 3. The most important methodological decision: no mandatory gold trajectory

We have discussed this extensively.

We do NOT want to impose one predefined sequence of steps on every task.

For example, if a task requires calculating transaction fees, an agent might use Python, SQL, or another valid sequence of operations. We cannot classify a trajectory as incorrect simply because it differs from a manually written reference solution.

Instead, we will establish a task specification before observing the model's execution.

It should define:
- The task objective.
- Required facts and constraints.
- Relevant source data.
- Expected output requirements.
- Independently verifiable facts or intermediate results where possible.
- Conditions that make operations valid.
- Rules for verifying the final answer.

The task specification defines what a valid solution must satisfy, not the exact sequence through which the agent must arrive there.

Alternative valid trajectories must be allowed.

# 4. We must distinguish different properties of a step

This is another major conclusion.

We cannot simply assign one binary correct/incorrect label to every intermediate step.

We need to distinguish:

**A. Local correctness**
Is the information, calculation, operation, or result correct?

**B. Task alignment**
Is the step justified by the task objective, constraints, or a legitimate verification requirement?

**C. Dependency**
Does a later operation or conclusion depend on this step?

**D. Downstream contribution**
Did the step contribute to, prevent, or have no demonstrated effect on subsequent failure?

These dimensions must not be collapsed.

Examples:
- A locally incorrect step may never be used downstream.
- A correct step may be unnecessary or irrelevant.
- An incorrect operation may produce a numerically correct answer by coincidence.
- A valid operation may fail because of an execution problem.
- A deviation from a manually constructed solution may still be completely valid.

We must also distinguish the earliest local error, earliest task-constraint violation, earliest consequential error, and earliest unrecovered error. They need not occur at the same point.

Unverifiable and ambiguous steps must remain separate from incorrect steps.

# 5. Our intended analytical structure

We have settled on the following overall research workflow:

1. **Task formalization:** Establish task requirements and independently verifiable constraints before model execution.
2. **Trajectory observation:** Record the agent's actual observable execution, including actions, tool calls, code, outputs, and decisions.
3. **Step-level diagnosis:** Identify local correctness, task alignment, and dependency validity.
4. **Failure and recovery analysis:** Determine where violations occur, how they affect subsequent execution, and whether the agent recovers.
5. **Uncertainty analysis:** Examine step-level and trajectory-level confidence in relation to actual correctness.
6. **Explainability analysis:** Investigate observable factors associated with failures and uncertainty–correctness mismatches.
7. **Counterfactual evaluation:** Intervene on selected suspected factors to investigate their downstream contribution.

This order matters.

We do not want to start by assuming which steps are failures. We first need a defensible way to identify and classify them.

# 6. Uncertainty and explainability

We want to study two different uncertainty targets:

- Step-level uncertainty: How confident is the agent about an individual operation or intermediate result?
- Trajectory-level uncertainty: How confident should the agent be that the overall task will eventually succeed, given the execution so far?

We understand that self-reported confidence is not automatically a calibrated probability.

Potential signals include token probabilities, explicit confidence, repeated-run disagreement, and other measurable uncertainty indicators. Their validity must be investigated rather than assumed.

Explainability should be based on observable execution evidence. We will not claim access to hidden internal reasoning.

We want to investigate relationships between observable factors, uncertainty, and correctness rather than simply generate explanations after a failure.

# 7. Counterfactual analysis

We have concluded that observing an early error followed by a failed answer is not sufficient to establish causation.

We want to investigate controlled interventions.

For example:
- Identify an incorrect intermediate filter.
- Replace its output with an independently verified correct result.
- Continue execution under controlled conditions.
- Compare downstream operations and final outcomes.

This can provide evidence about whether the suspected error contributed to the failure.

We must distinguish observational association from causal evidence and account for other possible contributing factors.

# 8. DABStep and the existing prototype

We are retaining DABStep as our current candidate benchmark and domain testbed.

We have already conducted a preliminary feasibility study on six tasks: 5, 49, 1305, 1753, 1871, and 2697.

Our previous feasibility analysis found that 30 of 36 examined intermediate results were objectively checkable. Some task-specific reference values remain unresolved.

We understand that DABStep does not provide comprehensive ground-truth intermediate trajectories.

That is not a reason to force a gold trajectory or immediately abandon the benchmark.

We will investigate whether we can construct reliable task specifications and independent verification procedures for a suitable subset.

We also understand that only ten development tasks currently have public answers in the material we inspected. We will not pretend that this automatically gives us 50–100 fully annotated tasks.

If more tasks are needed, we can develop our own reference specifications, use additional suitable benchmarks, or construct a carefully validated task set.

The existing agent prototype is preliminary. It currently has a scripted fake model, execution loop, parser, logger, and tests, but no real LLM backend or complete step-level evaluation system.

We will not mistake the existence of this prototype for research completion.

# 9. What is still unresolved — and what is NOT a reason to stop

We have not finalized:
- The exact operational definition and segmentation rules for a step.
- The precise task eligibility criteria.
- The annotation protocol and agreement methodology.
- The number of tasks and sample-size justification.
- The final model selection.
- The exact uncertainty metrics.
- The statistical analysis plan.
- The intervention design and controls.
- Whether DABStep alone is sufficient.
- The final title and narrow hypotheses.

These are legitimate research-design decisions.

We need to resolve them systematically, using literature, pilot experiments, sensitivity analysis, and evidence.

However, do not repeatedly question the overall research direction simply because these details remain open.

Also, I have not yet secured a second independent annotator. We should design the protocol so that independent annotation is possible and plan how to obtain it. This is a practical constraint to address, not a reason to abandon the project.

# 10. What I want from you now

I do not want another broad literature summary or another list of possible research topics.

I want you to act as a critical research adviser.

Help me turn the decisions above into a rigorous, defensible research methodology.

Our immediate priority should be:

**Evaluation Protocol v1.0**

It should resolve, in a logically ordered manner:

1. How a task is formally specified before execution.
2. What constitutes an observable intermediate step.
3. How step boundaries and granularity are determined reproducibly.
4. How task relevance is judged without imposing a gold trajectory.
5. How local correctness, operation validity, execution correctness, and conclusion validity are separated.
6. How dependencies and error propagation are represented.
7. How recovery and self-correction are identified.
8. How ambiguous and unverifiable steps are handled.
9. How independent annotation and reliability are measured.
10. How uncertainty is measured at step and trajectory levels.
11. How explainability is operationalized without claiming access to hidden reasoning.
12. How counterfactual interventions are designed to test suspected causal factors.

For every rule, explain:
- What exactly it means.
- Why it is necessary.
- How it will be applied.
- What evidence supports it.
- What limitations it introduces.
- How we can test whether the rule itself is reliable.

Do not invent universal thresholds or arbitrary definitions. Where evidence is insufficient, explicitly mark a proposal as tentative and design a pilot to validate it.

Most importantly, challenge my assumptions when necessary. Do not agree with me merely to be supportive. If a proposed dimension is redundant, a metric is unsuitable, or an experimental design cannot support a causal claim, explain why.

Our goal is not to make the project look impressive on paper. It is to produce results that are genuinely convincing to demanding ML reviewers.

Please treat this message as the current decision record for the project and proceed from here.

# 11. Decisions log

**D5. Execution isolation on Windows — decided 23 November 2026.**
Real runs happen on the Windows laptop, without Docker, WSL2 or a remote VM.
- The agent's working folder sits outside the repository.
- Answer files (oracles, contracts) are never placed inside the working folder.
- Code the agent runs gets no API keys (environment allowlist).
- Every logged code block is scanned for paths outside the working folder. Flagged runs are
  listed in runs/review_list.jsonl for manual review; a run is excluded if review confirms an
  attempt to access a path outside the working folder. Excluded runs are kept and reported,
  never deleted.
- Limitation: a local subprocess is not a secure sandbox. These rules reduce and detect
  leakage; they do not prevent it.
- Implemented 24–26 Nov 2026 (Track A, step 1); see CLAUDE.md for the limits.

**D13. Two tracks — decided 23 November 2026.**
- Track A (December minor project): extend the baseline-v0 harness.
- Track B (after exams): full LangGraph rebuild per docs/AGENT_SPEC_AND_BUILD_PLAN.md.
- Track A is the December deliverable. Track B keeps the research-quality goal from §1;
  the statement there that the December deadline is no longer relevant applies to Track B.

**D3. First model (Track A only) — decided 24 November 2026.**
- gemini-3.1-flash-lite via the Gemini API free tier, google-genai==3.6.1.
- Settings: temperature 1.0, thinking_level "minimal", max_output_tokens 1024.
  - Temperature: "For Gemini 3, we strongly recommend keeping the temperature parameter at
    its default value of 1.0" (https://docs.cloud.google.com/vertex-ai/generative-ai/docs/start/gemini-3-prompting-guide).
- Reason: gemini-3.5-flash-lite returned 503 UNAVAILABLE on 3 of 3 task-prompt calls on
  24 Nov 2026; gemini-3.1-flash-lite succeeded on the same request.
- Limitations:
  - The model ID has no version suffix.
  - Earliest shutdown is 7 May 2027 (released 7 May 2026;
    https://ai.google.dev/gemini-api/docs/deprecations).
  - Free-tier prompts may be used by Google (pricing page, free tier; not checked per model;
    https://ai.google.dev/gemini-api/docs/pricing).
  - Log-probability support not checked (not needed for Track A; Track B checks it).
- Track B's model is chosen after exams.
- 28 Nov 2026: exploratory batch with thinking_level low, max_output_tokens 4096 (thinking
  counts toward the limit). The setting for the repeated runs is chosen after this batch, on
  the same 10 exposed dev tasks; reported as exploratory.
- 28 Nov 2026: low-thinking batch scored 1/10 with 5 max_steps and ~2x tokens; repeated runs
  use minimal (D3 default).

**D1 (Track A), 27 Nov 2026: protocol v1 — rules 1 and 2 below.** The v0 and v1-prompt
batches of 26–27 Nov are kept as an exploratory pilot.
1. A reply with exactly one code block plus a FINAL ANSWER line: the code runs, the answer
   line is discarded, and the observation adds: "Your FINAL ANSWER was ignored because the
   reply also contained code. Check the output, then answer." Logged as
   final_answer_discarded: true.
2. A FINAL ANSWER given before any code block has run without error is rejected with:
   "Run code to check the data before giving a FINAL ANSWER." Logged as a format error.
- Protocol v0 (baseline behaviour) is kept and remains the default for the golden test.
- Also on 27 Nov 2026: HTTP 504 added to the retryable API statuses.
