"""JSON class for data wrangling JSON objects."""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class BaseModel(BaseModel):
    """Base class for data wrangling tasks with JSON."""

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]] = None):
        """Instantiates the class from a dict."""

        if data is None:
            return None

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the class to a dict."""

        return self.model_dump(mode="json", exclude_none=True, by_alias=True)
