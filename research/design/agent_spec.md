# Prototype Agent Spec (v0)

Scope: the contract the first prototype must obey. Out of scope: uncertainty
estimation, step-level checkers, planning logic, multi-model comparison.

## 1. State

State at step t = the ordered message list the model sees (system prompt, task,
and each previous model output and observation) + the list of successfully
executed code blocks. Nothing else is carried between steps.
- `prefix_id` = sha1 of the canonical JSON of (task_id, messages). This is the
  exact object a frozen-prefix sample conditions on.
- Observation messages use a fixed template, role "user":
  `Observation:\n<stdout after marker>\n<stderr if any>`.
  Invalid-output feedback: `Format error: <reason>`.
- The system prompt lives in a file with a `prompt_version` string, recorded in
  every log record.
- Prompts use relative paths only (e.g. `data/...`). The subprocess cwd is a
  per-run scratch dir containing the data at that relative path, so `prefix_id`
  is identical across machines.

## 2. Action protocol (prototype v0)

Pipeline: LLM output -> Action parser -> Action -> Executor -> Observation.
- The parser returns `Action(type="code" | "final" | "invalid", payload)`.
- v0 protocol: one fenced Python block per step to act; a line
  `FINAL ANSWER: <value>` to finish. The model is told to print intermediate
  values.
- Protocol is swappable: only the parser changes. Parse failures are logged
  (type="invalid") and never silently repaired, since they are a confound.
  - Each model output must contain exactly one fenced Python block OR exactly one
  `FINAL ANSWER:` line. Both, neither, or several code blocks -> `invalid`.
- On invalid: log it, append the `Format error` message, continue. Never repair.
- Termination: `final`, `max_steps` (default 10), or `max_invalid`
  (default 3 consecutive). The last record carries `terminated_reason`.

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
  - Subprocess env: PYTHONUTF8=1, PYTHONHASHSEED=0.
- "No network" is a prompt rule only in v0 (not enforced); known limitation.
- Truncation: log `stdout_len` (untruncated length); replay compares the
  truncated strings using the same limit.

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
- Add: `prompt_version`, `stdout_len`, `terminated_reason` (null except last record).
- Remove `samples` from the step record. Frozen-prefix samples go in a separate
  `samples.jsonl` keyed by `prefix_id` (added in the uncertainty phase).
  Keep `logprobs` for the main action.
- `run_id` is a label only and is not part of any identity check.

## Acceptance tests (before any real model)

1. FakeLLM solves task 5 end to end; final answer is NL.
2. Every logged record validates against the schema above.
3. Replay: for every step t, rebuilding from logged code blocks in a fresh
   subprocess reproduces the logged stdout exactly.
4. Re-running the whole fake run gives an identical log apart from `timestamp`
   and `run_id`.
5. Failure paths: a scripted run containing one failing code block and one
   invalid output. Both are logged, the failing block is not added to the
   executed list, the invalid output triggers a `Format error` message, the
   final answer is still reached, and replay still matches.