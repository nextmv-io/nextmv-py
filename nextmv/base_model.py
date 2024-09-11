"""JSON class for data wrangling JSON objects."""

from importlib import import_module
from typing import Any, Dict

from pydantic import BaseModel


class BaseModel(BaseModel):
    """Base class for data wrangling tasks with JSON."""

    def __dict__(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates the class from a dict."""

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the class to a dict."""

        return self.model_dump(mode="json", exclude_none=True, by_alias=True)


def from_dict(data: Dict[str, Any]):
    """Load a data model instance from a dict with associated class info."""

    module = import_module(data["class"]["module"])
    cls = getattr(module, data["class"]["name"])
    return cls.from_dict(data["attributes"])


def to_dict(obj: BaseModel):
    """Convert a data model instance to a dict with associated class info."""

    t = type(obj)
    return {
        "class": {
            "module": t.__module__,
            "name": t.__name__,
        },
        "attributes": t.to_dict(obj),
    }
