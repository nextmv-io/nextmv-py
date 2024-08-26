"""Configuration for a run."""

import argparse
import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from nextmv.base_model import BaseModel


@dataclass
class Parameter:
    """
    Parameter that is used in a `Configuration`. When a parameter is required,
    it is a good practice to provide a default value for it. This is because
    the configuration will raise an error if a required parameter is not
    provided through a command-line argument, an environment variable or a
    default value.
    """

    name: str
    """The name of the parameter."""
    param_type: type
    """The type of the parameter."""

    default: Optional[Any] = None
    """The default value of the parameter. Even though this is optional, it is
    recommended to provide a default value for all parameters."""
    description: Optional[str] = None
    """An optional description of the parameter. This is useful for generating
    help messages for the configuration."""
    required: bool = False
    """Whether the parameter is required. If a parameter is required, it will
    be an error to not provide a value for it, either trough a command-line
    argument, an environment variable or a default value."""


class Options:
    """
    Options for a run. To initialize options, pass in one or more `Parameter`
    objects. The options will look for the values of the given parameters in
    the following order: command-line arguments, environment variables, default
    values.

    Once the options are initialized, you can access the parameters as
    attributes of the `Options` object. For example, if you have a
    `Parameter` object with the name "duration", you can access it as
    `options.duration`.

    If a parameter is required and not provided through a command-line
    argument, an environment variable or a default value, an error will be
    raised.

    Parameters
    ----------
    *parameters : Parameter
        The parameters that are used in the options. At least one
        parameter is required.

    Examples
    --------
    >>> import nextmv
    >>>
    >>> options = nextmv.Options(
    ...     nextmv.Parameter("duration", str, "30s", description="solver duration", required=True),
    ...     nextmv.Parameter("threads", int, 4, description="computer threads", required=True),
    ... )
    >>>
    >>> print(options.duration, options.threads, options.to_dict())

    30s 4 {"duration": "30s", "threads": 4}

    Raises
    ------
    ValueError
        If no parameters are provided.
    ValueError
        If a required parameter is not provided through a command-line
        argument, an environment variable or a default value.
    TypeError
        If a parameter is not a `Parameter` object.
    ValueError
        If an environment variable is not of the type of the corresponding
        parameter.
    """

    def __init__(self, *parameters: Parameter):
        """Initializes the options."""

        if not parameters:
            return

        parser = argparse.ArgumentParser(
            add_help=True,
            usage="%(prog)s [options]",
            description="Options for %(prog)s. Use command-line arguments (highest precedence) "
            + "or environment variables.",
        )
        params_by_name: Dict[str, Parameter] = {}

        for p, param in enumerate(parameters):
            if not isinstance(param, Parameter):
                raise TypeError(f"expected a <Parameter> object, but got {type(param)} in index {p}")

            parser.add_argument(
                f"-{param.name}",
                f"--{param.name}",
                type=param.param_type,
                help=self._description(param),
            )
            params_by_name[param.name] = param

        args = parser.parse_args()

        for arg in vars(args):
            # First, attempt to set the value of a parameter from the
            # command-line args.
            value = getattr(args, arg)
            if value is not None:
                setattr(self, arg, value)
                continue

            # Second, attempt to set the value of a parameter from the
            # environment variables.
            param = params_by_name[arg]
            upper_name = arg.upper()
            env_value = os.getenv(upper_name)
            if env_value is not None:
                try:
                    typed_env_value = param.param_type(env_value)
                except ValueError:
                    raise ValueError(f'environment variable "{upper_name}" is not of type {param.param_type}') from None

                setattr(self, arg, typed_env_value)
                continue

            # Finally, attempt to set the value of a parameter from the default
            # value.
            if param.default is not None:
                setattr(self, arg, param.default)
                continue

            if not param.required:
                continue

            # At this point, the parameter is required and no value was
            # provided
            raise ValueError(
                f'parameter "{arg}" is required but not provided through: command-line args, env vars, or default value'
            )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the options to a dict.

        Returns
        -------
        Dict[str, Any]
            The options as a dict.
        """

        class model(BaseModel):
            config: Dict[str, Any]

        m = model.from_dict(data={"config": self.__dict__})

        return m.to_dict()["config"]

    @staticmethod
    def _description(param: Parameter) -> str:
        """Returns a description for a parameter."""

        description = f"[env var: {param.name.upper()}]"

        if param.required:
            description += " (required)"

        if param.default is not None:
            description += f" (default: {param.default})"

        description += f" (type: {param.param_type.__name__})"

        if param.description is not None:
            description += f": {param.description}"

        return description
