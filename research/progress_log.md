# Project progress log

Project: Explainable Analysis of Uncertainty-Correctness Relationships in Multi-Step Data-Analysis Agents
Team: Amrit Rajkumar, Ishian Deb Roy. Guide: Mr. Alok Choudhury (CSE, ADBU).
Milestones: started 30 Jul 2026; Phase I presentation 11 Sep 2026; Phase II presentation 14 Nov 2026; target completion mid-Dec 2026.

## Entries
- Sep 2026: literature review of agent explainability and trustworthy-agent surveys. Gap identified: step-level uncertainty and correctness in multi-step LLM agents (step-level ground truth is rare in agent benchmarks).
- Early Oct 2026: research question and two-phase method fixed (Phase 1: measure uncertainty and step-level correctness; Phase 2: discover mismatch patterns and test them with interventions). DABStep selected as candidate testbed.
- Early Oct 2026: DABStep feasibility study on 6 dev tasks (5, 49, 1305, 1753, 1871, 2697): 30 of 36 steps objectively checkable (0.83). Decision: DABStep stays the testbed. Unchecked steps are interpretation steps; task 2697 fee value not reproduced (ACI E reproduced).
- 18 Oct 2026: agent spec v0.1 committed (research/design/agent_spec.md); repo scaffold (src/agent, tests, scripts, tasks), requirements.txt and pytest.ini pushed.
- 18-21 Oct 2026: draft parser, executor and 29 tests written and reviewed; commit held back until review decisions are made. Review found real issues (see research/design/review_notes.md). Three design decisions pending (see research/design/open_decisions.md).
- 24 Oct 2026: executor fixes still waiting on four design decisions (draft parser/executor not committed). Added tasks/dev_tasks.json (the 10 DABStep dev tasks with public answers, exported by scripts/export_tasks.py) and src/agent/answers.py with 16 tests. Final answers are compared by numeric tolerance (1e-9), as sets for comma-separated lists, and by exact case-sensitive text otherwise. These follow the conventions in research/feasibility/reference_tasks.md; the case-sensitive strictness is a default that can be relaxed.
- Next: answer the four pending design decisions, apply the executor fixes, run tests on Windows, then LLM adapter with a fake model, logger, agent loop and replay test on task 5.
