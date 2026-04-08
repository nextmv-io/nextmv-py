"""Scoring functions for eval results."""

from __future__ import annotations

from typing import Any


def score_tool_sequence(expected: list[str], actual: list[str]) -> float:
    """Score how well the actual tool sequence matches the expected one.

    Returns 1.0 for an exact match, 0.0 for no overlap. Partial matches
    are scored as the fraction of expected tools that appear in order.
    """
    if not expected:
        return 1.0 if not actual else 0.0
    if not actual:
        return 0.0

    # Exact sequence match
    if expected == actual:
        return 1.0

    # Count how many expected tools appear in order in actual
    matched = 0
    actual_idx = 0
    for tool in expected:
        while actual_idx < len(actual):
            if actual[actual_idx] == tool:
                matched += 1
                actual_idx += 1
                break
            actual_idx += 1

    return matched / len(expected)


def score_outcome(
    tool_results: list[dict[str, Any]],
    success: dict[str, str],
) -> bool:
    """Check whether the tool results satisfy the success criteria.

    Supported criteria:
    - tool_called: True if the named tool appears in tool_results.
    - output_contains: True if any tool result content contains the string.
    """
    if not success:
        return True

    tool_called = success.get("tool_called")
    if tool_called is not None:
        found = any(r.get("tool") == tool_called for r in tool_results)
        if not found:
            return False

    output_contains = success.get("output_contains")
    if output_contains is not None:
        found = any(output_contains in r.get("content", "") for r in tool_results)
        if not found:
            return False

    return True
