"""Helpers for building Typer CLI commands and options from pure action functions.

This package is the CLI-side half of the shared-connectors framework. It
pairs with ``nextmv.cli.mcp.framework`` which provides the MCP-side helpers.
Both consume pure action functions from ``nextmv.cli.actions`` and generate
frontend wrappers with matching signatures.

Import at call sites as::

    from nextmv.cli import framework as cli

See ``docs/superpowers/specs/2026-04-10-mcp-cli-shared-connectors-design.md``
for the full design.
"""

from nextmv.cli.framework.command import Example, command
from nextmv.cli.framework.options import (
    AppDirOption,
    AppIdOption,
    AppIdRequiredOption,
    DefaultExperimentInstanceOption,
    DefaultInstanceIdOption,
    DescriptionOption,
    ExistOkOption,
    IsWorkflowOption,
    NameOption,
)
from nextmv.cli.framework.result import emit, format_save_message
from nextmv.cli.message import in_progress as progress  # short alias

__all__ = [
    "command",
    "emit",
    "format_save_message",
    "progress",
    "Example",
    "AppIdOption",
    "AppIdRequiredOption",
    "NameOption",
    "DescriptionOption",
    "DefaultInstanceIdOption",
    "DefaultExperimentInstanceOption",
    "IsWorkflowOption",
    "ExistOkOption",
    "AppDirOption",
]
