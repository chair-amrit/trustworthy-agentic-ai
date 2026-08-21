# 08 — Evaluation of Agent Explanations

## 1. Why Evaluation Matters

Generating an explanation is not enough.

A research system must also answer:

> **How do we know whether the explanation is actually good and trustworthy?**

An explanation can sound convincing while being unfaithful to the actual agent behavior.

Therefore, Agent Explainability requires **systematic evaluation**.

---

## 2. Core Evaluation Dimensions

The main dimensions learned are:

1. Faithfulness
2. Plausibility
3. Human usefulness
4. Counterfactual validity
5. Consistency

These dimensions answer different questions and should not be treated as interchangeable.

---

## 3. Faithfulness

Question:

> **Does the explanation reflect the factors that actually influenced the agent's behavior?**

Example:

    Explanation:
    "The agent selected Tool B because Tool A
    lacked the required information."

Test:

    Original:
    A incomplete
      ↓
    B selected

    Counterfactual:
    A complete
      ↓
    Observe agent behavior

If the behavior changes as predicted, the explanation gains behavioral support.

If B is still selected in most runs, the explanation is weakly supported.

### Key idea

> **Faithfulness is about whether the explanation is supported by the agent's behavior, not whether it sounds reasonable.**

---

## 4. Plausibility

Question:

> **Does the explanation make sense to a human?**

Example:

> "The agent selected Tool B because Tool A did not provide the required information."

A human may consider this a reasonable explanation.

However:

> **Plausibility ≠ Faithfulness**

An explanation can sound correct while not representing the actual factors influencing the decision.

---

## 5. Human Usefulness

Question:

> **Does the explanation help the intended user understand, evaluate, predict, or act on the agent's behavior?**

Example:

Technical explanation:

> "The policy transitioned to a different latent representation."

More useful explanation:

> "The agent used Tool B because Tool A did not provide the required information."

The second explanation is easier for a user to understand and apply.

Human usefulness can therefore be evaluated through user studies or task-based evaluations.

---

## 6. Counterfactual Validity

Question:

> **Does changing the factor mentioned in the explanation change behavior as predicted?**

Example:

    Explanation:
    "The agent selected B because A lacked tribe information."

    Intervention:
    Add tribe information to A.

    Expected:
    Agent should be less likely to retrieve B.

If behavior changes accordingly, the explanation receives counterfactual support.

If behavior does not change, the explanation is questionable.

Counterfactual validity is therefore closely related to faithfulness but focuses specifically on the **behavioral response to an intervention**.

---

## 7. Consistency

Question:

> **Does the explanation remain reasonably stable when equivalent conditions produce similar behavior?**

Example:

Run the same agent multiple times under equivalent conditions.

    Run 1:
    "Tool A was selected because..."

    Run 2:
    "Tool B was selected because..."

    Run 3:
    "Tool A was selected because..."

If the behavior and conditions are effectively equivalent but explanations vary substantially, this raises questions about explanation consistency.

Because LLM agents can be stochastic, consistency experiments should use appropriate controls and repeated trials.

---

## 8. Task Performance Is Separate

A major distinction:

> **Agent performance and explanation quality are different properties.**

Example:

    Task accuracy = 95%
    Explanation faithfulness = 40%

The agent performs well but provides weakly supported explanations.

Another possibility:

    Task accuracy = 60%
    Explanation faithfulness = 90%

The agent performs poorly but may accurately explain why it behaved that way.

Therefore, a serious evaluation should report task performance separately from explanation quality.

---

## 9. Practical Evaluation Methods

Different evaluation questions require different experiments.

### A. Behavioral Perturbation

Change an input or state variable and observe whether the behavior changes.

    Original:
    Action A

    Perturbed:
    Action B

This can help identify whether a factor influences the agent.

---

### B. Ablation

Remove a component and observe what changes.

Possible ablations include:

- Remove a tool
- Remove memory
- Remove a retrieved document
- Remove an agent message
- Remove an agent
- Remove a planning step

Example:

    Full system:
    A → B → C → Outcome X

    Without message from A:
    A → C → Outcome Y

This suggests that the removed communication may have influenced the system behavior.

---

### C. Counterfactual Intervention

Change the factor claimed by the explanation and re-run the agent.

    Explanation:
    "A caused B"

    Intervention:
    Change A

    Re-run

    Compare B

This provides behavioral evidence for or against the explanation.

---

### D. Trajectory Comparison

Compare complete executions rather than only final outputs.

    Original:
    Search → Retrieve A → Verify → Answer

    Counterfactual:
    Search → Retrieve A → Answer

Then analyze:

- Which actions changed?
- Which decisions changed?
- Which observations changed?
- Did the final outcome change?
- Where did the trajectories diverge?

---

## 10. Explanation Quality Is Multidimensional

Consider an explanation with these results:

| Dimension | Result |
|---|---|
| Plausibility | High |
| Faithfulness | Low |
| Usefulness | High |
| Counterfactual validity | Low |

This may be a **convincing but untrustworthy explanation**.

Another explanation might be:

| Dimension | Result |
|---|---|
| Plausibility | Medium |
| Faithfulness | High |
| Usefulness | Low |
| Counterfactual validity | High |

This may be scientifically stronger but poorly communicated.

Therefore:

> **There is no single dimension that completely defines explanation quality.**

---

## 11. Evaluation Must Match the Explanation Target

The evaluation experiment must test the factor relevant to the explanation being claimed.

Examples:

    Tool-choice explanation
          ↓
    Test tool-related factors

    Plan explanation
          ↓
    Test sequence/planning factors

    Communication explanation
          ↓
    Test message/communication factors

    Outcome explanation
          ↓
    Test factors affecting the final outcome

For example:

> "The Supervisor chose Agent A because A had database access."

A suitable intervention is to change database access or compare Agent A with another agent having the same capability.

Changing an unrelated factor would not properly test the explanation.

---

## 12. Example: Evaluating a Delegation Explanation

Explanation:

> "The Supervisor assigned the task to Agent A because A had access to the required database."

Baseline:

    A has database access
    B does not
      ↓
    A selected

Counterfactual:

    A has database access
    B also has database access
      ↓
    Observe delegation

If the Supervisor changes its selection when the supposed determining factor changes, the explanation gains support.

Other candidate factors can then be tested individually:

- Agent expertise
- Previous performance
- Agent description
- Tool availability
- Task wording
- Previous history
- Memory

This is controlled intervention-based testing.

---

## 13. Evaluation Pipeline

A useful overall structure is:

    Agent
      ↓
    Behavior / Trajectory
      ↓
    Explanation
      ↓
    Evidence
      ↓
    Evaluation

Evaluation can then include:

    Faithfulness
    Plausibility
    Usefulness
    Counterfactual validity
    Consistency

The important shift is:

> **Do not stop at explanation generation; validate the explanation.**

---

## 14. Research-Level Principle

A weak explainability study may do:

    Agent
      ↓
    Ask LLM:
    "Why did you do this?"
      ↓
    Generated explanation

A stronger study does:

    Agent behavior
      ↓
    Explanation claim
      ↓
    Identify claimed factor
      ↓
    Intervention / ablation
      ↓
    Re-run agent
      ↓
    Compare behavior
      ↓
    Evaluate faithfulness

The second approach provides empirical evidence rather than relying only on a plausible rationale.

---

## 15. Key Takeaways

1. Explanation generation and explanation evaluation are separate tasks.
2. **Faithfulness** asks whether the explanation reflects actual behavioral influences.
3. **Plausibility** asks whether the explanation sounds reasonable.
4. **Usefulness** asks whether the explanation helps the intended user.
5. **Counterfactual validity** tests whether changing a claimed cause changes behavior as predicted.
6. **Consistency** examines whether explanations remain stable under equivalent conditions.
7. Task performance should be reported separately from explanation quality.
8. Useful evaluation methods include:
   - Behavioral perturbation
   - Ablation
   - Counterfactual intervention
   - Trajectory comparison
   - Human evaluation
9. The evaluation method must match the **explanation target**.
10. The core principle is:

> **A good Agent Explainability system does not merely generate explanations; it provides evidence for why those explanations should be trusted.**