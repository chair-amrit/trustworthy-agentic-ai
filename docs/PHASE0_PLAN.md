# Phase 0 plan — migrate baseline harness to the LangGraph research agent

## Context
The repo holds a working baseline harness (tag `baseline-v0`): a text-protocol parser, a re-execution subprocess executor, a FakeLLM, a JSONL step logger, an answer checker and a hand-written `loop.py`, all driven by `scripts/run_fake.py` on DABStep task 5. `docs/AGENT_SPEC_AND_BUILD_PLAN.md` asks to rebuild this into a single-agent LangGraph `StateGraph` with typed tools, model adapters (API + open-weight), per-run workspaces, an event log + manifest, and tool replay — while preserving the baseline and keeping evaluation code outside the agent runtime. This is Phase 0: inspection + migration plan only. No files are changed until the owner approves and answers the open decisions.

## 1. Inspection findings (all read-only)

**Git**
- Branch `main`, in sync with `origin/main` at `9726a6f`. Only `CLAUDE.md` and `docs/` are untracked (the spec itself is not under version control yet).
- `baseline-v0` exists locally and on the remote (annotated tag object `8942cac`, pointing to commit `794dd0c`). The only change since the tag is `.gitignore`, removal of a stray `.pyc`, and adding the golden file.
- The spec says to use a feature branch, but the owner says to work on `main`. **The owner's rule wins:** no branches.

**Environment**
- venv Python 3.11.9. `python` is not on the bash PATH, so call `venv/Scripts/python.exe` directly.
- Not installed: LangGraph, LangChain, pydantic, DuckDB, matplotlib.
- No Docker and no WSL distro. Windows 11 Pro. GTX 1650 Ti with 4 GB VRAM, 7.8 GB RAM. No local model runtime (ollama, llama.cpp or vLLM).
- `.env` exists and is currently empty.

**Tests**
- `python -m pytest -q`: **58 passed in 12.8 s**. Run with no cache and no bytecode, temp files in the scratchpad.
- `tests/test_replay.py` is **empty**.
- `tests/golden/fake_task_5.jsonl` is **not asserted by any test**. It is identical to `runs/fake_task_5.jsonl`.
- `test_fake_run.py` imports `scripts.run_fake`. That works only under `python -m pytest`, not bare `pytest`.

**Data corpus** (`data/dabstep/data/context`, git-ignored)
- `payments.csv` (23.6 MB, 138,236 × 21), `fees.json`, `merchant_data.json`, `acquirer_countries.csv`, `merchant_category_codes.csv`, `manual.md`, `payments-readme.md`.
- Formats in use: **CSV, JSON, Markdown only**. No XLSX or PDF.
- `data/trial` is empty.

**Module review**

| Module | What it does | Verdict |
|---|---|---|
| `parser.py` | Strict text protocol: one ```python block XOR one `FINAL ANSWER:` line; never repairs output. 16 tests. | Sound. Reusable as the "text protocol" validator. |
| `executor.py` | Fresh subprocess per step; re-runs prior successful blocks, a marker line, then the current block; trims tracebacks; truncates output; `PYTHONHASHSEED=0`. | Logic reusable, but has defects (see the security risks below). |
| `llm.py` | `Completion`, `Model` Protocol, `FakeLLM` (scripted, explicit exhaustion). | Reusable. Needs capabilities/metadata, request IDs and native tool-call fields. |
| `logger.py` | Append-only JSONL with a field allowlist; rejects NaN. | The allowlist idea is reusable. The schema is a flat step record, not the spec's event envelope. |
| `answers.py` | Final-answer comparison (1e-9 tolerance, set comparison for lists, strict text). 16 tests. | Sound, but it is **evaluator code** and must leave the runtime. |
| `loop.py` | Message loop. Imports `answers_match` and reads `task["answer"]` **inside the runtime**. | Replaced by the graph. |
| `config.py` | Module constants (timeout 60 s, 2000 chars, 10 steps, 3 invalid). | Replaced by typed config + YAML. |
| `prompts/system_v0.txt` | v0 prompt, referenced by the golden log. | Keep frozen. |

- **Stale design records.** `research/design/open_decisions.md` and `review_notes.md` list fixes as pending.
  - Some fixes have landed: the bare-fence + FINAL line is now rejected, and failed/timeout observations are labelled.
  - Others have not: secret env, writable data dir, prior-step stderr bleed, checksums, RNG seeding.

## 2. Security and reproducibility risks found before implementation
1. **Answer leakage (critical).**
   - `loop.py` holds `task["answer"]` in the runtime.
   - The executor's working directory is `data/dabstep`, inside the repo. Model code can open `../../tasks/dev_tasks.json` (all 10 answers) or `../../research/feasibility/reference_tasks.md` (answers plus intermediate values).
   - Moving the run directory elsewhere does not fix this under a plain subprocess, because absolute paths still work. Only real isolation closes it. Experimental runs must therefore use the sandbox.
2. **Secret inheritance.** `_env()` copies all of `os.environ` into the child process (confirmed in `review_notes.md`). Any API key set later is visible to generated code.
3. **Writable inputs.** Generated code can overwrite `payments.csv`, which corrupts all later runs. No checksum is verified.
4. **No resource limits.**
   - No network block.
   - No memory or process limits.
   - `capture_output` buffers all output in memory before truncating, so a runaway print could exhaust 7.8 GB.
   - On a timeout only the direct child is killed; grandchild processes can survive on Windows.
5. **Observation contamination.** Prior steps' stderr (warnings) re-appears in every later observation. This is a research confound.
6. **Re-execution cost.** Every step re-reads the 23.6 MB CSV and re-runs all prior code, under one 60 s timeout. Late steps may time out spuriously. This bears on decision D2.
7. **Missing provenance and identity.**
   - Not recorded: git commit or dirty state, data checksums, timestamps, config hash.
   - `run_id` is a fixed label (`"fake-task-5"`), not a unique ID.
   - Re-running `run_fake.py` **appends** to the same log file.
   - `requirements.txt` is a freeze of the feasibility notebook environment (`datasets`, `ipykernel`), not of the agent's dependencies.
8. **Hardware limits.** 4 GB VRAM and 7.8 GB RAM constrain local open-weight models and the memory available to Docker Desktop.
9. **Checkpoint vs run confusion.** Resuming a LangGraph thread could silently continue one repetition as another. `thread_id` and `run_id` must be kept separate and resume must be explicit.
10. **Unversioned spec.** `CLAUDE.md` and `docs/` are untracked, so a manifest cannot reference a committed spec version.

## 3. File-by-file migration map
Key: **keep** = unchanged · **adapt** = edit in place · **move** = relocate · **replace** = superseded by new code · **archive** = frozen legacy, removed from the active path later.

Recommended strategy (pending decision D8):
- Build the new package `src/trustworthy_agent/` **alongside** the existing `src/agent/`.
- Port logic into new modules; do not edit the legacy files.
- Keep `src/agent/` and its tests running unchanged until the graph reproduces the task-5 behaviour (end of Phase 4).
- Then archive the legacy package. The `baseline-v0` tag keeps the original forever.

| File | Action | Target / reason |
|---|---|---|
| `.gitignore` | adapt | Add checkpoint DBs (`*.sqlite`), a run-root override, `!.env.example`. |
| `pytest.ini` | adapt | Add a `network` marker; core suite runs `-m "not network"`. |
| `readme.md` | adapt (later) | Append a "How to run" section; research text unchanged. |
| `requirements.txt` | adapt | Becomes the pinned lock of the agent environment, regenerated deliberately (D11). |
| *(new)* `pyproject.toml`, `.env.example` | new | Package metadata + dependencies; variable names only, no values. |
| `CLAUDE.md`, `docs/*` | keep | Untracked. Owner decides whether to commit them. |
| `src/agent/__init__.py` | keep → archive | Legacy package marker. |
| `src/agent/parser.py` | keep → archive | Logic ported to `protocol/text_protocol.py` if D1 = text (or hybrid). |
| `src/agent/executor.py` | keep → archive | Logic (runner, marker, traceback trim, `ExecResult`, `format_observation`) ported to `runtime/local_subprocess.py`. Fixes: env allowlist, per-run cwd, read-only input copy, streamed output cap. State semantics per D2. Labelled **non-sandboxed, dev only**. |
| `src/agent/llm.py` | keep → archive | `Completion`/`Model`/`FakeLLM` become `models/base.py` (`ModelResponse`, `ModelCapabilities`, `ModelMetadata`, `invoke`) and `models/adapters/fake.py`. |
| `src/agent/logger.py` | keep → archive | Allowlist + append-only ported to `telemetry/event_logger.py` with the spec's event envelope. |
| `src/agent/answers.py` | **move** | To `src/trustworthy_eval/answers.py`. Never imported by `trustworthy_agent`; an import-boundary test enforces this. |
| `src/agent/loop.py` | **replace** → archive | Replaced by `graph/{state,nodes,routing,workflow}.py`. |
| `src/agent/config.py` | **replace** → archive | Replaced by `config/settings.py` + `configs/*.yaml`; current constants become defaults. |
| `src/agent/prompts/system_v0.txt` | keep | Frozen; golden log references `system_v0`. New prompt is `system_v1.md` + `tool_policy_v1.md`. |
| `scripts/run_fake.py` | keep | Legacy golden-run script. The new entry point is `cli.py`. |
| `scripts/export_tasks.py` | adapt | Also emit an answer-free agent task file (D9). |
| `tasks/dev_tasks.json` | keep | Raw export with answers. Treated as **evaluator-side**. |
| `tasks/.gitkeep` | keep | Harmless. |
| `tests/test_answers.py` | **move** | To `tests/evaluation/`, together with `answers.py`. |
| `tests/test_{parser,executor,llm,logger,fake_run}.py` | keep → archive | Legacy suite stays green. Cases are ported into `tests/unit/…` for the new modules. At archive time they move to `tests/legacy/`. |
| `tests/test_replay.py` | replace | Empty today; real replay tests go in `tests/replay/` in Phase 5. |
| `tests/golden/fake_task_5.jsonl` | keep | Never modified. Add a test that the legacy run reproduces it exactly. |
| `research/**` (notes, history, literature, glossary, `dabstep_notes.md`, `literature_prioritization.md`, feasibility files) | keep | Feasibility files are oracle material and must never be in an agent workspace. `fee_rules.py` may later be *copied* into the evaluator. |
| `research/design/open_decisions.md`, `review_notes.md`, `research/progress_log.md` | adapt (owner's call) | Append a status update that reconciles which fixes landed. |
| `data/**`, `runs/**` | keep (ignored) | Source corpus; checksummed into each manifest. |

## 4. Proposed target directory tree
```text
trustworthy-agentic-ai/
├── CLAUDE.md  readme.md  pyproject.toml  requirements.txt  .env.example  .gitignore  pytest.ini
├── configs/
│   ├── agent.yaml                 # budgets, limits, prompt version, executor profile
│   └── models/
│       ├── fake.yaml
│       ├── api.yaml               # placeholder until D3
│       └── open_weight.yaml       # placeholder until D4
├── docs/                          # spec + start-here
├── src/
│   ├── agent/                     # LEGACY baseline (frozen; archived after Phase 4 parity)
│   ├── trustworthy_agent/         # agent runtime — never imports trustworthy_eval
│   │   ├── __init__.py  cli.py
│   │   ├── config/settings.py
│   │   ├── schemas/{actions,tool_io,outputs,events,manifest}.py
│   │   ├── protocol/{text_protocol,native_tools}.py   # one or both, per D1
│   │   ├── models/{base,factory}.py
│   │   ├── models/adapters/{fake,<api>,<open_weight>}.py
│   │   ├── tools/{registry,files,inspect_data,search_docs,python_exec,artifacts}.py   # + sql.py only if D6
│   │   ├── runtime/{workspace,sandbox,local_subprocess}.py   # + container/remote backend per D5
│   │   ├── graph/{state,nodes,routing,workflow}.py
│   │   ├── telemetry/{events,event_logger,manifest,provenance,replay,validate}.py
│   │   ├── tasks/loader.py        # reads answer-free task specs only
│   │   └── prompts/{system_v1.md,tool_policy_v1.md}
│   └── trustworthy_eval/          # evaluator (future): answers.py now, oracles/contracts later
├── tasks/
│   ├── dev_tasks.json             # raw export (contains answers → evaluator side)
│   └── agent/dabstep_dev.json     # derived, no answer field (location per D9)
├── tests/
│   ├── golden/fake_task_5.jsonl
│   ├── legacy/                    # (after archive) baseline tests
│   ├── unit/  integration/  replay/  safety/  evaluation/
│   └── fixtures/                  # tiny synthetic CSV/JSON/MD
├── scripts/                       # export_tasks.py, run_fake.py
├── research/                      # unchanged; protocol/ and experiments/ added in Phase 7
└── runs/                          # git-ignored; root configurable
    └── <experiment>/<run_id>/
        ├── manifest.json
        ├── events.jsonl
        ├── final.json
        └── workspace/{inputs (read-only copy), outputs/, scratch/}
# checkpoints in a separate SQLite file
```

## 5. Phase mapping (one vertical slice at a time; full suite after each)
- **Phase 0** (this plan).
  - Exit criteria met: tag preserved, nothing deleted.
  - Exit criterion still open: owner review of this plan.
- **Phase 1 — foundation**
  - Slice 1a: `pyproject.toml`, pydantic config models, `configs/agent.yaml`, golden-reproduction test for the legacy run.
  - Slice 1b: schemas for actions, tool I/O, final output, events and manifest.
  - Slice 1c: `runtime/workspace.py` (UUID `run_id`, per-run dirs, read-only input copy, checksums).
  - Slice 1d: `cli.py` shell, so a fake run can initialize and close.
  - Also: move `answers.py` to `trustworthy_eval`, add the answer-free task loader, and add the import-boundary test.
- **Phase 2 — models**
  - `models/base.py`, ported FakeLLM, capability flags, factory driven by config.
  - Real API and open-weight adapters only after D3 and D4. Their smoke tests are opt-in (`-m network`).
- **Phase 3 — tools**
  - `list_files`, `inspect_file`, `read_file_sample`, `search_text_sources` for CSV, JSON and MD only (D7).
  - `python_exec` behind the `Sandbox` interface, with the local subprocess as a labelled dev backend.
  - Artifact registry. SQL only if D6 says so.
- **Phase 4 — graph**
  - Typed state, nodes `initialize_run → load_task_context → agent_decide → validate_action → execute_tool → record_observation → check_budgets → finalize_response → close_run`, deterministic routing.
  - Budgets; SQLite checkpointing with explicit resume.
  - Parity: the fake model solves task 5 through the graph. Then archive the legacy package.
- **Phase 5 — telemetry and replay**
  - Event logger with envelope and sequence numbers; manifest provenance.
  - Tool replay that never calls the LLM; log-completeness validator; secret-scan test on logs.
- **Phase 6 — end-to-end** on one easy and one hard dev task, inside the sandbox from D5.
- **Phase 7 — pilot readiness**
  - Protocol v1.0, frozen log schema, split between exploratory and held-out tasks.
  - The held-out set needs tasks beyond the 10 public dev tasks.

New dependencies, each explained and pinned to exact versions checked on PyPI at install time:

| Dependency | Phase | Why |
|---|---|---|
| `pydantic` | 1 | Typed config and schema models |
| `langgraph` + `langgraph-checkpoint-sqlite` | 4 | Graph orchestration and checkpointing |
| Provider SDK | 2 | API adapter, only after D3 |
| `matplotlib` | Only when charts are needed | Chart artifacts |

## 6. Open decisions (not chosen; owner decides)

**Five decisions the owner reserved explicitly:**

**D1. Action protocol.**
- *Text protocol*: the model writes a ```python block or `FINAL ANSWER:`, as in the current parser.
  - Works on any model, including small open-weight ones.
  - The parser and its 16 tests already exist.
  - Tools like `inspect_file` would need a text syntax too.
- *Native tool calls*: the provider returns structured JSON, e.g. `{"name": "inspect_file", "args": {"path": "payments.csv"}}`.
  - Typed argument validation; multiple tools fit naturally.
  - Support varies by provider and is often weak on small open models, which can confound backend comparisons.

**D2. Python state between steps.**
- *Fresh re-execution with rollback*: today's approach; a failed step is forgotten.
  - Reproducible; replay uses the same mechanism.
  - Cost grows with every step (re-reads the 23.6 MB CSV each time).
- *Persistent session*: like a Jupyter kernel.
  - Fast and natural for the model.
  - State can include half-run failed steps; replay and isolation are harder.
- This also settles the existing question A/B in `open_decisions.md`.

**D3. First API model.**
- Criteria: native tool calls, **log-probability availability** (central for the uncertainty research), seed support, context size, cost.
- Provider capabilities must be checked at decision time, not assumed.

**D4. Open-weight runtime.**
- Options: local quantized server (llama.cpp or Ollama), HF transformers direct, vLLM on Linux, or a remote GPU (Colab, Kaggle, university).
- Constraint: 4 GB VRAM and 7.8 GB RAM locally.
- Logprob and tool-call support differ by runtime.

**D5. Execution isolation on Windows.**
- Options: Docker Desktop (needs a WSL2 install; neither is present), a WSL2 Linux sandbox, a remote Linux VM or server, Windows Sandbox (available on Win 11 Pro but hard to automate).
- In every case the local subprocess stays dev-only and labelled non-sandboxed.

**From spec §14, with evidence:**
- **D6. SQL / DuckDB.** None of the six feasibility solutions needed SQL; all used pandas. Evidence favours deferring it.
- **D7. Input formats.** The corpus is CSV + JSON + MD only. Evidence favours supporting just these three.

**Surfaced by inspection:**
- **D8. Package layout.** New `trustworthy_agent` alongside the frozen legacy `agent` (recommended), or refactor `src/agent` in place.
- **D9. Oracle storage.** Where answers live, and the name of the answer-free agent task file. Recommended: keep `tasks/dev_tasks.json` as evaluator-side and derive `tasks/agent/dabstep_dev.json`.
- **D10. Model adapters.** Own thin adapters over provider SDKs (recommended: full control of logprobs and raw metadata), or LangChain chat-model wrappers (less code, but an extra layer that can hide provider details).
- **D11. Dependency tooling.** `pyproject.toml` + pinned `pip freeze` lock (no new tool; recommended), or adopt `uv`/`pip-tools`.
- **D12. Committing docs and design records.** Whether to commit `CLAUDE.md` and `docs/`, and whether to update the stale `open_decisions.md` and `review_notes.md`.

## 7. Verification (applies to every slice after approval)
- `.\venv\Scripts\Activate.ps1; python -m pytest -q`. The legacy 58 tests must stay green until archive.
- Phase 1 adds: a golden-reproduction test for `tests/golden/fake_task_5.jsonl`, an import-boundary test (`trustworthy_agent` never imports `trustworthy_eval`), and a no-answer-leak test (no `answer` key in loader output, state, prompt or logs).
- Phase 3 adds safety tests: path traversal, env-secret visibility in the child process, writes to inputs, timeout, output flood. Network-block tests apply only to the sandbox backend.
- Phase 5 adds: replay with no LLM calls (asserted with a FakeLLM that raises if called), plus a secret scan of the logs.
- After each slice, report the exact pass/fail counts, changed files and known limitations.
