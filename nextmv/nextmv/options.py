"""Configuration for a run."""

import argparse
import builtins
import copy
import json
import os
from dataclasses import dataclass
from typing import Any, Optional, Union

from nextmv.base_model import BaseModel
from nextmv.deprecated import deprecated


@dataclass
class Parameter:
    """
    DEPRECATION WARNING
    ----------
    `Parameter` is deprecated, use `Option` instead.

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

    def __post_init__(self):
        deprecated(
            name="Parameter",
            reason="`Parameter` is deprecated, use `Option` instead.",
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Parameter":
        """
        DEPRECATION WARNING
        ----------
        `Parameter` is deprecated, use `Option` instead. Parameter.from_dict ->
        Option.from_dict

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

        deprecated(
            name="Parameter.from_dict",
            reason="`Parameter` is deprecated, use `Option` instead. Parameter.from_dict -> Option.from_dict",
        )

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
        DEPRECATION WARNING
        ----------
        `Parameter` is deprecated, use `Option` instead. Parameter.to_dict ->
        Option.to_dict

        Converts the parameter to a dict.

        Returns
        -------
        dict[str, Any]
            The parameter as a dict.
        """

        deprecated(
            name="Parameter.to_dict",
            reason="`Parameter` is deprecated, use `Option` instead. Parameter.to_dict -> Option.to_dict",
        )

        return {
            "name": self.name,
            "param_type": str(self.param_type),
            "default": self.default,
            "description": self.description,
            "required": self.required,
            "choices": self.choices,
        }


@dataclass
class Option:
    """
    `Option` that is used in `Options`. When an `Option` is required,
    it is a good practice to provide a default value for it. This is because
    the `Options` will raise an error if a required `Option` is not
    provided through a command-line argument, an environment variable or a
    default value.

    Attributes
    ----------
    name : str
        The name of the option.
    option_type : type
        The type of the option.
    default : Any, optional
        The default value of the option. Even though this is optional, it is
        recommended to provide a default value for all options.
    description : str, optional
        An optional description of the option. This is useful for generating
        help messages for the `Options`.
    required : bool, optional
        Whether the option is required. If an option is required, it will
        be an error to not provide a value for it, either trough a command-line
        argument, an environment variable or a default value.
    choices : list[Optional[Any]], optional
        Limits values to a specific set of choices.
    """

    name: str
    """The name of the option."""
    option_type: type
    """The type of the option."""

    default: Optional[Any] = None
    """
    The default value of the option. Even though this is optional, it is
    recommended to provide a default value for all options.
    """
    description: Optional[str] = None
    """
    An optional description of the option. This is useful for generating help
    messages for the `Options`.
    """
    required: bool = False
    """
    Whether the option is required. If a option is required, it will be an
    error to not provide a value for it, either trough a command-line argument,
    an environment variable or a default value.
    """
    choices: Optional[list[Any]] = None
    """Limits values to a specific set of choices."""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Option":
        """
        Creates an instance of `Option` from a dictionary.

        Parameters
        ----------
        data : dict[str, Any]
            The dictionary representation of an option.

        Returns
        -------
        Option
            An instance of `Option`.
        """

        option_type_string = data["option_type"]
        option_type = getattr(builtins, option_type_string.split("'")[1])

        return Option(
            name=data["name"],
            option_type=option_type,
            default=data.get("default"),
            description=data.get("description"),
            required=data.get("required", False),
            choices=data.get("choices"),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the option to a dict.

        Returns
        -------
        dict[str, Any]
            The option as a dict.
        """

        return {
            "name": self.name,
            "option_type": str(self.option_type),
            "default": self.default,
            "description": self.description,
            "required": self.required,
            "choices": self.choices,
        }


class Options:
    """
    Options for a run. To initialize options, pass in one or more `Option`
    objects. The options will look for the values of the given parameters in
    the following order: command-line arguments, environment variables, default
    values.

    Once the `Options` are initialized, you can access the underlying options as
    attributes of the `Options` object. For example, if you have an
    `Option` object with the name "duration", you can access it as
    `options.duration`.

    If an option is required and not provided through a command-line
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

    Attributes
    ----------
    *options : Option
        The list of `Option` objects that are used in the options. At least one
        option is required.

    Examples
    --------
    >>> import nextmv
    >>>
    >>> options = nextmv.Options(
    ...     nextmv.Option("duration", str, "30s", description="solver duration", required=False),
    ...     nextmv.Option("threads", int, 4, description="computer threads", required=False),
    ... )
    >>>
    >>> print(options.duration, options.threads, options.to_dict())

    30s 4 {"duration": "30s", "threads": 4}

    Raises
    ------
    ValueError
        If a required option is not provided through a command-line
        argument, an environment variable or a default value.
    TypeError
        If an option is not either an `Option` or `Parameter` (deprecated)
        object.
    ValueError
        If an environment variable is not of the type of the corresponding
        parameter.
    """

    PARSED = False

    def __init__(self, *options: Option):
        """Initializes the options."""

        self.options = copy.deepcopy(options)

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

        rm_keys = ["PARSED", "options"]
        for key in rm_keys:
            if key in self_dict:
                self_dict.pop(key)

        m = model.from_dict(data={"config": self_dict})

        return m.to_dict()["config"]

    def to_dict_cloud(self) -> dict[str, str]:
        """
        Converts the options to a dict that can be used in the Nextmv Cloud.
        Cloud has a hard requirement that options are passed as strings. This
        method converts the options to a dict with string values. This is
        useful for passing options to the Nextmv Cloud.
        As a side effect, this method parses the options if they have not been
        parsed yet. See the `parse` method for more information.

        Returns
        -------
        dict[str, str]
            The options as a dict with string values.
        """

        options_dict = self.to_dict()

        cloud_dict = {}
        for k, v in options_dict.items():
            if isinstance(v, str):
                cloud_dict[k] = v
            else:
                cloud_dict[k] = json.dumps(v)

        return cloud_dict

    def parameters_dict(self) -> list[dict[str, Any]]:
        """
        DEPRECATION WARNING
        ----------
        `Parameter` is deprecated, use `Option` instead. Options.parameters_dict
        -> Options.options_dict

        Converts the options to a list of dicts. Each dict is the dict
        representation of a `Parameter`.

        Returns
        -------
        list[dict[str, Any]]
            The list of dictionaries (parameter entries).
        """

        deprecated(
            name="Options.parameters_dict",
            reason="`Parameter` is deprecated, use `Option` instead. Options.parameters_dict -> Options.options_dict",
        )

        return [param.to_dict() for param in self.options]

    def options_dict(self) -> list[dict[str, Any]]:
        """
        Converts the `Options` to a list of dicts. Each dict is the dict
        representation of an `Option`.

        Returns
        -------
        list[dict[str, Any]]
            The list of dictionaries (`Option` entries).
        """

        return [opt.to_dict() for opt in self.options]

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
        ...     nextmv.Option("duration", str, "30s", description="solver duration", required=False),
        ...     nextmv.Option("threads", int, 4, description="computer threads", required=False),
        ... )
        >>> options.parse() # Does not raise an exception.

        Example 2
        -------
        >>> import nextmv
        >>>
        >>> options = nextmv.Options(
        ...     nextmv.Option("duration", str, "30s", description="solver duration", required=False),
        ...     nextmv.Option("threads", int, 4, description="computer threads", required=False),
        ... )
        >>> print(options.duration) # Parses the options.
        >>> options.parse() # Raises an exception because the options have already been parsed.

        Raises
        ------
        RuntimeError
            If the options have already been parsed.
        ValueError
            If a required option is not provided through a command-line
            argument, an environment variable or a default value.
        TypeError
            If an option is not an `Option` or `Parameter` (deprecated) object.
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

        self.options += new.options

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

        options = []
        for key, value in data.items():
            opt = Option(name=key, option_type=type(value), default=value)
            options.append(opt)

        return cls(*options)

    @classmethod
    def from_parameters_dict(cls, parameters_dict: list[dict[str, Any]]) -> "Options":
        """
        DEPRECATION WARNING
        ----------
        `Parameter` is deprecated, use `Option` instead. Options.from_parameters_dict
        -> Options.from_options_dict

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

        deprecated(
            name="Options.from_parameters_dict",
            reason="`Parameter` is deprecated, use `Option` instead. "
            "Options.from_parameters_dict -> Options.from_options_dict",
        )

        parameters = []
        for parameter_dict in parameters_dict:
            parameter = Parameter.from_dict(parameter_dict)
            parameters.append(parameter)

        return cls(*parameters)

    @classmethod
    def from_options_dict(cls, options_dict: list[dict[str, Any]]) -> "Options":
        """
        Creates an instance of `Options` from a list of `Option` objects in
        dict form. Each entry is the dict representation of an `Option`.

        Parameters
        ----------
        data : list[dict[str, Any]]
            The list of dictionaries (`Option` entries).

        Returns
        -------
        Options
            An instance of `Options`.
        """

        options = []
        for opt_dict in options_dict:
            opt = Option.from_dict(opt_dict)
            options.append(opt)

        return cls(*options)

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
            If a required option is not provided through a command-line
            argument, an environment variable or a default value.
        TypeError
            If an option is not an `Option` or `Parameter` (deprecated) object.
        ValueError
            If an environment variable is not of the type of the corresponding
            parameter.
        """

        self.PARSED = True

        if not self.options:
            return

        parser = argparse.ArgumentParser(
            add_help=True,
            usage="%(prog)s [options]",
            description="Options for %(prog)s. Use command-line arguments (highest precedence) "
            + "or environment variables.",
            allow_abbrev=False,
        )
        options_by_field_name: dict[str, Option] = {}

        for ix, option in enumerate(self.options):
            if not isinstance(option, Option) and not isinstance(option, Parameter):
                raise TypeError(
                    f"expected an <Option> (or deprecated <Parameter>) object, but got {type(option)} in index {ix}"
                )

            # See comment below about ipykernel adding a `-f` argument. We
            # restrict options from having the name 'f' or 'fff' for that
            # reason.
            if option.name == "f" or option.name == "fff":
                raise ValueError("option names 'f', 'fff' are reserved for internal use")

            if option.name == "PARSED":
                raise ValueError("option name 'PARSED' is reserved for internal use")

            # Remove any leading '-'. This is in line with argparse's behavior.
            option.name = option.name.lstrip("-")

            kwargs = {
                "type": self._option_type(option) if self._option_type(option) is not bool else str,
                "help": self._description(option),
            }

            if option.choices is not None:
                kwargs["choices"] = option.choices

            parser.add_argument(
                f"-{option.name}",
                f"--{option.name}",
                **kwargs,
            )

            # Store the option by its field name for easy access later. argparse
            # replaces '-' with '_', so we do the same here.
            options_by_field_name[option.name.replace("-", "_")] = option

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

            option = options_by_field_name[arg]

            # First, attempt to set the value of an option from the
            # command-line args.
            arg_value = getattr(args, arg)
            if arg_value is not None:
                value = self._option_value(option, arg_value)
                setattr(self, arg, value)
                continue

            # Second, attempt to set the value of am option from the
            # environment variables.
            upper_name = arg.upper()
            env_value = os.getenv(upper_name)
            if env_value is not None:
                try:
                    typed_env_value = (
                        self._option_type(option)(env_value) if self._option_type(option) is not bool else env_value
                    )
                except ValueError:
                    raise ValueError(
                        f'environment variable "{upper_name}" is not of type {self._option_type(option)}'
                    ) from None

                value = self._option_value(option, typed_env_value)
                setattr(self, arg, value)
                continue

            # Finally, attempt to set a default value. This is only allowed
            # for non-required options.
            if not option.required:
                setattr(self, arg, option.default)
                continue

            # At this point, the option is required and no value was
            # provided
            raise ValueError(
                f'option "{arg}" is required but not provided through: command-line args, env vars, or default value'
            )

    def _description(self, option: Option) -> str:
        """Returns a description for an option."""

        description = ""
        if isinstance(option, Parameter):
            description = "DEPRECATED (initialized with <Parameter>, use <Option> instead) "

        description += f"[env var: {option.name.upper()}]"

        if option.required:
            description += " (required)"

        if option.default is not None:
            description += f" (default: {option.default})"

        description += f" (type: {self._option_type(option).__name__})"

        if option.description is not None and option.description != "":
            description += f": {option.description}"

        return description

    def _option_value(self, option: Option, value: Any) -> Any:
        """Handles how the value of an option is extracted."""

        opt_type = self._option_type(option)
        if opt_type is not bool:
            return value

        value = str(value).lower()

        if value in ("true", "1", "t", "y", "yes"):
            return True

        return False

    @staticmethod
    def _option_type(option: Union[Option, Parameter]) -> type:
        """Auxiliary function for handling the type of an option. This function
        was introduced for backwards compatibility with the deprecated
        `Parameter` class. Once `Parameter` is removed, this function can be removed
        as well. When the function is removed, use the `option.option_type`
        attribute directly, instead of calling this function.
        """

        if isinstance(option, Option):
            return option.option_type
        elif isinstance(option, Parameter):
            return option.param_type
        else:
            raise TypeError(f"expected an <Option> (or deprecated <Parameter>) object, but got {type(option)}")
