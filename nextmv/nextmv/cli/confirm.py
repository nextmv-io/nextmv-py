import sys

from rich.prompt import Confirm


def get_confirmation(msg: str) -> bool:
    """
    Method to get a yes/no confirmation from the user.

    Parameters
    ----------
    msg : str
        The message to display to the user.

    Returns
    -------
    bool
        True if the user confirmed, False otherwise.
    """

    # If this is not an interactive terminal, do not ask for confirmation, to
    # avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        return False

    return Confirm.ask(
        msg,
        default=False,
        case_sensitive=False,
        show_default=True,
        show_choices=True,
    )
