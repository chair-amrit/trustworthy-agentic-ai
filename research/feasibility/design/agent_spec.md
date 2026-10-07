# Prototype Agent Spec (v0)

Scope: the contract the first prototype must obey. Out of scope: uncertainty
estimation, step-level checkers, planning logic, multi-model comparison.

## 1. State

State at step t = the ordered message list the model sees (system prompt, task,
and each previous model output and observation) + the list of successfully
executed code blocks. Nothing else is carried between steps.
- `prefix_id` = sha1 of the canonical JSON of (task_id, messages). This is the
  exact object a frozen-prefix sample conditions on.

## 2. Action protocol (prototype v0)

Pipeline: LLM output -> Action parser -> Action -> Executor -> Observation.
- The parser returns `Action(type="code" | "final" | "invalid", payload)`.
- v0 protocol: one fenced Python block per step to act; a line
  `FINAL ANSWER: <value>` to finish. The model is told to print intermediate
  values.
- Protocol is swappable: only the parser changes. Parse failures are logged
  (type="invalid") and never silently repaired, since they are a confound.

## 3. Execution and replay

- Each step runs in a fresh subprocess: a script made of all earlier
  successful code blocks, then a marker print, then the step-t code. The
  observation is the stdout after the marker (plus stderr).
- Failed steps (returncode != 0 or timeout) are logged and shown to the model,
  but are not added to the executed-code list.
- Rules: timeout per run, fixed working directory and data path, no network,
  PYTHONHASHSEED=0, pinned library versions, observation truncated to a fixed
  length (record a `truncated` flag), no randomness or timestamps in task code.
- Replay of prefix t = rebuild from the logged code blocks in a fresh
  subprocess. Live execution and replay use the same mechanism.

## 4. LLM adapter

`generate(messages, n=1, temperature=0.0, max_tokens=..., seed=None,
want_logprobs=False) -> list[Completion]`
- `Completion(text, token_logprobs | None, finish_reason, usage)`
- One implementation per backend (API, open-weight). Log-probs are None where
  the backend does not expose them.
- A `FakeLLM` returns scripted completions per step, for testing.

## 5. Step log (JSONL, one record per step)

```json
{
  "run_id": "", "task_id": 5, "step": 1,
  "prefix_id": "",
  "model": "", "temperature": 0.0, "seed": 0,
  "messages": [], "raw_output": "",
  "action_type": "code", "code": "", "final_answer": null,
  "stdout": "", "stderr": "", "returncode": 0,
  "timed_out": false, "truncated": false,
  "samples": [], "logprobs": null,
  "timestamp": ""
}
```
`samples` and `logprobs` are reserved for later uncertainty work.

## Acceptance tests (before any real model)

1. FakeLLM solves task 5 end to end; final answer is NL.
2. Every logged record validates against the schema above.
3. Replay: for every step t, rebuilding from logged code blocks in a fresh
   subprocess reproduces the logged stdout exactly.
4. Re-running the whole fake run gives an identical log (apart from timestamps).