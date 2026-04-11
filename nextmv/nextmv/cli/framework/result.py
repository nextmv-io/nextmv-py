"""Result rendering helpers for CLI commands.

``emit()`` is the default output branch for ``cli.command()``: prints the
action's return value as JSON, or saves it to a file with a success message
when ``--output`` was supplied.

``format_save_message()`` produces the save-to-file success message using the
structured-data-to-markup pattern described in the spec ("Design Principle:
Structured Data -> Rendered Markup").

``apply_on_success()`` handles ``cli.command(on_success=...)`` -- either a
``str.format`` template or a callable ``(result, kwargs) -> str``.
"""

import json
from pathlib import Path
from typing import Any, Callable

from nextmv.cli.message import print_json, success


def format_save_message(*, output: str, saved_noun: str | None) -> str:
    """Format the save-to-file success message.

    The default noun is ``"Result"``. A user-supplied ``saved_noun`` is
    capitalized at the first letter (so ``"run list"`` becomes ``"Run list"``)
    and embedded before ``"saved to [magenta]{output}[/magenta]."``.

    Whitespace-only ``saved_noun`` values (e.g. ``"   "``) are treated
    the same as ``None`` — they fall back to ``"Result"``.
    """
    noun = (saved_noun or "").strip() or "Result"
    noun = noun[0].upper() + noun[1:]
    return f"{noun} saved to [magenta]{output}[/magenta]."


def emit(
    result: Any,
    *,
    output: str | None = None,
    saved_noun: str | None = None,
) -> None:
    """Render ``result`` to stdout or to a file.

    When ``output`` is an empty or ``None`` value, prints the result as JSON.
    When ``output`` is a non-empty path, writes the result as JSON to that
    path and prints a save-success message instead.
    """
    if output:
        Path(output).write_text(json.dumps(result, indent=2))
        success(format_save_message(output=output, saved_noun=saved_noun))
        return
    print_json(result)


def apply_on_success(
    on_success: str | Callable[[Any, dict[str, Any]], str] | None,
    *,
    result: Any,
    kwargs: dict[str, Any],
) -> str | None:
    """Format the ``on_success`` handler into a display string.

    Returns ``None`` when ``on_success`` is ``None``. Returns the formatted
    string otherwise. The caller is responsible for passing the returned
    string to ``success(...)``.

    Templates are formatted via ``str.format(**kwargs)``. Callables receive
    ``(result, kwargs)`` and must return a string.
    """
    if on_success is None:
        return None
    if callable(on_success):
        return on_success(result, kwargs)
    return on_success.format(**kwargs)
