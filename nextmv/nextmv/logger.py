"""
Logger module that writes to stderr.

This module provides utilities for redirecting standard output to standard error
and for writing log messages directly to stderr.

Functions
---------
redirect_stdout
    Redirect all messages written to stdout to stderr.
reset_stdout
    Reset stdout to its original value.
log
    Log a message to stderr.
"""

import sys

# Original stdout reference held when redirection is active
__original_stdout = None
# Flag to track if stdout has been redirected
__stdout_redirected = False


def redirect_stdout() -> None:
    """
    Redirect all messages written to stdout to stderr.

    You can import the `redirect_stdout` function directly from `nextmv`:

    ```python
    from nextmv import redirect_stdout
    ```

    This function captures the current sys.stdout and replaces it with sys.stderr.
    When redirection is no longer needed, call `reset_stdout()` to restore the
    original stdout.

    Examples
    --------
    >>> redirect_stdout()
    >>> print("This will go to stderr")
    >>> reset_stdout()
    >>> print("This will go to stdout")
    """

    global __original_stdout, __stdout_redirected
    if __stdout_redirected:
        return
    __stdout_redirected = True

    __original_stdout = sys.stdout
    sys.stdout = sys.stderr


def reset_stdout() -> None:
    """
    Reset stdout to its original value.

    You can import the `reset_stdout` function directly from `nextmv`:

    ```python
    from nextmv import reset_stdout
    ```

    This function should always be called after `redirect_stdout()` to avoid
    unexpected behavior. It restores the original stdout that was captured
    during redirection.

    Examples
    --------
    >>> redirect_stdout()
    >>> print("This will go to stderr")
    >>> reset_stdout()
    >>> print("This will go to stdout")
    """
    global __original_stdout, __stdout_redirected
    if not __stdout_redirected:
        return
    __stdout_redirected = False

    if __original_stdout is None:
        sys.stdout = sys.__stdout__
        return

    sys.stdout = __original_stdout
    __original_stdout = None


def log(message: str) -> None:
    """
    Log a message to stderr.

    You can import the `log` function directly from `nextmv`:

    ```python
    from nextmv import log
    ```

    Parameters
    ----------
    message : str
        The message to log.

    Examples
    --------
    >>> log("An error occurred")
    An error occurred
    """

    print(message, file=sys.stderr)
