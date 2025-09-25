"""
Provides status enums for Nextmv application runs.

This module defines enumerations for representing the status of a run in a
Nextmv application. It includes a deprecated `Status` enum and the current
`StatusV2` enum.

Classes
-------
Status
    Deprecated status of a run.
StatusV2
    Represents the status of a run.
"""

from enum import Enum


class Status(str, Enum):
    """
    !!! warning
        `Status` is deprecated, use `StatusV2` instead.

    Status of a run.

    You can import the `Status` class directly from `nextmv`:

    ```python
    from nextmv import Status
    ```

    This enum represents the possible states of a run. It is deprecated and
    `StatusV2` should be used for new implementations.

    Attributes
    ----------
    failed : str
        Run failed.
    running : str
        Run is running.
    succeeded : str
        Run succeeded.

    Examples
    --------
    >>> from nextmv.cloud import Status
    >>> current_status = Status.running
    >>> if current_status == Status.succeeded:
    ...     print("Run completed successfully.")
    ... elif current_status == Status.failed:
    ...     print("Run failed.")
    ... else:
    ...     print(f"Run is currently {current_status.value}.")
    Run is currently running.

    """

    failed = "failed"
    """Run failed."""
    running = "running"
    """Run is running."""
    succeeded = "succeeded"
    """Run succeeded."""


class StatusV2(str, Enum):
    """
    Status of a run.

    You can import the `StatusV2` class directly from `nextmv`:

    ```python
    from nextmv import StatusV2
    ```

    This enum represents the comprehensive set of possible states for a run
    in Nextmv.

    Attributes
    ----------
    canceled : str
        Run was canceled.
    failed : str
        Run failed.
    none : str
        Run has no status.
    queued : str
        Run is queued.
    running : str
        Run is running.
    succeeded : str
        Run succeeded.

    Examples
    --------
    >>> from nextmv.cloud import StatusV2
    >>> run_status = StatusV2.queued
    >>> print(f"The run status is: {run_status.value}")
    The run status is: queued

    >>> if run_status == StatusV2.succeeded:
    ...     print("Processing complete.")
    ... elif run_status in [StatusV2.queued, StatusV2.running]:
    ...     print("Processing in progress.")
    ... else:
    ...     print("Processing has not started or has ended with issues.")
    Processing in progress.

    """

    canceled = "canceled"
    """Run was canceled."""
    failed = "failed"
    """Run failed."""
    none = "none"
    """Run has no status."""
    queued = "queued"
    """Run is queued."""
    running = "running"
    """Run is running."""
    succeeded = "succeeded"
    """Run succeeded."""
