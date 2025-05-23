"""
Provides base functionality for handling JSON data in models.

This module contains utilities for converting between dictionaries and model
instances, facilitating data serialization and deserialization.

Classes
-------
BaseModel:
    A base class extending Pydantic's BaseModel with additional methods for
    JSON data serialization and deserialization.

Functions
---------
from_dict:
    Load a data model instance from a dictionary containing class information
    and attributes.
"""

from importlib import import_module
from typing import Any, Optional

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    """
    Base class for data wrangling tasks with JSON.

    This class extends Pydantic's `BaseModel` to provide additional methods
    for converting between Python objects and JSON/dictionary representations.
    """

    @classmethod
    def from_dict(cls, data: Optional[dict[str, Any]] = None):
        """
        Instantiate the class from a dictionary.

        Parameters
        ----------
        data : dict[str, Any], optional
            The dictionary containing the data to instantiate the class.
            If None, returns None.

        Returns
        -------
        cls or None
            An instance of the class with the given data or None if data is None.
        """

        if data is None:
            return None

        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the class instance to a dictionary.

        The conversion uses Pydantic's model_dump method, excluding None values
        and using field aliases if defined.

        Returns
        -------
        dict[str, Any]
            Dictionary representation of the class instance.
        """

        return self.model_dump(mode="json", exclude_none=True, by_alias=True)


def from_dict(data: dict[str, Any]) -> Any:
    """
    Load a data model instance from a `dict` with associated class info.

    Parameters
    ----------
    data : dict[str, Any]
        The data to load.

    Returns
    -------
    Any
        The loaded data model instance.
    """

    module = import_module(data["class"]["module"])
    cls = getattr(module, data["class"]["name"])

    return cls.from_dict(data["attributes"])
