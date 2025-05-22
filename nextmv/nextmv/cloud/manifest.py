"""Module with the logic for handling an app manifest."""

import os
from enum import Enum
from typing import Any, Optional

import yaml
from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.model import _REQUIREMENTS_FILE, ModelConfiguration
from nextmv.options import Option, Options

FILE_NAME = "app.yaml"
"""Name of the app manifest file."""


class ManifestType(str, Enum):
    """
    Type of application in the manifest, based on the programming
    language.

    Attributes
    ----------
    PYTHON: str
        Python format
    GO: str
        Go format
    JAVA: str
        Java format
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

    Attributes
    ----------
    DEFAULT: str
        This runtime is used to run compiled applications such as Go binaries.
    PYTHON: str
        This runtime is used as the basis for all other Python runtimes and
        Python applications.
    JAVA: str
        This runtime is used to run Java applications.
    PYOMO: str
        This runtime provisions Python packages to run Pyomo applications.
    HEXALY: str
        This runtime provisions Python packages to run Hexaly applications.
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

    Attributes
    ----------
    command: Optional[str]
        The command to run to build the app. This command will be executed
        without a shell, i.e., directly. The command must exit with a status of
        0 to continue the push process of the app to Nextmv Cloud. This command
        is executed prior to the pre-push command.
    environment: Optional[dict[str, Any]]
        Environment variables to set when running the build command given as
        key-value pairs.
    """

    command: Optional[str] = None
    """
    The command to run to build the app. This command will be executed without
    a shell, i.e., directly. The command must exit with a status of 0 to
    continue the push process of the app to Nextmv Cloud. This command is
    executed prior to the pre-push command.
    """
    environment: Optional[dict[str, Any]] = None
    """
    Environment variables to set when running the build command given as
    key-value pairs.
    """

    def environment_to_dict(self) -> dict[str, str]:
        """
        Convert the environment variables to a dictionary.

        Returns
        -------
        dict[str, str]
            The environment variables as a dictionary.

        """

        if self.environment is None:
            return {}

        return {key: str(value) for key, value in self.environment.items()}


class ManifestPythonModel(BaseModel):
    """
    Model-specific instructions for a Python app.

    Attributes
    ----------
    name: str
        The name of the decision model.
    options: Optional[list[dict[str, Any]]]
        Options for the decision model. This is a data representation of the
        `nextmv.Options` class. It consists of a list of dicts. Each dict
        represents the `nextmv.Option` class. It is used to be able to
        reconstruct an Options object from data when loading a decision model.
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

    Attributes
    ----------
    pip_requirements: Optional[str]
        Path to a requirements.txt file containing (additional) Python
        dependencies that will be bundled with the app.
    model: Optional[ManifestPythonModel]
        Information about an encoded decision model as handlded via mlflow. This
        information is used to load the decision model from the app bundle.
    """

    pip_requirements: Optional[str] = Field(
        serialization_alias="pip-requirements",
        validation_alias=AliasChoices("pip-requirements", "pip_requirements"),
        default=None,
    )
    """
    Path to a requirements.txt file containing (additional) Python
    dependencies that will be bundled with the app.
    """
    model: Optional[ManifestPythonModel] = None
    """
    Information about an encoded decision model as handlded via mlflow. This
    information is used to load the decision model from the app bundle.
    """


class ManifestOption(BaseModel):
    """
    An option for the decision model that is recorded in the manifest.

    Attributes
    ----------
    name: str
        The name of the option.
    option_type: str
        The type of the option. This is a string representation of the
        `nextmv.Option` class.
    default: Optional[Any]
        The default value of the option.
    description: Optional[str]
        The description of the option.
    required: bool
        Whether the option is required or not.
    """

    name: str
    """The name of the option"""
    option_type: str = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "option_type"),
    )
    """The type of the option"""

    default: Optional[Any] = None
    """The default value of the option"""
    description: Optional[str] = ""
    """The description of the option"""
    required: bool = False
    """Whether the option is required or not"""
    additional_attributes: Optional[dict[str, Any]] = None
    """
    Optional additional attributes for the option. The Nextmv Cloud may
    perform validation on these attributes. For example, the maximum length of
    a string or the maximum value of an integer. These additional attributes
    will be shown in the help message of the `Options`.
    """

    @classmethod
    def from_option(cls, option: Option) -> "ManifestOption":
        """
        Create a `ManifestOption` from an `Option`.

        Parameters
        ----------
        option: Option
            The option to convert.

        Returns
        -------
        ManifestOption
            The converted option.
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
        Option
            The converted option.
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

    Attributes
    ----------
    strict: bool
        If strict is set to `True`, only the listed options will be allowed.
    items: list[ManifestOption]
        Optional. The actual list of options for the decision model. An option
        is a parameter that configures the decision model.
    """

    strict: Optional[bool] = False
    """If strict is set to `True`, only the listed options will be allowed."""
    items: Optional[list[ManifestOption]] = None
    """
    Optional. The actual list of options for the decision model. An option is a
    parameter that configures the decision model.
    """


class ManifestConfiguration(BaseModel):
    """
    Configuration for the decision model.

    Attributes
    ----------
    options: ManifestOptions
        Optional. The actual list of options for the decision model. An option
        is a parameter that configures the decision model.
    """

    options: ManifestOptions
    """Options for the decision model."""


class Manifest(BaseModel):
    """
    An application that runs on the Nextmv Platform must contain a file named
    `app.yaml` which is known as the app manifest. This file is used to specify
    the execution environment for the app.

    This class represents the app manifest and allows you to load it from a
    file or create it programmatically.

    Attributes
    ----------
    files: list[str]
        Mandatory. The files to include (or exclude) in the app.
    runtime: ManifestRuntime
        Mandatory. The runtime to use for the app, it provides the environment
        in which the app runs.
    type: ManifestType
        Mandatory. Type of application, based on the programming language.
    build: Optional[ManifestBuild]
        Optional. Build-specific attributes. The build.command to run to build
        the app. This command will be executed without a shell, i.e., directly.
        The command must exit with a status of 0 to continue the push process of
        the app to Nextmv Cloud. This command is executed prior to the pre-push
        command. The build.environment is used to set environment variables when
        running the build command given as key-value pairs.
    pre_push: Optional[str]
        Optional. A command to run before the app is pushed to the Nextmv Cloud.
        This command can be used to compile a binary, run tests or similar tasks.
        One difference with what is specified under build, is that the command
        will be executed via
    python: Optional[ManifestPython]
        Optional. Only for Python apps. Contains further Python-specific
        attributes.
    configuration: Optional[ManifestConfiguration]
        Optional. A list of options for the decision model. An option is a
        parameter that configures the decision model.
    """

    files: list[str]
    """Mandatory. The files to include (or exclude) in the app."""

    runtime: ManifestRuntime = ManifestRuntime.PYTHON
    """
    Mandatory. The runtime to use for the app, it provides the environment in
    which the app runs.
    """
    type: ManifestType = ManifestType.PYTHON
    """Mandatory. Type of application, based on the programming language."""
    build: Optional[ManifestBuild] = None
    """
    Optional. Build-specific attributes. The build.command to run to build the
    app. This command will be executed without a shell, i.e., directly. The
    command must exit with a status of 0 to continue the push process of the
    app to Nextmv Cloud. This command is executed prior to the pre-push
    command. The build.environment is used to set environment variables when
    running the build command given as key-value pairs.
    """
    pre_push: Optional[str] = Field(
        serialization_alias="pre-push",
        validation_alias=AliasChoices("pre-push", "pre_push"),
        default=None,
    )
    """
    Optional. A command to run before the app is pushed to the Nextmv Cloud.
    This command can be used to compile a binary, run tests or similar tasks.
    One difference with what is specified under build, is that the command will
    be executed via the shell (i.e., bash -c on Linux & macOS or cmd /c on
    Windows). The command must exit with a status of 0 to continue the push
    process. This command is executed just before the app gets bundled and
    pushed (after the build command).
    """
    python: Optional[ManifestPython] = None
    """
    Optional. Only for Python apps. Contains further Python-specific
    attributes.
    """
    configuration: Optional[ManifestConfiguration] = None
    """
    Optional. A list of options for the decision model. An option is a
    parameter that configures the decision model.
    """

    @classmethod
    def from_yaml(cls, dirpath: str) -> "Manifest":
        """
        Load a manifest from a YAML file.

        Parameters
        ----------
        dirpath: str
            Path to the directory containing the app.yaml file.

        Returns
        -------
        Manifest
            The loaded manifest.

        """

        with open(os.path.join(dirpath, FILE_NAME)) as file:
            raw_manifest = yaml.safe_load(file)

        return cls.from_dict(raw_manifest)

    def to_yaml(self, dirpath: str) -> None:
        """
        Write the manifest to a YAML file.

        Parameters
        ----------
        dirpath: str
            Path to the directory where the app.yaml file will be written.

        """

        with open(os.path.join(dirpath, FILE_NAME), "w") as file:
            yaml.dump(self.to_dict(), file)

    def extract_options(self) -> Optional[Options]:
        """
        Convert the manifest options to a `nextmv.Options` object. If the
        manifest does not have valid options defined in
        `.configuration.options.items`, this method simply returns a `None`.

        Returns
        -------
        Optional[Options]
            The options extracted from the manifest. If no options are found,
            `None` is returned.
        """

        if self.configuration is None or self.configuration.options is None or self.configuration.options.items is None:
            return None

        options = [option.to_option() for option in self.configuration.options.items]

        return Options(*options)

    @classmethod
    def from_model_configuration(cls, model_configuration: ModelConfiguration) -> "Manifest":
        """
        Create a Python manifest from a Python model configuration. Note that
        the `ModelConfiguration` is almost always used in conjunction with the
        `nextmv.Model` class. If you are not implementing an instance of
        `nextmv.Model`, maybe you should use the `from_options` method instead,
        to initialize the manifest with the options of the model.

        Parameters
        ----------
        model_configuration: ModelConfiguration
            The model configuration.

        Returns
        -------
        Manifest
            The Python manifest.
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
        Create a basic Python manifest from `Options`. If you have more files
        than just a `main.py`, make sure you modify the `.files` attribute of
        the resulting manifest. This method assumes that requirements are
        specified in a `requirements.txt` file. You may also specify a
        different requirements file once you instantiate the manifest.

        Parameters
        ----------
        options: Options
            The options to include in the manifest.

        Returns
        -------
        Manifest
            The manifest with the given options.
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
