"""Logger that writes to stderr."""

import sys


def redirect_stdout() -> None:
    """Redirect all messages written to stdout to stderr. When you do not want
    to redirect stdout anymore, call `reset_stdout`."""

    sys.stdout = sys.stderr


def reset_stdout() -> None:
    """Reset stdout to its original value. This function should always be
    called after `redirect_stdout` to avoid unexpected behavior."""

    sys.stdout = sys.__stdout__


def log(message: str) -> None:
    """
    Log a message to stderr.

    Args:
        message: The message to log.
    """

    print(message, file=sys.stderr)
