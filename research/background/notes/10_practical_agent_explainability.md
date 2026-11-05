# 10 — Practical Agent Explainability with LangGraph

## Objective

Move from conceptual Agent Explainability to a reproducible experiment:

`Agent → Trajectory → Explanation Hypothesis → Intervention → Behavioral Comparison → Faithfulness Evidence`

## 1. Minimal Experimental Agent

Use a small LangGraph agent:

`User → Router → Tool A / Tool B → Observation → Answer`

The goal is not agent performance; it is creating a **controlled environment for studying behavior**.

## 2. Trajectory Logging

Log enough information to reconstruct each execution:

`Step | State | Decision | Action | Tool | Observation | Next State`

Example:

`State₀ → Decision → search_tool() → Observation → State₁`

The stored trajectory becomes the behavioral record used for later analysis.

## 3. Explanation Hypothesis

Convert a self-explanation into a testable claim.

Example:

> "I selected the search tool because current information was required."

Record:

- **Target:** tool-selection decision
- **Claimed factor:** need for current information
- **Hypothesis:** changing information availability should change tool selection

## 4. Baseline vs Counterfactual

**Baseline:** run the original setup repeatedly.

**Intervention:** change only the claimed factor while controlling other relevant variables.

Example:

`No current information → search_tool`

vs.

`Current information provided → re-run agent`

Repeat both conditions because LLM-agent behavior can be stochastic.

## 5. Behavioral + Trajectory Analysis

Compare:

- Tool/action selection probability
- Decision changes
- First trajectory divergence
- Number of steps
- Final outcome

Example:

`P(search | baseline) = 0.94`

`P(search | intervention) = 0.21`

`ΔP = 0.73`

A large behavioral change supports the hypothesis that the manipulated factor influences the decision.

## 6. Experimental Controls

Change **one relevant factor at a time**.

Keep constant where possible:

- Model
- Prompt
- User query
- Tools
- Initial state
- Other context
- Sampling/settings

Changing multiple factors makes causal interpretation difficult.

## 7. Research Interpretation

Do not conclude:

> "This factor is the sole cause."

Instead conclude:

> "The intervention provides behavioral evidence that this factor influences the decision."

Other factors may contribute.

## 8. Minimal Research Pipeline

`Trajectory Logging`
→ `Explanation Claim`
→ `Claimed Factor`
→ `Baseline`
→ `Controlled Intervention`
→ `Repeated Runs`
→ `Trajectory Comparison`
→ `Quantified Behavioral Effect`
→ `Faithfulness Assessment`

## Key Takeaway

The practical shift is:

> **Do not merely record what the agent says caused its behavior; experimentally test whether changing the claimed factor actually changes the behavior.**