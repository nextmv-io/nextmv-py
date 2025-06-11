import datetime
import json
from typing import Any, Union


def deflated_serialize_json(obj: Union[dict, list], json_configurations: dict[str, Any] = None) -> str:
    """
    Serialize a Python object (dict or list) to a JSON string with default configuration for a deflated format.

    Parameters
    ----------
    obj : Union[dict, list]
        The Python object to serialize.
    json_configurations : dict, optional
        Additional configurations for JSON serialization. This allows customization
        of the Python `json.dumps` function. You can specify parameters like `indent`
        for pretty printing or `default` for custom serialization functions.

    Returns
    -------
    str
        A JSON string representation of the object.
    """

    # Apply a default configuration if not provided targeting a deflated format
    json_configurations = json_configurations or {}
    if "default" not in json_configurations:
        json_configurations["default"] = _custom_serial
    if "separators" not in json_configurations:
        json_configurations["separators"] = (",", ":")

    return json.dumps(
        obj,
        **json_configurations,
    )


def serialize_json(obj: Union[dict, list], json_configurations: dict[str, Any] = None) -> str:
    """
    Serialize a Python object (dict or list) to a JSON string.

    Parameters
    ----------
    obj : Union[dict, list]
        The Python object to serialize.
    json_configurations : dict, optional
        Additional configurations for JSON serialization. This allows customization
        of the Python `json.dumps` function. You can specify parameters like `indent`
        for pretty printing or `default` for custom serialization functions.

    Returns
    -------
    str
        A JSON string representation of the object.
    """

    # Apply some default configuration if not provided
    json_configurations = json_configurations or {}
    if "default" not in json_configurations:
        json_configurations["default"] = _custom_serial
    if "indent" not in json_configurations:
        json_configurations["indent"] = 2

    return json.dumps(
        obj,
        **json_configurations,
    )


def _custom_serial(obj: Any) -> str:
    """
    JSON serializer for objects not serializable by default json serializer.

    This function provides custom serialization for datetime objects, converting
    them to ISO format strings.

    Parameters
    ----------
    obj : Any
        The object to serialize.

    Returns
    -------
    str
        The serialized representation of the object.

    Raises
    ------
    TypeError
        If the object type is not supported for serialization.
    """

    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    raise TypeError(f"Type {type(obj)} not serializable")
