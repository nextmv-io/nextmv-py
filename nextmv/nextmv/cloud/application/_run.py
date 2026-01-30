"""
Application mixin for managing app runs.
"""

import io
import os
import pathlib
import shutil
import sys
import tarfile
import tempfile
from typing import TYPE_CHECKING, Any

import rich

from nextmv._serialization import deflated_serialize_json
from nextmv.base_model import BaseModel
from nextmv.cloud.assets import RunAsset
from nextmv.cloud.client import get_size
from nextmv.cloud.url import DownloadURL
from nextmv.input import Input, InputFormat
from nextmv.logger import log
from nextmv.options import Options
from nextmv.output import ASSETS_KEY, STATISTICS_KEY, Asset, Output, OutputFormat, Statistics
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.run import (
    ExternalRunResult,
    Run,
    RunConfiguration,
    RunInformation,
    RunLog,
    RunResult,
    TimestampedRunLog,
    TrackedRun,
)
from nextmv.status import StatusV2

# Maximum size of the run input/output in bytes. This constant defines the
# maximum allowed size for run inputs and outputs. When the size exceeds this
# value, the system will automatically use the large input upload and/or large
# result download endpoints.
_MAX_RUN_SIZE: int = 5 * 1024 * 1024

if TYPE_CHECKING:
    from . import Application


class ApplicationRunMixin:
    """
    Mixin class for managing app runs within an application.
    """

    def cancel_run(self: "Application", run_id: str) -> None:
        """
        Cancel a run.

        Parameters
        ----------
        run_id : str
            ID of the run to cancel.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.cancel_run("run-456")
        """

        _ = self.client.request(
            method="PATCH",
            endpoint=f"{self.endpoint}/runs/{run_id}/cancel",
        )

    def download_asset_content(
        self: "Application",
        asset: RunAsset,
        destination: str | pathlib.Path | io.BytesIO | None = None,
    ) -> Any | None:
        """
        Downloads an asset's content to a specified destination.

        Parameters
        ----------
        asset : RunAsset
            The asset to be downloaded.
        destination : str | pathlib.Path | io.BytesIO | None
            The destination where the asset will be saved. This can be a file path
            (as a string or pathlib.Path) or an io.BytesIO object. If None, the asset
            content will not be saved to a file, but returned immediately. If the asset
            type is JSON, the content will be returned as a dict.

        Returns
        -------
        Any or None
            If `destination` is None, returns the asset content: for JSON assets, a
            `dict` parsed from the JSON response; for other asset types, the raw
            `bytes` content. If `destination` is provided, the content is written
            to the given destination and the method returns `None`.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> assets = app.list_assets("run-123")
        >>> asset = assets[0]  # Assume we want to download the first asset
        >>> # Download to a file path
        >>> app.download_asset_content(asset, "polygons.geojson")
        >>> # Download to an in-memory bytes buffer
        >>> import io
        >>> buffer = io.BytesIO()
        >>> app.download_asset_content(asset, buffer)
        >>> # Download and get content directly (for JSON assets)
        >>> content = app.download_asset_content(asset)
        >>> print(content)
        {'type': 'FeatureCollection', 'features': [...]}
        """
        # First, get the download_url for the asset.
        download_url_response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{asset.run_id}/assets/{asset.id}",
        ).json()
        download_url = download_url_response["download_url"]
        asset_type = download_url_response.get("type", "json")

        # Now, download the asset content using the download_url.
        download_response = self.client.request(
            method="GET",
            endpoint=download_url,
            headers={"Content-Type": "application/json" if asset_type == "json" else "application/octet-stream"},
        )

        # Save the content to the specified destination.
        if destination is None:
            if asset_type == "json":
                return download_response.json()
            return download_response.content
        elif isinstance(destination, io.BytesIO):
            destination.write(download_response.content)
            return None
        else:
            with open(destination, "wb") as file:
                file.write(download_response.content)
            return None

    def list_assets(self: "Application", run_id: str) -> list[RunAsset]:
        """
        List the assets of a run.

        Retrieves a list of assets associated with a specific run. This method ONLY
        returns the asset metadata, the content needs to be fetched via the
        `download_asset_content` method.

        Parameters
        ----------
        run_id : str
            ID of the run to list assets for.

        Returns
        -------
        list[RunAsset]
            List of assets associated with the run.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> assets = app.list_assets("run-123")
        >>> for asset in assets:
        ...     print(asset.id, asset.name)
        b459daa6-1c13-48c6-b4c3-a262ea94cd04 clustering_polygons
        a1234567-89ab-cdef-0123-456789abcdef histogram
        """
        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/assets",
        )
        assets_data = response.json().get("items", [])
        for asset_data in assets_data:
            asset_data["run_id"] = run_id

        return [RunAsset.from_dict(asset) for asset in assets_data]

    def list_runs(self: "Application", status: StatusV2 | None = None) -> list[Run]:
        """
        List all runs.

        You can use the optional `status` parameter to filter runs by their
        status. Is not provided, all runs are returned.

        Parameters
        ----------
        status : StatusV2 | None
            Optional status to filter runs by.

        Returns
        -------
        list[Run]
            List of runs.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs",
        )

        runs = []
        for resp_run in response.json().get("runs", []):
            run = Run.from_dict(resp_run)
            if status is None:
                runs.append(run)
                continue

            if run.status_v2 == status:
                runs.append(run)

        return runs

    def new_run(  # noqa: C901 # Refactor this function at some point.
        self: "Application",
        input: Input | dict[str, Any] | BaseModel | str = None,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        upload_id: str | None = None,
        options: Options | dict[str, str] | None = None,
        configuration: RunConfiguration | dict[str, Any] | None = None,
        batch_experiment_id: str | None = None,
        external_result: ExternalRunResult | dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
    ) -> str:
        """
        Submit an input to start a new run of the application. Returns the
        `run_id` of the submitted run.

        Parameters
        ----------
        input: Union[Input, dict[str, Any], BaseModel, str]
            Input to use for the run. This can be a `nextmv.Input` object,
            `dict`, `BaseModel` or `str`.

            If `nextmv.Input` is used, and the `input_format` is either
            `nextmv.InputFormat.JSON` or `nextmv.InputFormat.TEXT`, then the
            input data is extracted from the `.data` property.

            If you want to work with `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`, you should use the `input_dir_path`
            argument instead. This argument takes precedence over the `input`.
            If `input_dir_path` is specified, this function looks for files in that
            directory and tars them, to later be uploaded using the
            `upload_data` method. If both the `input_dir_path` and `input`
            arguments are provided, the `input` is ignored.

            When `input_dir_path` is specified, the `configuration` argument must
            also be provided. More specifically, the
            `RunConfiguration.format.format_input.input_type` parameter
            dictates what kind of input is being submitted to the Nextmv Cloud.
            Make sure that this parameter is specified when working with the
            following input formats:

            - `nextmv.InputFormat.CSV_ARCHIVE`
            - `nextmv.InputFormat.MULTI_FILE`

            When working with JSON or text data, use the `input` argument
            directly.

            In general, if an input is too large, it will be uploaded with the
            `upload_data` method.
        instance_id: Optional[str]
            ID of the instance to use for the run. If not provided, the default
            instance ID associated to the Class (`default_instance_id`) is
            used.
        name: Optional[str]
            Name of the run.
        description: Optional[str]
            Description of the run.
        upload_id: Optional[str]
            ID to use when running a large input. If the `input` exceeds the
            maximum allowed size, then it is uploaded and the corresponding
            `upload_id` is used.
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
        batch_experiment_id: Optional[str]
            ID of a batch experiment to associate the run with. This is used
            when the run is part of a batch experiment.
        external_result: Optional[Union[ExternalRunResult, dict[str, Any]]]
            External result to use for the run. This can be a
            `nextmv.ExternalRunResult` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration. This is used when the run is an external run. We
            suggest that instead of specifying this parameter, you use the
            `track_run` method of the class.
        json_configurations: Optional[dict[str, Any]]
            Optional configurations for JSON serialization. This is used to
            customize the serialization before data is sent.
        input_dir_path: Optional[str]
            Path to a directory containing input files. If specified, the
            function will package the files in the directory into a tar file
            and upload it as a large input. This is useful for input formats
            like `nextmv.InputFormat.CSV_ARCHIVE` or `nextmv.InputFormat.MULTI_FILE`.
            If both `input` and `input_dir_path` are specified, the `input` is
            ignored, and the files in the directory are used instead.

        Returns
        ----------
        str
            ID (`run_id`) of the run that was submitted.

        Raises
        ----------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If the `input` is of type `nextmv.Input` and the .input_format` is
            not `JSON`. If the final `options` are not of type `dict[str,str]`.
        """

        tar_file = ""
        if input_dir_path is not None and input_dir_path != "":
            if not os.path.exists(input_dir_path):
                raise ValueError(f"Directory {input_dir_path} does not exist.")

            if not os.path.isdir(input_dir_path):
                raise ValueError(f"Path {input_dir_path} is not a directory.")

            tar_file = self._package_inputs(input_dir_path)

        input_data = self.__extract_input_data(input)

        input_size = 0
        if input_data is not None:
            input_size = get_size(input_data)

        upload_id_used = upload_id is not None
        if self.__upload_url_required(upload_id_used, input_size, tar_file, input):
            upload_url = self.upload_url()
            self.upload_data(data=input_data, upload_url=upload_url, tar_file=tar_file)
            upload_id = upload_url.upload_id
            upload_id_used = True

        options_dict = self.__extract_options_dict(options, json_configurations)

        # Builds the payload progressively based on the different arguments
        # that must be provided.
        payload = {}
        if upload_id_used:
            payload["upload_id"] = upload_id
        else:
            payload["input"] = input_data

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if len(options_dict) > 0:
            for k, v in options_dict.items():
                if not isinstance(v, str):
                    raise ValueError(f"options must be dict[str,str], option {k} has type {type(v)} instead.")
            payload["options"] = options_dict

        configuration_dict = self.__extract_run_config(input, configuration, input_dir_path)
        payload["configuration"] = configuration_dict

        if batch_experiment_id is not None:
            payload["batch_experiment_id"] = batch_experiment_id
        if external_result is not None:
            external_dict = (
                external_result.to_dict() if isinstance(external_result, ExternalRunResult) else external_result
            )
            payload["result"] = external_dict

        query_params = {}
        if instance_id is not None or self.default_instance_id is not None:
            query_params["instance_id"] = instance_id if instance_id is not None else self.default_instance_id

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/runs",
            payload=payload,
            query_params=query_params,
            json_configurations=json_configurations,
        )

        return response.json()["run_id"]

    def new_run_with_result(
        self: "Application",
        input: Input | dict[str, Any] | BaseModel | str = None,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        upload_id: str | None = None,
        run_options: Options | dict[str, str] | None = None,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        configuration: RunConfiguration | dict[str, Any] | None = None,
        batch_experiment_id: str | None = None,
        external_result: ExternalRunResult | dict[str, Any] | None = None,
        json_configurations: dict[str, Any] | None = None,
        input_dir_path: str | None = None,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Submit an input to start a new run of the application and poll for the
        result. This is a convenience method that combines the `new_run` and
        `run_result_with_polling` methods, applying polling logic to check when
        the run succeeded.

        Parameters
        ----------
        input: Union[Input, dict[str, Any], BaseModel, str]
            Input to use for the run. This can be a `nextmv.Input` object,
            `dict`, `BaseModel` or `str`.

            If `nextmv.Input` is used, and the `input_format` is either
            `nextmv.InputFormat.JSON` or `nextmv.InputFormat.TEXT`, then the
            input data is extracted from the `.data` property.

            If you want to work with `nextmv.InputFormat.CSV_ARCHIVE` or
            `nextmv.InputFormat.MULTI_FILE`, you should use the `input_dir_path`
            argument instead. This argument takes precedence over the `input`.
            If `input_dir_path` is specified, this function looks for files in that
            directory and tars them, to later be uploaded using the
            `upload_data` method. If both the `input_dir_path` and `input`
            arguments are provided, the `input` is ignored.

            When `input_dir_path` is specified, the `configuration` argument must
            also be provided. More specifically, the
            `RunConfiguration.format.format_input.input_type` parameter
            dictates what kind of input is being submitted to the Nextmv Cloud.
            Make sure that this parameter is specified when working with the
            following input formats:

            - `nextmv.InputFormat.CSV_ARCHIVE`
            - `nextmv.InputFormat.MULTI_FILE`

            When working with JSON or text data, use the `input` argument
            directly.

            In general, if an input is too large, it will be uploaded with the
            `upload_data` method.
        instance_id: Optional[str]
            ID of the instance to use for the run. If not provided, the default
            instance ID associated to the Class (`default_instance_id`) is
            used.
        name: Optional[str]
            Name of the run.
        description: Optional[str]
            Description of the run.
        upload_id: Optional[str]
            ID to use when running a large input. If the `input` exceeds the
            maximum allowed size, then it is uploaded and the corresponding
            `upload_id` is used.
        run_options: Optional[Union[Options, dict[str, str]]]
            Options to use for the run. This can be a `nextmv.Options` object
            or a dict. If a dict is used, the keys must be strings and the
            values must be strings as well. If a `nextmv.Options` object is
            used, the options are extracted from the `.to_cloud_dict()` method.
            Note that specifying `options` overrides the `input.options` (if
            the `input` is of type `nextmv.Input`).
        polling_options: PollingOptions
            Options to use when polling for the run result. This is a
            convenience method that combines the `new_run` and
            `run_result_with_polling` methods, applying polling logic to check
            when the run succeeded.
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.
        batch_experiment_id: Optional[str]
            ID of a batch experiment to associate the run with. This is used
            when the run is part of a batch experiment.
        external_result: Optional[Union[ExternalRunResult, dict[str, Any]]] = None
            External result to use for the run. This can be a
            `cloud.ExternalRunResult` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration. This is used when the run is an external run. We
            suggest that instead of specifying this parameter, you use the
            `track_run_with_result` method of the class.
        json_configurations: Optional[dict[str, Any]]
            Optional configurations for JSON serialization. This is used to
            customize the serialization before data is sent.
        input_dir_path: Optional[str]
            Path to a directory containing input files. If specified, the
            function will package the files in the directory into a tar file
            and upload it as a large input. This is useful for input formats
            like `nextmv.InputFormat.CSV_ARCHIVE` or `nextmv.InputFormat.MULTI_FILE`.
            If both `input` and `input_dir_path` are specified, the `input` is
            ignored, and the files in the directory are used instead.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This is
            required if the output is non-JSON. If the directory does not exist, it
            will be created. Uses the current directory by default.

        Returns
        ----------
        RunResult
            Result of the run.

        Raises
        ----------
        ValueError
            If the `input` is of type `nextmv.Input` and the `.input_format` is
            not `JSON`. If the final `options` are not of type `dict[str,str]`.
        requests.HTTPError
            If the response status code is not 2xx.
        TimeoutError
            If the run does not succeed after the polling strategy is exhausted
            based on time duration.
        RuntimeError
            If the run does not succeed after the polling strategy is exhausted
            based on number of tries.
        """

        run_id = self.new_run(
            input=input,
            instance_id=instance_id,
            name=name,
            description=description,
            upload_id=upload_id,
            options=run_options,
            configuration=configuration,
            batch_experiment_id=batch_experiment_id,
            external_result=external_result,
            json_configurations=json_configurations,
            input_dir_path=input_dir_path,
        )

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
            output_dir_path=output_dir_path,
        )

    def run_input(self: "Application", run_id: str, output_dir_path: str | None = ".") -> dict[str, Any] | None:
        """
        Get the input of a run.

        Retrieves the input data that was used for a specific run. This method
        handles both small and large inputs automatically - if the input size
        exceeds the maximum allowed size, it will fetch the input from a
        download URL. If the content format of the run is `csv-archive` or
        `multi-file`, then the `output_dir_path` parameter must be specified.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the input for.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON input files will be saved. This
            is required if the input is non-JSON. If the directory does not
            exist, it will be created. Uses the current directory by default.

        Returns
        -------
        dict[str, Any] | None
            Input data of the run as a dictionary. If the input format is
            non-JSON (e.g., csv-archive or multi-file), the method returns None
            after saving the input files to the specified `output_dir_path`.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> input_data = app.run_input("run-123")
        >>> print(input_data)
        {'locations': [...], 'vehicles': [...]}
        """
        run_information = self.run_metadata(run_id=run_id)

        query_params = None
        large = False
        if (
            run_information.metadata.input_size > _MAX_RUN_SIZE
            or run_information.metadata.format.format_input.input_type
            in {InputFormat.CSV_ARCHIVE, InputFormat.MULTI_FILE}
        ):
            query_params = {"format": "url"}
            large = True

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/input",
            query_params=query_params,
        )
        if not large:
            return response.json()

        download_url = DownloadURL.from_dict(response.json())
        download_response = self.client.request(
            method="GET",
            endpoint=download_url.url,
            headers={"Content-Type": "application/json"},
        )

        # See whether we can return the input directly or need to save to the given
        # directory
        if run_information.metadata.format.format_input.input_type != OutputFormat.JSON:
            if not output_dir_path or output_dir_path == "":
                raise ValueError(
                    "If the input format is not JSON, an output_dir_path must be provided.",
                )
            if not os.path.exists(output_dir_path):
                os.makedirs(output_dir_path, exist_ok=True)

            # Save .tar.gz file to a temp directory and extract contents to output_dir_path
            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_tar_path = os.path.join(tmpdirname, f"{run_id}.tar.gz")
                with open(temp_tar_path, "wb") as f:
                    f.write(download_response.content)
                shutil.unpack_archive(temp_tar_path, output_dir_path, filter=None)

            return

        # JSON input can be returned directly.
        return download_response.json()

    def run_metadata(self: "Application", run_id: str) -> RunInformation:
        """
        Get the metadata of a run.

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
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> metadata = app.run_metadata("run-123")
        >>> print(metadata.metadata.status_v2)
        StatusV2.succeeded
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/metadata",
        )

        info = RunInformation.from_dict(response.json())
        info.console_url = self.__console_url(info.id)

        return info

    def run_logs(self: "Application", run_id: str) -> RunLog:
        """
        Get the logs of a run.

        Parameters
        ----------
        run_id : str
            ID of the run to get logs for.

        Returns
        -------
        RunLog
            Logs of the run.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> logs = app.run_logs("run-123")
        >>> print(logs.stderr)
        'Warning: resource usage exceeded'
        """
        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/logs",
        )

        return RunLog.from_dict(response.json())

    def run_logs_with_polling(
        self: "Application",
        run_id: str,
        verbose: bool = False,
        rich_print: bool = False,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> list[TimestampedRunLog]:
        """
        Get the logs of a run with polling.

        Retrieves the logs of a run. This method polls for the logs until the
        run finishes executing or the polling strategy is exhausted. It is the
        "real-time" equivalent of the `run_logs` method. After the polling is
        done, all the logs are returned sorted by timestamp. You can use the
        `verbose` parameter to print the logs as they are obtained during the
        polling process. You can also use the `rich_print` parameter to enable
        rich printing for better formatting of the logs.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the logs for.
        verbose : bool, default=False
            Whether to print the logs as they are obtained during the polling
            process.
        rich_print : bool, default=False
            Whether to use rich printing for better formatting of the logs.
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the run logs.

        Returns
        -------
        list[TimestampedRunLog]
            List of timestamped logs of the run.

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
        >>> # Get run logs with polling
        >>> logs = app.run_logs_with_polling("run-123", polling_opts)
        >>> for log in logs:
        ...     print(f"[{log.timestamp}] {log.log}")
        [2024-01-01T12:00:00Z] Starting optimization...
        [2024-01-01T12:00:05Z] Found initial solution
        ...
        """

        sleep_duration_hint = 0
        logs = []
        query_params = None

        def polling_func() -> tuple[Any, bool]:
            nonlocal sleep_duration_hint
            nonlocal query_params

            # Perform the actual request to the API.
            response = self.client.request(
                method="GET",
                endpoint=f"{self.endpoint}/runs/{run_id}/logs/live",
                query_params=query_params,
            )
            json_resp = response.json()

            # Get the logs of the current request. Print them if verbose is
            # enabled and append them to the overall logs.
            for resp_log in json_resp.get("items", []):
                log_entry = TimestampedRunLog.from_dict(resp_log)
                if verbose:
                    msg = f"[{log_entry.timestamp}] {log_entry.log}"
                    if rich_print:
                        rich.print(msg, file=sys.stderr)
                    else:
                        log(msg)

                logs.append(log_entry)

            # We are done asking for logs if the run is in a final state.
            status_v2 = StatusV2(json_resp.get("status_v2", "none"))
            if status_v2 in {
                StatusV2.succeeded,
                StatusV2.failed,
                StatusV2.canceled,
            }:
                return logs, True

            # Store the server's hint for the next sleep duration.
            sleep_duration_hint = json_resp.get("next_available_in_seconds", 0)

            # Update the query parameters for the next request.
            since = json_resp.get("next_page_token")
            if since is not None:
                query_params = {"since": since}

            return logs, False

        def sleep_func() -> float:
            return sleep_duration_hint if sleep_duration_hint > 0 else 0

        polling_options.sleep_duration_func = sleep_func
        logs = poll(polling_options=polling_options, polling_func=polling_func)

        return sorted(logs, key=lambda log: log.timestamp)

    def run_result(self: "Application", run_id: str, output_dir_path: str | None = ".") -> RunResult:
        """
        Get the result of a run.

        Retrieves the complete result of a run, including the run output.

        Parameters
        ----------
        run_id : str
            ID of the run to get results for.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This is
            required if the output is non-JSON. If the directory does not exist, it
            will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Result of the run, including output.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

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
        self: "Application",
        run_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Get the result of a run with polling.

        Retrieves the result of a run including the run output. This method polls
        for the result until the run finishes executing or the polling strategy
        is exhausted.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the result for.
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the run result.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This is
            required if the output is non-JSON. If the directory does not exist, it
            will be created. Uses the current directory by default.

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

    def track_run(  # noqa: C901
        self: "Application",
        tracked_run: TrackedRun,
        instance_id: str | None = None,
        configuration: RunConfiguration | dict[str, Any] | None = None,
    ) -> str:
        """
        Track an external run.

        This method allows you to register in Nextmv a run that happened
        elsewhere, as though it were executed in the Nextmv platform. Having
        information about a run in Nextmv is useful for things like
        experimenting and testing.

        Please read the documentation on the `TrackedRun` class carefully, as
        there are important considerations to take into account when using this
        method. For example, if you intend to upload JSON input/output, use the
        `input`/`output` attributes of the `TrackedRun` class. On the other
        hand, if you intend to track files-based input/output, use the
        `input_dir_path`/`output_dir_path` attributes of the `TrackedRun`
        class.

        Parameters
        ----------
        tracked_run : TrackedRun
            The run to track.
        instance_id : Optional[str], default=None
            Optional instance ID if you want to associate your tracked run with
            an instance.
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.

        Returns
        -------
        str
            The ID of the run that was tracked.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If the tracked run does not have an input or output.

        Examples
        --------
        >>> from nextmv.cloud import Application
        >>> from nextmv import TrackedRun
        >>> app = Application(id="app_123")
        >>> tracked_run = TrackedRun(input={"data": [...]}, output={"solution": [...]})
        >>> run_id = app.track_run(tracked_run)
        """

        # Get the URL to upload the input to.
        url_input = self.upload_url()

        # Handle the case where the input is being uploaded as files. We need
        # to tar them.
        input_tar_file = ""
        input_dir_path = tracked_run.input_dir_path
        if input_dir_path is not None and input_dir_path != "":
            if not os.path.exists(input_dir_path):
                raise ValueError(f"Directory {input_dir_path} does not exist.")

            if not os.path.isdir(input_dir_path):
                raise ValueError(f"Path {input_dir_path} is not a directory.")

            input_tar_file = self._package_inputs(input_dir_path)

        # Handle the case where the input is uploaded as Input or a dict.
        upload_input = tracked_run.input
        if upload_input is not None and isinstance(tracked_run.input, Input):
            upload_input = tracked_run.input.data

        # Actually uploads de input.
        self.upload_data(data=upload_input, upload_url=url_input, tar_file=input_tar_file)

        # Get the URL to upload the output to.
        url_output = self.upload_url()

        # Handle the case where the output is being uploaded as files. We need
        # to tar them.
        output_tar_file = ""
        output_dir_path = tracked_run.output_dir_path
        if output_dir_path is not None and output_dir_path != "":
            if not os.path.exists(output_dir_path):
                raise ValueError(f"Directory {output_dir_path} does not exist.")

            if not os.path.isdir(output_dir_path):
                raise ValueError(f"Path {output_dir_path} is not a directory.")

            output_tar_file = self._package_inputs(output_dir_path)

        # Handle the case where the output is uploaded as Output or a dict.
        upload_output = tracked_run.output
        if upload_output is not None and isinstance(tracked_run.output, Output):
            upload_output = tracked_run.output.to_dict()

        # Actually uploads the output.
        self.upload_data(data=upload_output, upload_url=url_output, tar_file=output_tar_file)

        # Create the external run result and appends logs if required.
        external_result = ExternalRunResult(
            output_upload_id=url_output.upload_id,
            status=tracked_run.status.value,
            execution_duration=tracked_run.duration,
        )

        # Handle the stderr logs if provided.
        if tracked_run.logs is not None:
            url_stderr = self.upload_url()
            self.upload_data(data=tracked_run.logs_text(), upload_url=url_stderr)
            external_result.error_upload_id = url_stderr.upload_id

        if tracked_run.error is not None and tracked_run.error != "":
            external_result.error_message = tracked_run.error

        # Handle the statistics upload if provided.
        stats = tracked_run.statistics
        if stats is not None:
            if isinstance(stats, Statistics):
                stats_dict = stats.to_dict()
                stats_dict = {STATISTICS_KEY: stats_dict}
            elif isinstance(stats, dict):
                stats_dict = stats
                if STATISTICS_KEY not in stats_dict:
                    stats_dict = {STATISTICS_KEY: stats_dict}
            else:
                raise ValueError("tracked_run.statistics must be either a `Statistics` or `dict` object")

            url_stats = self.upload_url()
            self.upload_data(data=stats_dict, upload_url=url_stats)
            external_result.statistics_upload_id = url_stats.upload_id

        # Handle the assets upload if provided.
        assets = tracked_run.assets
        if assets is not None:
            if isinstance(assets, list):
                assets_list = []
                for ix, asset in enumerate(assets):
                    if isinstance(asset, Asset):
                        assets_list.append(asset.to_dict())
                    elif isinstance(asset, dict):
                        assets_list.append(asset)
                    else:
                        raise ValueError(f"tracked_run.assets, index {ix} must be an `Asset` or `dict` object")
                assets_dict = {ASSETS_KEY: assets_list}
            elif isinstance(assets, dict):
                assets_dict = assets
                if ASSETS_KEY not in assets_dict:
                    assets_dict = {ASSETS_KEY: assets_dict}
            else:
                raise ValueError("tracked_run.assets must be either a `list[Asset]`, `list[dict]`, or `dict` object")

            url_assets = self.upload_url()
            self.upload_data(data=assets_dict, upload_url=url_assets)
            external_result.assets_upload_id = url_assets.upload_id

        return self.new_run(
            upload_id=url_input.upload_id,
            external_result=external_result,
            instance_id=instance_id,
            name=tracked_run.name,
            description=tracked_run.description,
            configuration=configuration,
        )

    def track_run_with_result(
        self: "Application",
        tracked_run: TrackedRun,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        instance_id: str | None = None,
        output_dir_path: str | None = ".",
        configuration: RunConfiguration | dict[str, Any] | None = None,
    ) -> RunResult:
        """
        Track an external run and poll for the result. This is a convenience
        method that combines the `track_run` and `run_result_with_polling`
        methods. It applies polling logic to check when the run was
        successfully registered.

        Parameters
        ----------
        tracked_run : TrackedRun
            The run to track.
        polling_options : PollingOptions
            Options to use when polling for the run result.
        instance_id: Optional[str]
            Optional instance ID if you want to associate your tracked run with
            an instance.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This is
            required if the output is non-JSON. If the directory does not exist, it
            will be created. Uses the current directory by default.
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.

        Returns
        -------
        RunResult
            Result of the run.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If the tracked run does not have an input or output.
        TimeoutError
            If the run does not succeed after the polling strategy is
            exhausted based on time duration.
        RuntimeError
            If the run does not succeed after the polling strategy is
            exhausted based on number of tries.
        """
        run_id = self.track_run(
            tracked_run=tracked_run,
            instance_id=instance_id,
            configuration=configuration,
        )

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
            output_dir_path=output_dir_path,
        )

    def _package_inputs(self: "Application", dir_path: str) -> str:
        """
        This is an auxiliary function for packaging the inputs found in the
        provided `dir_path`. All the files found in the directory are tarred and
        g-zipped. This function returns the tar file path that contains the
        packaged inputs.
        """

        # Create a temporary directory for the output
        output_dir = tempfile.mkdtemp(prefix="nextmv-inputs-out-")

        # Define the output tar file name and path
        tar_filename = "inputs.tar.gz"
        tar_file_path = os.path.join(output_dir, tar_filename)

        # Create the tar.gz file
        with tarfile.open(tar_file_path, "w:gz") as tar:
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file == tar_filename:
                        continue

                    file_path = os.path.join(root, file)

                    # Skip directories, only process files
                    if os.path.isdir(file_path):
                        continue

                    # Create relative path for the archive
                    arcname = os.path.relpath(file_path, start=dir_path)
                    tar.add(file_path, arcname=arcname)

        return tar_file_path

    def __run_result(
        self: "Application",
        run_id: str,
        run_information: RunInformation,
        output_dir_path: str | None = ".",
    ) -> RunResult:
        """
        Get the result of a run.

        This is a private method that retrieves the complete result of a run,
        including the output data. It handles both small and large outputs,
        automatically using the appropriate API endpoints based on the output
        size. This method serves as the base implementation for retrieving
        run results, regardless of polling strategy.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the result for.
        run_information : RunInformation
            Information about the run, including metadata such as output size.
        output_dir_path : Optional[str], default="."
            Path to a directory where non-JSON output files will be saved. This is
            required if the output is non-JSON. If the directory does not exist, it
            will be created. Uses the current directory by default.

        Returns
        -------
        RunResult
            Result of the run, including all metadata and output data.
            For large outputs, the method will fetch the output from
            a download URL.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Notes
        -----
        This method automatically handles large outputs by checking if the
        output size exceeds _MAX_RUN_SIZE. If it does, the method will request
        a download URL and fetch the output data separately.
        """
        query_params = None
        use_presigned_url = False
        if (
            run_information.metadata.format.format_output.output_type != OutputFormat.JSON
            or run_information.metadata.output_size > _MAX_RUN_SIZE
        ):
            query_params = {"format": "url"}
            use_presigned_url = True

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}",
            query_params=query_params,
        )
        result = RunResult.from_dict(response.json())
        result.console_url = self.__console_url(result.id)

        if not use_presigned_url or result.metadata.status_v2 != StatusV2.succeeded:
            return result

        download_url = DownloadURL.from_dict(response.json()["output"])
        download_response = self.client.request(
            method="GET",
            endpoint=download_url.url,
            headers={"Content-Type": "application/json"},
        )

        # See whether we can attach the output directly or need to save to the given
        # directory
        if run_information.metadata.format.format_output.output_type != OutputFormat.JSON:
            if not output_dir_path or output_dir_path == "":
                raise ValueError(
                    "If the output format is not JSON, an output_dir_path must be provided.",
                )
            if not os.path.exists(output_dir_path):
                os.makedirs(output_dir_path, exist_ok=True)
            # Save .tar.gz file to a temp directory and extract contents to output_dir_path
            with tempfile.TemporaryDirectory() as tmpdirname:
                temp_tar_path = os.path.join(tmpdirname, f"{run_id}.tar.gz")
                with open(temp_tar_path, "wb") as f:
                    f.write(download_response.content)
                shutil.unpack_archive(temp_tar_path, output_dir_path, filter=None)
        else:
            result.output = download_response.json()

        return result

    def __console_url(self: "Application", run_id: str) -> str:
        """Auxiliary method to get the console URL for a run."""

        return f"{self.client.console_url}/app/{self.id}/run/{run_id}?view=details"

    def __upload_url_required(
        self: "Application",
        upload_id_used: bool,
        input_size: int,
        tar_file: str,
        input: Input | dict[str, Any] | BaseModel | str = None,
    ) -> bool:
        """
        Auxiliary function to determine if an upload URL is required
        based on the input size, type, and configuration.
        """

        if upload_id_used:
            return False

        non_json_payload = False
        if isinstance(input, str):
            non_json_payload = True
        elif isinstance(input, Input) and input.input_format != InputFormat.JSON:
            non_json_payload = True
        elif tar_file is not None and tar_file != "":
            non_json_payload = True

        size_exceeds = input_size > _MAX_RUN_SIZE

        return size_exceeds or non_json_payload

    def __extract_input_data(
        self: "Application",
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
        self: "Application",
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
                        continue

                    options_dict[k] = deflated_serialize_json(v, json_configurations=json_configurations)

        return options_dict

    def __extract_run_config(
        self: "Application",
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
