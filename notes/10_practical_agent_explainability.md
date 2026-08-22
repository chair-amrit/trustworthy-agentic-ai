# 10 — Practical Agent Explainability with LangGraph

## 1. Objective

The purpose of this stage is to move from conceptual understanding to a practical Agent Explainability workflow.

The basic objective is:

    Agent
      ↓
    Capture trajectory
      ↓
    Define explanation target
      ↓
    Form explanation hypothesis
      ↓
    Perform intervention
      ↓
    Compare behavior
      ↓
    Evaluate faithfulness

A simple LangGraph agent is sufficient for this work.

---

## 2. Minimal Agent Architecture

Do not start with a complex autonomous system.

Use a small graph such as:

    START
      ↓
    Router
      ↓
    ┌───────────────┐
    ↓               ↓
    Search Tool   Database Tool
    ↓               ↓
    └───────┬───────┘
            ↓
         Evaluator
            ↓
           END

The purpose is not to build a powerful agent.

The purpose is to create a controlled environment in which agent behavior can be observed and tested.

---

## 3. Trajectory Logging

The practical first step is to capture the agent's execution trajectory.

A simple record can contain:

    Step
    State
    Decision
    Action
    Tool
    Observation
    Next State

Example:

    Step 1

    State:
    User asks for current weather

    Decision:
    External information is required

    Action:
    weather_tool()

    Observation:
    32°C

    Step 2

    State:
    Weather result available

    Decision:
    Provide answer

    Action:
    generate_response()

    Outcome:
    "The current temperature is 32°C."

The important output is not only the final answer but the structured sequence of events.

---

## 4. Practical Trajectory Schema

A simple implementation can use a structure such as:

    {
        "step": 1,
        "state": ...,
        "decision": ...,
        "action": ...,
        "tool": ...,
        "observation": ...,
        "next_state": ...
    }

The exact schema can change depending on the LangGraph implementation.

The important requirement is that the stored data allows the execution to be reconstructed as:

    State
      ↓
    Decision
      ↓
    Action
      ↓
    Observation
      ↓
    Next State

---

## 5. Explanation Target

Before running an explainability experiment, define exactly what is being explained.

Example:

    Question:
    Why did the router select search_tool?

Explanation target:

    Decision / Tool choice

This should not be confused with:

    Why was the final answer correct?

The experiment must match the explanation target.

---

## 6. Explanation Hypothesis

Suppose the agent provides the explanation:

> "I selected the search tool because the user requested current information."

Convert this into a testable hypothesis:

    Claimed factor:
    Need for current information

    Behavioral target:
    Selection of search_tool

The explanation is now something that can be experimentally tested rather than simply accepted.

---

## 7. Baseline Execution

Run the original agent under normal conditions.

Example:

    User:
    "What is today's temperature?"

    Context:
    No current temperature available

    Trajectory:

    User query
      ↓
    Router
      ↓
    search_tool
      ↓
    Weather result
      ↓
    Final answer

Repeat the execution sufficiently many times to estimate the normal behavior.

This creates the baseline distribution.

---

## 8. Counterfactual Intervention

Now modify only the factor claimed by the explanation.

Original:

    Current information not available
      ↓
    Router
      ↓
    search_tool

Counterfactual:

    Current information already provided in context
      ↓
    Router
      ↓
    Observe selected action

The rest of the experimental setup should remain controlled as much as possible.

---

## 9. Repeated Counterfactual Runs

Run the modified condition repeatedly as well.

For example:

    Baseline:
    search_tool selected = 94/100

    Counterfactual:
    search_tool selected = 21/100

This indicates that providing the required information substantially changed tool-selection behavior.

The counterfactual result therefore provides behavioral evidence relevant to the explanation hypothesis.

---

## 10. Compare Trajectories

Do not compare only the final answer.

Example:

    Baseline trajectory:

    State₀
      ↓
    Router
      ↓
    search_tool
      ↓
    Observation
      ↓
    Answer

    Counterfactual trajectory:

    State₀'
      ↓
    Router
      ↓
    Direct answer
      ↓
    END

The important analysis includes:

    - Tool/action change
    - Decision change
    - Trajectory length
    - First divergence point
    - Final outcome

---

## 11. First Divergence Point

Suppose:

    Baseline:

    State₀
      ↓
    Action A
      ↓
    Action B
      ↓
    Action C

    Counterfactual:

    State₀'
      ↓
    Action A
      ↓
    Action D

The first divergence is:

    Action B → Action D

This point is useful for investigating where the intervention changed the agent's behavior.

---

## 12. Quantitative Comparison

Record measurable behavioral outcomes.

For example:

    P(search_tool | baseline) = 0.94

    P(search_tool | counterfactual) = 0.21

A simple effect measure is:

    ΔP =
    P(search_tool | baseline)
    -
    P(search_tool | counterfactual)

Therefore:

    ΔP = 0.94 - 0.21
       = 0.73

This represents a 73 percentage-point reduction in search-tool selection.

More advanced statistical analysis can be added later.

---

## 13. Practical Experiment Pipeline

A complete basic experiment is:

    LangGraph Agent
          ↓
    Trajectory Logger
          ↓
    Baseline Runs
          ↓
    Explanation Hypothesis
          ↓
    Identify Claimed Factor
          ↓
    Counterfactual Intervention
          ↓
    Counterfactual Runs
          ↓
    Trajectory Comparison
          ↓
    Behavioral Measurement
          ↓
    Faithfulness Assessment

This is the practical implementation of the concepts learned earlier.

---

## 14. What Makes This Research-Oriented?

Simply logging an agent trajectory is not yet an explainability experiment.

A stronger research setup is:

    Agent behavior
          ↓
    Explanation claim
          ↓
    Testable hypothesis
          ↓
    Controlled intervention
          ↓
    Repeated execution
          ↓
    Behavioral comparison
          ↓
    Evidence for or against the claim

The important transition is:

> **From "the agent says this is why" to "we experimentally test whether this factor actually influences behavior."**

---

## 15. Minimal First Experiment

A suitable first implementation should contain:

### Agent

One router and two tools.

### Logging

Store:

    state
    decision
    action
    observation
    step

### Explanation

One claimed reason for tool selection.

### Intervention

Change exactly one relevant factor.

### Repeated Runs

Run both baseline and counterfactual conditions multiple times.

### Evaluation

Compare:

    Tool-selection probability
    Trajectory
    First divergence point
    Final outcome

---

## 16. Expected Experimental Output

A simple result table could look like:

| Condition | Tool A | Tool B | Avg. Steps |
|---|---:|---:|---:|
| Baseline | 92% | 8% | 3.2 |
| Counterfactual | 31% | 69% | 2.4 |

This allows the experiment to produce an empirical result rather than only a qualitative explanation.

---

## 17. Core Principle

The practical Agent Explainability workflow can be summarized as:

    Behavior
      ↓
    Explanation hypothesis
      ↓
    Intervention
      ↓
    Re-execution
      ↓
    Behavioral + trajectory comparison
      ↓
    Faithfulness evidence

The goal is to make explanations **testable**, rather than treating generated rationales as automatically trustworthy.

---

## 18. Key Takeaways

1. A small LangGraph agent is sufficient for initial explainability experiments.
2. The first practical artifact should be a **trajectory logger**.
3. Every experiment should explicitly define the **explanation target**.
4. A self-explanation can be converted into a **testable hypothesis**.
5. Establish a baseline before intervention.
6. Change one relevant factor and keep other variables controlled.
7. Run repeated baseline and counterfactual trials.
8. Compare both **behavior and complete trajectories**.
9. Identify the **first divergence point** between executions.
10. Quantify behavioral differences instead of relying only on qualitative observations.
11. A practical research pipeline is:

    Agent
      ↓
    Trajectory
      ↓
    Explanation hypothesis
      ↓
    Intervention
      ↓
    Behavioral evidence
      ↓
    Faithfulness evaluation