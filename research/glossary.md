# Glossary

- Agent: an LLM that solves a task in several steps, running tools (here, Python code) and reading the results.
- Trajectory: the sequence of states, actions and observations produced while solving one task.
- Step: one action of the agent (here, one piece of Python code) plus the observation it produced.
- Uncertainty: how unsure the model is about its next action at a step. Planned measures: sampling disagreement (ask the model many times from the same state and see how much its actions differ), verbalized confidence (ask it to state its confidence) and token probabilities (logits).
- Correctness: whether the result of a step is objectively right, checked against an independent computation.
- Mismatch: uncertainty and correctness disagree - uncertain but correct, or confident but wrong.
- Frozen prefix: the exact conversation and state up to step t, reused so the model can be sampled many times from the same moment.
- Replay: rebuilding the state at step t by re-running all earlier successful code in a fresh process.
- Checkable step: a step whose result can be verified by an independent, deterministic computation.
- Executor: the program that runs the model's code in a separate process and returns its output.
- Parser: the program that reads the model's reply and decides whether it is code, a final answer or invalid.
- pytest: a tool that runs automatic tests (small programs that check code against known answers).
- Subprocess: a separate program started by the main program; here, a fresh Python run for each step.
- Fingerprint (hash): a short code computed from data; the same data always gives the same fingerprint.