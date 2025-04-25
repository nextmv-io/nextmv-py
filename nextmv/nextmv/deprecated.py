import warnings


def deprecated(name: str, reason: str):
    """A very simple functon to mark something as deprecated."""

    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn(f"{name}: {reason}", category=DeprecationWarning, stacklevel=2)
    warnings.simplefilter("default", DeprecationWarning)
