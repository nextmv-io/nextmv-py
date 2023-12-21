"""This module contains the application class."""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from nextmv.base_model import BaseModel
from nextmv.cloud.acceptance_test import AcceptanceTest, Metric
from nextmv.cloud.batch_experiment import BatchExperiment, BatchExperimentMetadata, BatchExperimentRun
from nextmv.cloud.client import Client, get_size
from nextmv.cloud.input_set import InputSet

_MAX_RUN_SIZE: int = 5 * 1024 * 1024
"""Maximum size of the run input/output. This value is used to determine
whether to use the large input upload and/or result download endpoints."""


class DownloadURL(BaseModel):
    """Result of getting a download URL."""

    url: str
    """URL to use for downloading the file."""


class ErrorLog(BaseModel):
    """Error log of a run, when it was not successful."""

    error: str | None = None
    """Error message."""
    stdout: str | None = None
    """Standard output."""
    stderr: str | None = None
    """Standard error."""


class Metadata(BaseModel):
    """Metadata of a run, whether it was successful or not."""

    application_id: str
    """ID of the application where the run was submitted to."""
    application_instance_id: str
    """ID of the instance where the run was submitted to."""
    application_version_id: str
    """ID of the version of the application where the run was submitted to."""
    created_at: datetime
    """Date and time when the run was created."""
    duration: float
    """Duration of the run in milliseconds."""
    error: str
    """Error message if the run failed."""
    input_size: float
    """Size of the input in bytes."""
    output_size: float
    """Size of the output in bytes."""
    status: str
    """Status of the run."""


class PollingOptions(BaseModel):
    """Options to use when polling for a run result."""

    backoff: float = 1
    """Backoff factor to use between polls. Leave this at 1 to poll at a
    constant rate."""
    delay: float = 1
    """Delay to use between polls, in seconds."""
    initial_delay: float = 1
    """Initial delay to use before starting the polling strategy, in
    seconds."""
    max_delay: float = 20
    """Maximum delay to use between polls, in seconds. This parameter is
    activated when the backoff parameter is greater than 1, such that the delay
    is increasing after each poll."""
    max_duration: float = 60
    """Maximum duration of the polling strategy, in seconds."""
    max_tries: int = 20
    """Maximum number of tries to use."""


class RunInformation(BaseModel):
    """Information of a run."""

    description: str
    """Description of the run."""
    id: str
    """ID of the run."""
    metadata: Metadata
    """Metadata of the run."""
    name: str
    """Name of the run."""
    user_email: str
    """Email of the user who submitted the run."""


class RunResult(RunInformation):
    """Result of a run, wheter it was successful or not."""

    error_log: ErrorLog | None = None
    """Error log of the run. Only available if the run failed."""
    output: dict[str, Any] | None = None
    """Output of the run. Only available if the run succeeded."""


class UploadURL(BaseModel):
    """Result of getting an upload URL."""

    upload_id: str
    """ID of the upload."""
    upload_url: str
    """URL to use for uploading the file."""


@dataclass
class Application:
    """An application is a published decision model that can be executed."""

    client: Client
    """Client to use for interacting with the Nextmv Cloud API."""
    id: str
    """ID of the application."""

    default_instance_id: str = "devint"
    """Default instance ID to use for submitting runs."""
    endpoint: str = "v1/applications/{id}"
    """Base endpoint for the application."""
    experiments_endpoint: str = "{base}/experiments"
    """Base endpoint for the experiments in the application."""

    def __post_init__(self):
        """Logic to run after the class is initialized."""

        self.endpoint = self.endpoint.format(id=self.id)
        self.experiments_endpoint = self.experiments_endpoint.format(base=self.endpoint)

    def acceptance_test(self, acceptance_test_id: str) -> AcceptanceTest:
        """
        Get an acceptance test.

        Args:
            acceptance_test_id: ID of the acceptance test.

        Returns:
            Acceptance test.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/acceptance/{acceptance_test_id}",
        )

        return AcceptanceTest.from_dict(response.json())

    def batch_experiment(self, batch_id: str) -> BatchExperiment:
        """
        Get a batch experiment.

        Args:
            batch_id: ID of the batch experiment.

        Returns:
            Batch experiment.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}",
        )

        return BatchExperiment.from_dict(response.json())

    def input_set(self, input_set_id: str) -> InputSet:
        """
        Get an input set.

        Args:
            input_set_id: ID of the input set.

        Returns:
            Input set.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/inputsets/{input_set_id}",
        )

        return InputSet.from_dict(response.json())

    def list_acceptance_tests(self) -> list[AcceptanceTest]:
        """
        List all acceptance tests.

        Returns:
            List of acceptance tests.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/acceptance",
        )

        return [AcceptanceTest.from_dict(acceptance_test) for acceptance_test in response.json()]

    def list_batch_experiments(self) -> list[BatchExperimentMetadata]:
        """
        List all batch experiments.

        Returns:
            List of batch experiments.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch",
        )

        return [BatchExperimentMetadata.from_dict(batch_experiment) for batch_experiment in response.json()]

    def list_input_sets(self) -> list[InputSet]:
        """
        List all input sets.

        Returns:
            List of input sets.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/inputsets",
        )

        return [InputSet.from_dict(input_set) for input_set in response.json()]

    def new_acceptance_test(
        self,
        candidate_instance_id: str,
        control_instance_id: str,
        id: str,
        metrics: list[Metric | dict[str, Any]],
        name: str,
        input_set_id: str | None = None,
        description: str | None = None,
    ) -> AcceptanceTest:
        """
        Create a new acceptance test. The acceptance test is based on a batch
        experiment. If you already started a batch experiment, you don't need
        to provide the input_set_id parameter. In that case, the ID of the
        acceptance test and the batch experiment must be the same. If the batch
        experiment does not exist, you can provide the input_set_id parameter
        and a new batch experiment will be created for you.

        Args:
            candidate_instance_id: ID of the candidate instance.
            control_instance_id: ID of the control instance.
            id: ID of the acceptance test.
            metrics: List of metrics to use for the acceptance test.
            name: Name of the acceptance test.
            input_set_id: ID of the input set to use for the underlying batch
                experiment, in case it hasn't been started.
            description: Description of the acceptance test.

        Returns:
            Acceptance test.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
            ValueError: If the batch experiment ID does not match the
                acceptance test ID.
        """

        if input_set_id is None:
            batch_experiment = self.batch_experiment(batch_id=id)
            batch_experiment_id = batch_experiment.id
        else:
            batch_experiment_id = self.new_batch_experiment(
                name=name,
                input_set_id=input_set_id,
                instance_ids=[candidate_instance_id, control_instance_id],
                description=description,
                id=id,
            )

        if batch_experiment_id != id:
            raise ValueError(f"batch experiment_id ({batch_experiment_id}) does not match acceptance test id ({id})")

        payload_metrics = [{}] * len(metrics)
        for i, metric in enumerate(metrics):
            payload_metrics[i] = metric.to_dict() if isinstance(metric, Metric) else metric

        payload = {
            "candidate": {"instance_id": candidate_instance_id},
            "control": {"instance_id": control_instance_id},
            "metrics": payload_metrics,
            "experiment_id": batch_experiment_id,
            "name": name,
        }
        if description is not None:
            payload["description"] = description
        if id is not None:
            payload["id"] = id

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/acceptance",
            payload=payload,
        )

        return AcceptanceTest.from_dict(response.json())

    def new_batch_experiment(
        self,
        name: str,
        input_set_id: str,
        instance_ids: list[str],
        description: str | None = None,
        id: str | None = None,
        option_sets: dict[str, Any] | None = None,
        runs: list[BatchExperimentRun | dict[str, Any]] | None = None,
    ) -> str:
        """
        Create a new batch experiment.

        Args:
            name: Name of the batch experiment.
            input_set_id: ID of the input set to use for the experiment.
            instance_ids: List of instance IDs to use for the experiment.
            description: Description of the batch experiment.
            id: ID of the batch experiment.
            option_sets: Option sets to use for the experiment.
            runs: Runs to use for the experiment.

        Returns:
            ID of the batch experiment.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        payload = {
            "name": name,
            "input_set_id": input_set_id,
            "instance_ids": instance_ids,
        }
        if description is not None:
            payload["description"] = description
        if id is not None:
            payload["id"] = id
        if option_sets is not None:
            payload["option_sets"] = option_sets
        if runs is not None:
            payload_runs = [{}] * len(runs)
            for i, run in enumerate(runs):
                payload_runs[i] = run.to_dict() if isinstance(run, BatchExperimentRun) else run
            payload["runs"] = payload_runs

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/batch",
            payload=payload,
        )

        return response.json()["id"]

    def new_input_set(
        self,
        id: str,
        name: str,
        description: str | None = None,
        end_time: datetime | None = None,
        instance_id: str | None = None,
        maximum_runs: int | None = None,
        run_ids: list[str] | None = None,
        start_time: datetime | None = None,
    ) -> InputSet:
        """
        Create a new input set.

        Args:
            id: ID of the input set.
            name: Name of the input set.
            description: Description of the input set.
            end_time: End time of the runs to construct the input set.
            instance_id: ID of the instance to use for the input set. If not
                provided, the default_instance_id will be used.
            maximum_runs: Maximum number of runs to use for the input set.
            run_ids: IDs of the runs to use for the input set.
            start_time: Start time of the runs to construct the input set.

        Returns:
            Input set.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        payload = {
            "id": id,
            "name": name,
        }
        if description is not None:
            payload["description"] = description
        if end_time is not None:
            payload["end_time"] = end_time.isoformat()
        if instance_id is not None:
            payload["instance_id"] = instance_id
        if maximum_runs is not None:
            payload["maximum_runs"] = maximum_runs
        if run_ids is not None:
            payload["run_ids"] = run_ids
        if start_time is not None:
            payload["start_time"] = start_time.isoformat()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/inputsets",
            payload=payload,
        )

        return InputSet.from_dict(response.json())

    def new_run(
        self,
        input: dict[str, Any] = None,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        upload_id: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> str:
        """
        Submit an input to start a new run of the application. Returns the
        run_id of the submitted run.

        Args:
            input: Input to use for the run.
            instance_id: ID of the instance to use for the run. If not
                provided, the default_instance_id will be used.
            name: Name of the run.
            description: Description of the run.
            upload_id: ID to use when running a large input.
            options: Options to use for the run.

        Returns:
            ID of the submitted run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        input_size = 0
        if input is not None:
            input_size = get_size(input)

        upload_id_used = upload_id is not None
        if not upload_id_used and input_size > _MAX_RUN_SIZE:
            upload_url = self.upload_url()
            self.upload_large_input(upload_url=upload_url, input=input)
            upload_id = upload_url.upload_id
            upload_id_used = True

        payload = {}
        if upload_id_used:
            payload["upload_id"] = upload_id
        else:
            payload["input"] = input

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if options is not None:
            payload["options"] = options

        query_params = {
            "instance_id": instance_id if instance_id is not None else self.default_instance_id,
        }
        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/runs",
            payload=payload,
            query_params=query_params,
        )

        return response.json()["run_id"]

    def new_run_with_result(
        self,
        input: dict[str, Any] = None,
        instance_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        upload_id: str | None = None,
        run_options: dict[str, Any] | None = None,
        polling_options: PollingOptions = None,
    ) -> RunResult:
        """
        Submit an input to start a new run of the application and poll for the
        result. This is a convenience method that combines the new_run and
        run_result_with_polling methods, applying polling logic to check when
        the run succeeded.

         Args:
            input: Input to use for the run.
            instance_id: ID of the instance to use for the run. If not
                provided, the default_instance_id will be used.
            name: Name of the run.
            description: Description of the run.
            upload_id: ID to use when running a large input.
            run_options: Options to use for the run.
            polling_options: Options to use when polling for the run result. If
                not provided, the default options will be used.

         Returns:
            Result of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
            TimeoutError: If the run does not succeed after the polling
                strategy is exhausted based on time duration.
            RuntimeError: If the run does not succeed after the polling
                strategy is exhausted based on number of tries.
        """

        run_id = self.new_run(
            input=input,
            instance_id=instance_id,
            name=name,
            description=description,
            upload_id=upload_id,
            options=run_options,
        )

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
        )

    def run_metadata(self, run_id: str) -> RunInformation:
        """
        Get the metadata of a run. The result does not include the run output.

        Args:
            run_id: ID of the run.

        Returns:
            Metadata of the run (Run result with no output).

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/metadata",
        )

        return RunInformation.from_dict(response.json())

    def run_result(self, run_id: str) -> RunResult:
        """
        Get the result of a run. The result includes the run output.

        Args:
            run_id: ID of the run.

        Returns:
            Result of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        run_information = self.run_metadata(run_id=run_id)

        return self._run_result(run_id=run_id, run_information=run_information)

    def run_result_with_polling(
        self,
        run_id: str,
        polling_options: PollingOptions,
    ) -> RunResult:
        """
        Get the result of a run. The result includes the run output. This
        method polls for the result until the run finishes executing or the
        polling strategy is exhausted.

        Args:
            run_id: ID of the run.

        Returns:
            Result of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        if polling_options is None:
            polling_options = PollingOptions()

        time.sleep(polling_options.initial_delay)
        delay = polling_options.delay
        polling_ok = False
        for _ in range(polling_options.max_tries):
            run_information = self.run_metadata(run_id=run_id)
            if run_information.metadata.status in ["succeeded", "failed"]:
                polling_ok = True
                break

            if delay > polling_options.max_duration:
                raise TimeoutError(
                    f"run {run_id} did not succeed after {delay} seconds",
                )

            sleep_duration = min(delay, polling_options.max_delay)
            time.sleep(sleep_duration)
            delay *= polling_options.backoff

        if not polling_ok:
            raise RuntimeError(
                f"run {run_id} did not succeed after {polling_options.max_tries} tries",
            )

        return self._run_result(run_id=run_id, run_information=run_information)

    def upload_large_input(
        self,
        upload_url: UploadURL,
        input: dict[str, Any],
    ) -> None:
        """
        Upload the file located at the given path to the provided upload URL.

        Args:
            upload_url: Upload URL to use for uploading the file.
            input_path: Path to the input file.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PUT",
            endpoint=upload_url.upload_url,
            payload=input,
            headers={"Content-Type": "application/json"},
        )

    def upload_url(self) -> UploadURL:
        """
        Get an upload URL to use for uploading a file.

        Returns:
            Result of getting an upload URL.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/runs/uploadurl",
        )

        return UploadURL.from_dict(response.json())

    def _run_result(
        self,
        run_id: str,
        run_information: RunInformation,
    ) -> RunResult:
        """
        Get the result of a run. The result includes the run output. This is a
        private method that is the base for retrieving a run result, regardless
        of polling.

        Args:
            run_id: ID of the run.
            run_information: Information of the run.

        Returns:
            Result of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """
        query_params = None
        large_output = False
        if run_information.metadata.output_size > _MAX_RUN_SIZE:
            query_params = {"format": "url"}
            large_output = True

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}",
            query_params=query_params,
        )
        if not large_output:
            return RunResult.from_dict(response.json())

        download_url = DownloadURL.from_dict(response.json())
        response2 = self.client.request(
            method="GET",
            endpoint=download_url.url,
        )

        return RunResult.from_dict(response2.json())
