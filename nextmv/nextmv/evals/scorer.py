"""Scoring functions for MCP eval results."""

from typing import Any


def score_tool_sequence(expected: list[str], actual: list[str]) -> float:
    """Score whether the expected tools were called (order-independent).

    Returns the fraction of expected tools that appear in actual.
    Extra tools in actual are not penalized. An empty expected
    list scores 1.0.
    """
    if not expected:
        return 1.0

    actual_set = set(actual)
    hits = sum(1 for tool in expected if tool in actual_set)
    return hits / len(expected)


def score_outcome(
    tool_results: list[dict[str, Any]],
    criteria: dict[str, str],
) -> bool:
    """Check whether tool results meet the success criteria.

    Supported criteria:
    - "contains": check if any tool result contains the substring
    - "tool_called": check if a specific tool was invoked

    Returns True if all criteria pass, or if criteria is empty.
    """
    if not criteria:
        return True

    if "contains" in criteria:
        substring = criteria["contains"]
        found = any(substring in str(r.get("content", "")) for r in tool_results)
        if not found:
            return False

    if "tool_called" in criteria:
        tool_name = criteria["tool_called"]
        found = any(r.get("tool") == tool_name for r in tool_results)
        if not found:
            return False

    return True
