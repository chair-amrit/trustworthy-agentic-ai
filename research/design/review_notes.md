# Review of draft parser/executor (Oct 2026)

Two independent reviews (an AI assistant and a second AI reviewer) of the draft parser and executor. The main claims were tested against the real code.

## Confirmed by test
- Model code can overwrite files in the working directory (a test overwrote a data-like file).
- Model code can read environment variables, including secrets such as API keys.
- Warnings printed by an earlier step appear again in the current step's error output.
- A reply with a bare fence plus a FINAL ANSWER line is parsed as a final answer (it should be invalid).

## Not confirmed
- Claim: a silent failure such as sys.exit(1) gives the model an empty "(no output)" observation. In the test the model sees a traceback ending in SystemExit: 1.

## Smaller items
- The prefix fingerprint should include data version and settings.
- The replay check should compare fingerprints of the full output, not only truncated text.
- Fixing the Python hash seed alone does not make code deterministic; seed random generators too.
- Subprocess output is buffered in memory before truncation.
- The executor is a controlled code runner, not a security sandbox.

## Status
Fixes wait on the decisions in open_decisions.md. 29 tests passed on Linux; they are to be run on Windows after the fixes.