"""
Application module for interacting with local Nextmv applications.

This module provides functionality to interact with applications in Nextmv,
including application management, running applications, and managing inputs.

Classes
-------
DownloadURL
    Result of getting a download URL.
PollingOptions
    Options for polling when waiting for run results.
UploadURL
    Result of getting an upload URL.
Application
    Class for interacting with applications in Nextmv Cloud.

Functions
---------
poll
    Function to poll for results with configurable options.
"""

import json
import os
import shutil
import tempfile
import webbrowser
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, Union

from nextmv import cloud
from nextmv._serialization import deflated_serialize_json
from nextmv.base_model import BaseModel
from nextmv.input import DEFAULT_INPUT_JSON_FILE, INPUTS_KEY, Input, InputFormat
from nextmv.local.executor import LOGS_FILE
from nextmv.local.runner import run
from nextmv.logger import log
from nextmv.manifest import Manifest
from nextmv.options import Options
from nextmv.output import DEFAULT_OUTPUT_JSON_FILE, LOGS_KEY, OUTPUTS_KEY, SOLUTIONS_KEY, OutputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.run import ErrorLog, Format, RunConfiguration, RunInformation, RunResult, TrackedRun, TrackedRunStatus
from nextmv.safe import safe_id
from nextmv.status import StatusV2


@dataclass
class Application:
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

    description: Optional[str] = None
    """Description of the application."""

    @classmethod
    def initialize(
        cls,
        src: Optional[str] = None,
        description: Optional[str] = None,
        destination: Optional[str] = None,
    ) -> "Application":
        """
        Initialize a sample Nextmv application, locally.

        This method will create a new application in the local file system. The
        application is a dir with the name given by `src` (it becomes the
        _source_ of the app), under the location given by `destination`. If the
        `destination` parameter is not specified, the current working directory
        is used as default. This method will scaffold the application with the
        necessary files and directories to have an opinionated structure for
        your decision model. Once the application is initialized, you are
        encouraged to complete it with the decision model itself, so that the
        application can be run locally.

        If the `src` parameter is not provided, a random name will be generated
        for the application.

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

        Returns
        -------
        Application
            The initialized application instance.
        """

        destination_dir = os.getcwd() if destination is None else destination
        app_id = src if src is not None else safe_id("app")

        # Create the new directory with the given name.
        app_src = os.path.join(destination_dir, app_id)
        if os.path.exists(app_src):
            raise FileExistsError(f"destination dir for src already exists: {app_src}")

        os.makedirs(app_src, exist_ok=False)

        # Get the path to the initial app structure template.
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        initial_app_structure_path = os.path.join(current_file_dir, "..", "default_app")
        initial_app_structure_path = os.path.normpath(initial_app_structure_path)

        # Copy everything from initial_app_structure to the new directory.
        if os.path.exists(initial_app_structure_path):
            shutil.copytree(initial_app_structure_path, app_src, dirs_exist_ok=True)

        return cls(
            src=app_src,
            description=description,
        )

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

        runs_dir = os.path.join(self.src, ".nextmv", "runs")
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

    def run_result(self, run_id: str, output_dir_path: Optional[str] = ".") -> RunResult:
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
        output_dir_path: Optional[str] = ".",
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
            if run_information.metadata.status_v2 in {
                StatusV2.succeeded,
                StatusV2.failed,
                StatusV2.canceled,
            }:
                return run_information, True

            return None, False

        run_information = poll(polling_options=polling_options, polling_func=polling_func)

        return self.__run_result(
            run_id=run_id,
            run_information=run_information,
            output_dir_path=output_dir_path,
        )

    def run_visuals(self, run_id: str) -> None:
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

        Raises
        ------
        ValueError
            If the `.nextmv/runs` directory does not exist at the application
            source, or if the specified run ID does not exist.
        """

        runs_dir = os.path.join(self.src, ".nextmv", "runs")
        if not os.path.exists(runs_dir):
            raise ValueError(f"`.nextmv/runs` dir does not exist at app source: {self.src}")

        run_dir = os.path.join(runs_dir, run_id)
        if not os.path.exists(run_dir):
            raise ValueError(f"`{run_id}` run dir does not exist at: {runs_dir}")

        visuals_dir = os.path.join(run_dir, "visuals")
        if not os.path.exists(visuals_dir):
            raise ValueError(f"`visuals` dir does not exist at: {run_dir}")

        for file in os.listdir(visuals_dir):
            if file.endswith(".html"):
                file_path = os.path.join(visuals_dir, file)
                webbrowser.open_new_tab(f"file://{os.path.realpath(file_path)}")

    def new_run(
        self,
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        options: Optional[Union[Options, dict[str, str]]] = None,
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
        input_dir_path: Optional[str] = None,
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
            looks for files in that directory and tars them, to later be
            uploaded using the `upload_large_input` method. If both the
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

            In general, if an input is too large, it will be uploaded with the
            `upload_large_input` method.
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
            If the manifest.yaml file cannot be found in the specified `src` directory.

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

        self.__validate_input_dir_path_and_configuration(input_dir_path, configuration)

        if self.src is None:
            raise ValueError("`src` property for the `Application` must be specified to run the application locally")

        if input is None and input_dir_path is None:
            raise ValueError("Either `input` or `input_directory` must be specified")

        try:
            manifest = Manifest.from_yaml(self.src)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Could not find manifest.yaml in {self.src}. Maybe specify a different `src` dir?"
            ) from e

        input_data = None if input_dir_path else self.__extract_input_data(input)
        options_dict = self.__extract_options_dict(options, json_configurations)
        run_config_dict = self.__extract_run_config(input, configuration, input_dir_path)
        run_id = run(
            app_id=self.src,
            src=self.src,
            manifest=manifest,
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
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        run_options: Optional[Union[Options, dict[str, str]]] = None,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
        input_dir_path: Optional[str] = None,
        output_dir_path: Optional[str] = ".",
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
            looks for files in that directory and tars them, to later be
            uploaded using the `upload_large_input` method. If both the
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

            In general, if an input is too large, it will be uploaded with the
            `upload_large_input` method.
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
            If the manifest.yaml file cannot be found in the specified `src`
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

    def sync(  # noqa: C901
        self,
        target: cloud.Application,
        run_ids: Optional[list[str]] = None,
        instance_id: Optional[str] = None,
        verbose: Optional[bool] = False,
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
        if self.src is None:
            raise ValueError(
                "`src` property for the `Application` must be specified to sync the application to Nextmv Cloud"
            )

        if target.client is None:
            raise ValueError(
                "`client` property for the target `Application` must be specified to sync the application to Cloud"
            )

        if not target.exists(target.client, target.id):
            raise ValueError(
                "target Application does not exist in Nextmv Cloud, create it with `cloud.Application.new`"
            )
        if verbose:
            log(f"☁️ Starting sync of local application `{self.src}` to Nextmv Cloud application `{target.id}`.")

        # Create a temp dir to store the outputs that are written by default to
        # ".". During the sync process, we don't need to keep these outputs, so
        # we can use a temp dir that will be deleted after the sync is done.
        with tempfile.TemporaryDirectory(prefix="nextmv-sync-run-") as temp_results_dir:
            runs_dir = os.path.join(self.src, ".nextmv", "runs")
            if run_ids is None:
                # If runs are not specified, by default we sync all local runs that
                # can be found.
                dirs = os.listdir(runs_dir)
                run_ids = [d for d in dirs if os.path.isdir(os.path.join(runs_dir, d))]

                if verbose:
                    log(f"ℹ️  Found {len(run_ids)} local runs to sync from {runs_dir}.")
            else:
                if verbose:
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
                )
                if synced:
                    total += 1

            if verbose:
                log(
                    f"🚀 Process completed, synced local application `{self.src}` to "
                    f"Nextmv Cloud application `{target.id}`: "
                    f"{total}/{len(run_ids)} runs."
                )

    def __run_result(
        self,
        run_id: str,
        run_information: RunInformation,
        output_dir_path: Optional[str] = ".",
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

        runs_dir = os.path.join(self.src, ".nextmv", "runs")
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
        input_dir_path: Optional[str],
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]],
    ) -> None:
        """
        Auxiliary function to validate the directory path and configuration.
        """

        if input_dir_path is None or input_dir_path == "":
            return

        if configuration is None:
            raise ValueError(
                "If dir_path is provided, a RunConfiguration must also be provided.",
            )

        config_format = self.__extract_config_format(configuration)

        if config_format is None:
            raise ValueError(
                "If dir_path is provided, RunConfiguration.format must also be provided.",
            )

        input_type = self.__extract_input_type(config_format)

        if input_type is None or input_type in (InputFormat.JSON, InputFormat.TEXT):
            raise ValueError(
                "If dir_path is provided, RunConfiguration.format.format_input.input_type must be set to a valid type. "
                f"Valid types are: {[InputFormat.CSV_ARCHIVE, InputFormat.MULTI_FILE]}",
            )

    def __extract_config_format(self, configuration: Union[RunConfiguration, dict[str, Any]]) -> Any:
        """Extract format from configuration, handling both RunConfiguration objects and dicts."""
        if isinstance(configuration, RunConfiguration):
            return configuration.format

        if isinstance(configuration, dict):
            config_format = configuration.get("format")
            if config_format is not None and isinstance(config_format, dict):
                return Format.from_dict(config_format) if hasattr(Format, "from_dict") else config_format

            return config_format

        raise ValueError("Configuration must be a RunConfiguration object or a dict.")

    def __extract_input_type(self, config_format: Any) -> Any:
        """Extract input type from config format."""
        if isinstance(config_format, dict):
            format_input = config_format.get("format_input") or config_format.get("input")
            if format_input is None:
                raise ValueError(
                    "If dir_path is provided, RunConfiguration.format.format_input must also be provided.",
                )

            if isinstance(format_input, dict):
                return format_input.get("input_type") or format_input.get("type")

            return getattr(format_input, "input_type", None)

        # Handle Format object
        if config_format.format_input is None:
            raise ValueError(
                "If dir_path is provided, RunConfiguration.format.format_input must also be provided.",
            )

        return config_format.format_input.input_type

    def __extract_input_data(
        self,
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
    ) -> Optional[Union[dict[str, Any], str]]:
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
        options: Optional[Union[Options, dict[str, str]]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
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
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
        dir_path: Optional[str] = None,
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
        instance_id: Optional[str] = None,
        verbose: Optional[bool] = False,
    ) -> bool:
        """
        Syncs a local run to a Nextmv Cloud target application. Returns True if
        the run was synced, False if it was skipped (already synced).
        """

        if verbose:
            log(f"🔄 Syncing local run `{run_id}`... ")

        # For files-based runs, the result files are written by default to ".".
        # Avoid this using a dedicated temp dir.
        run_result = self.run_result(run_id, output_dir_path=temp_dir)
        input_type = run_result.metadata.format.format_input.input_type

        # Skip runs that have already been synced.
        already_synced = run_result.synced_run_id is not None and run_result.synced_at is not None
        if already_synced:
            if verbose:
                log(f"   ⏭️  Skipping local run `{run_id}`, already synced at {run_result.synced_at.isoformat()}.")

            return False

        # Skip runs that don't have the supported type. TODO: delete this when
        # external runs support CSV_ARCHIVE and MULTI_FILE. Right now,
        # submitting an external result with a new run is limited to JSON and
        # TEXT. After this if statement is removed, the rest of the code should
        # work with CSV_ARCHIVE and MULTI_FILE as well, as using the input dir
        # path is already considered.
        if input_type not in {InputFormat.JSON, InputFormat.TEXT}:
            if verbose:
                log(
                    f"   ⏭️  Skipping local run `{run_id}`, unsupported input type: {input_type.value}. "
                    f"Supported types are: {[InputFormat.JSON.value, InputFormat.TEXT.value]}",
                )

            return False

        # Check that it is a valid run with inputs, outputs, logs, etc.
        if not self.__valid_run_result(run_result, runs_dir, run_id):
            if verbose:
                log(f"   ❌  Skipping local run `{run_id}`, invalid run (missing inputs, outputs or logs).")

            return False

        status = TrackedRunStatus.SUCCEEDED
        if run_result.metadata.status_v2 != StatusV2.succeeded:
            status = TrackedRunStatus.FAILED

        # Read the logs of the run and place each line as an element in a list
        run_dir = os.path.join(runs_dir, run_id)
        with open(os.path.join(run_dir, LOGS_KEY, LOGS_FILE)) as f:
            stderr_logs = f.readlines()

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
        if run_result.metadata.format.format_output.output_type == OutputFormat.JSON:
            tracked_run.output = run_result.output
        else:
            tracked_run.output_dir_path = os.path.join(run_dir, OUTPUTS_KEY, SOLUTIONS_KEY)

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
        run_result.synced_run_id = tracked_id
        run_result.synced_at = datetime.now(timezone.utc)
        with open(os.path.join(run_dir, f"{run_id}.json"), "w") as f:
            json.dump(run_result.to_dict(), f, indent=2)

        if verbose:
            log(f"✅ Synced local run `{run_id}` as remote run `{tracked_id}`.")

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

        # Validate outputs
        if not self.__validate_outputs(run_dir, run_result.metadata.format.format_output.output_type):
            return False

        # Validate logs
        if not self.__validate_logs(run_dir):
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

    def __validate_outputs(self, run_dir: str, output_type: OutputFormat) -> bool:
        """Validate that the outputs directory and files exist for the given output type."""
        outputs_dir = os.path.join(run_dir, OUTPUTS_KEY)
        if not os.path.exists(outputs_dir):
            return False

        solutions_dir = os.path.join(outputs_dir, SOLUTIONS_KEY)
        if not os.path.exists(solutions_dir):
            return False

        if output_type == OutputFormat.JSON:
            solution_file = os.path.join(solutions_dir, DEFAULT_OUTPUT_JSON_FILE)

            return os.path.isfile(solution_file)

        # For CSV_ARCHIVE and MULTI_FILE, solutions_dir should be a directory
        return os.path.isdir(solutions_dir)

    def __validate_logs(self, run_dir: str) -> bool:
        """Validate that the logs directory and file exist."""
        logs_dir = os.path.join(run_dir, LOGS_KEY)
        if not os.path.exists(logs_dir):
            return False

        logs_file = os.path.join(logs_dir, LOGS_FILE)

        return os.path.isfile(logs_file)
