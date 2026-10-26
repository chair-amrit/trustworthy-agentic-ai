"""Action parser (spec v0.1, section 2).

LLM output -> Action. The parser never repairs output: anything that does not
follow the protocol is returned as type="invalid" with a reason.

v0 protocol: exactly ONE fenced ```python block, OR exactly ONE line starting
with 'FINAL ANSWER:'. Anything else is invalid.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Only ```python / ```py fences count. Bare ``` fences are treated as invalid.
CODE_BLOCK_RE = re.compile(
    r"```(?:python|py)[ \t]*\n(.*?)```", re.DOTALL | re.IGNORECASE
)
FINAL_RE = re.compile(r"^[ \t]*FINAL ANSWER:[ \t]*(.*?)[ \t]*$", re.MULTILINE)


@dataclass(frozen=True)
class Action:
    type: str            # "code" | "final" | "invalid"
    payload: str = ""    # code text, final answer text, or "" if invalid
    reason: str = ""     # why it is invalid ("" otherwise)


def _invalid(reason: str) -> Action:
    return Action("invalid", "", reason)


def parse_action(text: str) -> Action:
    text = text.replace("\r\n", "\n")
    blocks = CODE_BLOCK_RE.findall(text)
    # 'FINAL ANSWER:' inside a code block (e.g. in a print) must not count.
    outside = CODE_BLOCK_RE.sub("", text)
    finals = FINAL_RE.findall(outside)

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
