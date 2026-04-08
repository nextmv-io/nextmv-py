"""Load eval cases from YAML files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml

from nextmv.evals.agent import ToolCall


@dataclass
class EvalCase:
    """A single eval case loaded from YAML."""

    id: str
    task: str
    expected_tools: list[str]
    success: dict[str, str] = field(default_factory=dict)
    deterministic: list[ToolCall] = field(default_factory=list)


def load_eval_cases(path: str) -> list[EvalCase]:
    """Load eval cases from a YAML file."""
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
                success=raw.get("success", {}),
                deterministic=deterministic,
            )
        )

    return cases
