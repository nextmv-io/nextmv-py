import sys

from rich.prompt import Confirm


def get_confirmation(msg: str, default: bool = False) -> bool:
    """
    Method to get a yes/no confirmation from the user.

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
