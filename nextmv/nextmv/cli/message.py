"""
The message module is used to print messages to the user with pre-defined
formatting. Logging, in general, is always printed to stderr.
"""

import sys
import typing
from enum import Enum
from typing import Any

import questionary
import rich
import typer
from rich.prompt import Confirm

# Shared questionary style that matches the CLI's [code] tag rendering:
# bold with no color overrides, letting the terminal's default foreground
# color show through.
QUESTIONARY_STYLE = questionary.Style(
    [
        ("qmark", "noinherit"),
        ("question", "noinherit"),
        ("answer", "fg:ansimagenta"),
        ("pointer", "fg:ansimagenta bold"),
        ("highlighted", "fg:ansimagenta bold underline"),
        ("selected", ""),
        ("instruction", "fg:ansiyellow italic"),
    ]
)


def message(msg: str, emoji: str | None = None) -> None:
    """
    Pretty-print a message. Your message should end with a period. The use of
    emojis is encouraged to give context to the message. An emoji should be a
    string as specified in:
    https://rich.readthedocs.io/en/latest/markup.html#emoji.

    Parameters
    ----------
    msg : str
        The message to display.
    emoji : str | None
        An optional emoji to prefix the message. If None, no emoji is used. The
        emoji should be a string as specified in:
        https://rich.readthedocs.io/en/latest/markup.html#emoji. For example:
        `:hourglass_flowing_sand:`.
    """

    msg = _format(msg)
    if emoji:
        rich.print(f"{emoji} {msg}", file=sys.stderr)
        return

    rich.print(msg, file=sys.stderr)


def info(msg: str) -> None:
    """
    Pretty-print an informational message. Your message should end with a
    period.

    Parameters
    ----------
    msg : str
        The informational message to display.
    """

    message(msg, emoji=":bulb:")


def in_progress(msg: str) -> None:
    """
    Pretty-print an in-progress message with an hourglass emoji. Your message
    should end with a period.

    Parameters
    ----------
    msg : str
        The in-progress message to display.
    """

    message(msg, emoji=":hourglass_flowing_sand:")


def success(msg: str) -> None:
    """
    Pretty-print a success message. Your message should end with a period.

    Parameters
    ----------
    msg : str
        The success message to display.
    """

    message(msg, emoji=":white_check_mark:")


def warning(msg: str) -> None:
    """
    Pretty-print a warning message. Your message should end with a period.

    Parameters
    ----------
    msg : str
        The warning message to display.
    """

    msg = _format(msg)
    rich.print(f":construction: [yellow] Warning:[/yellow] {msg}", file=sys.stderr)


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

    msg = _format(msg)
    rich.print(f":x: [red]Error:[/red] {msg}", file=sys.stderr)

    raise typer.Exit(code=1)


def print_json(data: dict[str, Any] | list[dict[str, Any]]) -> None:
    """
    Pretty-print json-serializable data as JSON to stdout.

    Parameters
    ----------
    data : dict[str, Any] | list[dict[str, Any]]
        The data to print as JSON.
    """

    rich.print_json(data=data)


def enum_values(enum_class: Enum) -> str:
    """
    Get a nicely formatted string of the values of an Enum class, using commas
    and an oxford comma.

    Parameters
    ----------
    enum_class : Enum
        The Enum class to get the values from.

    Returns
    -------
    str
        A nicely formatted string of the values of the Enum class.
    """

    values = [f"[magenta]{member.value}[/magenta]" for member in enum_class]
    if len(values) == 0:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return " and ".join(values)

    return ", ".join(values[:-1]) + ", and " + values[-1]


def confirmation(msg: str, default: bool = False) -> bool:
    """
    Prompt the user to get a yes/no confirmation.

    Parameters
    ----------
    msg : str
        The message to display to the user.
    default : bool, optional
        The default value if the user just presses Enter. Default is False.

    Returns
    -------
    bool
        True if the user confirmed, False otherwise.
    """

    # If this is not an interactive terminal, do not ask for confirmation, to
    # avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        return default

    return Confirm.ask(
        msg,
        default=default,
        case_sensitive=False,
        show_default=True,
        show_choices=True,
    )


def choice(msg: str, choices: typing.Iterable[str], default: str | None = None) -> str:
    """
    Prompt the user to select one option from a list of choices.

    Parameters
    ----------
    msg : str
        The message to display as the selection prompt.
    choices : typing.Iterable[str]
        The available options the user can choose from.
    default : str | None, optional
        The option that is pre-selected when the prompt appears. If None, no
        default is pre-selected. Default is None.

    Returns
    -------
    str
        The option selected by the user.

    Raises
    ------
    typer.Exit
        Exits the program with code 1 if the operation is cancelled or no
        selection is made.
    """

    # If this is not an interactive terminal, do not ask for confirmation, to
    # avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        return default

    try:
        selection = questionary.select(
            msg,
            choices=choices,
            default=default,
            qmark="💡",
            style=QUESTIONARY_STYLE,
        ).ask(
            kbi_msg="❌ Operation cancelled by user.",
        )
    except Exception as e:
        error(f"Operation cancelled by user: {e}")

    if selection is None:
        error("No selection made.")

    return selection


def directory_path(msg: str, default: str | None = None) -> str:
    """
    Prompt the user to enter or select a directory path.

    Parameters
    ----------
    msg : str
        The message to display as the directory path prompt.
    default : str | None, optional
        The default directory path pre-filled in the prompt. If None, no
        default is pre-filled. Default is None.

    Returns
    -------
    str
        The directory path entered or selected by the user.

    Raises
    ------
    typer.Exit
        Exits the program with code 1 if the operation is cancelled or no
        directory path is provided.
    """
    # If this is not an interactive terminal, do not ask for confirmation, to
    # avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        return default

    try:
        dirpath = questionary.path(
            message=msg,
            default=default,
            only_directories=True,
            qmark="💡",
            style=QUESTIONARY_STYLE,
        ).ask(
            kbi_msg="❌ Operation cancelled by user.",
        )
    except Exception as e:
        error(f"Operation cancelled by user: {e}")

    if dirpath is None:
        error("No directory path provided.")

    return dirpath


def _format(msg: str) -> str:
    """
    Format a message to ensure it ends with a period.

    Parameters
    ----------
    msg : str
        The message to format.
    """
    msg = msg.rstrip("\n")
    if not msg.endswith("."):
        msg += "."

    return msg
