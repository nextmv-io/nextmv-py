"""Defines ndarray type."""

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
