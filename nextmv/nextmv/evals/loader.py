"""Load eval cases from YAML files."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import yaml

from nextmv.evals.agent import ToolCall

# Default location for tool_groups.yaml, next to eval case files.
_DEFAULT_TOOL_GROUPS_PATH = os.path.join(
    os.path.dirname(__file__), "cases", "tool_groups.yaml",
)


@dataclass
class EvalCase:
    """A single eval case loaded from YAML."""

    id: str
    task: str
    expected_tools: list[str]
    tools: list[str] = field(default_factory=list)
    success: dict[str, str] = field(default_factory=dict)
    deterministic: list[ToolCall] = field(default_factory=list)


def load_tool_groups(path: str = _DEFAULT_TOOL_GROUPS_PATH) -> dict[str, list[str]]:
    """Load tool group definitions from a YAML file.

    Returns a mapping of group name to list of tool names.
    """
    with open(path) as f:
        return yaml.safe_load(f)


def _resolve_tools(
    raw: dict[str, Any],
    tool_groups: dict[str, list[str]],
) -> list[str]:
    """Resolve the tool list for a case.

    If the case has explicit ``tools``, return those.
    If the case has ``tool_groups``, expand each group name
    into its tool list and return the combined (deduplicated) set.
    Otherwise return an empty list (all tools).
    """
    if raw.get("tools"):
        return raw["tools"]

    group_names = raw.get("tool_groups", [])
    if not group_names:
        return []

    tools: list[str] = []
    seen: set[str] = set()
    for name in group_names:
        for tool in tool_groups.get(name, []):
            if tool not in seen:
                tools.append(tool)
                seen.add(tool)
    return tools


def load_eval_cases(
    path: str,
    tool_groups: dict[str, list[str]] | None = None,
) -> list[EvalCase]:
    """Load eval cases from a YAML file.

    If *tool_groups* is not provided, loads the default
    ``cases/tool_groups.yaml`` automatically.
    """
    if tool_groups is None:
        tool_groups = load_tool_groups()

    with open(path) as f:
        raw_cases = yaml.safe_load(f)

    cases = []
    for raw in raw_cases:
        deterministic = []
        for step in raw.get("deterministic", []):
            deterministic.append(
                ToolCall(name=step["tool"], arguments=step.get("args", {}))
            )

        cases.append(
            EvalCase(
                id=raw["id"],
                task=raw["task"],
                expected_tools=raw.get("expected_tools", []),
                tools=_resolve_tools(raw, tool_groups),
                success=raw.get("success", {}),
                deterministic=deterministic,
            )
        )

    return cases
