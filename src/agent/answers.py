"""Final-answer comparison.

Conventions come from research/feasibility/reference_tasks.md:
- numbers are equal if they differ by at most 1e-9 (the DABStep reference
  answers carry floating-point noise, e.g. -0.94810300000017)
- comma-separated lists are compared as sets (order does not matter)
- everything else must match exactly after trimming whitespace
  (case-sensitive; this strictness is a default and can be relaxed later)

This judges FINAL answers only. Step-level checkers are separate.
"""
from __future__ import annotations

import math

ABS_TOL = 1e-9


def _as_number(text: str):
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def _normalise_item(text: str):
    text = text.strip()
    number = _as_number(text)
    return number if number is not None else text


def _as_set(text: str) -> set:
    return {_normalise_item(part) for part in text.split(",") if part.strip()}


def answers_match(predicted: str, expected: str, abs_tol: float = ABS_TOL) -> bool:
    p, e = predicted.strip(), expected.strip()
    if p == e:
        return True
    p_num, e_num = _as_number(p), _as_number(e)
    if p_num is not None and e_num is not None:
        return math.isclose(p_num, e_num, rel_tol=0.0, abs_tol=abs_tol)
    if "," in p or "," in e:
        return _as_set(p) == _as_set(e)
    return False