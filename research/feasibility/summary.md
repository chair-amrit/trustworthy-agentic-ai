# DABStep Feasibility Summary

## Project Context

This minor project studies uncertainty in multi-step LLM data-analysis agents. The core question is why an agent's uncertainty sometimes disagrees with its actual correctness during multi-step execution, and what observable factors explain these mismatches, including uncertain-but-correct and confident-but-wrong cases.

Phase 1 measures uncertainty using sampling disagreement from a frozen state/prefix, verbalized confidence, and logit-based measures, together with step-level correctness. Phase 2 identifies mismatch patterns from trajectories and tests them through controlled interventions. The current scope is one controlled data-analysis environment.

## Why This Feasibility Check

The DABStep benchmark (Adyen) provides final ground-truth answers but not intermediate-step correctness. Since the study requires objective step-level correctness, this feasibility check tested whether such correctness can be defined for DABStep tasks.

## Method

- Six tasks were selected from the DABStep dev split, the only split with public answers: 5, 49, 1305, 1753, 1871, and 2697 (2 easy, 4 hard). Task 70 was excluded because its public answer is "Not Applicable" and the manual does not define a fraud-rate fine threshold, so it has no real intermediate steps.
- Each task was solved by hand in pandas, one step per cell, with intermediate values recorded.
- A step is considered **Checkable** only when an independent computation gives a single deterministic value, such as a count, shape, number, or set. A step is **Not checkable** when it depends on a judgment call, ambiguous definition, or multiple equally valid approaches.
- Checkability is defined as:
  `checkable steps / total steps`
- The decision rule set in advance was: if most steps are checkable, DABStep remains the testbed; if very few are checkable, a separate task set would be built.

## Results

| Task | Steps | Checkable | Ratio |
|------|-------|-----------|-------|
| 5    | 3     | 3         | 1.00  |
| 49   | 8     | 7         | 0.88  |
| 1305 | 5     | 4         | 0.80  |
| 1753 | 6     | 5         | 0.83  |
| 1871 | 7     | 6         | 0.86  |
| 2697 | 7     | 5         | 0.71  |
| **Total** | **36** | **30** | **0.83** |

Final answers were reproduced for tasks 5, 49, 1305, 1753, and 1871. For task 2697, the selected ACI (E) was reproduced, but the fee value was not; the public answer gives 13.57.

The six non-checkable steps were: task 49 (choice of fraud definition: count vs. volume vs. rate; the manual defines fraud as fraudulent volume / total volume, and only that reproduces the public answer), task 1305 (interpreting "average fee" as an unweighted mean over matching rules), task 1753 (interpreting "applicable" as a merchant-level match plus at least one matching transaction), task 1871 (interpretation of the question), and task 2697 (the fee aggregation convention and the reported fee value).

Task 1871's public answer contains floating-point noise (-0.94810300000017 versus -0.948103), so future checking must use a tolerance of 1e-9.

For task 2697, 12 per-transaction variants and 8 aggregate-volume variants were tested; none reproduced 13.57. ACI E was the lowest-fee choice under strict matching in both mean and minimum aggregation.

## Caveats

1. The unchecked steps are all interpretation or definition steps. They were validated only through the public final answer, not through an independent check.
2. Only the 10 dev tasks have public answers. The 450-task main split has hidden answers, so the verified pool is small. Scaling up therefore requires building step-level checkers.
3. Task 2697's fee value is not reproduced. Some ground truth therefore cannot currently be matched; such steps should be tagged and excluded from the uncertainty-correctness analysis rather than counted as agent errors.
4. Step granularity was chosen by the author when decomposing each task, so the checkability ratio is specific to this decomposition and should be treated as an estimate, not a benchmark property.

## Decision

By the pre-set decision rule, 0.83 indicates that most steps are checkable, so DABStep remains the testbed. Interpretation steps will be handled through explicit documented choices, while unreproducible steps will be excluded from analysis.

## Hypotheses

These are hypotheses for future agent experiments, not results. No agent has been run yet.

- An agent may be confidently wrong when it uses total fraud count or fraud volume instead of the manual's fraud-rate definition (task 49), potentially producing NL instead of BE.
- An agent may stop at the 47 merchant-level fee rules instead of identifying the 34 rules that also match at least one March transaction (task 1753).
- An agent may apply the changed rate to all January transactions instead of only the 12 transactions matching fee rule 384 (task 1871).

## Artifacts

- `research/feasibility/reference_tasks.md`: step-level reference solutions for the six tasks
- `research/feasibility/fee_rules.py`: shared fee-rule matching helpers

## Next Steps

1. Review the testbed decision with the guide.
2. Build automatic step-level checkers from the reference solutions.
3. Pilot a small open-weight model (for logits) and an API model on a few of these tasks, with trajectory logging and frozen-prefix sampling.