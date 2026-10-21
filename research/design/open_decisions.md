# Prototype design decisions

Status as of 21 Oct 2026. Draft parser/executor code is under review; nothing below is final.

## Decisions made while writing the first draft (need owner sign-off)
1. Only ```python and ```py fences count as code; bare fences are invalid.
2. Observation wording additions: "(no output)" and "[output truncated]".
3. Working directory is data/dabstep (spec v0.1 said a per-run scratch copy).
4. Code blocks run through a shared runner (python -c) with one namespace.
5. A timeout discards partial output.
6. Defaults: 60 s timeout, 2000-character observation, 10 steps, 3 consecutive invalid outputs.
7. If an earlier block fails during replay, an error is raised.
8. Layout: src/agent/{config,parser,executor,llm,logger,loop}.py, tests/, scripts/, tasks/; runs/ is gitignored.

## Open questions for the project owner
1. After a crashed step: forget the whole step (A) or keep what ran before the crash (B, notebook-like)? Draft leans A.
2. Start every observation with an explicit succeeded/failed status line? Leaning yes.
3. Formatting mistakes by the model: strict (reject and tell the model) or lenient? Leaning strict; count format errors and revisit after real runs.

## Fixes proposed (pending approval)
- Scratch folder for model-created files; data files read-only; data checksum verified at the start of every run.
- Hide secret environment variables from executed code.
- Separate earlier-step warnings from the current step's report.
- Reject replies that contain a bare fence plus a FINAL ANSWER line.
- Store fingerprints of full stdout/stderr; include data version and settings in the prefix fingerprint.
- Seed random number generators in the runner.

## Deferred
Output-size cap for runaway prints, partial output on timeout kept for diagnostics, process-tree cleanup, backup of runs/ logs.