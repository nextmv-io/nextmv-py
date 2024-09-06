"""Defines ndarray type."""

try:
    import numpy as np
    from pydantic import BeforeValidator, PlainSerializer
    from typing_extensions import Annotated

    ndarray = Annotated[
        np.ndarray,
        BeforeValidator(lambda x: x),
        PlainSerializer(lambda x: x.tolist()),
    ]

    def from_list(x):
        return np.array(x)

except ImportError:
    from typing import Any, List

    ndarray = List[Any]

    def from_list(x):
        return x
