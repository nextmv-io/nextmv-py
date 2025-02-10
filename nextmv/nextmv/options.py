"""Configuration for a run."""

import argparse
import builtins
import copy
import os
from dataclasses import dataclass
from typing import Any, Optional

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
    choices : list[Optional[Any]], optional
        Limits values to a specific set of choices.
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
    choices: list[Optional[Any]] = None
    """Limits values to a specific set of choices."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Parameter":
        """
        Creates an instance of `Parameter` from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
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
            choices=data.get("choices"),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the parameter to a dict.

        Returns
        -------
        dict[str, Any]
            The parameter as a dict.
        """

        return {
            "name": self.name,
            "param_type": str(self.param_type),
            "default": self.default,
            "description": self.description,
            "required": self.required,
            "choices": self.choices,
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

    Options are parsed from the given sources when an attribute is accessed.
    Alternatively, you can call the `parse` method to parse the options
    manually. Options that are _not_ parsed may be merged with other unparsed
    options, by using the `merge` method. Once options are parsed, they cannot
    be merged with other options. After options are parsed, you may get the
    help message by running the script with the `-h/--help` flag.

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
    ...     nextmv.Parameter("duration", str, "30s", description="solver duration", required=False),
    ...     nextmv.Parameter("threads", int, 4, description="computer threads", required=False),
    ... )
    >>>
    >>> print(options.duration, options.threads, options.to_dict())

    30s 4 {"duration": "30s", "threads": 4}

    Raises
    ------
    ValueError
        If a required parameter is not provided through a command-line
        argument, an environment variable or a default value.
    TypeError
        If a parameter is not a `Parameter` object.
    ValueError
        If an environment variable is not of the type of the corresponding
        parameter.
    """

    PARSED = False

    def __init__(self, *parameters: Parameter):
        """Initializes the options."""

        self.parameters = copy.deepcopy(parameters)

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the options to a dict. As a side effect, this method parses
        the options if they have not been parsed yet. See the `parse` method
        for more information.

        Returns
        -------
        dict[str, Any]
            The options as a dict.
        """

        if not self.PARSED:
            self._parse()

        class model(BaseModel):
            config: dict[str, Any]

        self_dict = copy.deepcopy(self.__dict__)

        rm_keys = ["parameters", "PARSED"]
        for key in rm_keys:
            if key in self_dict:
                self_dict.pop(key)

        m = model.from_dict(data={"config": self_dict})

        return m.to_dict()["config"]

    def parameters_dict(self) -> list[dict[str, Any]]:
        """
        Converts the options to a list of dicts. Each dict is the dict
        representation of a `Parameter`.

        Returns
        -------
        list[dict[str, Any]]
            The list of dictionaries (parameter entries).
        """

        return [param.to_dict() for param in self.parameters]

    def parse(self):
        """
        Parses the options using command-line arguments, environment variables
        and default values, in that order. Under the hood, the `argparse`
        library is used. When command-line arguments are parsed, the help menu
        is created, thus parsing Options more than once may result in
        unexpected behavior.

        This method is called automatically when an attribute is accessed. If
        you want to parse the options manually, you can call this method.

        After Options have been parsed, they cannot be merged with other
        Options. If you need to merge Options, do so before parsing them.

        Example 1
        -------
        >>> import nextmv
        >>>
        >>> options = nextmv.Options(
        ...     nextmv.Parameter("duration", str, "30s", description="solver duration", required=False),
        ...     nextmv.Parameter("threads", int, 4, description="computer threads", required=False),
        ... )
        >>> options.parse() # Does not raise an exception.

        Example 2
        -------
        >>> import nextmv
        >>>
        >>> options = nextmv.Options(
        ...     nextmv.Parameter("duration", str, "30s", description="solver duration", required=False),
        ...     nextmv.Parameter("threads", int, 4, description="computer threads", required=False),
        ... )
        >>> print(options.duration) # Parses the options.
        >>> options.parse() # Raises an exception because the options have already been parsed.

        Raises
        ------
        RuntimeError
            If the options have already been parsed.
        ValueError
            If a required parameter is not provided through a command-line
            argument, an environment variable or a default value.
        TypeError
            If a parameter is not a `Parameter` object.
        ValueError
            If an environment variable is not of the type of the corresponding
            parameter.
        """

        if self.PARSED:
            raise RuntimeError("options have already been parsed")

        self._parse()

    def merge(self, new: "Options") -> "Options":
        """
        Merges the current options with the new options. This method cannot be
        used if any of the options have been parsed. When options are parsed,
        values are read from the command-line arguments, environment variables
        and default values. Merging options after parsing would result in
        unpredictable behavior.

        Parameters
        ----------
        new : Options
            The new options to merge.

        Raises
        ------
        RuntimeError
            If the current options have already been parsed.
        RuntimeError
            If the new options have already been parsed.

        Returns
        -------
        Options
            The merged options.
        """

        if self.PARSED:
            raise RuntimeError(
                "base options have already been parsed, cannot merge. See `Options.parse()` for more information."
            )

        if new.PARSED:
            raise RuntimeError(
                "new options have already been parsed, cannot merge. See `Options.parse()` for more information."
            )

        self.parameters += new.parameters

        self._parse()

        return self

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Options":
        """
        Creates an instance of `Options` from a dictionary. The dictionary
        should have the following structure:

        {
            "duration": "30",
            "threads": 4,
        }

        Parameters
        ----------
        data : dict[str, Any]
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
    def from_parameters_dict(cls, parameters_dict: list[dict[str, Any]]) -> "Options":
        """
        Creates an instance of `Options` from parameters in dict form. Each
        entry is the dict representation of a `Parameter`.

        Parameters
        ----------
        data : list[dict[str, Any]]
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

    def __getattr__(self, name: str) -> Any:
        """
        Gets an attribute of the options. This is called when an attribute
        is accessed. It parses the options if they have not been parsed yet.
        """

        if not self.PARSED:
            self._parse()

        return super().__getattribute__(name)

    def _parse(self):  # noqa: C901
        """
        Parses the options using command-line arguments, environment variables
        and default values.

        Raises
        ------
        ValueError
            If a required parameter is not provided through a command-line
            argument, an environment variable or a default value.
        TypeError
            If a parameter is not a `Parameter` object.
        ValueError
            If an environment variable is not of the type of the corresponding
            parameter.
        """

        self.PARSED = True

        if not self.parameters:
            return

        parser = argparse.ArgumentParser(
            add_help=True,
            usage="%(prog)s [options]",
            description="Options for %(prog)s. Use command-line arguments (highest precedence) "
            + "or environment variables.",
            allow_abbrev=False,
        )
        params_by_field_name: dict[str, Parameter] = {}

        for p, param in enumerate(self.parameters):
            if not isinstance(param, Parameter):
                raise TypeError(f"expected a <Parameter> object, but got {type(param)} in index {p}")

            # See comment below about ipykernel adding a `-f` argument. We
            # restrict parameters from having the name 'f' or 'fff' for that
            # reason.
            if param.name == "f" or param.name == "fff":
                raise ValueError("parameter names 'f', 'fff' are reserved for internal use")

            if param.name == "PARSED":
                raise ValueError("parameter name 'PARSED' is reserved for internal use")

            # Remove any leading '-'. This is in line with argparse's behavior.
            param.name = param.name.lstrip("-")

            kwargs = {
                "type": param.param_type if param.param_type is not bool else str,
                "help": self._description(param),
            }

            if param.choices is not None:
                kwargs["choices"] = param.choices

            parser.add_argument(
                f"-{param.name}",
                f"--{param.name}",
                **kwargs,
            )

            # Store the parameter by its field name for easy access later. argparse
            # replaces '-' with '_', so we do the same here.
            params_by_field_name[param.name.replace("-", "_")] = param

        # The ipkyernel uses a `-f` argument by default that it passes to the
        # execution. We don’t want to ignore this argument because we get an
        # error. Fix source: https://stackoverflow.com/a/56349168
        parser.add_argument(
            "-f",
            "--f",
            "--fff",
            help=argparse.SUPPRESS,
            default="1",
        )
        args = parser.parse_args()

        for arg in vars(args):
            if arg == "fff" or arg == "f":
                continue

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

        if value in ("true", "1", "t", "y", "yes"):
            return True

        return False
