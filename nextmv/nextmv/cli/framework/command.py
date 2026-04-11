"""``cli.command()`` builder and helpers.

Given a pure action function under ``nextmv.cli.actions``, generates a Typer
command wrapper whose signature mirrors the action's (minus the ``client``
parameter, plus framework-injected flags like ``--profile`` and optionally
``--output``). The wrapper reads metadata from the action's ``Annotated``
parameters so the same aliases drive both CLI and MCP tool registration.

This module is imported at call sites as part of ``cli`` via::

    from nextmv.cli import framework as cli
    list = cli.command(app, list_apps, ...)

This file currently contains only the ``_render_examples`` helper. The
full ``cli.command()`` builder lands in Task 6.
"""

from typing import Tuple

Example = Tuple[str, str]  # (description, command)


def _render_examples(examples: tuple[Example, ...]) -> str:
    """Render a tuple of ``(description, command)`` pairs into a Rich-formatted
    examples block suitable for appending to a Typer command docstring.

    The output reproduces the hand-written format used on ``develop``:

    * Header: ``[bold][underline]Examples[/underline][/bold]``
    * Bullet per pair: ``- {description}``
    * Command under each bullet: ``    $ [dim]{command}[/dim]``
    * Blank lines between entries.

    Rich markup inside ``description`` is passed through verbatim so
    inline highlights like ``[magenta]hare[/magenta]`` render correctly.
    """
    lines: list[str] = ["", "[bold][underline]Examples[/underline][/bold]", ""]
    for description, command in examples:
        lines.append(f"- {description}")
        lines.append(f"    $ [dim]{command}[/dim]")
        lines.append("")
    return "\n".join(lines)
