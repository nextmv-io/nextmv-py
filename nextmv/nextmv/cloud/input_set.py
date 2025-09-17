"""Definitions for input sets and related cloud objects.

This module provides classes for managing inputs and input sets in the Nextmv Cloud.

Classes
-------
ManagedInput
    An input created for experimenting with an application.
InputSet
    A collection of inputs from associated runs.
"""

from datetime import datetime
from typing import Optional

from nextmv.base_model import BaseModel
from nextmv.run import Format


class ManagedInput(BaseModel):
    """An input created for experimenting with an application.

    You can import the `ManagedInput` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManagedInput
    ```

    This class represents an input that was uploaded to the Nextmv Cloud
    for experimentation purposes. It contains metadata about the input,
    such as its ID, name, description, and creation time.

    Parameters
    ----------
    id : str
        Unique identifier of the input.
    name : str, optional
        User-defined name of the input.
    description : str, optional
        User-defined description of the input.
    run_id : str, optional
        Identifier of the run that created this input.
    upload_id : str, optional
        Identifier of the upload that created this input.
    format : Format, optional
        Format of the input (e.g., JSON, CSV).
    created_at : datetime, optional
        Timestamp when the input was created.
    updated_at : datetime, optional
        Timestamp when the input was last updated.

    Examples
    --------
    >>> input = ManagedInput(id="inp_123456789")
    >>> print(input.id)
    inp_123456789
    """

    id: str
    """ID of the input."""

    name: Optional[str] = None
    """Name of the input."""
    description: Optional[str] = None
    """Description of the input."""
    run_id: Optional[str] = None
    """ID of the run that created the input."""
    upload_id: Optional[str] = None
    """ID of the upload that created the input."""
    format: Optional[Format] = None
    """Format of the input."""
    created_at: Optional[datetime] = None
    """Creation time of the input."""
    updated_at: Optional[datetime] = None
    """Last update time of the input."""


class InputSet(BaseModel):
    """A collection of inputs from associated runs.

    You can import the `InputSet` class directly from `cloud`:

    ```python
    from nextmv.cloud import InputSet
    ```

    An input set aggregates multiple inputs used for experimentation with an application
    in the Nextmv Cloud. It allows organizing and managing related inputs
    for comparison and analysis.

    Parameters
    ----------
    app_id : str
        Identifier of the application that the input set belongs to.
    created_at : datetime
        Timestamp when the input set was created.
    description : str
        User-defined description of the input set.
    id : str
        Unique identifier of the input set.
    input_ids : list[str]
        List of identifiers of the inputs in the input set.
    name : str
        User-defined name of the input set.
    updated_at : datetime
        Timestamp when the input set was last updated.
    inputs : list[ManagedInput]
        List of ManagedInput objects contained in this input set.

    Examples
    --------
    >>> input_set = InputSet(
    ...     app_id="app_123456789",
    ...     id="is_987654321",
    ...     name="My Input Set",
    ...     description="A collection of routing inputs",
    ...     input_ids=["inp_111", "inp_222"],
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     inputs=[]
    ... )
    >>> print(input_set.name)
    My Input Set
    >>> print(len(input_set.input_ids))
    2
    """

    app_id: str
    """ID of the application that the input set belongs to."""
    created_at: datetime
    """Creation time of the input set."""
    description: str
    """Description of the input set."""
    id: str
    """ID of the input set."""
    input_ids: list[str]
    """IDs of the inputs in the input set."""
    name: str
    """Name of the input set."""
    updated_at: datetime
    """Last update time of the input set."""
    inputs: list[ManagedInput]
    """List of inputs in the input set."""
