"""Configuration for a run."""

import argparse
import builtins
import copy
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from nextmv.base_model import BaseModel


@dataclass
class Parameter:
    """
    Parameter that is used in a `Configuration`. When a parameter is required,
    it is a good practice to provide a default value for it. This is because
    the configuration will raise an error if a required parameter is not
    provided through a command-line argument, an environment variable or a
    default value.

    Parameters
    ----------
    name : str
        The name of the parameter.
    param_type : type
        The type of the parameter.
    default : Any, optional
        The default value of the parameter. Even though this is optional, it is
        recommended to provide a default value for all parameters.
    description : str, optional
        An optional description of the parameter. This is useful for generating
        help messages for the configuration.
    required : bool, optional
        Whether the parameter is required. If a parameter is required, it will
        be an error to not provide a value for it, either trough a command-line
        argument, an environment variable or a default value.
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

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parameter":
        """
        Creates an instance of `Parameter` from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            The dictionary representation of a parameter.

        Returns
        -------
        Parameter
            An instance of `Parameter`.
        """

        param_type_string = data["param_type"]
        param_type = getattr(builtins, param_type_string.split("'")[1])

        return Parameter(
            name=data["name"],
            param_type=param_type,
            default=data.get("default"),
            description=data.get("description"),
            required=data.get("required", False),
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the parameter to a dict.

        Returns
        -------
        Dict[str, Any]
            The parameter as a dict.
        """

        return {
            "name": self.name,
            "param_type": str(self.param_type),
            "default": self.default,
            "description": self.description,
            "required": self.required,
        }


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

    Options works as a Namespace, so you can assign new attributes to it. For
    example, you can do `options.foo = "bar"`.

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

        self.parameters = copy.deepcopy(parameters)

        parser = argparse.ArgumentParser(
            add_help=True,
            usage="%(prog)s [options]",
            description="Options for %(prog)s. Use command-line arguments (highest precedence) "
            + "or environment variables.",
        )
        params_by_field_name: Dict[str, Parameter] = {}

        for p, param in enumerate(parameters):
            if not isinstance(param, Parameter):
                raise TypeError(f"expected a <Parameter> object, but got {type(param)} in index {p}")

            # Remove any leading '-'. This is in line with argparse's behavior.
            param.name = param.name.lstrip("-")

            parser.add_argument(
                f"-{param.name}",
                f"--{param.name}",
                type=param.param_type if param.param_type is not bool else str,
                help=self._description(param),
            )

            # Store the parameter by its field name for easy access later. argparse
            # replaces '-' with '_', so we do the same here.
            params_by_field_name[param.name.replace("-", "_")] = param

        args = parser.parse_args()

        for arg in vars(args):
            param = params_by_field_name[arg]

            # First, attempt to set the value of a parameter from the
            # command-line args.
            arg_value = getattr(args, arg)
            if arg_value is not None:
                value = self._parameter_value(param, arg_value)
                setattr(self, arg, value)
                continue

            # Second, attempt to set the value of a parameter from the
            # environment variables.
            upper_name = arg.upper()
            env_value = os.getenv(upper_name)
            if env_value is not None:
                try:
                    typed_env_value = param.param_type(env_value) if param.param_type is not bool else env_value
                except ValueError:
                    raise ValueError(f'environment variable "{upper_name}" is not of type {param.param_type}') from None

                value = self._parameter_value(param, typed_env_value)
                setattr(self, arg, value)
                continue

            # Finally, attempt to set a default value. This is only allowed
            # for non-required parameters.
            if not param.required:
                setattr(self, arg, param.default)
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

        self_dict = copy.deepcopy(self.__dict__)
        self_dict.pop("parameters")
        m = model.from_dict(data={"config": self_dict})

        return m.to_dict()["config"]

    def parameters_dict(self) -> List[Dict[str, Any]]:
        """
        Converts the options to a list of dicts. Each dict is the dict
        representation of a `Parameter`.

        Returns
        -------
        List[Dict[str, Any]]
            The list of dictionaries (parameter entries).
        """

        return [param.to_dict() for param in self.parameters]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Options":
        """
        Creates an instance of `Options` from a dictionary. The dictionary
        should have the following structure:

        {
            "duration": "30",
            "threads": 4,
        }

        Parameters
        ----------
        data : Dict[str, Any]
            The dictionary representation of the options.

        Returns
        -------
        Options
            An instance of `Options`.
        """

        parameters = []
        for key, value in data.items():
            parameter = Parameter(name=key, param_type=type(value), default=value)
            parameters.append(parameter)

        return cls(*parameters)

    @classmethod
    def from_parameters_dict(cls, parameters_dict: List[Dict[str, Any]]) -> "Options":
        """
        Creates an instance of `Options` from parameters in dict form. Each
        entry is the dict representation of a `Parameter`.

        Parameters
        ----------
        data : List[Dict[str, Any]]
            The list of dictionaries (parameter entries).

        Returns
        -------
        Options
            An instance of `Options`.
        """

        parameters = []
        for parameter_dict in parameters_dict:
            parameter = Parameter.from_dict(parameter_dict)
            parameters.append(parameter)

        return cls(*parameters)

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

    @staticmethod
    def _parameter_value(parameter: Parameter, value: Any) -> Any:
        """Handles how the value of a parameter is extracted."""

        param_type = parameter.param_type
        if param_type is not bool:
            return value

        value = str(value).lower()

        if value in ("true", "True", "TRUE", "1", "t", "T", "y", "Y", "yes", "Yes", "YES"):
            return True

        return False
