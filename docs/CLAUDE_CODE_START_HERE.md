# Claude Code — Start Here

You are helping implement the **Research-Grade Data Analysis Agent** in the existing `trustworthy-agentic-ai` repository.

## First, read the full specification

Read `AGENT_SPEC_AND_BUILD_PLAN.md` completely before editing any file. It is the source of truth for v1 requirements and build phases.

## Your first task is planning only — do not code yet

1. Inspect the repository's current Git status, branches, tags, file tree, source files, tests, configuration, and README.
2. Confirm that `baseline-v0` exists locally and remotely if remote access is available. Do not modify or delete it.
3. Read the current implementations of the parser, executor, answer checker, logger, model interface, prompts, feasibility scripts, and tests.
4. Identify which modules can be reused, which need adapters/refactoring, and which are replaced by LangGraph orchestration.
5. Produce a migration plan mapping every existing file to one of:
   - keep unchanged
   - adapt
   - move
   - replace
   - archive
6. Propose the exact target directory tree.
7. Identify blockers that require user decisions (API provider, open-weight runtime, Docker/VM availability, SQL tool necessity, input formats).
8. Map the plan to the phases and acceptance criteria in the specification.
9. Identify security and reproducibility risks before implementation.

Return the inspection findings and proposed implementation plan. Do not make edits until the user approves the plan.

## Non-negotiable constraints

- Use LangGraph with a custom stateful graph for controlled orchestration.
- Use one agent with tools for v1. Do not add multi-agent complexity.
- The same graph and tools must work with API and open-weight model adapters.
- A model backend is selected per run through configuration.
- Keep research evaluation/oracle code separate from the agent runtime.
- Never expose benchmark reference answers, evaluation contracts, or ground-truth values to the agent.
- Log observable requests, tool calls, code, results, errors, state updates, artifacts, and provenance.
- Do not ask for or log hidden chain-of-thought.
- A LangGraph node, model turn, tool call, and research step are not automatically the same unit.
- Do not claim a subprocess is a secure sandbox.
- Do not overwrite or discard prior feasibility work or the baseline harness.
- Do not make commits or push without explicit approval.

## Implementation discipline after approval

Implement one phase or vertical slice at a time. For each slice:

1. State the intended change.
2. List files to create/edit.
3. Implement only that slice.
4. Add/update tests.
5. Run the relevant tests and then the full suite.
6. Report exact results, changed files, known limitations, and next step.

Never generate the whole application in one large pass. Avoid speculative dependencies and premature UI work.

## Additional instructions from the project owner
- Work directly on main. Do not create branches.
- In your plan, list these as open decisions and do NOT choose them: (1) action protocol: text protocol vs native tool calls; (2) Python state between steps: fresh re-execution with rollback vs persistent session; (3) first API model; (4) open-weight runtime; (5) execution isolation on Windows.
- Ask before any design or research decision. Explain technical terms plainly.