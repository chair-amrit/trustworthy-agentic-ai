# Project: trustworthy-agentic-ai

Minor research project (ADBU, 5th semester). Working title: "Explainable Analysis of
Uncertainty–Correctness Relationships in Multi-Step Data-Analysis Agents" (provisional).
Broad question: which observable intermediate factors contribute to failures in multi-step
agents, and how do they relate to uncertainty and correctness during execution?

## How to work with the owner
- The owner is a student new to software tooling: explain technical terms plainly, with a small example.
- Ask before any design or research decision (protocol, metrics, models, state semantics).
  List options with trade-offs and wait.
- Work in small slices: state the change, list the files, implement only that slice, add tests,
  run tests, report exact results and limits.
- Do not commit or push unless asked. Work directly on main; do not create branches.
- Never invent citations or claim results that do not exist. Mark anything unverified.

## Research rules
- No gold trajectory. Correctness is judged by task contracts/oracles kept OUTSIDE the agent
  runtime. The agent must never see reference answers or contracts.
- Log only observable behaviour (code, tool calls, outputs, errors, confidence signals).
  Never ask for or log hidden chain-of-thought.
- A graph node, a model turn, a tool call and a research step are different things.
- A subprocess is not a secure sandbox; say so wherever relevant.
- The backend (API vs open-weight) is an experimental condition: record exact model ID,
  settings and capabilities.
- Keep exploratory pilot tasks separate from held-out confirmatory tasks.

## Repo map
- src/agent/: parser.py, executor.py, answers.py, logger.py, llm.py (FakeLLM), loop.py
  (Track B replaces it with a LangGraph graph), config.py, prompts/,
  workspace.py (per-run working folder, read-only inputs, checksums),
  tasks.py (agent-side loader, refuses tasks with "answer"),
  pathscan.py (ast path scan, run flags, review list)
- tests/ (pytest; tests/golden/fake_task_5.jsonl is the baseline fake-run log), scripts/
  (incl. make_agent_tasks.py: regenerates tasks/agent/ from tasks/dev_tasks.json),
  tasks/dev_tasks.json (10 DABStep dev tasks with public answers; evaluator side only),
  tasks/agent/dabstep_dev.json (same tasks without answers; the only file the agent side loads),
  research/, docs/ (build spec)
- data/ and runs/ are git-ignored. Never commit .env.
- Git tag baseline-v0 marks the working baseline harness. Never modify or delete it.

## Commands (Windows PowerShell, venv, Python 3.11.9)
- Activate: .\venv\Scripts\Activate.ps1
- Tests: python -m pytest -q
- Explain any new dependency before adding it; pin versions.

## Current state (keep updated)
- Two tracks:
  - Track A (December minor project): extend the baseline-v0 harness (D13, decided 23 Nov 2026).
  - Track B (after exams): full LangGraph rebuild, following docs/AGENT_SPEC_AND_BUILD_PLAN.md
    and docs/PHASE0_PLAN.md.
- Baseline harness runs a scripted fake model on DABStep task 5. No real LLM backend yet;
  replay not implemented.
- D5 decided 23 Nov 2026 (execution isolation): real runs happen on the Windows laptop.
  - The agent's working folder sits outside the repo.
  - Answer files are never inside the working folder.
  - Code the agent runs gets no API keys.
  - Every logged code block is scanned for paths outside the working folder. Flagged runs
    are listed in runs/review_list.jsonl for manual review; a run is excluded if review
    confirms an attempt to access a path outside the working folder. Excluded runs are kept
    and reported, never deleted.
  - This is not a sandbox. The subprocess can still reach anything the user account can.
- Track A step 1 (safety) built 24–26 Nov 2026:
  - Env allowlist: the child starts from an empty environment plus a fixed list
    (executor.py); started with -P -s (no imports from the working folder, no user site).
  - Per-run working folder D:\tagent_work\<run_id>\ (config.WORK_ROOT; workspace.py);
    an existing run_id or a folder inside the repo is refused; folders are kept after runs.
  - Inputs copied into it read-only, SHA-256 checksums before and after; a change flags the run.
  - Answer-free agent task file tasks/agent/dabstep_dev.json (scripts/make_agent_tasks.py;
    tasks.py refuses any task with "answer"). run_agent never reads answers; scripts fill
    matches_reference from tasks/dev_tasks.json after the run.
  - Path scan (pathscan.py, ast only): path_flags on every step, run-level flagged + reasons
    in runs/<run_id>.manifest.json, flagged lines appended to runs/review_list.jsonl.
  - DABStep folders in the Hugging Face cache deleted 26 Nov 2026.
  - Limits: not a sandbox; the scan catches paths written in the code (mentions), not what
    the code actually touched; tasks/dev_tasks.json (with answers) is still in the repo.
- D3 decided 24 Nov 2026 (Track A only): gemini-3.1-flash-lite, Gemini API free tier,
  google-genai==3.6.1; temperature 1.0, thinking_level "minimal", max_output_tokens 1024.
  Track B's model is chosen after exams.
- Still open (never decide silently): D1, D2, D4, D6–D12, deferred to Track B
  (see docs/PHASE0_PLAN.md §6).
  Decisions log: docs/DECISION_RECORD.md §11.
- Only 10 DABStep dev tasks have public answers; more tasks need own validated
  specifications, generated task families, or another benchmark.