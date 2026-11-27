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
PROTOCOL_VERSION = "v0"   # action protocol (D1); v1 = Track A, decided 27 Nov 2026

# --- Real model backend (D3, Track A only; decided 24 Nov 2026) -------------
ENV_PATH = REPO_ROOT / ".env"           # MODEL_API_KEY, read in the parent only
GEMINI_MODEL_ID = "gemini-3.1-flash-lite"
GEMINI_TEMPERATURE = 1.0                # Google's recommended default for Gemini 3
GEMINI_THINKING_LEVEL = "minimal"
GEMINI_MAX_OUTPUT_TOKENS = 1024         # thinking tokens count toward this limit
GEMINI_SDK = "google-genai==3.6.1"

# Retries (our own; the SDK's retries are switched off): only these HTTP statuses,
# plus network/connection errors and timeouts (see llm.is_transient_network_error),
# waiting these many seconds before retry 1, 2, 3, 4. Then the run stops ("api_failed").
API_RETRY_STATUSES = (429, 500, 503, 504)
API_RETRY_WAITS_S = (5, 15, 45, 90)
API_MAX_REQUESTS_PER_MINUTE = 12        # pacing; every attempt counts as a request
API_REQUEST_TIMEOUT_S = 120             # per attempt; a hung call fails as a timeout