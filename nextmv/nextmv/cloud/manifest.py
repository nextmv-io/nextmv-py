"""Module with the logic for handling an app manifest.

This module provides classes and functions for managing Nextmv app manifests.
Manifest files (app.yaml) define how an application is built, run, and deployed
on the Nextmv Cloud platform.

Classes
-------
ManifestType
    Enum for application types based on programming language.
ManifestRuntime
    Enum for runtime environments where apps run on Nextmv Cloud.
ManifestBuild
    Class for build-specific attributes in the manifest.
ManifestPythonModel
    Class for model-specific instructions for Python apps.
ManifestPython
    Class for Python-specific instructions in the manifest.
ManifestOption
    Class representing an option for the decision model in the manifest.
ManifestOptions
    Class containing a list of options for the decision model.
ManifestConfiguration
    Class for configuration settings for the decision model.
Manifest
    Main class representing an app manifest for Nextmv Cloud.

Constants
--------
FILE_NAME
    Name of the app manifest file.
"""

import os
from enum import Enum
from typing import Any, Optional

import yaml
from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.model import _REQUIREMENTS_FILE, ModelConfiguration
from nextmv.options import Option, Options

MANIFEST_FILE_NAME = "app.yaml"
"""Name of the app manifest file.

This constant defines the standard filename for Nextmv app manifest files.

You can import the `FILE_NAME` constant directly from `cloud`:

```python
from nextmv.cloud import FILE_NAME
```

Notes
-----
All Nextmv applications must include an app.yaml file for proper deployment.
"""


class ManifestType(str, Enum):
    """
    Type of application in the manifest, based on the programming language.

    You can import the `ManifestType` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestType
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
    >>> from nextmv.cloud import ManifestType
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


class ManifestRuntime(str, Enum):
    """
    Runtime (environment) where the app will be run on Nextmv Cloud.

    You can import the `ManifestRuntime` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestRuntime
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
    >>> from nextmv.cloud import ManifestRuntime
    >>> runtime = ManifestRuntime.PYTHON
    >>> runtime
    <ManifestRuntime.PYTHON: 'ghcr.io/nextmv-io/runtime/python:3.11'>
    >>> str(runtime)
    'ghcr.io/nextmv-io/runtime/python:3.11'
    """

    DEFAULT = "ghcr.io/nextmv-io/runtime/default:latest"
    """This runtime is used to run compiled applications such as Go binaries."""
    PYTHON = "ghcr.io/nextmv-io/runtime/python:3.11"
    """
    This runtime is used as the basis for all other Python runtimes and Python
    applications.
    """
    JAVA = "ghcr.io/nextmv-io/runtime/java:latest"
    """This runtime is used to run Java applications."""
    PYOMO = "ghcr.io/nextmv-io/runtime/pyomo:latest"
    """This runtime provisions Python packages to run Pyomo applications."""
    HEXALY = "ghcr.io/nextmv-io/runtime/hexaly:latest"
    """
    Based on the python runtime, it provisions (pre-installs) the Hexaly solver
    to run Python applications.
    """


class ManifestBuild(BaseModel):
    """
    Build-specific attributes.

    You can import the `ManifestBuild` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestBuild
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
    >>> from nextmv.cloud import ManifestBuild
    >>> build_config = ManifestBuild(
    ...     command="make build",
    ...     environment={"DEBUG": "true"}
    ... )
    >>> build_config.command
    'make build'
    """

    command: Optional[str] = None
    """The command to run to build the app.

    This command will be executed without a shell, i.e., directly. The command
    must exit with a status of 0 to continue the push process of the app to
    Nextmv Cloud. This command is executed prior to the pre-push command.
    """
    environment: Optional[dict[str, Any]] = None
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
        >>> from nextmv.cloud import ManifestBuild
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

    You can import the `ManifestPythonModel` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestPythonModel
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
    >>> from nextmv.cloud import ManifestPythonModel
    >>> python_model_config = ManifestPythonModel(
    ...     name="routing_model",
    ...     options=[{"name": "max_vehicles", "type": "int", "default": 10}]
    ... )
    >>> python_model_config.name
    'routing_model'
    """

    name: str
    """The name of the decision model."""
    options: Optional[list[dict[str, Any]]] = None
    """
    Options for the decision model. This is a data representation of the
    `nextmv.Options` class. It consists of a list of dicts. Each dict
    represents the `nextmv.Option` class. It is used to be able to
    reconstruct an Options object from data when loading a decision model.
    """


class ManifestPython(BaseModel):
    """
    Python-specific instructions.

    You can import the `ManifestPython` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestPython
    ```

    Parameters
    ----------
    pip_requirements : Optional[str], default=None
        Path to a requirements.txt file containing (additional) Python
        dependencies that will be bundled with the app.
        Aliases: `pip-requirements`.
    model : Optional[ManifestPythonModel], default=None
        Information about an encoded decision model as handled via mlflow. This
        information is used to load the decision model from the app bundle.

    Examples
    --------
    >>> from nextmv.cloud import ManifestPython, ManifestPythonModel
    >>> python_config = ManifestPython(
    ...     pip_requirements="requirements.txt",
    ...     model=ManifestPythonModel(name="my_model")
    ... )
    >>> python_config.pip_requirements
    'requirements.txt'
    """

    pip_requirements: Optional[str] = Field(
        serialization_alias="pip-requirements",
        validation_alias=AliasChoices("pip-requirements", "pip_requirements"),
        default=None,
    )
    """Path to a requirements.txt file.

    Contains (additional) Python dependencies that will be bundled with the
    app.
    """
    model: Optional[ManifestPythonModel] = None
    """Information about an encoded decision model.

    As handled via mlflow. This information is used to load the decision model
    from the app bundle.
    """


class ManifestOption(BaseModel):
    """
    An option for the decision model that is recorded in the manifest.

    You can import the `ManifestOption` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestOption
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
    additional_attributes : Optional[dict[str, Any]], default=None
        Optional additional attributes for the option. The Nextmv Cloud may
        perform validation on these attributes. For example, the maximum
        length of a string or the maximum value of an integer. These
        additional attributes will be shown in the help message of the
        `Options`.

    Examples
    --------
    >>> from nextmv.cloud import ManifestOption
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
        serialization_alias="type",
        validation_alias=AliasChoices("type", "option_type"),
    )
    """The type of the option (e.g., "string", "int", "bool", "float)."""

    default: Optional[Any] = None
    """The default value of the option"""
    description: Optional[str] = ""
    """The description of the option"""
    required: bool = False
    """Whether the option is required or not"""
    additional_attributes: Optional[dict[str, Any]] = None
    """Optional additional attributes for the option.

    The Nextmv Cloud may perform validation on these attributes. For example,
    the maximum length of a string or the maximum value of an integer. These
    additional attributes will be shown in the help message of the `Options`.
    """

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
        >>> from nextmv.cloud import ManifestOption
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
        >>> from nextmv.cloud import ManifestOption
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
        )


class ManifestOptions(BaseModel):
    """
    Options for the decision model.

    You can import the `ManifestOptions` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestOptions
    ```

    Parameters
    ----------
    strict : Optional[bool], default=False
        If strict is set to `True`, only the listed options will be allowed.
    items : Optional[list[ManifestOption]], default=None
        The actual list of options for the decision model. An option
        is a parameter that configures the decision model.

    Examples
    --------
    >>> from nextmv.cloud import ManifestOptions, ManifestOption
    >>> options_config = ManifestOptions(
    ...     strict=True,
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

    strict: Optional[bool] = False
    """If strict is set to `True`, only the listed options will be allowed."""
    items: Optional[list[ManifestOption]] = None
    """The actual list of options for the decision model.

    An option is a parameter that configures the decision model.
    """


class ManifestConfiguration(BaseModel):
    """
    Configuration for the decision model.

    You can import the `ManifestConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import ManifestConfiguration
    ```

    Parameters
    ----------
    options : ManifestOptions
        Options for the decision model.

    Examples
    --------
    >>> from nextmv.cloud import ManifestConfiguration, ManifestOptions, ManifestOption
    >>> model_config = ManifestConfiguration(
    ...     options=ManifestOptions(
    ...         items=[ManifestOption(name="debug_mode", option_type="bool", default=False)]
    ...     )
    ... )
    >>> model_config.options.items[0].name
    'debug_mode'
    """

    options: ManifestOptions
    """Options for the decision model."""


class Manifest(BaseModel):
    """
    Represents an app manifest (`app.yaml`) for Nextmv Cloud.

    You can import the `Manifest` class directly from `cloud`:

    ```python
    from nextmv.cloud import Manifest
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

    Examples
    --------
    >>> from nextmv.cloud import Manifest, ManifestRuntime, ManifestType
    >>> manifest = Manifest(
    ...     files=["main.py", "model_logic/"],
    ...     runtime=ManifestRuntime.PYTHON,
    ...     type=ManifestType.PYTHON,
    ... )
    >>> manifest.files
    ['main.py', 'model_logic/']
    """

    files: list[str]
    """The files to include (or exclude) in the app. This is mandatory."""

    runtime: ManifestRuntime = ManifestRuntime.PYTHON
    """The runtime to use for the app.

    It provides the environment in which the app runs. This is mandatory.
    """
    type: ManifestType = ManifestType.PYTHON
    """Type of application, based on the programming language. This is mandatory."""
    build: Optional[ManifestBuild] = None
    """Build-specific attributes.

    The `build.command` to run to build the app. This command will be executed
    without a shell, i.e., directly. The command must exit with a status of 0
    to continue the push process of the app to Nextmv Cloud. This command is
    executed prior to the pre-push command. The `build.environment` is used to
    set environment variables when running the build command given as key-value
    pairs.
    """
    pre_push: Optional[str] = Field(
        serialization_alias="pre-push",
        validation_alias=AliasChoices("pre-push", "pre_push"),
        default=None,
    )
    """A command to run before the app is pushed to the Nextmv Cloud.

    This command can be used to compile a binary, run tests or similar tasks.
    One difference with what is specified under build, is that the command will
    be executed via the shell (i.e., `bash -c` on Linux & macOS or `cmd /c` on
    Windows). The command must exit with a status of 0 to continue the push
    process. This command is executed just before the app gets bundled and
    pushed (after the build command).
    """
    python: Optional[ManifestPython] = None
    """Python-specific attributes.

    Only for Python apps. Contains further Python-specific attributes.
    """
    configuration: Optional[ManifestConfiguration] = None
    """Configuration for the decision model.

    A list of options for the decision model. An option is a parameter that
    configures the decision model.
    """

    @classmethod
    def from_yaml(cls, dirpath: str) -> "Manifest":
        """
        Load a manifest from a YAML file.

        The YAML file is expected to be named `app.yaml` and located in the
        specified directory.

        Parameters
        ----------
        dirpath : str
            Path to the directory containing the `app.yaml` file.

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

        >>> from nextmv.cloud import Manifest
        >>> # manifest = Manifest.from_yaml("./my_app_dir") # This would be run
        >>> # assert manifest.type == "python"
        """

        with open(os.path.join(dirpath, MANIFEST_FILE_NAME)) as file:
            raw_manifest = yaml.safe_load(file)

        return cls.from_dict(raw_manifest)

    def to_yaml(self, dirpath: str) -> None:
        """
        Write the manifest to a YAML file.

        The manifest will be written to a file named `app.yaml` in the
        specified directory.

        Parameters
        ----------
        dirpath : str
            Path to the directory where the `app.yaml` file will be written.

        Raises
        ------
        IOError
            If there is an error writing the file.
        yaml.YAMLError
            If there is an error serializing the manifest to YAML.

        Examples
        --------
        >>> from nextmv.cloud import Manifest
        >>> manifest = Manifest(files=["solver.py"], type="python")
        >>> # manifest.to_yaml("./output_dir") # This would create ./output_dir/app.yaml
        """

        with open(os.path.join(dirpath, MANIFEST_FILE_NAME), "w") as file:
            yaml.dump(self.to_dict(), file)

    def extract_options(self) -> Optional[Options]:
        """
        Convert the manifest options to a `nextmv.Options` object.

        If the manifest does not have valid options defined in
        `.configuration.options.items`, this method returns `None`.

        Returns
        -------
        Optional[nextmv.options.Options]
            The options extracted from the manifest. If no options are found,
            `None` is returned.

        Examples
        --------
        >>> from nextmv.cloud import Manifest, ManifestConfiguration, ManifestOptions, ManifestOption
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

        return Options(*options)

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
        >>> from nextmv.model import ModelConfiguration, Options, Option
        >>> from nextmv.cloud import Manifest
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
                options=ManifestOptions(
                    strict=False,
                    items=[ManifestOption.from_option(opt) for opt in model_configuration.options.options],
                ),
            )

        return manifest

    @classmethod
    def from_options(cls, options: Options) -> "Manifest":
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

        Returns
        -------
        Manifest
            The manifest with the given options.

        Examples
        --------
        >>> from nextmv.options import Options, Option
        >>> from nextmv.cloud import Manifest
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
                options=ManifestOptions(
                    strict=False,
                    items=[ManifestOption.from_option(opt) for opt in options.options],
                ),
            ),
        )

        return manifest
