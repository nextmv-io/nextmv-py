"""Defines ndarray type."""

from typing import Iterable

import numpy as np
from pydantic import BeforeValidator, PlainSerializer
from typing_extensions import Annotated

ndarray = Annotated[
    np.ndarray,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: ndarray_to_list(x)),
]


def ndarray_from_list(x: Iterable):
    return np.array(x)


def ndarray_to_list(x: np.ndarray):
    return x.tolist()
