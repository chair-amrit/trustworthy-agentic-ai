"""Central settings for the prototype agent (spec v0.1)."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Downloaded DABStep files (inside the repo, git-ignored). This is only the
# SOURCE that gets copied; executed code never runs here (D5).
DATA_ROOT = REPO_ROOT / "data" / "dabstep"
CONTEXT_SOURCE = DATA_ROOT / "data" / "context"

# D5: one working folder per run, OUTSIDE the repo: WORK_ROOT/<run_id>/.
# Prompts use paths relative to that folder (data/context/payments.csv).
WORK_ROOT = Path(r"D:\tagent_work")

TIMEOUT_S = 60          # per subprocess run (prior blocks + current block)
MAX_OBS_CHARS = 2000    # observation truncation limit
MAX_STEPS = 10          # termination: step budget
MAX_INVALID = 3         # termination: consecutive invalid outputs
PROMPT_VERSION = "system_v0"