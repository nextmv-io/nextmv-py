"""
Application module for interacting with local Nextmv applications.

This module provides functionality to interact with applications in Nextmv,
including application management, running applications, and managing inputs.

Classes
-------
Application
    Class for interacting with local Nextmv applications.
"""

import json
import os
import shutil
import sys
import tempfile
import webbrowser
from datetime import datetime, timezone
from typing import Any

import rich
from pydantic import Field

from nextmv import cloud
from nextmv._serialization import deflated_serialize_json
from nextmv.base_model import BaseModel
from nextmv.content_format import ContentFormat
from nextmv.input import INPUTS_KEY, Input, InputFormat
from nextmv.local.local import (
    DEFAULT_INPUT_JSON_FILE,
    DEFAULT_INPUT_TEXT_FILE,
    DEFAULT_OUTPUT_JSON_FILE,
    LOGS_FILE,
    LOGS_KEY,
    NEXTMV_DIR,
    RUNS_KEY,
)
from nextmv.local.registry import Registry
from nextmv.local.runner import run
from nextmv.logger import log
from nextmv.manifest import Manifest, ManifestType
from nextmv.options import Options
from nextmv.output import ASSETS_KEY, METRICS_KEY, OUTPUTS_KEY, SOLUTIONS_KEY, STATISTICS_KEY, OutputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.run import (
    ErrorLog,
    Format,
    FormatInput,
    Run,
    RunConfiguration,
    RunInformation,
    RunResult,
    SyncedRun,
    TrackedRun,
    TrackedRunStatus,
)
from nextmv.safe import safe_id
from nextmv.status import StatusV2


class Application(BaseModel):
    """
    A decision model that can be executed.

    You can import the `Application` class directly from `local`:

    ```python
    from nextmv.local import Application
    ```

    This class represents an application in Nextmv, providing methods to
    interact with the application, run it with different inputs, manage
    versions, instances, experiments, and more.

    Parameters
    ----------
    src : str
        Source of the application, when initialized locally. An application's
        source typically refers to the directory containing the `app.yaml`
        manifest.
    description : Optional[str], default=None
        Description of the application.

    Examples
    --------
    >>> from nextmv.local import Application
    >>> app = Application(src="path/to/app")
    >>> # Retrieve an app's run result
    >>> result = app.run_result("run-id")
    """

    src: str
    """
    Source of the application, when initialized locally. An application's
    source typically refers to the directory containing the `app.yaml`
    manifest.
    """
    app_id: str | None = None
    """
    ID of the application. This ID is auto-generated if not provided.
    """

    description: str | None = None
    """Description of the application."""
    manifest: Manifest | None = Field(default=None, exclude=True)
    """
    Manifest of the application. A manifest is a file named `app.yaml` that
    must be present at the root of the application's `src` directory. If you
    specify this argument when creating the Application, the provided manifest
    will be written to the `src` directory, overriding any existing manifest
    file.
    """
    content_format: InputFormat | None = None
    """
    The content format of the application, which is determined by the manifest.
    """

    def model_post_init(self, __context) -> None:
        """
        Actions taken after the Application model is initialized.
        """

        # If this application is already registered, we use the information in
        # the registry to normalize some of the attributes of the class.
        reg = Registry.from_yaml()
        entry = reg.entry(app_id=self.app_id, src=self.src)
        if entry is not None:
            self.app_id = entry.app_id
            self.src = entry.src
            self.description = entry.description
            self.content_format = entry.content_format

        if self.manifest is not None:
            self.manifest.to_yaml(self.src)

        try:
            manifest = Manifest.from_yaml(self.src)
            self.manifest = manifest

        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Could not find app.yaml in `{self.src}`. Maybe specify a different `src` dir?"
            ) from e

        content_format = InputFormat.JSON
        if self.manifest.configuration is not None and self.manifest.configuration.content is not None:
            content_format = self.manifest.configuration.content.format

        self.content_format = content_format

        # Always normalize the source path to an absolute path, to avoid issues
        # with relative paths.
        self.src = os.path.abspath(self.src)

    @classmethod
    def from_registry(cls, src: str | None = None, app_id: str | None = None) -> "Application":
        """
        Load an application from the local registry.

        The local registry is a YAML file stored at `$HOME/.nextmv/registry.yaml`
        that keeps track of locally registered applications. This method looks
        for an entry in the local registry that matches the provided `src` or
        `app_id`, and loads the application from the corresponding source path.

        Specify either the `src` or the `app_id` to identify the application to
        load. If both are provided, the method will prioritize loading by
        `app_id`.

        Parameters
        ----------
        src : str | None
            Source path of the application to load. This is typically the path
            to the directory containing the application's manifest (`app.yaml`).
        app_id : str | None
            ID of the application to load. This ID is auto-generated if not
            provided during registration.

        Returns
        -------
        Application
            The loaded application instance.

        Raises
        ------
        ValueError
            If neither `src` nor `app_id` is provided, or if no matching entry is found in the registry.

        Examples
        --------
        Assuming an application is registered in the local registry with the following entry:

        ```yaml
        apps:
          - app_id: "app-123"
            src: "/path/to/app"
        ```

        >>> from nextmv.local import Application
        >>> app = Application.from_registry(app_id="app-123")
        >>> print(app.src)
        /path/to/app
        """

        if src is None and app_id is None:
            raise ValueError("Either `src` or `app_id` must be provided to load an application from the registry")

        reg = Registry.from_yaml()
        entry = reg.entry(app_id=app_id, src=src)

        if entry is None:
            raise ValueError("No matching entry found in the registry for the provided `src` or `app_id`")

        try:
            manifest = Manifest.from_yaml(entry.src)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Could not find app.yaml in `{entry.src}`. Maybe specify a different `src` dir?"
            ) from e

        if not os.path.exists(entry.src):
            raise FileNotFoundError(f"App was found in the registry but the path does not exist: {entry.src}")

        return cls(
            src=entry.src,
            app_id=entry.app_id,
            manifest=manifest,
            description=entry.description,
        )

    @classmethod
    def get_or_register(cls, app_src: str, app_id: str | None = None) -> tuple["Application", bool]:
        """
        Get a local application from the registry or register it if it does not
        exist.

        This function checks if a local application with the given source and
        ID is already registered in the local registry. If it is, it retrieves
        and returns that application. If it is not registered, it creates a new
        `Application` instance with the provided source and ID, registers it in
        the local registry, and then returns it. The boolean in the returned
        tuple indicates whether a new application was registered (True) or an
        existing one was retrieved (False).

        Parameters
        ----------
        app_src : str
            The source path of the application to get or register.
        app_id : Optional[str]
            The ID of the application to get or register. If None, the ID will be
            derived from the application source.

        Returns
        -------
        tuple[Application, bool]
            A tuple containing the local application retrieved from the registry or
            newly registered, and a boolean indicating whether the application was
            newly registered.
        """

        app = cls(src=app_src, app_id=app_id)
        if app.is_registered():
            return cls.from_registry(src=app_src, app_id=app_id), False

        app.register()

        return app, True

    @classmethod
    def initialize(
        cls,
        src: str | None = None,
        description: str | None = None,
        destination: str | None = None,
        manifest_type: ManifestType = ManifestType.PYTHON,
        content_format: ContentFormat = ContentFormat.JSON,
        should_register: bool = False,
    ) -> "Application":
        """
        Initialize a sample Nextmv application, locally.

        This method will create a new application from a template in the local
        file system. The application is a dir with the name given by `src` (it
        becomes the _source_ of the app), under the location given by
        `destination`. If the `destination` parameter is not specified, the
        current working directory is used as default. This method will scaffold
        the application with the necessary files and directories to have an
        opinionated structure for your decision model. The template used is
        determined by the combination of `manifest_type` and `content_format`.
        Once the application is initialized, you are encouraged to complete it
        with the decision model itself, so that the application can be run
        locally.

        If the `src` parameter is not provided, a random name will be generated
        for the application. If `should_register` is set to True, the
        application will also be registered in the local registry after
        initialization.

        Parameters
        ----------
        src : str, optional
            Source (ID, name) of the application. Will be generated if not
            provided.
        description : str, optional
            Description of the application.
        destination : str, optional
            Destination directory where the application will be initialized. If
            not provided, the current working directory will be used.
        manifest_type : ManifestType, default=ManifestType.PYTHON
            Type of manifest to use for the application. Determines the
            language/runtime template that will be scaffolded.
        content_format : ContentFormat, default=ContentFormat.JSON
            Content format of the application's input and output. Determines
            which template variant is used when scaffolding the application.
        should_register : bool, default=False
            Whether to register the application in the local registry after
            initialization. If True, the application will be added to
            `$HOME/.nextmv/registry.yaml`.

        Returns
        -------
        Application
            The initialized application instance.
        """

        destination_dir = os.getcwd() if not destination else destination
        app_id = src if src else safe_id("local-app")

        # Create the new directory with the given name.
        app_src = os.path.join(destination_dir, app_id)
        if os.path.exists(app_src):
            raise FileExistsError(f"destination dir for src already exists: {app_src}")

        os.makedirs(app_src, exist_ok=False)

        if manifest_type == ManifestType.BINARY:
            manifest_type = ManifestType.GO

        # Get the path to the initial app structure template.
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        template = f"{manifest_type.value}_{content_format.value}_template"
        initial_app_structure_path = os.path.join(current_file_dir, "..", "templates", template)
        initial_app_structure_path = os.path.normpath(initial_app_structure_path)

        # Copy everything from initial_app_structure to the new directory.
        if not os.path.exists(initial_app_structure_path):
            raise FileNotFoundError(f"Initial app structure template not found at: {initial_app_structure_path}")

        shutil.copytree(initial_app_structure_path, app_src, dirs_exist_ok=True)

        local_app = cls(
            src=app_src,
            description=description,
            content_format=InputFormat(content_format),
        )

        if should_register:
            local_app.register()

        return local_app

    def is_registered(self) -> bool:
        """
        Check if the local application is registered in the local registry.

        This method checks if the application has an entry in the local registry.

        Returns
        -------
        bool
            True if the application is registered, False otherwise.
        """

        reg = Registry.from_yaml()
        entry = reg.entry(app_id=self.app_id, src=self.src)

        return entry is not None

    def list_runs(self, status: StatusV2 | None = None) -> list[Run]:
        """
        List all runs for the application.

        Parameters
        ----------
        status : Optional[StatusV2]
            If specified, only runs with the given status will be returned.

        Returns
        -------
        list[Run]
            A list of all runs associated with the application.
        """

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        dirs = os.listdir(runs_dir)
        if not dirs:
            return []

        run_ids = [d for d in dirs if os.path.isdir(os.path.join(runs_dir, d))]
        if not run_ids:
            return []

        runs = []
        for run_id in run_ids:
            try:
                info = self.run_metadata(run_id=run_id)
            except (ValueError, FileNotFoundError, json.JSONDecodeError, OSError) as e:
                # Skip runs with expected errors (missing/corrupted files)
                log(f"Warning: Skipping run '{run_id}' due to error: {e}")
                continue

            run = info.to_run()
            if status is not None and run.status_v2 != status:
                continue

            runs.append(run)

        return runs

    def new_run(
        self,
        input: Input | dict[str, Any] | BaseModel | str = None,
        name: str | None = None,
        description: str | None = None,
        options: Options | dict[str, str] | None = None,
        configuration: RunConfiguration | dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
    ) -> str:
        """
        Run the application locally with the provided input.

        This method is the local equivalent to `cloud.Application.new_run`,
        which submits the input to Nextmv Cloud. This method runs the
        application locally using the `src` of the app.

        Make sure that the `src` attribute is set on the `Application` class
        before running locally, as it is required by the method.

        Parameters
        ----------
        input: Union[Input, dict[str, Any], BaseModel, str]
            Input to use for the run. This can be a `nextmv.Input` object,
            `dict`, `BaseModel` or `str`.

            If `nextmv.Input` is used, and the `input_format` is either
            `nextmv.InputFormat.JSON` or `nextmv.InputFormat.TEXT`, then the
            input data is extracted from the `.data` property.

            If you want to work with `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`, you should use the
            `input_dir_path` argument instead. This argument takes precedence
            over the `input`. If `input_dir_path` is specified, this function
            looks for files in that directory and tars them. If both the
            `input_dir_path` and `input` arguments are provided, the `input`
            is ignored.

            When `input_dir_path` is specified, the `configuration` argument
            must also be provided. More specifically, the
            `RunConfiguration.format.format_input.input_type` parameter
            dictates what kind of input is being submitted to the Nextmv Cloud.
            Make sure that this parameter is specified when working with the
            following input formats:

            - `nextmv.InputFormat.CSV_ARCHIVE`
            - `nextmv.InputFormat.MULTI_FILE`

            When working with JSON or text data, use the `input` argument
            directly.
        name: Optional[str]
            Name of the local run.
        description: Optional[str]
            Description of the local run.
        options: Optional[Union[Options, dict[str, str]]]
            Options to use for the run. This can be a `nextmv.Options` object
            or a dict. If a dict is used, the keys must be strings and the
            values must be strings as well. If a `nextmv.Options` object is
            used, the options are extracted from the `.to_cloud_dict()` method.
            Note that specifying `options` overrides the `input.options` (if
            the `input` is of type `nextmv.Input`).
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.
        json_configurations: Optional[dict[str, Any]]
            Optional configurations for JSON serialization. This is used to
            customize the serialization before data is sent.
        input_dir_path: Optional[str]
            Path to a directory containing input files. This is useful for
            input formats like `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`. If both `input` and
            `input_dir_path` are specified, the `input` is ignored, and the
            files in the directory are used instead.

        Returns
        -------
        str
            ID (`run_id`) of the local run that was executed.

        Raises
        ------
        ValueError
            If the `src` property for the `Application` is not specified.
            If neither `input` nor `input_dir_path` is specified.
            If `input_dir_path` is specified but `configuration` is not provided.
        FileNotFoundError
            If the app.yaml file cannot be found in the specified `src` directory.

        Examples
        --------
        >>> from nextmv.local import Application
        >>> app = Application(id="my-app", src="/path/to/app")
        >>> run_id = app.new_run(
        ...     input={"vehicles": [{"id": "v1"}]},
        ...     options={"duration": "10s"}
        ... )
        >>> print(f"Local run completed with ID: {run_id}")
        """

        configuration = self.__validate_input_dir_path_and_configuration(input_dir_path, configuration)

        if self.src is None:
            raise ValueError("`src` property for the `Application` must be specified to run the application locally")

        if input is None and input_dir_path is None:
            raise ValueError("Either `input` or `input_directory` must be specified")

        input_data = None if input_dir_path else self.__extract_input_data(input)
        options_dict = self.__extract_options_dict(options, json_configurations)
        run_config_dict = self.__extract_run_config(input, configuration, input_dir_path)
        run_id = run(
            app_id=self.app_id if self.app_id is not None else "",
            src=self.src,
            manifest=self.manifest,
            run_config=run_config_dict,
            name=name,
            description=description,
            input_data=input_data,
            inputs_dir_path=input_dir_path,
            options=options_dict,
        )

        return run_id

    def new_run_with_result(
        self,
        input: Input | dict[str, Any] | BaseModel | str = None,
        name: str | None = None,
        description: str | None = None,
        run_options: Options | dict[str, str] | None = None,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        configuration: RunConfiguration | dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Submit an input to start a new local run of the application and poll
        for the result. This is a convenience method that combines the
        `new_run` and `run_result_with_polling` methods, applying
        polling logic to check when the local run succeeded.

        This method is the local equivalent to
        `cloud.Application.new_run_with_result`, which submits the input to
        Nextmv Cloud. This method runs the application locally using the `src`
        of the app.

        Make sure that the `src` attribute is set on the `Application` class
        before running locally, as it is required by the method.

        Parameters
        ----------
        input: Union[Input, dict[str, Any], BaseModel, str]
            Input to use for the run. This can be a `nextmv.Input` object,
            `dict`, `BaseModel` or `str`.

            If `nextmv.Input` is used, and the `input_format` is either
            `nextmv.InputFormat.JSON` or `nextmv.InputFormat.TEXT`, then the
            input data is extracted from the `.data` property.

            If you want to work with `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`, you should use the
            `input_dir_path` argument instead. This argument takes precedence
            over the `input`. If `input_dir_path` is specified, this function
            looks for files in that directory and tars them. If both the
            `input_dir_path` and `input` arguments are provided, the `input` is
            ignored.

            When `input_dir_path` is specified, the `configuration` argument
            must also be provided. More specifically, the
            `RunConfiguration.format.format_input.input_type` parameter
            dictates what kind of input is being submitted to the Nextmv Cloud.
            Make sure that this parameter is specified when working with the
            following input formats:

            - `nextmv.InputFormat.CSV_ARCHIVE`
            - `nextmv.InputFormat.MULTI_FILE`

            When working with JSON or text data, use the `input` argument
            directly.
        name: Optional[str]
            Name of the local run.
        description: Optional[str]
            Description of the local run.
        run_options: Optional[Union[Options, dict[str, str]]]
            Options to use for the run. This can be a `nextmv.Options` object
            or a dict. If a dict is used, the keys must be strings and the
            values must be strings as well. If a `nextmv.Options` object is
            used, the options are extracted from the `.to_cloud_dict()` method.
            Note that specifying `options` overrides the `input.options` (if
            the `input` is of type `nextmv.Input`).
        polling_options: PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the run result.
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.
        json_configurations: Optional[dict[str, Any]]
            Optional configurations for JSON serialization. This is used to
            customize the serialization before data is sent.
        input_dir_path: Optional[str]
            Path to a directory containing input files. This is useful for
            input formats like `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`. If both `input` and
            `input_dir_path` are specified, the `input` is ignored, and the
            files in the directory are used instead.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This
            is required if the output is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Result of the run, including output.

        Raises
        ------
        ValueError
            If the `src` property for the `Application` is not specified. If
            neither `input` nor `inputs_dir_path` is specified. If
            `inputs_dir_path` is specified but `configuration` is not provided.
        FileNotFoundError
            If the app.yaml file cannot be found in the specified `src`
            directory.

        Examples
        --------
        >>> from nextmv.local import Application
        >>> app = Application(id="my-app", src="/path/to/app")
        >>> run_result = app.new_run_with_result(
        ...     input={"vehicles": [{"id": "v1"}]},
        ...     options={"duration": "10s"}
        ... )
        >>> print(f"Local run completed with ID: {run_result.id}")
        """

        run_id = self.new_run(
            input=input,
            name=name,
            description=description,
            options=run_options,
            configuration=configuration,
            json_configurations=json_configurations,
            input_dir_path=input_dir_path,
        )

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
            output_dir_path=output_dir_path,
        )

    def register(self) -> None:
        """
        Register the local application in the local registry.

        This method adds an entry for the application in the local registry,
        which is stored as a YAML file at `$HOME/.nextmv/registry.yaml`. The
        registry keeps track of locally registered applications, allowing you
        to manage and list them easily.

        If the application is already registered, this method does nothing.
        """

        reg = Registry.from_yaml()
        entry = reg.register(src=self.src, app_id=self.app_id, description=self.description)
        self.app_id = entry.app_id
        self.src = entry.src

    def run_input(self, run_id: str, output_dir_path: str | None = ".") -> dict[str, Any] | str | None:
        """
        Get the input of a local run.

        This method retrieves the input of a run that was executed locally
        using the `new_run` or `new_run_with_result` method. This is the local
        equivalent to `cloud.Application.run_input`, which retrieves the input
        of a remote run in Nextmv Cloud.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve input for.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON input files will be saved. This
            is required if the input is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        dict[str, Any] | str | None
            The input of the run depending on the input format. If the input
            format is JSON, a dict is returned. If the input format is text, a
            string is returned. For multi-file and csv-archive, the input files
            are saved to the given `output_dir_path`, and the method returns
            `None`.
        """

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        run_dir = os.path.join(runs_dir, run_id)
        if not os.path.exists(run_dir):
            raise ValueError(f"`{run_id}` run dir does not exist at: {runs_dir}")

        # See whether we can attach the output directly or need to save to the given
        # directory
        run_information = self.run_metadata(run_id=run_id)
        input_type = run_information.metadata.format.format_input.input_type
        if input_type != InputFormat.JSON and (not output_dir_path or output_dir_path == ""):
            raise ValueError(
                "The format of the input is not JSON: an `output_dir_path` must be provided.",
            )

        inputs_path = os.path.join(run_dir, INPUTS_KEY)
        if input_type == InputFormat.JSON:
            input_file = os.path.join(inputs_path, DEFAULT_INPUT_JSON_FILE)
            if not os.path.exists(input_file):
                return None

            with open(input_file) as f:
                input_data = json.load(f)

            return input_data

        elif input_type == InputFormat.TEXT:
            input_file = os.path.join(inputs_path, DEFAULT_INPUT_TEXT_FILE)
            if not os.path.exists(input_file):
                return None

            with open(input_file) as f:
                input_data = f.read()

            return input_data

        elif input_type in {InputFormat.CSV_ARCHIVE, InputFormat.MULTI_FILE}:
            if not os.path.exists(inputs_path):
                return None

            output_dir = os.path.join(output_dir_path)
            os.makedirs(output_dir, exist_ok=True)
            shutil.copytree(inputs_path, output_dir, dirs_exist_ok=True)

            return None

        raise ValueError(f"Unsupported input format: {input_type}")

    def run_logs(self, run_id: str) -> str:
        """
        Get the logs of a local run.

        If the run does not have any logs, or they are empty, then this method
        simply returns a blank string. This method is equivalent to fetching
        the content of the `.nextmv/runs/{run_id}/logs/logs.log` file.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve logs for.

        Returns
        -------
        str
            The contents of the logs file for the run.

        Raises
        ------
        ValueError
            If the `.nextmv/runs` directory does not exist at the application
            source, or if the specified run ID does not exist.
        """

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        run_dir = os.path.join(runs_dir, run_id)
        if not os.path.exists(run_dir):
            raise ValueError(f"`{run_id}` run dir does not exist at: {runs_dir}")

        logs_dir = os.path.join(run_dir, LOGS_KEY)
        if not os.path.exists(logs_dir):
            return ""

        logs_file = os.path.join(logs_dir, LOGS_FILE)
        if not os.path.exists(logs_file):
            return ""

        with open(logs_file) as f:
            logs = f.read()

        return logs

    def run_metadata(self, run_id: str) -> RunInformation:
        """
        Get the metadata of a local run.

        This method is the local equivalent to
        `cloud.Application.run_metadata`, which retrieves the metadata of a
        remote run in Nextmv Cloud. This method is used to get the metadata of
        a run that was executed locally using the `new_run` or
        `new_run_with_result` method.

        Retrieves information about a run without including the run output.
        This is useful when you only need the run's status and metadata.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve metadata for.

        Returns
        -------
        RunInformation
            Metadata of the run (run information without output).

        Raises
        ------
        ValueError
            If the `.nextmv/runs` directory does not exist at the application
            source, or if the specified run ID does not exist.

        Examples
        --------
        >>> metadata = app.run_metadata("run-789")
        >>> print(metadata.metadata.status_v2)
        StatusV2.succeeded
        """

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        run_dir = os.path.join(runs_dir, run_id)
        if not os.path.exists(run_dir):
            raise ValueError(f"`{run_id}` run dir does not exist at: {runs_dir}")

        info_file = os.path.join(run_dir, f"{run_id}.json")
        if not os.path.exists(info_file):
            raise ValueError(f"`{info_file}` file does not exist at: {run_dir}")

        with open(info_file) as f:
            info_dict = json.load(f)

        info = RunInformation.from_dict(info_dict)

        return info

    def run_result(self, run_id: str, output_dir_path: str | None = ".") -> RunResult:
        """
        Get the local result of a run.

        This method is the local equivalent to `cloud.Application.run_result`,
        which retrieves the result of a remote run in Nextmv Cloud. This method
        is used to get the result of a run that was executed locally using the
        `new_run` or `new_run_with_result` method.

        Retrieves the complete result of a run, including the run output.

        Parameters
        ----------
        run_id : str
            ID of the run to get results for.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This
            is required if the output is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Result of the run, including output.

        Raises
        ------
        ValueError
            If the `.nextmv/runs` directory does not exist at the application
            source, or if the specified run ID does not exist.

        Examples
        --------
        >>> result = app.run_result("run-123")
        >>> print(result.metadata.status_v2)
        'succeeded'
        """

        run_information = self.run_metadata(run_id=run_id)

        return self.__run_result(
            run_id=run_id,
            run_information=run_information,
            output_dir_path=output_dir_path,
        )

    def run_result_with_polling(
        self,
        run_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Get the result of a local run with polling.

        This method is the local equivalent to
        `cloud.Application.run_result_with_polling`, which retrieves the result
        of a remote run in Nextmv Cloud. This method is used to get the result
        of a run that was executed locally using the `new_run` or
        `new_run_with_result` method.

        Retrieves the result of a run including the run output. This method
        polls for the result until the run finishes executing or the polling
        strategy is exhausted.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the result for.
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the run result.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This
            is required if the output is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Complete result of the run including output data.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        TimeoutError
            If the run does not complete after the polling strategy is
            exhausted based on time duration.
        RuntimeError
            If the run does not complete after the polling strategy is
            exhausted based on number of tries.

        Examples
        --------
        >>> from nextmv.cloud import PollingOptions
        >>> # Create custom polling options
        >>> polling_opts = PollingOptions(max_tries=50, max_duration=600)
        >>> # Get run result with polling
        >>> result = app.run_result_with_polling("run-123", polling_opts)
        >>> print(result.output)
        {'solution': {...}}
        """

        def polling_func() -> tuple[Any, bool]:
            run_information = self.run_metadata(run_id=run_id)
            if run_information.metadata.run_is_finalized():
                return run_information, True

            return None, False

        run_information = poll(polling_options=polling_options, polling_func=polling_func)

        return self.__run_result(
            run_id=run_id,
            run_information=run_information,
            output_dir_path=output_dir_path,
        )

    def run_visuals(self, run_id: str) -> list[str]:
        """
        Open the local run visuals in a web browser.

        This method opens the visual representation of a locally executed run
        in the default web browser. It assumes that the run was executed locally
        using the `new_run` or `new_run_with_result` method and that
        the necessary visualization files are present.

        If the run was correctly configured to produce visual assets, then the
        run will contain a `visuals` directory with one or more HTML files.
        Each file is opened in a new tab in the default web browser.

        Parameters
        ----------
        run_id : str
            ID of the local run to visualize.

        Returns
        -------
        list[str]
            The local URLs of the visual files that were opened in the web browser.

        Raises
        ------
        ValueError
            If the `.nextmv/runs` directory does not exist at the application
            source, or if the specified run ID does not exist.
        """

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        run_dir = os.path.join(runs_dir, run_id)
        if not os.path.exists(run_dir):
            raise ValueError(f"`{run_id}` run dir does not exist at: {runs_dir}")

        visuals_dir = os.path.join(run_dir, "visuals")
        if not os.path.exists(visuals_dir):
            raise ValueError(f"`visuals` dir does not exist at: {run_dir}")

        urls = []
        for file in os.listdir(visuals_dir):
            if file.endswith(".html"):
                file_path = os.path.join(visuals_dir, file)
                url_path = f"file://{os.path.realpath(file_path)}"
                webbrowser.open_new_tab(url_path)
                urls.append(url_path)

        return urls

    def sync(  # noqa: C901
        self,
        target: cloud.Application,
        run_ids: list[str] | None = None,
        instance_id: str | None = None,
        verbose: bool | None = False,
        rich_print: bool | None = False,
    ) -> None:
        """
        Sync the local application to a Nextmv Cloud application target.

        The `Application` class allows you to perform and handle local
        application runs with methods such as:

        - `new_run`
        - `new_run_with_result`
        - `run_metadata`
        - `run_result`
        - `run_result_with_polling`

        The runs produced locally live under `self.src/.nextmv/runs`. This
        method syncs those runs to a Nextmv Cloud application target, making
        them available for remote execution and management.

        Parameters
        ----------
        target : cloud.Application
            Target Nextmv Cloud application where the local application runs
            will be synced to.
        run_ids : Optional[list[str]], default=None
            List of run IDs to sync. If None, all local runs found under
            `self.src/.nextmv/runs` will be synced.
        instance_id : Optional[str], default=None
            Optional instance ID if you want to associate your runs with an
            instance.
        verbose : Optional[bool], default=False
            Whether to print verbose output during the sync process. Useful for
            debugging a large number of runs being synced.
        rich_print : Optional[bool], default=False
            Whether to use rich printing for output during the sync process.

        Raises
        ------
        ValueError
            If the `src` property is not specified.
        ValueError
            If the `client` property is not specified.
        ValueError
            If the application does not exist in Nextmv Cloud.
        ValueError
            If a run does not exist locally.
        requests.HTTPError
            If the response status code is not 2xx.
        """

        if not target.exists(target.client, target.id):
            raise ValueError(
                "target Application does not exist in Nextmv Cloud, create it with `cloud.Application.new`"
            )
        if verbose:
            if rich_print:
                rich.print(
                    f":cloud_with_lightning:  Starting sync of local application [magenta]{self.src}[/magenta] to "
                    f"Nextmv Cloud application [magenta]{target.id}[/magenta].",
                    file=sys.stderr,
                )
            else:
                log(f"☁️ Starting sync of local application `{self.src}` to Nextmv Cloud application `{target.id}`.")

        # Create a temp dir to store the outputs that are written by default to
        # ".". During the sync process, we don't need to keep these outputs, so
        # we can use a temp dir that will be deleted after the sync is done.
        with tempfile.TemporaryDirectory(prefix="nextmv-sync-run-") as temp_results_dir:
            runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
            if not run_ids:
                # If runs are not specified, by default we sync all local runs that
                # can be found.
                if not os.path.exists(runs_dir):
                    raise ValueError(
                        f"`.nextmv/runs` dir does not exist at app source: {self.src}, try making a run first"
                    )

                dirs = os.listdir(runs_dir)
                run_ids = [d for d in dirs if os.path.isdir(os.path.join(runs_dir, d))]

                if verbose:
                    if rich_print:
                        rich.print(
                            f":bulb: Found [magenta]{len(run_ids)}[/magenta] local runs to "
                            f"sync from [magenta]{runs_dir}[/magenta].",
                            file=sys.stderr,
                        )
                    else:
                        log(f"ℹ️  Found {len(run_ids)} local runs to sync from {runs_dir}.")
            else:
                if verbose:
                    if rich_print:
                        rich.print(
                            f":bulb: Syncing [magenta]{len(run_ids)}[/magenta] specified local runs from "
                            f"[magenta]{runs_dir}[/magenta].",
                            file=sys.stderr,
                        )
                    else:
                        log(f"ℹ️  Syncing {len(run_ids)} specified local runs from {runs_dir}.")

            total = 0
            for run_id in run_ids:
                synced = self.__sync_run(
                    target=target,
                    run_id=run_id,
                    runs_dir=runs_dir,
                    temp_dir=temp_results_dir,
                    instance_id=instance_id,
                    verbose=verbose,
                    rich_print=rich_print,
                )
                if synced:
                    total += 1

            if not verbose:
                return

            if rich_print:
                rich.print(
                    f":rocket: Process completed, synced local application [magenta]{self.src}[/magenta] to "
                    f"Nextmv Cloud application [magenta]{target.id}[/magenta]: "
                    f"[magenta]{total}[/magenta]/[magenta]{len(run_ids)}[/magenta] runs.",
                    file=sys.stderr,
                )
                return

            log(
                f"🚀 Process completed, synced local application `{self.src}` to "
                f"Nextmv Cloud application `{target.id}`: "
                f"{total}/{len(run_ids)} runs."
            )

    def update(
        self,
        app_id: str | None = None,
        description: str | None = None,
        content_format: InputFormat | None = None,
    ) -> None:
        """
        Update the local application.

        This method allows you to update the local application's metadata, such
        as its app_id, description and content format. It does not affect
        the application's source code or runs.

        Parameters
        ----------
        app_id : Optional[str]
            New app_id for the application. If None, the app_id is not updated.
        description : Optional[str]
            New description for the application. If None, the description is not
            updated.
        content_format : Optional[InputFormat]
            New content format for the application. If None, the content format
            is not updated.
        """

        reg = Registry.from_yaml()

        # Use both app_id and src to identify the entry for maximum specificity
        updated_entry = reg.update_entry(
            src=self.src,
            app_id=self.app_id,
            new_app_id=app_id,
            description=description,
            content_format=content_format,
        )

        if updated_entry is None:
            raise ValueError(f"Application with app_id `{self.app_id}` and src `{self.src}` is not registered locally.")

        # Update the instance attributes to reflect the changes
        if app_id is not None:
            self.app_id = app_id
        if description is not None:
            self.description = description
        if content_format is not None:
            self.content_format = content_format

    def __run_result(
        self,
        run_id: str,
        run_information: RunInformation,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Get the result of a local run.

        This is a private method that retrieves the complete result of a run,
        including the output data, from a local source. This method serves as
        the base implementation for retrieving run results, regardless of
        polling strategy.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the result for.
        run_information : RunInformation
            Information about the run, including metadata such as output size.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This
            is required if the output is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Result of the run, including all metadata and output data.

        Raises
        ------
        ValueError
            If the output format is not JSON and no output_dir_path is
            provided.
            If the output format is unknown.
        """

        result = RunResult.from_dict(run_information.to_dict())
        if result.metadata.error:
            result.error_log = ErrorLog(error=result.metadata.error)

        if result.metadata.status_v2 != StatusV2.succeeded:
            return result

        # See whether we can attach the output directly or need to save to the given
        # directory
        output_type = run_information.metadata.format.format_output.output_type
        if output_type != OutputFormat.JSON and (not output_dir_path or output_dir_path == ""):
            raise ValueError(
                "The output format is not JSON: an `output_dir_path` must be provided.",
            )

        runs_dir = os.path.join(self.src, NEXTMV_DIR, RUNS_KEY)
        solutions_dir = os.path.join(runs_dir, run_id, OUTPUTS_KEY, SOLUTIONS_KEY)

        if output_type == OutputFormat.JSON:
            with open(os.path.join(solutions_dir, DEFAULT_OUTPUT_JSON_FILE)) as f:
                result.output = json.load(f)
        elif output_type in {OutputFormat.CSV_ARCHIVE, OutputFormat.MULTI_FILE}:
            shutil.copytree(solutions_dir, output_dir_path, dirs_exist_ok=True)
        else:
            raise ValueError(f"Unknown output type: {output_type}")

        return result

    def __validate_input_dir_path_and_configuration(
        self,
        input_dir_path: str | None,
        configuration: RunConfiguration | dict[str, Any] | None,
    ) -> RunConfiguration:
        """
        Auxiliary function to validate the directory path and configuration.
        """

        if configuration is None:
            if self.manifest.configuration is not None and self.manifest.configuration.content is not None:
                configuration = RunConfiguration(
                    format=Format(
                        format_input=FormatInput(
                            input_type=self.manifest.configuration.content.format,
                        ),
                    ),
                )
        elif isinstance(configuration, dict):
            # Forcefully turn the configuration into a RunConfiguration object to
            # make it easier to deal with in the other functions.
            configuration = RunConfiguration.from_dict(configuration)

        if input_dir_path is None or input_dir_path == "":
            return configuration

        if configuration is None:
            raise ValueError(
                "If `dir_path` is provided, either a `RunConfiguration` must also be provided or "
                "the application's manifest (app.yaml) must include the format under "
                "`configuration.content.format`.",
            )

        config_format = configuration.format
        if config_format is None:
            raise ValueError(
                "If `dir_path` is provided, `RunConfiguration.format` must also be provided.",
            )

        input_type = config_format.format_input
        if input_type is None:
            raise ValueError(
                "If `dir_path` is provided, `RunConfiguration.format.format_input` must also be provided.",
            )

        if input_type is None or input_type in (InputFormat.JSON, InputFormat.TEXT):
            raise ValueError(
                "If `dir_path` is provided, `RunConfiguration.format.format_input.input_type` must be set to "
                f"a valid type. Valid types are: {[InputFormat.CSV_ARCHIVE, InputFormat.MULTI_FILE]}",
            )

        return configuration

    def __extract_input_data(
        self,
        input: Input | dict[str, Any] | BaseModel | str = None,
    ) -> dict[str, Any] | str | None:
        """
        Auxiliary function to extract the input data from the input, based on
        its type.
        """

        input_data = None
        if isinstance(input, BaseModel):
            input_data = input.to_dict()
        elif isinstance(input, dict) or isinstance(input, str):
            input_data = input
        elif isinstance(input, Input):
            input_data = input.data

        return input_data

    def __extract_options_dict(
        self,
        options: Options | dict[str, str] | None = None,
        json_configurations: dict[str, Any] | None = None,
    ) -> dict[str, str]:
        """
        Auxiliary function to extract the options that will be sent to the
        application for execution.
        """

        options_dict = {}
        if options is not None:
            if isinstance(options, Options):
                options_dict = options.to_dict_cloud()
            elif isinstance(options, dict):
                for k, v in options.items():
                    if isinstance(v, str):
                        options_dict[k] = v
                    else:
                        options_dict[k] = deflated_serialize_json(v, json_configurations=json_configurations)

        return options_dict

    def __extract_run_config(
        self,
        input: Input | dict[str, Any] | BaseModel | str = None,
        configuration: RunConfiguration | dict[str, Any] | None = None,
        dir_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Auxiliary function to extract the run configuration that will be sent
        to the application for execution.
        """

        if configuration is not None:
            configuration_dict = (
                configuration.to_dict() if isinstance(configuration, RunConfiguration) else configuration
            )
            return configuration_dict

        configuration = RunConfiguration()
        configuration.resolve(input=input, dir_path=dir_path)
        configuration_dict = configuration.to_dict()

        return configuration_dict

    def __sync_run(  # noqa: C901
        self,
        target: cloud.Application,
        run_id: str,
        runs_dir: str,
        temp_dir: str,
        instance_id: str | None = None,
        verbose: bool | None = False,
        rich_print: bool | None = False,
    ) -> bool:
        """
        Syncs a local run to a Nextmv Cloud target application. Returns True if
        the run was synced, False if it was skipped (already synced).
        """

        if verbose:
            if rich_print:
                rich.print(
                    f":hourglass_flowing_sand: Syncing local run [magenta]{run_id}[/magenta]...",
                    file=sys.stderr,
                )
            else:
                log(f"🔄 Syncing local run `{run_id}`... ")

        # For files-based runs, the result files are written by default to ".".
        # Avoid this using a dedicated temp dir.
        run_result = self.run_result(run_id, output_dir_path=temp_dir)
        input_type = run_result.metadata.format.format_input.input_type

        # Skip runs that have already been synced.
        synced_run, already_synced = run_result.is_synced(app_id=target.id, instance_id=instance_id)
        if already_synced:
            if verbose:
                if rich_print:
                    rich.print(
                        f"\t:fast_forward: Skipping local run [magenta]{run_id}[/magenta], already synced with "
                        f"[magenta]{synced_run.to_dict()}[/magenta].",
                        file=sys.stderr,
                    )
                else:
                    log(f"   ⏭️  Skipping local run `{run_id}`, already synced with {synced_run.to_dict()}.")

            return False

        # Check that it is a valid run with inputs, outputs, logs, etc.
        if not self.__valid_run_result(run_result, runs_dir, run_id):
            if verbose:
                if rich_print:
                    rich.print(
                        f"\t:x: Skipping local run [magenta]{run_id}[/magenta], invalid run (missing inputs).",
                        file=sys.stderr,
                    )
                else:
                    log(f"   ❌  Skipping local run `{run_id}`, invalid run (missing inputs).")

            return False

        status = TrackedRunStatus.SUCCEEDED
        if run_result.metadata.status_v2 != StatusV2.succeeded:
            status = TrackedRunStatus.FAILED

        # Read the logs of the run and place each line as an element in a list
        run_dir = os.path.join(runs_dir, run_id)
        logs_path = os.path.join(run_dir, LOGS_KEY, LOGS_FILE)
        if os.path.exists(logs_path):
            with open(logs_path) as f:
                stderr_logs = f.read()

        # Create the tracked run object and start configuring it.
        tracked_run = TrackedRun(
            status=status,
            duration=int(run_result.metadata.duration),
            error=run_result.metadata.error,
            logs=stderr_logs,
            name=run_result.name,
            description=run_result.description,
        )

        # Resolve the input according to its type.
        inputs_path = os.path.join(run_dir, INPUTS_KEY)
        if input_type == InputFormat.JSON:
            with open(os.path.join(inputs_path, DEFAULT_INPUT_JSON_FILE)) as f:
                tracked_run.input = json.load(f)
        elif input_type == InputFormat.TEXT:
            with open(os.path.join(inputs_path, "input")) as f:
                tracked_run.input = f.read()
        else:
            tracked_run.input_dir_path = inputs_path

        # Resolve the output according to its type.
        output_type = run_result.metadata.format.format_output.output_type
        if output_type == OutputFormat.JSON:
            tracked_run.output = run_result.output
        else:
            tracked_run.output_dir_path = os.path.join(run_dir, OUTPUTS_KEY, SOLUTIONS_KEY)

        # Resolve the statistics according to their type and presence. If
        # working with JSON, the statistics should be resolved from the output.
        if output_type in {OutputFormat.CSV_ARCHIVE, OutputFormat.MULTI_FILE}:
            stats_file_path = os.path.join(run_dir, OUTPUTS_KEY, STATISTICS_KEY, f"{STATISTICS_KEY}.json")
            if os.path.exists(stats_file_path):
                with open(stats_file_path) as f:
                    tracked_run.statistics = json.load(f)

        # Resolve the metrics
        if output_type in {OutputFormat.CSV_ARCHIVE, OutputFormat.MULTI_FILE}:
            metrics_file_path = os.path.join(run_dir, OUTPUTS_KEY, METRICS_KEY, f"{METRICS_KEY}.json")
            if os.path.exists(metrics_file_path):
                with open(metrics_file_path) as f:
                    tracked_run.metrics = json.load(f)

        # Resolve the assets according to their type and presence. If working
        # with JSON, the assets should be resolved from the output.
        if output_type in {OutputFormat.CSV_ARCHIVE, OutputFormat.MULTI_FILE}:
            assets_file_path = os.path.join(run_dir, OUTPUTS_KEY, ASSETS_KEY, f"{ASSETS_KEY}.json")
            if os.path.exists(assets_file_path):
                with open(assets_file_path) as f:
                    tracked_run.assets = json.load(f)

        # Actually sync the run by tracking it remotely on Nextmv Cloud.
        configuration = RunConfiguration(
            format=Format(
                format_input=run_result.metadata.format.format_input,
                format_output=run_result.metadata.format.format_output,
            ),
        )
        tracked_id = target.track_run(
            tracked_run=tracked_run,
            instance_id=instance_id,
            configuration=configuration,
        )

        # Mark the local run as synced by updating the local run info.
        synced_run = SyncedRun(
            run_id=tracked_id,
            synced_at=datetime.now(timezone.utc),
            app_id=target.id,
            instance_id=instance_id,
        )
        run_result.add_synced_run(synced_run)
        with open(os.path.join(run_dir, f"{run_id}.json"), "w") as f:
            json.dump(run_result.to_dict(), f, indent=2)

        if verbose:
            if rich_print:
                rich.print(
                    f"\t:white_check_mark: Synced local run [magenta]{run_id}[/magenta] as remote run "
                    f"[magenta]{synced_run.to_dict()}[/magenta].",
                    file=sys.stderr,
                )
            else:
                log(f"✅ Synced local run `{run_id}` as remote run `{synced_run.to_dict()}`.")

        return True

    def __valid_run_result(self, run_result: RunResult, runs_dir: str, run_id: str) -> bool:
        """
        Validate that a run result has all required files and directories.

        This method checks that a local run has the expected directory structure
        and files, including inputs, outputs, and logs.

        Parameters
        ----------
        run_result : RunResult
            The run result to validate.
        runs_dir : str
            Path to the runs directory.
        run_id : str
            ID of the run to validate.

        Returns
        -------
        bool
            True if the run is valid, False otherwise.
        """
        run_dir = os.path.join(runs_dir, run_id)

        # Check that the run directory exists
        if not os.path.exists(run_dir):
            return False

        # Validate inputs
        if not self.__validate_inputs(run_dir, run_result.metadata.format.format_input.input_type):
            return False

        return True

    def __validate_inputs(self, run_dir: str, input_type: InputFormat) -> bool:
        """Validate that the inputs directory and files exist for the given input type."""
        inputs_path = os.path.join(run_dir, INPUTS_KEY)
        if not os.path.exists(inputs_path):
            return False

        if input_type == InputFormat.JSON:
            input_file = os.path.join(inputs_path, DEFAULT_INPUT_JSON_FILE)

            return os.path.isfile(input_file)

        if input_type == InputFormat.TEXT:
            input_file = os.path.join(inputs_path, "input")

            return os.path.isfile(input_file)

        # For CSV_ARCHIVE and MULTI_FILE, inputs_path should be a directory
        return os.path.isdir(inputs_path)
