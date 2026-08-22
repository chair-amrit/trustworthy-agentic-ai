# 09 — Faithfulness Testing & Experimental Design

## 1. Purpose

Generating an explanation is not enough. We need to test whether the explanation is supported by the agent's actual behavior.

The central research question is:

> **How can we experimentally determine whether an explanation is faithful?**

A basic structure is:

    Explanation Claim
          ↓
    Identify Claimed Factor
          ↓
    Intervene on That Factor
          ↓
    Observe Behavioral Change

---

## 2. Explanation Claim

Start with what the agent or explainer claims.

Example:

> "I selected Tool B because Tool A lacked the required information."

The claimed factor is:

> Tool A lacked the required information.

The experiment should directly test whether changing this factor changes the agent's behavior.

---

## 3. Baseline

First establish the original behavior before making changes.

Example:

    Condition A — Baseline

    Document A = incomplete
          ↓
    Agent execution
          ↓
    Agent retrieves Document B

The baseline gives us the reference behavior against which the intervention will be compared.

---

## 4. Intervention

Change the factor identified by the explanation while keeping other relevant conditions controlled.

Example:

    Condition B — Intervention

    Document A = complete
          ↓
    Agent execution
          ↓
    Observe whether B is retrieved

The objective is to determine whether changing the claimed factor changes the agent's behavior.

---

## 5. Control Variables

A strong experiment changes the relevant factor while keeping other important variables constant.

Control as much as possible:

- Model
- Prompt
- User query
- Tools
- Initial state
- Other documents
- Memory
- Temperature/settings
- Environment

For example:

    Changed:
    Document A completeness

    Controlled:
    User query
    Model
    Prompt
    Tools
    Other documents
    Initial state

Changing multiple variables simultaneously makes causal interpretation difficult.

---

## 6. Repeated Runs

LLM-based agents may behave stochastically, so a single execution is often insufficient.

Example:

    Baseline:
    Tool B selected = 96/100 runs

    Intervention:
    Tool B selected = 8/100 runs

This indicates a large behavioral difference.

Another example:

    Baseline:
    Tool B selected = 96/100 runs

    Intervention:
    Tool B selected = 93/100 runs

The intervention had little effect, so the proposed explanation is weakly supported.

Repeated runs help distinguish consistent effects from occasional variation.

---

## 7. Quantifying Behavioral Change

Instead of only saying:

> "The behavior changed."

Measure the change.

For example:

    P(B | baseline) = 0.96

    P(B | intervention) = 0.08

A simple behavioral effect can be represented as:

    ΔP = P(B | baseline) - P(B | intervention)

Therefore:

    ΔP = 0.96 - 0.08
       = 0.88

This represents an 88 percentage-point decrease in the probability of selecting B.

More advanced statistical tests can be added later, but the fundamental idea is:

> **Turn behavioral differences into measurable quantities.**

---

## 8. Ablation

**Ablation** means removing a component and observing what changes.

Possible ablations include:

- Remove a tool
- Remove memory
- Remove a retrieved document
- Remove an agent message
- Remove an agent
- Remove a planning step

Example:

    Full system:

    Agent A
      ↓
    Message
      ↓
    Agent B
      ↓
    Outcome X

    Ablation:

    Agent A
      ↓
    No message
      ↓
    Agent B
      ↓
    Outcome Y

If behavior changes, the removed component was behaviorally relevant.

However:

> **Ablation shows dependency, but does not automatically prove the exact causal mechanism.**

---

## 9. Perturbation vs Ablation

These concepts are related but different.

### Perturbation

A factor is **changed**.

    Document A:
    Incomplete
      ↓
    Complete

### Ablation

A factor is **removed**.

    Document A:
    Present
      ↓
    Removed

Both can be used to investigate behavioral dependence.

---

## 10. One-Variable-at-a-Time Testing

Suppose the Supervisor selects Agent A and we suspect several possible factors:

- A has database access
- A has greater expertise
- A performed well previously
- A's description appears more suitable
- B lacks a required tool

Do not change all of them at once.

Instead:

    Test 1:
    Give B database access

    Test 2:
    Equalize expertise

    Test 3:
    Remove previous performance information

    Test 4:
    Modify agent descriptions

Then compare each result against the same baseline.

This helps identify candidate influential factors.

---

## 11. Example: Delegation Experiment

Explanation:

> "The Supervisor chose Agent A because A has database access."

### Baseline

    A → database access
    B → no database access

          ↓

    Supervisor → Agent A

### Counterfactual 1

    A → database access
    B → database access

          ↓

    Supervisor → ?

If the Supervisor now frequently selects B, database access may be an influential factor.

### Counterfactual 2

    A → no database access
    B → no database access

          ↓

    Supervisor → ?

This tests whether database access is necessary for A's selection.

A clean experiment changes only the factor being tested.

---

## 12. Trajectory Comparison

Do not compare only final outputs.

Compare the trajectories.

### Original

    State₀
      ↓
    Retrieve A
      ↓
    Evaluate A
      ↓
    Retrieve B
      ↓
    Answer

### Counterfactual

    State₀'
      ↓
    Retrieve A
      ↓
    Evaluate A
      ↓
    Answer

Now investigate:

> **Where did the two trajectories first diverge?**

The first divergence can help identify where the intervention affected the agent's decision process.

---

## 13. First Divergence Point

Example:

### Original

    State₀
      ↓
    Action A
      ↓
    Action B
      ↓
    Action C
      ↓
    Answer X

### Counterfactual

    State₀
      ↓
    Action A
      ↓
    Action D
      ↓
    Answer Y

The first divergence is:

    Action B → Action D

This gives a focused point for investigating why the agent's behavior changed.

---

## 14. Faithfulness Is Not Necessarily Binary

Behavioral evidence is often a matter of degree.

Example:

    Baseline:
    B selected = 95%

    Intervention:
    B selected = 70%

The intervention affected behavior, but the factor is clearly not the only determinant.

Therefore:

> **A factor can be influential without being the sole cause of a decision.**

This is especially important for complex agent behavior.

---

## 15. Multiple Factors Can Influence One Decision

An agent decision may depend on several variables:

    Query
      +
    Previous state
      +
    Tool availability
      +
    Retrieved evidence
      +
    Memory
      +
    Agent history
          ↓
       Decision

Therefore, experiments may need to compare the relative influence of several candidate factors.

The research question can evolve from:

> "Is X the cause?"

to:

> "How much does X influence the decision compared with Y and Z?"

---

## 16. Practical Experimental Template

For each explanation claim, record:

    Explanation claim:
    What the agent/explainer says.

    Target behavior:
    Decision / action / outcome being explained.

    Claimed factor:
    What supposedly influenced the behavior.

    Baseline:
    Original condition and behavior.

    Intervention:
    Factor that was changed.

    Control variables:
    What was kept constant.

    Repeated trials:
    Number of runs.

    Behavioral result:
    Baseline vs intervention.

    Trajectory difference:
    Where the executions diverged.

    Quantified effect:
    Measured behavioral change.

    Interpretation:
    What the evidence supports.

    Limitation:
    What alternative explanations remain.

---

## 17. Example: Tool Selection

Agent explanation:

> "I called the web-search tool because the query required current information."

### Baseline

    Current-information query
      ↓
    Web search selected in 94/100 runs

### Intervention

Provide the required current information directly in the context while keeping the other conditions controlled.

    Same query + information already available
      ↓
    Web search selected in 21/100 runs

Interpretation:

> Providing the required information substantially reduced web-search usage, supporting the hypothesis that information availability influences tool selection.

However, we should not conclude that this is the only reason the agent uses web search.

---

## 18. Example: Weak Effect

Suppose:

    Baseline:
    Tool B selected = 92/100

    Intervention:
    Claimed factor removed
    Tool B selected = 89/100

The factor may have a small influence, but the effect is weak.

A better next step is to test other candidate factors under the same baseline conditions:

    Factor A
      ↓
    Measure ΔP

    Factor B
      ↓
    Measure ΔP

    Factor C
      ↓
    Measure ΔP

Then compare the behavioral effects.

For example:

    Database requirement → ΔP = 0.03
    Tool availability     → ΔP = 0.41
    Previous state        → ΔP = 0.27
    Prompt wording        → ΔP = 0.08

This would provide evidence that tool availability and previous state are more influential than the factor claimed in the original self-explanation.

Important:

> **The factor with the largest measured effect is evidence of a stronger influence, not automatically the sole cause or complete explanation.**

---

## 19. Research Mindset

A weak approach is:

    Agent
      ↓
    Ask:
    "Why did you do this?"
      ↓
    Accept the answer

A stronger approach is:

    Agent behavior
      ↓
    Explanation claim
      ↓
    Identify claimed factor
      ↓
    Intervention / ablation
      ↓
    Re-run repeatedly
      ↓
    Compare behavior
      ↓
    Compare trajectories
      ↓
    Quantify effect
      ↓
    Consider alternative explanations

The key research mindset is:

> **Do not only ask what explanation the agent gives. Ask what experiment could falsify that explanation.**

---

## 20. Key Takeaways

1. Start with an explicit **explanation claim**.
2. Identify the **claimed factor** responsible for the behavior.
3. Establish a **baseline**.
4. Change one relevant factor while controlling other variables.
5. Re-run the agent multiple times.
6. Measure the behavioral difference quantitatively.
7. Compare complete trajectories and identify the first divergence point.
8. Use **ablation** to study the effect of removing components.
9. Use **perturbation** to study the effect of changing components.
10. Do not assume that a behavioral effect proves a factor is the sole cause.
11. Consider multiple candidate factors and compare their relative effects.
12. The core experimental workflow is:

    Explanation Claim
          ↓
    Claimed Factor
          ↓
    Baseline
          ↓
    Controlled Intervention
          ↓
    Repeated Runs
          ↓
    Behavioral + Trajectory Comparison
          ↓
    Quantified Effect
          ↓
    Interpretation + Limitations