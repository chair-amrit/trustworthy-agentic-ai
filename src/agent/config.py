"""Central settings for the prototype agent (spec v0.1)."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Working directory of executed code. Prompts use paths relative to this
# folder (e.g. data/context/payments.csv), so prefix_ids match on any machine.
DATA_ROOT = REPO_ROOT / "data" / "dabstep"

TIMEOUT_S = 60          # per subprocess run (prior blocks + current block)
MAX_OBS_CHARS = 2000    # observation truncation limit
MAX_STEPS = 10          # termination: step budget
MAX_INVALID = 3         # termination: consecutive invalid outputs
PROMPT_VERSION = "system_v0"