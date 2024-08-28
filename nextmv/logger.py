"""Logger that writes to stderr."""

import sys

__original_stdout = None

stdout_redirected: bool = False
"""Flag to indicate if stdout is currently redirected."""


def redirect_stdout() -> None:
    """Redirect all messages written to stdout to stderr. When you do not want
    to redirect stdout anymore, call `reset_stdout`."""

    global __original_stdout
    global stdout_redirected

    __original_stdout = sys.stdout
    sys.stdout = sys.stderr
    stdout_redirected = True


def reset_stdout() -> None:
    """Reset stdout to its original value. This function should always be
    called after `redirect_stdout` to avoid unexpected behavior."""

    global stdout_redirected
    global __original_stdout

    if __original_stdout is None:
        return

    sys.stdout = __original_stdout
    stdout_redirected = False
    __original_stdout = None


def log(message: str) -> None:
    """
    Log a message to stderr.

    Args:
        message: The message to log.
    """

    print(message, file=sys.stderr)
