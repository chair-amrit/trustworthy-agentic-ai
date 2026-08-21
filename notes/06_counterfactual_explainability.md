# 06 — Counterfactual Agent Explainability

## 1. What Is a Counterfactual?

A counterfactual asks:

> **What would the agent have done if an important condition had been different?**

Instead of only asking:

> "Why did the agent choose Tool A?"

we ask:

> "What would happen if the supposed reason for choosing Tool A were changed?"

Example:

    Original:
    Question requires current information
      ↓
    Agent selects Tool A

    Counterfactual:
    Question does not require current information
      ↓
    Agent is executed again

The difference between the two executions provides behavioral evidence about what influenced the decision.

---

## 2. Basic Counterfactual Procedure

A basic counterfactual experiment follows:

    1. Observe original behavior
           ↓
    2. Identify the explanation claim
           ↓
    3. Identify the claimed important factor
           ↓
    4. Intervene on that factor
           ↓
    5. Re-run the agent
           ↓
    6. Compare original and counterfactual behavior

The main idea is:

> **Claim → Intervention → Re-execution → Behavioral comparison → Evidence**

---

## 3. Counterfactual vs Normal Explanation

### Normal explanation

Question:

> Why did you choose Tool A?

Agent:

> "I chose Tool A because current information was required."

This gives a stated rationale.

### Counterfactual explanation

Question:

> What would happen if current information were not required?

Then the modified scenario is actually tested.

If the agent changes its behavior, the result provides stronger evidence that the claimed factor influenced the decision.

---

## 4. Counterfactuals Should Be Actual Interventions

There is an important difference between:

    Asking the LLM:
    "What would you do if Document A
    contained the missing information?"

and:

    Modify Document A
          ↓
    Actually execute the agent
          ↓
    Observe its behavior

The first produces a **generated hypothetical**.

The second provides **behavioral evidence**.

For faithfulness research, actual interventions are therefore more useful than simply asking an LLM to imagine what would happen.

---

## 5. What Is an Intervention?

An **intervention** means deliberately changing a factor and observing the resulting agent behavior.

Possible intervention points include:

- User input
- Agent state
- Retrieved evidence
- Memory
- Tool availability
- Tool output
- Previous action
- Previous observation
- Agent communication
- Another agent's message

Example:

    Original:
    Tool A is available
      ↓
    Agent selects Tool A

    Intervention:
    Tool A is unavailable
      ↓
    Agent selects Tool B

This lets us study whether tool availability influenced the decision.

---

## 6. Counterfactuals Can Target Different Behaviors

Counterfactual testing can be applied to different explanation targets.

### Action Counterfactual

Question:

> What change would make the agent choose a different action?

Example:

    Original → search_web()

    Counterfactual → search_database()

---

### Plan Counterfactual

Question:

> What change would make the agent follow a different sequence?

Example:

    Original:
    Search → Retrieve → Verify → Answer

    Counterfactual:
    Search → Answer

This helps investigate why verification was included in the plan.

---

### Evidence Counterfactual

Question:

> What happens when the evidence influencing the decision is changed?

Example:

    Evidence A
       ↓
    Agent selects B

    Change Evidence A
       ↓
    Agent selects C

This suggests that the evidence influenced the decision.

---

### Outcome Counterfactual

Question:

> What happens to the final outcome when an earlier condition changes?

Example:

    Original:
    Tool A → Result X → Answer X

    Counterfactual:
    Tool A → Result Y → Answer Y

---

## 7. Counterfactual Trajectories

In agent systems, we are often interested in comparing **trajectories**, not only final outputs.

Example:

    Original trajectory:

    State₀
      ↓
    Search A
      ↓
    Observation X
      ↓
    Search B
      ↓
    Answer

    Counterfactual trajectory:

    State₀'
      ↓
    Search A
      ↓
    Observation Y
      ↓
    Answer

The important question becomes:

> **How did changing X → Y change the subsequent trajectory?**

This is more informative than simply comparing two final answers.

---

## 8. Minimal and Controlled Counterfactuals

A useful experimental principle is:

> **Change as little as possible.**

Suppose we want to test whether missing information in Document A caused retrieval of Document B.

A controlled experiment would be:

    Original:
    Document A = incomplete

    Counterfactual:
    Document A = complete

Everything else should remain as consistent as possible.

Avoid simultaneously changing:

- User query
- Model
- Prompt
- Tools
- Documents
- Temperature
- Memory

Changing multiple variables makes it difficult to determine what actually caused the behavioral difference.

---

## 9. Example: Testing Document Sufficiency

Consider:

    User Question
          ↓
    Retrieve A
          ↓
    Evaluate A
          ↓
    If insufficient → Retrieve B
          ↓
    Answer

Suppose the explanation is:

> "The agent retrieved B because A lacked disease information."

Create two conditions.

### Condition 1 — Original

    A lacks disease information
      ↓
    Agent execution

### Condition 2 — Counterfactual

    A contains disease information
      ↓
    Agent execution

Suppose repeated runs produce:

    Original:
    Retrieve B = 96/100 runs

    Counterfactual:
    Retrieve B = 8/100 runs

The large behavioral difference supports the claim that the availability of disease information in A influences the decision to retrieve B.

---

## 10. Interpreting Weak Counterfactual Effects

Suppose instead:

    Original:
    Retrieve B = 93/100 runs

    Counterfactual:
    Retrieve B = 88/100 runs

The intervention had little effect.

Therefore:

> The proposed factor is probably not the primary determinant of the behavior.

However, this does **not** prove that the agent is random.

Other factors may be influencing the decision, such as:

- State/history
- Other evidence
- Tool descriptions
- Prompt structure
- Learned behavior
- Stochasticity
- Interactions between variables

Further controlled experiments are required.

---

## 11. Multi-Agent Counterfactuals

Counterfactual reasoning becomes especially useful in multi-agent systems.

Example:

    Agent A
       ↓
    Message
       ↓
    Agent B
       ↓
    Decision

To test whether A's message influenced B:

### Original

    Agent A:
    "Evidence A is reliable."
       ↓
    Agent B:
    Accepts evidence A

### Counterfactual

    Agent A:
    "Evidence A is unreliable."

    or

    Agent A sends no reliability message

       ↓

    Observe Agent B's decision

If B's behavior changes significantly, this provides evidence that A's communication influenced B.

---

## 12. Counterfactual vs Testing a Different Variable

A controlled experiment must match the research question.

Suppose the question is:

> Did Research Agent A's message influence the Verifier?

Changing the reliability of the evidence itself tests:

> Does evidence quality influence the Verifier?

That is a different causal question.

Therefore:

> **The intervention must target the factor specified by the explanation claim.**

---

## 13. Counterfactuals and Faithfulness

The connection to Module 5 is:

    Explanation claim
          ↓
    Identify claimed cause
          ↓
    Counterfactual intervention
          ↓
    Observe behavioral change
          ↓
    Evidence for or against faithfulness

Therefore:

> **Counterfactual testing is one practical way of investigating whether an explanation is faithful to agent behavior.**

---

## 14. Limitations

Counterfactual evidence must still be interpreted carefully.

Changing one factor can accidentally change other properties.

For example, modifying a document may change:

- Semantic similarity
- Retrieval score
- Document length
- Wording
- Token distribution

Therefore, a good counterfactual experiment requires:

- Controlled interventions
- Clear baselines
- Repeated trials
- Appropriate control variables
- Comparison of both actions and trajectories

---

## 15. Practical LangGraph Connection

A simple LangGraph experiment can record:

    Original:
    state
    decision
    action
    observation
    next_state
    outcome

Then create:

    Counterfactual:
    modified_state
    decision
    action
    observation
    next_state
    outcome

Finally compare:

    Δ Decision
    Δ Action
    Δ Trajectory
    Δ Outcome

This forms the basis of a basic Agent Explainability experiment.

---

## 16. Key Takeaways

1. A counterfactual asks what would happen if an important condition were different.
2. Stronger counterfactual explanations use **actual interventions and re-execution**, not only hypothetical text generation.
3. The basic process is:

    Claim
      ↓
    Intervention
      ↓
    Re-run
      ↓
    Compare behavior
      ↓
    Evaluate evidence

4. Counterfactuals can target actions, plans, evidence, outcomes, and multi-agent communication.
5. In agent systems, comparing **trajectories** can be more informative than comparing only final outputs.
6. Good experiments change one relevant factor while controlling other variables.
7. A behavioral difference supports the idea that the changed factor influenced the decision, but experiments must still be carefully controlled before making causal claims.