"""NumPy ndarray wrapper for Pydantic model integration.

This module provides utilities to handle NumPy arrays in Pydantic models.

Variables
---------
ndarray : Annotated
    A type annotation for NumPy arrays in Pydantic models.
"""

from typing import Annotated

import numpy as np
from pydantic import BeforeValidator, PlainSerializer

ndarray = Annotated[
    np.ndarray,
    BeforeValidator(lambda x: x),
    PlainSerializer(lambda x: x.tolist()),
]
"""
ndarray: An annotated type that represents a NumPy array.

You can import the `ndarray` type directly from `nextmv_sklearn`:

```python
from nextmv_sklearn import ndarray
```

This type is designed for use with Pydantic models to properly handle
NumPy arrays for validation and serialization.

The BeforeValidator ensures the input is preserved as is, while
PlainSerializer converts the ndarray to a Python list when serializing.

Examples
--------
>>> from pydantic import BaseModel
>>> from nextmv_sklearn import ndarray
>>> import numpy as np
>>>
>>> class MyModel(BaseModel):
...     data: ndarray
...
>>> model = MyModel(data=np.array([1, 2, 3]))
>>> model.model_dump_json()
'{"data":[1,2,3]}'
"""
