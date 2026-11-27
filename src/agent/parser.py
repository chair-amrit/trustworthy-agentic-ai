"""Action parser (spec v0.1, section 2).

LLM output -> Action. The parser never repairs output: anything that does not
follow the protocol is returned as type="invalid" with a reason.

v0 protocol: exactly ONE fenced ```python block, OR exactly ONE line starting
with 'FINAL ANSWER:'. Anything else is invalid.

v1 protocol (D1, Track A, 27 Nov 2026) differs in one parsing case: a reply with
exactly one code block AND exactly one FINAL ANSWER line is a code action; the
answer line is discarded (Action.discarded_final holds it) and the loop tells
the model so. The loop also rejects a FINAL ANSWER given before any code block
has run without error (rule 2; see loop.py). Everything else parses as in v0.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Only ```python / ```py fences count. Bare ``` fences are treated as invalid.
CODE_BLOCK_RE = re.compile(
    r"```(?:python|py)[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE
)
FINAL_RE = re.compile(r"^[ \t]*FINAL ANSWER:[ \t]*(.*?)[ \t]*$", re.MULTILINE)

PROTOCOLS = ("v0", "v1")

# v1 feedback texts (fixed; part of the protocol).
DISCARDED_FINAL_NOTE = (
    "Your FINAL ANSWER was ignored because the reply also contained code. "
    "Check the output, then answer."
)
EARLY_FINAL_REASON = "Run code to check the data before giving a FINAL ANSWER"


@dataclass(frozen=True)
class Action:
    type: str                   # "code" | "final" | "invalid"
    payload: str = ""           # code text, final answer text, or "" if invalid
    reason: str = ""            # why it is invalid ("" otherwise)
    discarded_final: str = ""   # v1 only: answer line dropped from a code+answer reply


def _invalid(reason: str) -> Action:
    return Action("invalid", "", reason)


def check_protocol(protocol: str) -> None:
    if protocol not in PROTOCOLS:
        raise ValueError(f"unknown protocol {protocol!r}; expected one of {PROTOCOLS}")


def parse_action(text: str, protocol: str = "v0") -> Action:
    check_protocol(protocol)
    text = text.replace("\r\n", "\n")
    blocks = CODE_BLOCK_RE.findall(text)
    # 'FINAL ANSWER:' inside a code block (e.g. in a print) must not count.
    outside = CODE_BLOCK_RE.sub("", text)
    finals = FINAL_RE.findall(outside)

    # v1 rule 1: one code block + one answer line -> run the code, drop the answer.
    if protocol == "v1" and len(blocks) == 1 and len(finals) == 1:
        code = blocks[0].strip("\n")
        if code.strip():
            return Action("code", code, discarded_final=finals[0].strip())

    if blocks and finals:
        return _invalid("output contains both a code block and a FINAL ANSWER line")
    if len(blocks) > 1:
        return _invalid("output contains more than one code block")
    if len(finals) > 1:
        return _invalid("output contains more than one FINAL ANSWER line")

    if len(blocks) == 1:
        code = blocks[0].strip("\n")
        if not code.strip():
            return _invalid("the code block is empty")
        return Action("code", code)

    if len(finals) == 1:
        if "```" in text:
            return _invalid("output contains a code fence with a FINAL ANSWER line")
        answer = finals[0].strip()
        if not answer:
            return _invalid("the FINAL ANSWER line is empty")
        return Action("final", answer)

    if "```" in text:
        return _invalid("the code fence is not a closed ```python block")
    return _invalid("output has no ```python code block and no FINAL ANSWER line")


def format_error(reason: str) -> str:
    """Fixed feedback template sent back to the model after an invalid output."""
    return (
        f"Format error: {reason}. Reply with exactly one ```python code block, "
        "or exactly one line starting with 'FINAL ANSWER:'."
    )
