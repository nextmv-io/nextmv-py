"""
Utilities for handling deprecated functionality within the Nextmv Python SDK.

This module provides tools to mark functions, methods, or features as deprecated,
emitting appropriate warnings to users. These warnings inform users that the
functionality will be removed in a future release and suggest alternative approaches.

The main purpose of this module is to help with the smooth transition when
API changes are necessary, giving users time to update their code before
functionality is removed completely.
"""

import warnings


class NextmvDeprecationWarning(DeprecationWarning):
    """Deprecation warning emitted by the Nextmv SDK."""


def deprecated(name: str, reason: str) -> None:
    """
    Mark functionality as deprecated with a warning message.

    This function emits a DeprecationWarning when called, indicating that
    the functionality will be removed in a future release.

    Parameters
    ----------
    name : str
        The name of the function, method, or feature being deprecated.
    reason : str
        The reason why the functionality is being deprecated, possibly
        with suggestions for alternative approaches.

    Examples
    --------
    >>> def some_function():
    ...     deprecated("feature_x", "Use feature_y instead")
    ...     # function implementation
    """

    warnings.warn(
        f"{name}: {reason}. This functionality will be removed in the next major release.",
        category=NextmvDeprecationWarning,
        stacklevel=3,
    )
