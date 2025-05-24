"""Utilities for handling deprecated functionality within the Nextmv Python SDK.

This module provides tools to mark functions, methods, or features as deprecated,
emitting appropriate warnings to users. These warnings inform users that the
functionality will be removed in a future release and suggest alternative approaches.

The main purpose of this module is to help with the smooth transition when
API changes are necessary, giving users time to update their code before
functionality is removed completely.
"""

import warnings


def deprecated(name: str, reason: str) -> None:
    """Mark functionality as deprecated with a warning message.

    This function emits a DeprecationWarning when called, indicating that
    the functionality will be removed in a future release.

    Parameters
    ----------
    name : str
        The name of the function, method, or feature being deprecated.
    reason : str
        The reason why the functionality is being deprecated, possibly
        with suggestions for alternative approaches.

    Notes
    -----
    This function temporarily changes the warning filter to ensure the
    deprecation warning is shown, then resets it afterward.

    Examples
    --------
    >>> def some_function():
    ...     deprecated("feature_x", "Use feature_y instead")
    ...     # function implementation
    """

    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(
        f"{name}: {reason}. This functionality will be removed in a future release",
        category=DeprecationWarning,
        stacklevel=2,
    )
    warnings.simplefilter("default", DeprecationWarning)
