"""JSON class for data wrangling JSON objects."""

import json
from importlib import import_module
from typing import Any, Dict

from pydantic import BaseModel

from nextmv import ndarray


class BaseModel(BaseModel):
    """Base class for data wrangling tasks with JSON."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Instantiates the class from a dict."""

        for key, value in cls.__annotations__.items():
            if key in data and value is ndarray.ndarray:
                data[key] = ndarray.from_list(data[key])

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the class to a dict."""

        return self.model_dump(mode="json", exclude_none=True, by_alias=True)

    @classmethod
    def from_json(cls, s):
        """Instantiates the class from a JSON string."""
        return cls.from_dict(json.loads(s))

    def to_json(self):
        """Converts the class to a JSON string."""
        return json.dumps(self.to_dict())


def from_dict(data: Dict[str, Any]):
    module = import_module(data["class"]["module"])
    cls = getattr(module, data["class"]["name"])
    return cls.from_dict(data["attributes"])


def to_dict(obj: BaseModel):
    t = type(obj)
    return {
        "class": {
            "module": t.__module__,
            "name": t.__name__,
        },
        "attributes": t.to_dict(obj),
    }


def from_json(s):
    return from_dict(json.loads(s))


def to_json(obj: BaseModel):
    return json.dumps(to_dict(obj))
