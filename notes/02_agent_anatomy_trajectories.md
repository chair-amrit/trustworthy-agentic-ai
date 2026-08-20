# 02 — Agent Anatomy & Trajectories

## 1. Agent as a Sequential System

An agent can be understood as a repeated transition process:

`State → Decision → Action → Observation → New State`

Understanding these components is necessary before attempting to explain agent behavior.

---

## 2. State

**State** is the information relevant to the agent at a particular point in execution.

It may include:

- Current goal or query
- Conversation/context
- Previous actions
- Retrieved information
- Tool results
- Relevant history or memory
- Current progress

A useful analogy in LangGraph is a **checkpoint**: a snapshot of the agent's current execution context.

Example:

    State₀:
    Goal = find cheapest flight
    Context = user request
    Previous actions = none
    Available tools = search, calculator

After a tool call:

    State₁:
    Goal = find cheapest flight
    Search result = Flight A ₹4500, Flight B ₹3900
    Previous action = search

The state changes because the agent has gained new information.

---

## 3. Decision

A **decision** is the agent's choice about what to do next given its current state.

Example:

    State₁
      ↓
    Decision:
    "Compare the available flights."

A decision is not necessarily the same thing as the action that executes it.

---

## 4. Action

An **action** is the operation the agent actually performs.

Examples:

    call_tool()
    retrieve_document()
    ask_user()
    delegate_to_agent()
    write_response()
    terminate()

Tool calls are therefore one type of action, not the complete definition of action.

A useful distinction is:

> **Decision = chosen next step**

> **Action = executed operation**

---

## 5. Observation

An **observation** is the information returned after an action.

Example:

    Action:
    search_flights()

    Observation:
    Flight A = ₹4500
    Flight B = ₹3900
    Flight C = ₹4100

The observation can then become part of the next state.

---

## 6. Trajectory

A **trajectory** is the complete sequence of states, decisions/actions, and observations across one execution.

Conceptually:

`τ = (S₀, A₀, O₀, S₁, A₁, O₁, ..., Sₙ)`

The notation is less important than the structure:

    State₀
      ↓
    Decision
      ↓
    Action
      ↓
    Observation
      ↓
    State₁
      ↓
    Decision
      ↓
    Action
      ↓
    Observation
      ↓
    ...
      ↓
    Outcome

The complete sequence represents the agent's trajectory.

---

## 7. Why Transitions Matter

Explanation can target not only individual states, but also transitions:

- Why did `State₀ → Decision₀` occur?
- Why did `Decision₀ → Action₀` occur?
- Why did `Action₀ → Observation₀ → State₁` change the next decision?
- Why did the agent follow this trajectory rather than another?

This is why the trajectory is useful as an **explanation object**.

---

## 8. LangGraph Mapping

These concepts map naturally to LangGraph:

| Agent concept | LangGraph view |
|---|---|
| State | Graph state |
| Decision/action processing | Node execution |
| Tool call | Tool/action |
| Observation | Tool result |
| State transition | State update / edge routing |
| Complete execution | Trajectory |

A practical trajectory log can record:

    Step
    State
    Decision
    Action
    Observation
    Next state
    Outcome

This gives us a structured record of what happened during execution.

---

## 9. Important Distinction

> **Trajectory tells us what happened. Explainability tries to tell us why it happened.**

For example:

    Trajectory:
    Agent → called Search Tool

    Explanation:
    Agent chose Search Tool because the current state
    indicated that external information was required.

The trajectory provides the behavioral record; the explanation attempts to account for that behavior.

---

## 10. Key Takeaways

1. **State** = relevant information and progress at a particular point in execution.
2. **Decision** = what the agent chooses to do next.
3. **Action** = what the agent actually executes.
4. **Observation** = information produced by the environment or tool after an action.
5. **Trajectory** = the complete sequence of these events across an execution.
6. Explanation can target individual events **or transitions between them**.
7. A trajectory is evidence about behavior, but **it is not itself an explanation**.