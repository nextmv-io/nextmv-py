"""
Module for general utility methods for Application.

Avoid abusing this module, as you should try to keep domain-specific
functionality together and not rely on generic utilities.
"""

import requests


def _is_not_exist_error(e: requests.HTTPError) -> bool:
    """
    Check if the error is a known 404 Not Found error.

    This is an internal helper function that examines HTTPError objects to determine
    if they represent a "Not Found" (404) condition, either directly or through a
    nested exception.

    Parameters
    ----------
    e : requests.HTTPError
        The HTTP error to check.

    Returns
    -------
    bool
        True if the error is a 404 Not Found error, False otherwise.

    Examples
    --------
    >>> try:
    ...     response = requests.get('https://api.example.com/nonexistent')
    ...     response.raise_for_status()
    ... except requests.HTTPError as err:
    ...     if _is_not_exist_error(err):
    ...         print("Resource does not exist")
    ...     else:
    ...         print("Another error occurred")
    Resource does not exist
    """
    if (
        # Check whether the error is caused by a 404 status code - meaning the app does not exist.
        (hasattr(e, "response") and hasattr(e.response, "status_code") and e.response.status_code == 404)
        or
        # Check a possibly nested exception as well.
        (
            hasattr(e, "__cause__")
            and hasattr(e.__cause__, "response")
            and hasattr(e.__cause__.response, "status_code")
            and e.__cause__.response.status_code == 404
        )
    ):
        return True
    return False
