from enum import Enum


class Status(str, Enum):
    """Status of a run. Deprecated: use StatusV2."""

    failed = "failed"
    """Run failed."""
    running = "running"
    """Run is running."""
    succeeded = "succeeded"
    """Run succeeded."""


class StatusV2(str, Enum):
    """Status of a run."""

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
