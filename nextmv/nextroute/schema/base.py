"""Base class for data wrangling."""

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class _Base:
    """Base class for data wrangling tasks."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Instantiates the class from a dict."""

        return cls(**data)

    @classmethod
    def from_json(cls, filepath: str):
        """Instantiates the class from a JSON file."""

        with open(filepath) as f:
            data = json.load(f)

        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Converts the class to a dict."""

        return asdict(
            self,
            dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
        )
