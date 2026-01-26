import queue
import sys
import threading

from rich.prompt import Confirm

from nextmv.cli.message import info


def get_confirmation(msg: str, timeout: int = 30) -> bool:
    """
    Method to get a yes/no confirmation from the user with a timeout.

    Parameters
    ----------
    msg : str
        The message to display to the user.
    timeout : int
        The timeout in seconds to wait for a response.

    Returns
    -------
    bool
        True if the user confirmed, False otherwise.
    """

    # If this is not an interactive terminal, do not ask for confirmation, to
    # avoid hanging indefinitely waiting for a user response.
    if not sys.stdin.isatty():
        return False

    result_queue = queue.Queue()

    def ask():
        result = Confirm.ask(
            msg,
            default=False,
            case_sensitive=False,
            show_default=True,
            show_choices=True,
        )
        result_queue.put(result)

    t = threading.Thread(target=ask, daemon=True)
    t.start()

    try:
        return result_queue.get(timeout=float(timeout))

    except queue.Empty:
        print("\n", file=sys.stderr)
        info(
            msg=f"No response received within [magenta]{timeout}s[/magenta], assuming no ([magenta]n[/magenta]).",
            emoji=":bulb:",
        )

        return False
