"""Module with the logic for handling an app manifest."""

import os
from enum import Enum
from typing import Any, Dict, List, Optional

import yaml
from pydantic import Field

from nextmv.base_model import BaseModel

FILE_NAME = "app.yaml"
"""Name of the app manifest file."""


class ManifestType(str, Enum):
    """Type of application in the manifest, based on the programming
    language."""

    PYTHON = "python"
    """Python format"""
    GO = "go"
    """Go format"""
    JAVA = "java"
    """Java format"""


class ManifestRuntime(str, Enum):
    """Runtime (environment) where the app will be run on Nextmv Cloud."""

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
    """Build-specific attributes."""

    command: Optional[str] = None
    """
    The command to run to build the app. This command will be executed without
    a shell, i.e., directly. The command must exit with a status of 0 to
    continue the push process of the app to Nextmv Cloud. This command is
    executed prior to the pre-push command.
    """
    environment: Optional[Dict[str, Any]] = None
    """
    Environment variables to set when running the build command given as
    key-value pairs.
    """

    def environment_to_dict(self) -> Dict[str, str]:
        """
        Convert the environment variables to a dictionary.

        Returns
        -------
        Dict[str, str]
            The environment variables as a dictionary.

        """

        if self.environment is None:
            return {}

        return {key: str(value) for key, value in self.environment.items()}


class ManifestPython(BaseModel):
    """Python-specific instructions."""

    pip_requirements: Optional[str] = Field(alias="pip-requirements", default=None)
    """
    Path to a requirements.txt file containing (additional) Python
    dependencies that will be bundled with the app.
    """


class Manifest(BaseModel):
    """
    An application that runs on the Nextmv Platform must contain a file named
    `app.yaml` which is known as the app manifest. This file is used to specify
    the execution environment for the app.

    This class represents the app manifest and allows you to load it from a
    file or create it programmatically.
    """

    files: List[str]
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
    pre_push: Optional[str] = Field(alias="pre-push", default=None)
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

    @classmethod
    def from_yaml(cls, dirpath: str) -> "Manifest":
        """
        Load a manifest from a YAML file.

        Parameters
        ----------
        dirpath : str
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
        dirpath : str
            Path to the directory where the app.yaml file will be written.

        """

        with open(os.path.join(dirpath, FILE_NAME), "w") as file:
            yaml.dump(self.to_dict(), file)
