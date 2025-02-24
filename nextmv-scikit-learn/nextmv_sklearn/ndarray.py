from typing import Annotated

import numpy as np
from pydantic import BeforeValidator, PlainSerializer

ndarray = Annotated[
    np.ndarray,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: x.tolist()),
]
