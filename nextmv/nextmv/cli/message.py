"""
The message module is used to print messages to the user with pre-defined
formatting. User messages are always printed to stderr.
"""

import sys

import rich
import typer


def error(msg: str) -> None:
    """
    Pretty-print an error message and exit with code 1. Your message should end
    with a period.

    Parameters
    ----------
    msg : str
        The error message to display.

    Raises
    ------
    typer.Exit
        Exits the program with code 1.
    """

    if not msg.endswith("."):
        msg += "."

    rich.print(f"[red]Error:[/red] {msg}", file=sys.stderr)

    raise typer.Exit(code=1)


def success(msg: str) -> None:
    """
    Pretty-print a success message. Your message should end with a period.

    Parameters
    ----------
    msg : str
        The success message to display.
    """

    if not msg.endswith("."):
        msg += "."

    rich.print(f":white_check_mark: {msg}", file=sys.stderr)


def warning(msg: str) -> None:
    """
    Pretty-print a warning message. Your message should end with a period.

    Parameters
    ----------
    msg : str
        The warning message to display.
    """

    if not msg.endswith("."):
        msg += "."

    rich.print(f":construction: {msg}", file=sys.stderr)


def info(msg: str, emoji: str | None = None) -> None:
    """
    Pretty-print an informational message. Your message should end with a
    period. The use of emojis is encouraged to give context to the message. An
    emoji should be a string as specified in:
    https://rich.readthedocs.io/en/latest/markup.html#emoji.

    Parameters
    ----------
    msg : str
        The informational message to display.
    emoji : str | None
        An optional emoji to prefix the message. If None, no emoji is used. The
        emoji should be a string as specified in:
        https://rich.readthedocs.io/en/latest/markup.html#emoji. For example:
        `:hourglass_flowing_sand:`.
    """

    if not msg.endswith("."):
        msg += "."

    if emoji:
        rich.print(f"{emoji} {msg}", file=sys.stderr)
        return

    rich.print(msg, file=sys.stderr)
