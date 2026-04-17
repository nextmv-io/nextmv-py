"""
Module with the logic for handling an app manifest.

This module provides classes and functions for managing Nextmv app manifests.
Manifest files (app.yaml) define how an application is built, run, and deployed
on the Nextmv platform.

Classes
-------
ManifestType
    Enum for application types based on programming language.
ManifestRuntime
    Enum for runtime environments where apps run on Nextmv.
ManifestPythonArch
    Enum for target architecture for bundling Python apps.
ManifestBuild
    Class for build-specific attributes in the manifest.
ManifestPythonModel
    Class for model-specific instructions for Python apps.
ManifestPython
    Class for Python-specific instructions in the manifest.
ManifestOptionUI
    Class for UI attributes of options in the manifest.
ManifestOption
    Class representing an option for the decision model in the manifest.
ManifestOptions
    Class containing a list of options for the decision model.
ManifestValidation
    Class for validation rules for options in the manifest.
ManifestContentMultiFileInput
    Class for multi-file content format input configuration.
ManifestContentMultiFileOutput
    Class for multi-file content format output configuration.
ManifestContentMultiFile
    Class for multi-file content format configuration.
ManifestContent
    Class for content configuration specifying how app input/output is handled.
ManifestConfiguration
    Class for configuration settings for the decision model.
Manifest
    Main class representing an app manifest for Nextmv.

Functions
---------
default_python_manifest
    Creates a default Python manifest as a starting point for applications.
find_files
    Find all files matching the given filters in the given directory.
initialize_manifest
    Initialize a manifest file of a given type in a specified directory.
resolve_manifest
    Resolve a manifest file from a specified path, returning a `Manifest` object.

Constants
--------
MANIFEST_FILE_NAME
    Name of the app manifest file.
"""

import glob
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from typing import Any

import yaml
from pydantic import AliasChoices, Field, field_validator

from nextmv.account import AccountMemberRole
from nextmv.base_model import BaseModel
from nextmv.content_format import ContentFormat, InputFormat
from nextmv.options import Option, Options, OptionsEnforcement

MANIFEST_FILE_NAME = "app.yaml"
"""Name of the app manifest file.

This constant defines the standard filename for Nextmv app manifest files.

You can import the `MANIFEST_FILE_NAME` constant directly from `nextmv`:

```python
from nextmv import MANIFEST_FILE_NAME
```

Notes
-----
All Nextmv applications must include an app.yaml file for proper deployment.
"""

# When working with the `Model`, we expect to be working in a notebook
# environment, and not interact with the local filesystem a lot. We use the
# `ModelConfiguration` to specify the dependencies that the `Model` requires.
# To work with the "push" logic of uploading an app to Nextmv Cloud, we need a
# requirement file that we use to gather dependencies, install them, and bundle
# them in the app. This file is used as a placeholder for the dependencies that
# the model requires and that we install and bundle with the app.
_REQUIREMENTS_FILE = "model_requirements.txt"


class ManifestType(str, Enum):
    """
    Type of application in the manifest, based on the programming language.

    You can import the `ManifestType` class directly from `nextmv`:

    ```python
    from nextmv import ManifestType
    ```

    This enum defines the supported programming languages for applications
    that can be deployed on Nextmv Cloud.

    Attributes
    ----------
    PYTHON : str
        Python format, used for Python applications.
    GO : str
        Go format, used for Go applications.
    JAVA : str
        Java format, used for Java applications.

    Examples
    --------
    >>> from nextmv import ManifestType
    >>> manifest_type = ManifestType.PYTHON
    >>> manifest_type
    <ManifestType.PYTHON: 'python'>
    >>> str(manifest_type)
    'python'
    """

    PYTHON = "python"
    """Python format"""
    GO = "go"
    """Go format"""
    JAVA = "java"
    """Java format"""
    BINARY = "binary"
    """Binary format"""


_MANDATORY_FILES_PER_TYPE = {
    ManifestType.PYTHON: ["main.py"],
    ManifestType.GO: ["main"],
    ManifestType.BINARY: ["main"],
    ManifestType.JAVA: ["main.jar"],
}
"""
Mapping of mandatory files required for each manifest type.
"""


class ManifestRuntime(str, Enum):
    """
    Runtime (environment) where the app will be run on Nextmv Cloud.

    You can import the `ManifestRuntime` class directly from `nextmv`:

    ```python
    from nextmv import ManifestRuntime
    ```

    This enum defines the supported runtime environments for applications
    that can be deployed on Nextmv Cloud.

    Attributes
    ----------
    DEFAULT : str
        This runtime is used to run compiled applications such as Go binaries.
    PYTHON : str
        This runtime is used as the basis for all other Python runtimes and
        Python applications.
    JAVA : str
        This runtime is used to run Java applications.
    PYOMO : str
        This runtime provisions Python packages to run Pyomo applications.
    HEXALY : str
        This runtime provisions Python packages to run Hexaly applications.

    Examples
    --------
    >>> from nextmv import ManifestRuntime
    >>> runtime = ManifestRuntime.PYTHON
    >>> runtime
    <ManifestRuntime.PYTHON: 'ghcr.io/nextmv-io/runtime/python:3.11'>
    >>> str(runtime)
    'ghcr.io/nextmv-io/runtime/python:3.11'
    """

    DEFAULT = "ghcr.io/nextmv-io/runtime/default:latest"
    """A runtime used to run compiled applications such as Go binaries."""
    PYTHON = "ghcr.io/nextmv-io/runtime/python:3.11"
    """A runtime used to run standard Python applications."""
    JAVA = "ghcr.io/nextmv-io/runtime/java:latest"
    """A runtime used to run Java applications."""
    PYOMO = "ghcr.io/nextmv-io/runtime/pyomo:latest"
    """A runtime provisioning Python packages to run Pyomo applications."""
    CUOPT = "ghcr.io/nextmv-io/runtime/cuopt:latest"
    """A runtime providing the NVIDIA cuOpt solver."""
    GAMSPY = "ghcr.io/nextmv-io/runtime/gamspy:latest"
    """A runtime provisioning the GAMS Python API and supported solvers."""


class ManifestPythonArch(str, Enum):
    """
    Target architecture for bundling Python apps.

    You can import the `ManifestPythonArch` class directly from `nextmv`:

    ```python
    from nextmv import ManifestPythonArch
    ```

    Attributes
    ----------
    ARM64 : str
        ARM 64-bit architecture.
    AMD64 : str
        AMD 64-bit architecture.

    Examples
    --------
    >>> from nextmv import ManifestPythonArch
    >>> arch = ManifestPythonArch.ARM64
    >>> arch
    <ManifestPythonArch.ARM64: 'arm64'>
    >>> str(arch)
    'arm64'
    """

    ARM64 = "arm64"
    """ARM 64-bit architecture."""
    AMD64 = "amd64"
    """AMD 64-bit architecture."""


class ManifestBuild(BaseModel):
    """
    Build-specific attributes.

    You can import the `ManifestBuild` class directly from `nextmv`:

    ```python
    from nextmv import ManifestBuild
    ```

    Parameters
    ----------
    command : Optional[str], default=None
        The command to run to build the app. This command will be executed
        without a shell, i.e., directly. The command must exit with a status of
        0 to continue the push process of the app to Nextmv Cloud. This command
        is executed prior to the pre-push command.
    environment : Optional[dict[str, Any]], default=None
        Environment variables to set when running the build command given as
        key-value pairs.

    Examples
    --------
    >>> from nextmv import ManifestBuild
    >>> build_config = ManifestBuild(
    ...     command="make build",
    ...     environment={"DEBUG": "true"}
    ... )
    >>> build_config.command
    'make build'
    """

    command: str | None = None
    """The command to run to build the app.

    This command will be executed without a shell, i.e., directly. The command
    must exit with a status of 0 to continue the push process of the app to
    Nextmv Cloud. This command is executed prior to the pre-push command.
    """
    environment: dict[str, Any] | None = None
    """Environment variables to set when running the build command.

    Given as key-value pairs.
    """

    def environment_to_dict(self) -> dict[str, str]:
        """
        Convert the environment variables to a dictionary.

        Returns
        -------
        dict[str, str]
            The environment variables as a dictionary of string key-value pairs.
            Returns an empty dictionary if no environment variables are set.

        Examples
        --------
        >>> from nextmv import ManifestBuild
        >>> build_config = ManifestBuild(environment={"COUNT": 1, "NAME": "test"})
        >>> build_config.environment_to_dict()
        {'COUNT': '1', 'NAME': 'test'}
        >>> build_config_empty = ManifestBuild()
        >>> build_config_empty.environment_to_dict()
        {}
        """

        if self.environment is None:
            return {}

        return {key: str(value) for key, value in self.environment.items()}


class ManifestPythonModel(BaseModel):
    """
    Model-specific instructions for a Python app.

    You can import the `ManifestPythonModel` class directly from `nextmv`:

    ```python
    from nextmv import ManifestPythonModel
    ```

    Parameters
    ----------
    name : str
        The name of the decision model.
    options : Optional[list[dict[str, Any]]], default=None
        Options for the decision model. This is a data representation of the
        `nextmv.Options` class. It consists of a list of dicts. Each dict
        represents the `nextmv.Option` class. It is used to be able to
        reconstruct an Options object from data when loading a decision model.

    Examples
    --------
    >>> from nextmv import ManifestPythonModel
    >>> python_model_config = ManifestPythonModel(
    ...     name="routing_model",
    ...     options=[{"name": "max_vehicles", "type": "int", "default": 10}]
    ... )
    >>> python_model_config.name
    'routing_model'
    """

    name: str
    """The name of the decision model."""
    options: list[dict[str, Any]] | None = None
    """
    Options for the decision model. This is a data representation of the
    `nextmv.Options` class. It consists of a list of dicts. Each dict
    represents the `nextmv.Option` class. It is used to be able to
    reconstruct an Options object from data when loading a decision model.
    """


class ManifestPython(BaseModel):
    """
    Python-specific instructions.

    You can import the `ManifestPython` class directly from `nextmv`:

    ```python
    from nextmv import ManifestPython
    ```

    Parameters
    ----------
    pip_requirements : Optional[Union[str, list[str]]], default=None
        Path to a requirements.txt file containing (additional) Python
        dependencies that will be bundled with the app. Alternatively, you can provide a
        list of strings, each representing a package to install, e.g.,
        `["nextmv==0.28.2", "ortools==9.12.4544"]`.
        Aliases: `pip-requirements`.
    model : Optional[ManifestPythonModel], default=None
        Information about an encoded decision model as handled via mlflow. This
        information is used to load the decision model from the app bundle.

    Examples
    --------
    >>> from nextmv import ManifestPython, ManifestPythonModel
    >>> python_config = ManifestPython(
    ...     pip_requirements="requirements.txt",
    ...     model=ManifestPythonModel(name="my_model")
    ... )
    >>> python_config.pip_requirements
    'requirements.txt'
    """

    pip_requirements: str | list[str] | None = Field(
        serialization_alias="pip-requirements",
        validation_alias=AliasChoices("pip-requirements", "pip_requirements"),
        default=None,
    )
    """
    Path to a requirements.txt file or list of packages.

    Contains (additional) Python dependencies that will be bundled with the
    app. Can be either a string path to a requirements.txt file or a list
    of package specifications.
    """
    arch: ManifestPythonArch | None = None
    """
    The architecture this model is meant to run on. One of "arm64" or "amd64". Uses
    "arm64" if not specified.
    """
    version: str | float | None = None
    """
    The Python version this model is meant to run with. Uses "3.11" if not specified.
    """
    model: ManifestPythonModel | None = None
    """
    Information about an encoded decision model.

    As handled via mlflow. This information is used to load the decision model
    from the app bundle.
    """

    @field_validator("version", mode="before")
    @classmethod
    def validate_version(cls, v: str | float | None) -> str | None:
        """
        Validate and convert the Python version field to a string.

        This validator allows the version to be specified as either a float or string
        in the manifest for convenience, but ensures it's stored internally as a string.

        Parameters
        ----------
        v : Optional[Union[str, float]]
            The version value to validate. Can be None, a string, or a float.

        Returns
        -------
        Optional[str]
            The version as a string, or None if the input was None.

        Examples
        --------
        >>> ManifestPython.validate_version(3.11)
        '3.11'
        >>> ManifestPython.validate_version("3.11")
        '3.11'
        >>> ManifestPython.validate_version(None) is None
        True
        """
        # We allow the version to be a float in the manifest for convenience, but we want
        # to store it as a string internally.
        if v is None:
            return None
        if isinstance(v, float):
            return str(v)
        return v


class ManifestOptionUI(BaseModel):
    """
    UI attributes for an option in the manifest.

    You can import the `ManifestOptionUI` class directly from `nextmv`:

    ```python
    from nextmv import ManifestOptionUI
    ```

    Parameters
    ----------
    control_type : str, optional
        The type of control to use for the option in the Nextmv Cloud UI. This is
        useful for defining how the option should be presented in the Nextmv
        Cloud UI. Current control types include "input", "select", "slider", and
        "toggle". This attribute is not used in the local `Options` class, but
        it is used in the Nextmv Cloud UI to define the type of control to use for
        the option. This will be validated by the Nextmv Cloud, and availability
        is based on option_type.
    hidden_from : list[AccountMemberRole], optional
        A list of team roles to which this option will be hidden in the UI. For
        example, if you want to hide an option from the "operator" role, you can
        pass `hidden_from=["operator"]`.

        Each roles is validated during API handling to ensure they are one of:
        `"root"`, `"admin"`, `"developer"`, `"operator"`, or `"viewer"`
    display_name : str, optional
        An optional display name for the option. This is useful for making
        the option more user-friendly in the UI.

    Examples
    --------
    >>> from nextmv import ManifestOptionUI
    >>> ui_config = ManifestOptionUI(control_type="input")
    >>> ui_config.control_type
    'input'
    """

    control_type: str | None = None
    """The type of control to use for the option in the Nextmv Cloud UI."""
    hidden_from: list[AccountMemberRole] | None = None
    """A list of team roles for which this option will be hidden in the UI."""
    display_name: str | None = None
    """An optional display name for the option. This is useful for making
    the option more user-friendly in the UI.
    """


class ManifestOption(BaseModel):
    """
    An option for the decision model that is recorded in the manifest.

    You can import the `ManifestOption` class directly from `nextmv`:

    ```python
    from nextmv import ManifestOption
    ```

    Parameters
    ----------
    name : str
        The name of the option.
    option_type : str
        The type of the option. This is a string representation of the
        `nextmv.Option` class (e.g., "string", "int", "bool", "float").
        Aliases: `type`.
    default : Optional[Any], default=None
        The default value of the option.
    description : Optional[str], default=""
        The description of the option.
    required : bool, default=False
        Whether the option is required or not.
    local_only : bool, default=False
        Whether the option is only used locally and should not be sent to Nextmv Cloud.
    additional_attributes : Optional[dict[str, Any]], default=None
        Optional additional attributes for the option. The Nextmv Cloud may
        perform validation on these attributes. For example, the maximum
        length of a string or the maximum value of an integer. These
        additional attributes will be shown in the help message of the
        `Options`.
    ui : Optional[ManifestOptionUI], default=None
        Optional UI attributes for the option. This is a dictionary that can
        contain additional information about how the option should be displayed
        in the Nextmv Cloud UI. This is not used in the local `Options` class,
        but it is used in the Nextmv Cloud UI to define how the option should be
        presented.

    Examples
    --------
    >>> from nextmv import ManifestOption
    >>> option = ManifestOption(
    ...     name="solve.duration",
    ...     option_type="string",
    ...     default="30s",
    ...     description="Maximum duration for the solver."
    ... )
    >>> option.name
    'solve.duration'
    """

    name: str
    """The name of the option"""
    option_type: str = Field(
        serialization_alias="option_type",
        validation_alias=AliasChoices("type", "option_type"),
    )
    """The type of the option (e.g., "string", "int", "bool", "float)."""

    default: Any | None = None
    """The default value of the option"""
    description: str | None = ""
    """The description of the option"""
    required: bool = False
    """Whether the option is required or not"""
    local_only: bool = False
    """Whether the option is only used locally and should not be sent to Nextmv Cloud."""
    additional_attributes: dict[str, Any] | None = None
    """Optional additional attributes for the option."""
    ui: ManifestOptionUI | None = None
    """Optional UI attributes for the option."""

    def model_post_init(self, __context) -> None:
        """
        Validations done after parsing the model.

        Raises
        ------
        ValueError
            If validation fails. A descriptive error message is provided in this case.
        """

        # It does not make sense to define options as required AND them being local only,
        # since this would make Platform runs via UI cumbersome to impossible.
        if self.required and self.local_only:
            raise ValueError(f"Option '{self.name}' cannot be both required and local only.")

    @classmethod
    def from_option(cls, option: Option) -> "ManifestOption":
        """
        Create a `ManifestOption` from an `Option`.

        Parameters
        ----------
        option : nextmv.options.Option
            The option to convert.

        Returns
        -------
        ManifestOption
            The converted option.

        Raises
        ------
        ValueError
            If the `option.option_type` is unknown.

        Examples
        --------
        >>> from nextmv.options import Option
        >>> from nextmv import ManifestOption
        >>> sdk_option = Option(name="max_stops", option_type=int, default=100)
        >>> manifest_opt = ManifestOption.from_option(sdk_option)
        >>> manifest_opt.name
        'max_stops'
        >>> manifest_opt.option_type
        'int'
        """
        option_type = option.option_type
        if option_type is str:
            option_type = "string"
        elif option_type is bool:
            option_type = "bool"
        elif option_type is int:
            option_type = "int"
        elif option_type is float:
            option_type = "float"
        else:
            raise ValueError(f"unknown option type: {option_type}")

        return cls(
            name=option.name,
            option_type=option_type,
            default=option.default,
            description=option.description,
            required=option.required,
            additional_attributes=option.additional_attributes,
            ui=ManifestOptionUI(
                control_type=option.control_type,
                hidden_from=option.hidden_from,
                display_name=option.display_name,
            )
            if option.control_type or option.hidden_from or option.display_name
            else None,
        )

    def to_option(self) -> Option:
        """
        Convert the `ManifestOption` to an `Option`.

        Returns
        -------
        nextmv.options.Option
            The converted option.

        Raises
        ------
        ValueError
            If the `self.option_type` is unknown.

        Examples
        --------
        >>> from nextmv import ManifestOption
        >>> manifest_opt = ManifestOption(name="max_stops", option_type="int", default=100)
        >>> sdk_option = manifest_opt.to_option()
        >>> sdk_option.name
        'max_stops'
        >>> sdk_option.option_type
        <class 'int'>
        """

        option_type_string = self.option_type
        if option_type_string == "string":
            option_type = str
        elif option_type_string == "bool":
            option_type = bool
        elif option_type_string == "int":
            option_type = int
        elif option_type_string == "float":
            option_type = float
        else:
            raise ValueError(f"unknown option type: {option_type_string}")

        return Option(
            name=self.name,
            option_type=option_type,
            default=self.default,
            description=self.description,
            required=self.required,
            additional_attributes=self.additional_attributes,
            control_type=self.ui.control_type if self.ui else None,
            hidden_from=self.ui.hidden_from if self.ui else None,
            display_name=self.ui.display_name if self.ui else None,
        )


class ManifestValidation(BaseModel):
    """
    Validation rules for options in the manifest.

    You can import the `ManifestValidation` class directly from `nextmv`:

    ```python
    from nextmv import ManifestValidation
    ```

    Parameters
    ----------
    enforce : str, default="none"
        The enforcement level for the validation rules. This can be set to
        "none" or "all". If set to "none", no validation will be performed
        on the options prior to creating a run. If set to "all", all validation
        rules will be enforced on the options, and runs will not be created
        if any of the rules of the options are violated.

    Examples
    --------
    >>> from nextmv import ManifestValidation
    >>> validation = ManifestValidation(enforce="all")
    >>> validation.enforce
    'all'
    """

    enforce: str = "none"
    """The enforcement level for the validation rules.
    This can be set to "none" or "all". If set to "none", no validation will
    be performed on the options prior to creating a run. If set to "all", all
    validation rules will be enforced on the options, and runs will not be
    created if any of the rules of the options are violated.
    """


class ManifestOptions(BaseModel):
    """
    Options for the decision model.

    You can import the `ManifestOptions` class directly from `nextmv`:

    ```python
    from nextmv import ManifestOptions
    ```

    Parameters
    ----------
    strict : Optional[bool], default=False
        If strict is set to `True`, only the listed options will be allowed.
    items : Optional[list[ManifestOption]], default=None
        The actual list of options for the decision model. An option
        is a parameter that configures the decision model.
    validation: Optional[ManifestValidation], default=None
        Optional validation rules for all options.
    format : Optional[list[str]], default=None
        A list of strings that define how options are transformed into command
        line arguments. Use `{{name}}` to refer to the option name and
        `{{value}}` to refer to the option value.


    Examples
    --------
    >>> from nextmv import ManifestOptions, ManifestOption
    >>> options_config = ManifestOptions(
    ...     strict=True,
    ...     validation=ManifestValidation(enforce="all"),
    ...     items=[
    ...         ManifestOption(name="timeout", option_type="int", default=60),
    ...         ManifestOption(name="vehicle_capacity", option_type="float", default=100.0)
    ...     ]
    ... )
    >>> options_config.strict
    True
    >>> len(options_config.items)
    2
    """

    strict: bool | None = False
    """If strict is set to `True`, only the listed options will be allowed."""
    validation: ManifestValidation | None = None
    """Optional validation rules for all options."""
    items: list[ManifestOption] | None = None
    """The actual list of options for the decision model.

    An option is a parameter that configures the decision model.
    """
    format: list[str] | None = None
    """A list of strings that define how options are transformed into command line arguments.

    Use `{{name}}` to refer to the option name and `{{value}}` to refer to the option value.
    For example, `["-{{name}}", "{{value}}"]` will transform an option named `max_vehicles`
    with a value of `10` into the command line argument `-max_vehicles 10`.
    """

    @classmethod
    def from_options(
        cls,
        options: Options,
        validation: OptionsEnforcement = None,
        format: list[str] | None = None,
    ) -> "ManifestOptions":
        """
        Create a `ManifestOptions` from a `nextmv.Options`.

        Parameters
        ----------
        options : nextmv.options.Options
            The options to convert.
        validation : Optional[OptionsEnforcement], default=None
            Optional validation rules for the options. If provided, it will be
            used to set the `validation` attribute of the `ManifestOptions`.
        format : Optional[list[str]], default=None
            A list of strings that define how options are transformed into
            command line arguments. Use `{{name}}` to refer to the option name
            and `{{value}}` to refer to the option value.

            For example, `["-{{name}}", "{{value}}"]` will transform an option
            named `max_vehicles` with a value of `10` into the command line
            argument `-max_vehicles 10`.

        Returns
        -------
        ManifestOptions
            The converted options.

        Examples
        --------
        >>> from nextmv.options import Options, Option
        >>> from nextmv import ManifestOptions
        >>> sdk_options = Options(Option("max_vehicles", int, 5))
        >>> manifest_options = ManifestOptions.from_options(sdk_options)
        >>> manifest_options.items[0].name
        'max_vehicles'
        """

        items = [ManifestOption.from_option(option) for option in options.options]
        return cls(
            strict=validation.strict if validation else False,
            validation=ManifestValidation(enforce="all" if validation and validation.validation_enforce else "none"),
            items=items,
            format=format,
        )


class ManifestContentMultiFileInput(BaseModel):
    """
    Configuration for multi-file content format input.

    You can import the `ManifestContentMultiFileInput` class directly from `nextmv`:

    ```python
    from nextmv import ManifestContentMultiFileInput
    ```

    Parameters
    ----------
    path : str
        The path to the input file or directory.


    Examples
    --------
    >>> from nextmv import ManifestContentMultiFileInput
    >>> input_config = ManifestContentMultiFileInput(path="data/input/")
    >>> input_config.path
    'data/input/'
    """

    path: str | None = "inputs/"
    """
    The path to the input file or directory. The default value is a directory
    named `inputs/`.
    """


class ManifestContentMultiFileOutput(BaseModel):
    """
    Configuration for multi-file content format output.

    You can import the `ManifestContentMultiFileOutput` class directly from `nextmv`:

    ```python
    from nextmv import ManifestContentMultiFileOutput
    ```

    Parameters
    ----------
    statistics : Optional[str], default=""
        Deprecated: Use `metrics` instead. The path to the statistics file.
    metrics : Optional[str], default=""
        The path to the metrics file.
    assets : Optional[str], default=""
        The path to the assets file.
    solutions : Optional[str], default=""
        The path to the solutions directory.

    Examples
    --------
    >>> from nextmv import ManifestContentMultiFileOutput
    >>> output_config = ManifestContentMultiFileOutput(
    ...     metrics="my-outputs/metrics.json",
    ...     assets="my-outputs/assets.json",
    ...     solutions="my-outputs/solutions/"
    ... )
    >>> output_config.metrics
    'my-outputs/metrics.json'
    """

    statistics: str | None = "outputs/statistics/statistics.json"
    """Deprecated: Use `metrics` instead. The path to the statistics file."""
    metrics: str | None = "outputs/metrics/metrics.json"
    """The path to the metrics file."""
    assets: str | None = "outputs/assets/assets.json"
    """The path to the assets file."""
    solutions: str | None = "outputs/solutions/"
    """The path to the solutions directory."""


class ManifestContentMultiFile(BaseModel):
    """
    Configuration for multi-file content format.

    You can import the `ManifestContentMultiFile` class directly from `nextmv`:

    ```python
    from nextmv import ManifestContentMultiFile
    ```

    Parameters
    ----------
    input : ManifestContentMultiFileInput
        Configuration for multi-file content format input.
    output : ManifestContentMultiFileOutput
        Configuration for multi-file content format output.

    Examples
    --------
    >>> from nextmv import ManifestContentMultiFile, ManifestContentMultiFileInput, ManifestContentMultiFileOutput
    >>> multi_file_config = ManifestContentMultiFile(
    ...     input=ManifestContentMultiFileInput(path="data/input/"),
    ...     output=ManifestContentMultiFileOutput(
    ...         metrics="my-outputs/metrics.json",
    ...         assets="my-outputs/assets.json",
    ...         solutions="my-outputs/solutions/"
    ...     )
    ... )
    >>> multi_file_config.input.path
    'data/input/'

    """

    input: ManifestContentMultiFileInput | None = None
    """Configuration for multi-file content format input."""
    output: ManifestContentMultiFileOutput | None = None
    """Configuration for multi-file content format output."""

    def model_post_init(self, __context) -> None:
        if self.input is None:
            self.input = ManifestContentMultiFileInput(
                path="inputs/",
            )

        if self.output is None:
            self.output = ManifestContentMultiFileOutput(
                solutions="outputs/solutions/",
                metrics="outputs/metrics/metrics.json",
                assets="outputs/assets/assets.json",
            )


class ManifestContent(BaseModel):
    """
    Content configuration for specifying how the app input/output is handled.

    You can import the `ManifestContent` class directly from `nextmv`:

    ```python
    from nextmv import ManifestContent
    ```

    Parameters
    ----------
    format : str
        The format of the content. Must be one of "json", "multi-file", or "csv-archive".
    multi_file : Optional[ManifestContentMultiFile], default=None
        Configuration for multi-file content format.

    Examples
    --------
    >>> from nextmv import ManifestContent
    >>> content_config = ManifestContent(
    ...     format="multi-file",
    ...     multi_file=ManifestContentMultiFile(
    ...         input=ManifestContentMultiFileInput(path="data/input/"),
    ...         output=ManifestContentMultiFileOutput(
    ...             metrics="my-outputs/metrics.json",
    ...             assets="my-outputs/assets.json",
    ...             solutions="my-outputs/solutions/"
    ...         )
    ...     )
    ... )
    >>> content_config.format
    'multi-file'
    >>> content_config.multi_file.input.path
    'data/input/'
    """

    format: ContentFormat | InputFormat | None = ContentFormat.JSON
    """
    !!! warning
        `InputFormat` is deprecated, but kept for backward compatibility. Use `ContentFormat` instead.

    The format of the content. Can only be `ContentFormat.JSON` or
    `ContentFormat.MULTI_FILE`.
    """
    multi_file: ManifestContentMultiFile | None = Field(
        serialization_alias="multi-file",
        validation_alias=AliasChoices("multi-file", "multi_file"),
        default=None,
    )
    """Configuration for multi-file content format."""

    def model_post_init(self, __context) -> None:
        """
        Post-initialization validation to ensure format field contains valid values.

        This method is automatically called by Pydantic after the model is initialized
        to validate that the format field contains one of the acceptable values.

        Parameters
        ----------
        __context : Any
            Pydantic context (unused in this implementation).

        Raises
        ------
        ValueError
            If the format field contains an invalid value that is not one of the
            acceptable formats.
        """

        # Translate deprecated InputFormat values to ContentFormat for backward
        # compatibility.
        if type(self.format) is InputFormat:
            if self.format == InputFormat.JSON:
                self.format = ContentFormat.JSON
            elif self.format == InputFormat.MULTI_FILE:
                self.format = ContentFormat.MULTI_FILE

        acceptable_formats = [ContentFormat.JSON, ContentFormat.MULTI_FILE, InputFormat.TEXT, InputFormat.CSV_ARCHIVE]
        if self.format not in acceptable_formats:
            raise ValueError(f"Invalid format: {self.format}. Must be one of {acceptable_formats}.")

        if self.format == ContentFormat.MULTI_FILE and self.multi_file is None:
            self.multi_file = ManifestContentMultiFile(
                input=ManifestContentMultiFileInput(
                    path="inputs/",
                ),
                output=ManifestContentMultiFileOutput(
                    solutions="outputs/solutions/",
                    metrics="outputs/metrics/metrics.json",
                    assets="outputs/assets/assets.json",
                ),
            )


class ManifestConfiguration(BaseModel):
    """
    Configuration for the decision model.

    You can import the `ManifestConfiguration` class directly from `nextmv`:

    ```python
    from nextmv import ManifestConfiguration
    ```

    Parameters
    ----------
    options : Optional[ManifestOptions], default=None
        Options for the decision model.
    content : Optional[ManifestContent], default=None
        Content configuration for specifying how the app input/output is handled.

    Examples
    --------
    >>> from nextmv import ManifestConfiguration, ManifestOptions, ManifestOption
    >>> model_config = ManifestConfiguration(
    ...     options=ManifestOptions(
    ...         items=[ManifestOption(name="debug_mode", option_type="bool", default=False)]
    ...     )
    ... )
    >>> model_config.options.items[0].name
    'debug_mode'
    """

    options: ManifestOptions | None = None
    """Options for the decision model."""
    content: ManifestContent | None = None
    """Content configuration for specifying how the app input/output is
    handled."""

    def model_post_init(self, __context) -> None:
        """
        Post-initialization validation to ensure content field is properly
        initialized.
        """
        if self.content is None:
            self.content = ManifestContent(format=ContentFormat.JSON)


class ManifestExecution(BaseModel):
    """
    Execution configuration for the decision model.

    You can import the `ManifestExecution` class directly from `nextmv`:

    ```python
    from nextmv import ManifestExecution
    ```

    Parameters
    ----------
    entrypoint : Optional[str], default=None
        The entrypoint for the decision model, e.g.: `./app.py`.
    cwd : Optional[str], default=None
        The working directory to set when running the app, e.g.: `./src/`.

    Examples
    --------
    >>> from nextmv import ManifestExecution
    >>> exec_config = ManifestExecution(
    ...     entrypoint="./app.py",
    ...     cwd="./src/"
    ... )
    >>> exec_config.entrypoint
    './app.py'
    """

    entrypoint: str | None = None
    """The entrypoint for the decision model, e.g.: `./app.py`."""
    cwd: str | None = None
    """The working directory to set when running the app, e.g.: `./src/`."""


@dataclass
class ModelConfiguration:
    """
    Configuration class for Nextmv models.

    You can import the `ModelConfiguration` class directly from `nextmv`:

    ```python
    from nextmv import ModelConfiguration
    ```

    This class holds the configuration for a model, defining how a Python model
    is encoded and loaded for use in Nextmv Cloud.

    Parameters
    ----------
    name : str
        A personalized name for the model. This is required.
    requirements : list[str], optional
        A list of Python dependencies that the decision model requires,
        formatted as they would appear in a requirements.txt file.
    options : Options, optional
        Options that the decision model requires.
    options_enforcement:
        Enforcement of options for the model. This controls how options
        are handled when the model is run.

    Examples
    --------
    >>> from nextmv import ModelConfiguration, Options
    >>> config = ModelConfiguration(
    ...     name="my_routing_model",
    ...     requirements=["nextroute>=1.0.0"],
    ...     options=Options({"max_time": 60}),
    ...     options_enforcement=OptionsEnforcement(
                strict=True,
                validation_enforce=True
            )
    ... )
    """

    name: str
    """The name of the decision model."""
    requirements: list[str] | None = None
    """A list of Python dependencies that the decision model requires."""
    options: Options | None = None
    """Options that the decision model requires."""
    options_enforcement: OptionsEnforcement | None = None
    """Enforcement of options for the model."""


class Manifest(BaseModel):
    """
    Represents an app manifest (`app.yaml`) for Nextmv Cloud.

    You can import the `Manifest` class directly from `nextmv`:

    ```python
    from nextmv import Manifest
    ```

    An application that runs on the Nextmv Platform must contain a file named
    `app.yaml` which is known as the app manifest. This file is used to specify
    the execution environment for the app.

    This class represents the app manifest and allows you to load it from a
    file or create it programmatically.

    Parameters
    ----------
    files : list[str]
        The files to include (or exclude) in the app. This is mandatory.
    runtime : ManifestRuntime, default=ManifestRuntime.PYTHON
        The runtime to use for the app, it provides the environment
        in which the app runs. This is mandatory.
    type : ManifestType, default=ManifestType.PYTHON
        Type of application, based on the programming language. This is
        mandatory.
    build : Optional[ManifestBuild], default=None
        Build-specific attributes. The `build.command` to run to build
        the app. This command will be executed without a shell, i.e., directly.
        The command must exit with a status of 0 to continue the push process of
        the app to Nextmv Cloud. This command is executed prior to the pre-push
        command. The `build.environment` is used to set environment variables when
        running the build command given as key-value pairs.
    pre_push : Optional[str], default=None
        A command to run before the app is pushed to the Nextmv Cloud.
        This command can be used to compile a binary, run tests or similar tasks.
        One difference with what is specified under build, is that the command
        will be executed via the shell (i.e., `bash -c` on Linux & macOS or
        `cmd /c` on Windows). The command must exit with a status of 0 to
        continue the push process. This command is executed just before the app
        gets bundled and pushed (after the build command).
        Aliases: `pre-push`.
    python : Optional[ManifestPython], default=None
        Only for Python apps. Contains further Python-specific
        attributes.
    configuration : Optional[ManifestConfiguration], default=None
        A list of options for the decision model. An option is a
        parameter that configures the decision model.
    entrypoint : Optional[str], default=None
        Optional entrypoint for the decision model. When not specified, the
        following default entrypoints are used, according to the `.runtime`:
        - `ManifestRuntime.PYTHON`, `ManifestRuntime.HEXALY`, `ManifestRuntime.PYOMO`: `./main.py`
        - `ManifestRuntime.DEFAULT`: `./main`
        - Java: `./main.jar`

    Examples
    --------
    >>> from nextmv import Manifest, ManifestRuntime, ManifestType
    >>> manifest = Manifest(
    ...     files=["main.py", "model_logic/"],
    ...     runtime=ManifestRuntime.PYTHON,
    ...     type=ManifestType.PYTHON,
    ... )
    >>> manifest.files
    ['main.py', 'model_logic/']
    """

    type: ManifestType = ManifestType.PYTHON
    """
    Type of application, based on the programming language. This is mandatory.
    """
    runtime: ManifestRuntime = ManifestRuntime.PYTHON
    """
    The runtime to use for the app. It provides the environment in which the
    app runs. This is mandatory.
    """
    python: ManifestPython | None = None
    """
    Python-specific attributes. Only for Python apps. Contains further
    Python-specific attributes.
    """
    files: list[str] = Field(
        min_length=1,
    )
    """The files to include (or exclude) in the app. This is mandatory."""
    configuration: ManifestConfiguration | None = None
    """
    Configuration for the decision model. A list of options for the decision
    model. An option is a parameter that configures the decision model.
    """
    build: ManifestBuild | None = None
    """
    Build-specific attributes.

    The `build.command` to run to build the app. This command will be executed
    without a shell, i.e., directly. The command must exit with a status of 0
    to continue the push process of the app to Nextmv Cloud. This command is
    executed prior to the pre-push command. The `build.environment` is used to
    set environment variables when running the build command given as key-value
    pairs.
    """
    pre_push: str | None = Field(
        serialization_alias="pre-push",
        validation_alias=AliasChoices("pre-push", "pre_push"),
        default=None,
    )
    """
    A command to run before the app is pushed to the Nextmv Cloud.

    This command can be used to compile a binary, run tests or similar tasks.
    One difference with what is specified under build, is that the command will
    be executed via the shell (i.e., `bash -c` on Linux & macOS or `cmd /c` on
    Windows). The command must exit with a status of 0 to continue the push
    process. This command is executed just before the app gets bundled and
    pushed (after the build command).
    """
    execution: ManifestExecution | None = None
    """
    Optional execution configuration for the decision model. Allows configuration of
    entrypoint and more.
    """

    def model_post_init(self, __context) -> None:
        """
        Post-initialization validation to ensure required fields are properly
        initialized and to set default values for optional fields.
        """
        if self.configuration is None:
            self.configuration = ManifestConfiguration(
                content=ManifestContent(
                    format=ContentFormat.JSON,
                ),
            )

    @classmethod
    def from_yaml(cls, dirpath: str = ".") -> "Manifest":
        """
        Load a manifest from a YAML file.

        The YAML file is expected to be named `app.yaml` and located in the
        specified directory.

        Parameters
        ----------
        dirpath : str, optional
            Path to the directory containing the `app.yaml` file. Defaults to
            the current directory `.`.

        Returns
        -------
        Manifest
            The loaded manifest.

        Raises
        ------
        FileNotFoundError
            If the `app.yaml` file is not found in `dirpath`.
        yaml.YAMLError
            If there is an error parsing the YAML file.

        Examples
        --------
        Assuming an `app.yaml` file exists in `./my_app_dir`:

        ```yaml
        # ./my_app_dir/app.yaml
        files:
          - main.py
        runtime: ghcr.io/nextmv-io/runtime/python:3.11
        type: python
        ```

        >>> from nextmv import Manifest
        >>> # manifest = Manifest.from_yaml("./my_app_dir") # This would be run
        >>> # assert manifest.type == "python"
        >>> # If the `app.yaml` file is in the current directory:
        >>> # manifest = Manifest.from_yaml() # This is equivalent to Manifest.from_yaml(".")
        """

        dirpath = os.path.normpath(os.path.expanduser(dirpath))

        with open(os.path.join(dirpath, MANIFEST_FILE_NAME)) as file:
            raw_manifest = yaml.safe_load(file)

        return cls.from_dict(raw_manifest)

    def to_yaml(self, dirpath: str = ".") -> None:
        """
        Write the manifest to a YAML file.

        The manifest will be written to a file named `app.yaml` in the
        specified directory.

        Parameters
        ----------
        dirpath : str, optional
            Path to the directory where the `app.yaml` file will be written. Defaults to
            the current directory `.`.

        Raises
        ------
        IOError
            If there is an error writing the file.
        yaml.YAMLError
            If there is an error serializing the manifest to YAML.

        Examples
        --------
        >>> from nextmv import Manifest
        >>> manifest = Manifest(files=["solver.py"], type="python")
        >>> # manifest.to_yaml("./output_dir") # This would create ./output_dir/app.yaml
        >>> # manifest.to_yaml() # This would create ./app.yaml
        """

        with open(os.path.join(dirpath, MANIFEST_FILE_NAME), "w") as file:
            yaml.dump(
                self.to_dict(),
                file,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
                width=120,
            )

    def extract_options(self, should_parse: bool = True) -> Options | None:
        """
        Convert the manifest options to a `nextmv.Options` object.

        If the manifest does not have valid options defined in
        `.configuration.options.items`, this method returns `None`.

        Use the `should_parse` argument to decide if you want the options
        parsed, or not. For more information on option parsing, please read the
        docstrings on the `.parse()` method of the `nextmv.Options` object.

        Parameters
        ----------
        should_parse : bool, default=True
            Whether to parse the options, or not. By default, options are
            parsed. When command-line arguments are parsed, the help menu is
            created, thus parsing Options more than once may result in
            unexpected behavior.

        Returns
        -------
        Optional[nextmv.options.Options]
            The options extracted from the manifest. If no options are found,
            `None` is returned.

        Examples
        --------
        >>> from nextmv import Manifest, ManifestConfiguration, ManifestOptions, ManifestOption
        >>> manifest = Manifest(
        ...     files=["main.py"],
        ...     configuration=ManifestConfiguration(
        ...         options=ManifestOptions(
        ...             items=[
        ...                 ManifestOption(name="duration", option_type="string", default="10s")
        ...             ]
        ...         )
        ...     )
        ... )
        >>> sdk_options = manifest.extract_options()
        >>> sdk_options.get_option("duration").default
        '10s'
        >>> empty_manifest = Manifest(files=["main.py"])
        >>> empty_manifest.extract_options() is None
        True
        """

        if self.configuration is None or self.configuration.options is None or self.configuration.options.items is None:
            return None

        options = [option.to_option() for option in self.configuration.options.items]

        opt = Options(*options)
        if should_parse:
            opt.parse()

        return opt

    @classmethod
    def from_model_configuration(
        cls,
        model_configuration: ModelConfiguration,
    ) -> "Manifest":
        """
        Create a Python manifest from a `nextmv.model.ModelConfiguration`.

        Note that the `ModelConfiguration` is almost always used in
        conjunction with the `nextmv.Model` class. If you are not
        implementing an instance of `nextmv.Model`, consider using the
        `from_options` method instead to initialize the manifest with the
        options of the model.

        The resulting manifest will have:

        - `files` set to `["main.py", f"{model_configuration.name}/**"]`
        - `runtime` set to `ManifestRuntime.PYTHON`
        - `type` set to `ManifestType.PYTHON`
        - `python.pip_requirements` set to the default requirements file name.
        - `python.model.name` set to `model_configuration.name`.
        - `python.model.options` populated from `model_configuration.options`.
        - `configuration.options` populated from `model_configuration.options`.

        Parameters
        ----------
        model_configuration : nextmv.model.ModelConfiguration
            The model configuration.

        Returns
        -------
        Manifest
            The Python manifest.

        Examples
        --------
        >>> from nextmv.model import ModelConfiguration
        >>> from nextmv.options import Options, Option
        >>> from nextmv import Manifest
        >>> opts = Options(Option(name="vehicle_count", option_type=int, default=5))
        >>> mc = ModelConfiguration(name="vehicle_router", options=opts)
        >>> manifest = Manifest.from_model_configuration(mc)
        >>> manifest.python.model.name
        'vehicle_router'
        >>> manifest.files
        ['main.py', 'vehicle_router/**']
        >>> manifest.configuration.options.items[0].name
        'vehicle_count'
        """

        manifest_python_dict = {
            "pip-requirements": _REQUIREMENTS_FILE,
            "model": {
                "name": model_configuration.name,
            },
        }

        if model_configuration.options is not None:
            manifest_python_dict["model"]["options"] = model_configuration.options.options_dict()

        manifest_python = ManifestPython.from_dict(manifest_python_dict)
        manifest = cls(
            files=["main.py", f"{model_configuration.name}/**"],
            runtime=ManifestRuntime.PYTHON,
            type=ManifestType.PYTHON,
            python=manifest_python,
        )

        if model_configuration.options is not None:
            manifest.configuration = ManifestConfiguration(
                options=ManifestOptions.from_options(
                    options=model_configuration.options,
                    validation=model_configuration.options_enforcement,
                ),
            )

        return manifest

    @classmethod
    def from_options(cls, options: Options, validation: OptionsEnforcement = None) -> "Manifest":
        """
        Create a basic Python manifest from `nextmv.options.Options`.

        If you have more files than just a `main.py`, make sure you modify
        the `.files` attribute of the resulting manifest. This method assumes
        that requirements are specified in a `requirements.txt` file. You may
        also specify a different requirements file once you instantiate the
        manifest.

        The resulting manifest will have:
        - `files` set to `["main.py"]`
        - `runtime` set to `ManifestRuntime.PYTHON`
        - `type` set to `ManifestType.PYTHON`
        - `python.pip_requirements` set to `"requirements.txt"`.
        - `configuration.options` populated from the provided `options`.

        Parameters
        ----------
        options : nextmv.options.Options
            The options to include in the manifest.
        validation : nextmv.options.OptionsEnforcement, default=None
            The validation rules for the options. This is used to set the
            `validation` attribute of the `ManifestOptions`.

        Returns
        -------
        Manifest
            The manifest with the given options.

        Examples
        --------
        >>> from nextmv.options import Options, Option
        >>> from nextmv import Manifest
        >>> opts = Options(
        ...     Option(name="max_runtime", option_type=str, default="60s"),
        ...     Option(name="use_heuristic", option_type=bool, default=True)
        ... )
        >>> manifest = Manifest.from_options(opts)
        >>> manifest.files
        ['main.py']
        >>> manifest.python.pip_requirements
        'requirements.txt'
        >>> len(manifest.configuration.options.items)
        2
        >>> manifest.configuration.options.items[0].name
        'max_runtime'
        """

        manifest = cls(
            files=["main.py"],
            runtime=ManifestRuntime.PYTHON,
            type=ManifestType.PYTHON,
            python=ManifestPython(pip_requirements="requirements.txt"),
            configuration=ManifestConfiguration(
                options=ManifestOptions.from_options(options=options, validation=validation),
            ),
        )

        return manifest

    def confirm_mandatory_files(self, present_files: list[str]) -> None:
        """
        Confirm that all mandatory files are present in the given list of
        files.

        This method checks that all mandatory files for the manifest's type are
        present in the provided list of files. If a custom execution
        configuration with an entrypoint is provided, it checks for the
        presence of the custom entrypoint instead of the default mandatory
        files.

        Parameters
        ----------
        present_files : list[str]
            The list of files to check against the mandatory files.
        """

        found_files = {os.path.normpath(file): True for file in present_files}

        # Check for mandatory files (if a custom execution config is provided we check the
        # custom entrypoint instead)
        mandatory_files = []
        if self.execution is None or self.execution.entrypoint is None:
            mandatory_files = _MANDATORY_FILES_PER_TYPE[self.type]
        else:
            mandatory_files.append(os.path.normpath(self.execution.entrypoint))
        missing_files = [file for file in mandatory_files if file not in found_files]

        if missing_files:
            raise Exception(f"missing mandatory files: {', '.join(missing_files)}")


def default_python_manifest() -> Manifest:
    """
    Creates a default Python manifest as a starting point for applications
    being executed on the Nextmv Platform.

    You can import the `default_python_manifest` function directly from `nextmv`:

    ```python
    from nextmv import default_python_manifest
    ```

    Returns
    -------
    Manifest
        A default Python manifest with common settings.
    """

    m = Manifest(
        files=["main.py"],
        runtime=ManifestRuntime.PYTHON,
        type=ManifestType.PYTHON,
        python=ManifestPython(pip_requirements="requirements.txt"),
    )

    return m


def find_files(
    app_dir: str,
    filters: list[str],
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """
    Find all files matching the given filters in the given directory.

    This function supports glob patterns with recursive matching, negation
    patterns (starting with '!'), and directory patterns (ending with '/').
    It temporarily changes to the app directory to perform globbing, then
    returns to the original directory.

    You can import the `find_files` function directly from `nextmv`:

    ```python
    from nextmv import find_files
    ```

    Parameters
    ----------
    app_dir : str
        The root directory to search for files.
    filters : list[str]
        List of glob patterns to match files. Patterns starting with '!'
        are treated as exclusions. Patterns ending with '/' are treated
        as directory wildcards (equivalent to '/*').

    Returns
    -------
    tuple[list[str], list[str], list[dict[str, str]]]
        A tuple containing three elements:
        - found: List of found file paths (relative to app_dir)
        - missing: List of patterns that didn't match any files (excluding negation patterns)
        - files: List of dicts with 'interior_path' (relative path) and 'absolute_path' keys

    Raises
    ------
    Exception
        If there is an error changing to the app directory.

    Examples
    --------
    >>> # Find Python files
    >>> found, missing, files = find_files("/path/to/app", ["*.py", "src/"])
    >>> # Exclude cache files
    >>> found, missing, files = find_files("/path/to/app", ["*.py", "!__pycache__/*"])

    Notes
    -----
    - Only files are returned; directories are automatically excluded
    - Negation patterns don't cause an error if they don't match anything
    - The function changes the current working directory temporarily during execution
    """

    found = []
    missing = []

    # Temporarily switch to the directory to make the globbing work
    cwd = os.getcwd()
    try:
        os.chdir(app_dir)
    except OSError as e:
        raise Exception(f"error changing to file root directory: {e}") from e

    try:
        filtered_files: set[str] = set()
        for filter in filters:
            # We support "some/path/" ending with a "/". We consider it equivalent
            # to "some/path/*".
            pattern = filter
            if filter.endswith("/"):
                pattern = filter + "*"
            # If the pattern starts with a '!': negate the pattern
            negated = False
            if pattern.startswith("!"):
                pattern = pattern[1:]
                negated = True
            matches = {os.path.normpath(m) for m in glob.glob(pattern, recursive=True)}
            if not matches and not negated:
                missing.append(filter)
            else:
                if negated:
                    filtered_files = {f for f in filtered_files if f not in matches}
                else:
                    filtered_files.update([f for f in matches if os.path.isfile(f)])
        found = sorted(filtered_files)
    finally:
        # Switch back to the original directory
        os.chdir(cwd)
    files = []
    for file in found:
        files.append(
            {
                "interior_path": file,
                "absolute_path": os.path.join(app_dir, file),
            }
        )

    return found, missing, files


def initialize_manifest(manifest_type: ManifestType, content_format: ContentFormat, dirpath: str | None = ".") -> str:
    """
    Writes a sample manifest file, based on the given type and content format,
    to the given directory path.

    The sample manifest files are located in the `templates` directory of the
    package. The file that corresponds to the given type and content format is
    copied to the specified directory path with the name `app.yaml`. If no
    `dirpath` is provided, the file is written to the current directory.

    You can import the `initialize_manifest` function directly from `nextmv`:

    ```python
    from nextmv import initialize_manifest
    ```

    Parameters
    ----------
    manifest_type : ManifestType
        The type of manifest to write. This determines which sample manifest
        file is copied.
    content_format : ContentFormat
        The content format to write in the manifest. This determines which
        sample manifest file is copied.
    dirpath : Optional[str], default="."
        The directory path where the sample manifest file will be written. If
        not provided, it defaults to the current directory.

    Returns
    -------
    str
        The path to the initialized manifest file.
    """

    dirpath = os.path.normpath(os.path.expanduser(dirpath))
    os.makedirs(dirpath, exist_ok=True)
    destination = os.path.join(dirpath, MANIFEST_FILE_NAME)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    template = f"{manifest_type.value}_{content_format.value}_app.yaml"
    src = os.path.join(current_dir, "templates", template)

    dst = shutil.copy(src, destination)

    return dst


def resolve_manifest(self, manifest: Manifest | None = None) -> Manifest | None:
    """
    Resolve the manifest to use for loading the input data.

    If a manifest is provided directly, it is returned as-is. Otherwise, the
    method looks for an `app.yaml` file in the current working directory and
    loads it as a manifest if it exists.

    Parameters
    ----------
    manifest : Manifest, optional
        The manifest to use. If provided, it is returned unchanged.

    Returns
    -------
    Manifest or None
        The resolved manifest, or `None` if no manifest is found.
    """

    if manifest is not None:
        return manifest

    if os.path.exists(MANIFEST_FILE_NAME):
        return Manifest.from_yaml()

    return None
