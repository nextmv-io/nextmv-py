"""This module contains the application class."""

import json
import random
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

import requests

from nextmv.base_model import BaseModel
from nextmv.cloud import package
from nextmv.cloud.acceptance_test import AcceptanceTest, ExperimentStatus, Metric
from nextmv.cloud.batch_experiment import (
    BatchExperiment,
    BatchExperimentInformation,
    BatchExperimentMetadata,
    BatchExperimentRun,
)
from nextmv.cloud.client import Client, get_size
from nextmv.cloud.input_set import InputSet, ManagedInput
from nextmv.cloud.instance import Instance, InstanceConfiguration
from nextmv.cloud.manifest import Manifest
from nextmv.cloud.run import (
    ExternalRunResult,
    Format,
    FormatInput,
    RunConfiguration,
    RunInformation,
    RunLog,
    RunResult,
    TrackedRun,
)
from nextmv.cloud.safe import name_and_id
from nextmv.cloud.scenario import Scenario, ScenarioInputType, _option_sets, _scenarios_by_id
from nextmv.cloud.secrets import Secret, SecretsCollection, SecretsCollectionSummary
from nextmv.cloud.status import StatusV2
from nextmv.cloud.version import Version
from nextmv.input import Input, InputFormat
from nextmv.logger import log
from nextmv.model import Model, ModelConfiguration
from nextmv.options import Options
from nextmv.output import Output

_MAX_RUN_SIZE: int = 5 * 1024 * 1024
"""Maximum size of the run input/output. This value is used to determine
whether to use the large input upload and/or result download endpoints."""


class DownloadURL(BaseModel):
    """Result of getting a download URL."""

    url: str
    """URL to use for downloading the file."""


@dataclass
class PollingOptions:
    """
    Options to use when polling for a run result.

    The Cloud API will be polled for the result. The polling stops if:

    * The maximum number of polls (tries) are exhausted. This is specified by
      the `max_tries` parameter.
    * The maximum duration of the polling strategy is reached. This is
      specified by the `max_duration` parameter.

    Before conducting the first poll, the `initial_delay` is used to sleep.
    After each poll, a sleep duration is calculated using the following
    strategy, based on exponential backoff with jitter:

    ```
    sleep_duration = min(`max_delay`, `delay` + `backoff` * 2 ** i + Uniform(0, `jitter`))
    ```

    Where:
    * i is the retry (poll) number.
    * Uniform is the uniform distribution.

    Note that the sleep duration is capped by the `max_delay` parameter.
    """

    backoff: float = 0.9
    """
    Exponential backoff factor, in seconds, to use between polls.
    """
    delay: float = 0.1
    """Base delay to use between polls, in seconds."""
    initial_delay: float = 1
    """
    Initial delay to use before starting the polling strategy, in seconds.
    """
    max_delay: float = 20
    """Maximum delay to use between polls, in seconds."""
    max_duration: float = 300
    """Maximum duration of the polling strategy, in seconds."""
    max_tries: int = 100
    """Maximum number of tries to use."""
    jitter: float = 1
    """
    Jitter to use for the polling strategy. A uniform distribution is sampled
    between 0 and this number. The resulting random number is added to the
    delay for each poll, adding a random noise. Set this to 0 to avoid using
    random jitter.
    """
    verbose: bool = False
    """Whether to log the polling strategy. This is useful for debugging."""
    stop: Optional[Callable[[], bool]] = None
    """
    Function to call to check if the polling should stop. This is useful for
    stopping the polling based on external conditions. The function should
    return True to stop the polling and False to continue. The function does
    not receive any arguments. The function is called before each poll.
    """


_DEFAULT_POLLING_OPTIONS: PollingOptions = PollingOptions()
"""Default polling options to use when polling for a run result."""


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

    def cancel_run(self, run_id: str) -> None:
        """
        Cancel a run.

        Args:
            run_id: ID of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PATCH",
            endpoint=f"{self.endpoint}/runs/{run_id}/cancel",
        )

    def delete(self) -> None:
        """
        Delete the application.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=self.endpoint,
        )

    def delete_acceptance_test(self, acceptance_test_id: str) -> None:
        """
        Deletes an acceptance test, along with all the associated information
        such as the underlying batch experiment.

        Args:
            acceptance_test_id: ID of the acceptance test.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/acceptance/{acceptance_test_id}",
        )

    def delete_batch_experiment(self, batch_id: str) -> None:
        """
        Deletes a batch experiment, along with all the associated information,
        such as its runs.

        Parameters
        ----------
        batch_id: str
            ID of the batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}",
        )

    def delete_scenario_test(self, scenario_test_id: str) -> None:
        """
        Deletes a scenario test. Scenario tests are based on the batch
        experiments API, so this function summons `delete_batch_experiment`.

        Parameters
        ----------
        scenario_test_id: str
            ID of the scenario test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.delete_batch_experiment(batch_id=scenario_test_id)

    def delete_secrets_collection(self, secrets_collection_id: str) -> None:
        """
        Deletes a secrets collection.

        Args:
            secrets_collection_id: ID of the secrets collection.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

    @staticmethod
    def exists(client: Client, id: str) -> bool:
        """
        Check if an application exists.

        Args:
            client: Client to use for interacting with the Nextmv Cloud API.
            id: ID of the application.

        Returns:
            True if the application exists, False otherwise.
        """

        try:
            _ = client.request(
                method="GET",
                endpoint=f"v1/applications/{id}",
            )
            # If the request was successful, the application exists.
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            # Re-throw the exception if it is not the expected 404 error.
            raise e from None

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

    def instance(self, instance_id: str) -> Instance:
        """
        Get an instance.

        Args:
            instance_id: ID of the instance.

        Returns:
            Instance.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/instances/{instance_id}",
        )

        return Instance.from_dict(response.json())

    def instance_exists(self, instance_id: str) -> bool:
        """
        Check if an instance exists.

        Args:
            instance_id: ID of the instance.

        Returns:
            True if the instance exists, False otherwise.
        """

        try:
            self.instance(instance_id=instance_id)
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            raise e

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

        Returns
        -------
        list[BatchExperimentMetadata]
            List of batch experiments.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch",
            query_params={"type": "batch"},
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

    def list_instances(self) -> list[Instance]:
        """
        List all instances.

        Returns:
            List of instances.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/instances",
        )

        return [Instance.from_dict(instance) for instance in response.json()]

    def list_managed_inputs(self) -> list[ManagedInput]:
        """
        List all managed inputs.

        Returns
        -------
        list[ManagedInput]
            List of managed inputs.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/inputs",
        )

        return [ManagedInput.from_dict(managed_input) for managed_input in response.json()]

    def list_scenario_tests(self) -> list[BatchExperimentMetadata]:
        """
        List all batch scenario tests. Scenario tests are based on the batch
        experiments API, so this function returns the same information as
        `list_batch_experiments`, albeit using a different query parameter.

        Returns
        -------
        list[BatchExperimentMetadata]
            List of scenario tests.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch",
            query_params={"type": "scenario"},
        )

        return [BatchExperimentMetadata.from_dict(batch_experiment) for batch_experiment in response.json()]

    def list_secrets_collections(self) -> list[SecretsCollectionSummary]:
        """
        List all secrets collections.

        Returns:
            List of secrets collections.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets",
        )

        return [SecretsCollectionSummary.from_dict(secrets) for secrets in response.json()["items"]]

    def list_versions(self) -> list[Version]:
        """
        List all versions.

        Returns:
            List of versions.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions",
        )

        return [Version.from_dict(version) for version in response.json()]

    def managed_input(self, managed_input_id: str) -> ManagedInput:
        """
        Get a managed input.

        Parameters
        ----------
        managed_input_id: str
            ID of the managed input.

        Returns
        -------
        ManagedInput
            The managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
        )

        return ManagedInput.from_dict(response.json())

    @classmethod
    def new(
        cls,
        client: Client,
        name: str,
        id: Optional[str] = None,
        description: Optional[str] = None,
        is_workflow: Optional[bool] = None,
        exist_ok: bool = False,
    ) -> "Application":
        """
        Create a new application.

        Args:
            client: Client to use for interacting with the Nextmv Cloud API.
            name: Name of the application.
            id: ID of the application. Will be generated if not provided.
            description: Description of the application.
            is_workflow: Whether the application is a Decision Workflow.
            exist_ok: If True and an application with the same ID already exists,
                return the existing application instead of creating a new one.

        Returns:
            The new application.
        """

        if exist_ok and cls.exists(client=client, id=id):
            return Application(client=client, id=id)

        payload = {
            "name": name,
        }

        if description is not None:
            payload["description"] = description
        if id is not None:
            payload["id"] = id
        if is_workflow is not None:
            payload["is_pipeline"] = is_workflow

        response = client.request(
            method="POST",
            endpoint="v1/applications",
            payload=payload,
        )

        return cls(client=client, id=response.json()["id"])

    def new_acceptance_test(
        self,
        candidate_instance_id: str,
        baseline_instance_id: str,
        id: str,
        metrics: list[Union[Metric, dict[str, Any]]],
        name: str,
        input_set_id: Optional[str] = None,
        description: Optional[str] = None,
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
            baseline_instance_id: ID of the baseline instance.
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
            try:
                batch_experiment = self.batch_experiment(batch_id=id)
                batch_experiment_id = batch_experiment.id
            except requests.HTTPError as e:
                if e.response.status_code != 404:
                    raise e

                raise ValueError(
                    f"batch experiment {id} does not exist, input_set_id must be defined to create a new one"
                ) from e
        else:
            batch_experiment_id = self.new_batch_experiment(
                name=name,
                input_set_id=input_set_id,
                instance_ids=[candidate_instance_id, baseline_instance_id],
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
            "control": {"instance_id": baseline_instance_id},
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

    def new_acceptance_test_with_result(
        self,
        candidate_instance_id: str,
        baseline_instance_id: str,
        id: str,
        metrics: list[Union[Metric, dict[str, Any]]],
        name: str,
        input_set_id: Optional[str] = None,
        description: Optional[str] = None,
        polling_options: PollingOptions = _DEFAULT_POLLING_OPTIONS,
    ) -> AcceptanceTest:
        """
        Create a new acceptance test and poll for the result. This is a
        convenience method that combines the new_acceptance_test with polling
        logic to check when the acceptance test is done.

        Args:
            candidate_instance_id: ID of the candidate instance.
            baseline_instance_id: ID of the baseline instance.
            id: ID of the acceptance test.
            metrics: List of metrics to use for the acceptance test.
            name: Name of the acceptance test.
            input_set_id: ID of the input set to use for the underlying batch
                experiment, in case it hasn't been started.
            description: Description of the acceptance test.
            polling_options: Options to use when polling for the run result.

        Returns:
            Result of the acceptance test.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
            TimeoutError: If the acceptance test does not succeed after the
                polling strategy is exhausted based on time duration.
            RuntimeError: If the acceptance test does not succeed after the
                polling strategy is exhausted based on number of tries.
        """
        _ = self.new_acceptance_test(
            candidate_instance_id=candidate_instance_id,
            baseline_instance_id=baseline_instance_id,
            id=id,
            metrics=metrics,
            name=name,
            input_set_id=input_set_id,
            description=description,
        )

        def polling_func() -> tuple[AcceptanceTest, bool]:
            test_information = self.acceptance_test(acceptance_test_id=id)
            if test_information.status in [
                ExperimentStatus.completed,
                ExperimentStatus.failed,
                ExperimentStatus.canceled,
            ]:
                return test_information, True

            return None, False

        test_information = poll(polling_options=polling_options, polling_func=polling_func)

        return test_information

    def new_batch_experiment(
        self,
        name: str,
        input_set_id: Optional[str] = None,
        instance_ids: Optional[list[str]] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
        option_sets: Optional[dict[str, dict[str, str]]] = None,
        runs: Optional[list[Union[BatchExperimentRun, dict[str, Any]]]] = None,
        type: Optional[str] = "batch",
    ) -> str:
        """
        Create a new batch experiment.

        Parameters
        ----------
        name: str
            Name of the batch experiment.
        input_set_id: str
            ID of the input set to use for the batch experiment.
        instance_ids: list[str]
            List of instance IDs to use for the batch experiment.
        description: Optional[str]
            Optional description of the batch experiment.
        id: Optional[str]
            ID of the batch experiment. Will be generated if not provided.
        option_sets: Optional[dict[str, dict[str, str]]]
            Option sets to use for the batch experiment. This is a dictionary
            where the keys are option set IDs and the values are dictionaries
            with the actual options.
        runs: Optional[list[BatchExperimentRun]]
            List of runs to use for the batch experiment.
        type: Optional[str]
            Type of the batch experiment. This is used to determine the
            experiment type. The default value is "batch". If you want to
            create a scenario test, set this to "scenario".

        Returns
        -------
        str
            ID of the batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {
            "name": name,
        }
        if input_set_id is not None:
            payload["input_set_id"] = input_set_id
        if instance_ids is not None:
            payload["instance_ids"] = instance_ids
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
        if type is not None:
            payload["type"] = type

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
        description: Optional[str] = None,
        end_time: Optional[datetime] = None,
        instance_id: Optional[str] = None,
        maximum_runs: Optional[int] = None,
        run_ids: Optional[list[str]] = None,
        start_time: Optional[datetime] = None,
        inputs: Optional[list[ManagedInput]] = None,
    ) -> InputSet:
        """
        Create a new input set. You can create an input set from three
        different methodologies:

        1. Using `instance_id`, `start_time`, `end_time` and `maximum_runs`.
           Instance runs will be obtained from the application matching the
           criteria of dates and maximum number of runs.
        2. Using `run_ids`. The input set will be created using the list of
           runs specified by the user.
        3. Using `inputs`. The input set will be created using the list of
           inputs specified by the user. This is useful for creating an input
           set from a list of inputs that are already available in the
           application.

        Parameters
        ----------
        id: str
            ID of the input set
        name: str
            Name of the input set.
        description: Optional[str]
            Optional description of the input set.
        end_time: Optional[datetime]
            End time of the input set. This is used to filter the runs
            associated with the input set.
        instance_id: Optional[str]
            ID of the instance to use for the input set. This is used to
            filter the runs associated with the input set. If not provided,
            the application’s `default_instance_id` is used.
        maximum_runs: Optional[int]
            Maximum number of runs to use for the input set. This is used to
            filter the runs associated with the input set. If not provided,
            all runs are used.
        run_ids: Optional[list[str]]
            List of run IDs to use for the input set.
        start_time: Optional[datetime]
            Start time of the input set. This is used to filter the runs
            associated with the input set.
        inputs: Optional[list[ExperimentInput]]
            List of inputs to use for the input set. This is used to create
            the input set from a list of inputs that are already available in
            the application.


        Returns
        -------
        InputSet
            The new input set.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
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
        if inputs is not None:
            payload["inputs"] = [input.to_dict() for input in inputs]

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/inputsets",
            payload=payload,
        )

        return InputSet.from_dict(response.json())

    def new_instance(
        self,
        version_id: str,
        id: str,
        name: str,
        description: Optional[str] = None,
        configuration: Optional[InstanceConfiguration] = None,
        exist_ok: bool = False,
    ) -> Instance:
        """
        Create a new instance and associate it with a version.

        Args:
            version_id: ID of the version to associate the instance with.
            id: ID of the instance. Will be generated if not provided.
            name: Name of the instance. Will be generated if not provided.
            description: Description of the instance. Will be generated if not provided.
            configuration: Configuration to use for the instance.
            exist_ok: If True and an instance with the same ID already exists,
                return the existing instance instead of creating a new one.

        Returns:
            Instance.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        if exist_ok and id is None:
            raise ValueError("If exist_ok is True, id must be provided")

        if exist_ok and self.instance_exists(instance_id=id):
            return self.instance(instance_id=id)

        payload = {
            "version_id": version_id,
        }

        if id is not None:
            payload["id"] = id
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if configuration is not None:
            payload["configuration"] = configuration.to_dict()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/instances",
            payload=payload,
        )

        return Instance.from_dict(response.json())

    def new_managed_input(
        self,
        id: str,
        name: str,
        description: Optional[str] = None,
        upload_id: Optional[str] = None,
        run_id: Optional[str] = None,
        format: Optional[Union[Format, dict[str, any]]] = None,
    ) -> ManagedInput:
        """
        Create a new managed input. There are two methods for creating a
        managed input:

        1. Specifying the `upload_id` parameter. You may use the `upload_url`
           method to obtain the upload ID and the `upload_large_input` method
           to upload the data to it.
        2. Specifying the `run_id` parameter. The managed input will be
           created from the run specified by the `run_id` parameter.

        Either the `upload_id` or the `run_id` parameter must be specified.

        Parameters
        ----------
        id: str
            ID of the managed input.
        name: str
            Name of the managed input.
        description: Optional[str]
            Optional description of the managed input.
        upload_id: Optional[str]
            ID of the upload to use for the managed input.
        run_id: Optional[str]
            ID of the run to use for the managed input.
        format: Optional[Format]
            Format of the managed input. Default will be formatted as `JSON`.

        Returns
        -------
        ManagedInput
            The new managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If neither the `upload_id` nor the `run_id` parameter is
            specified.
        """

        if upload_id is None and run_id is None:
            raise ValueError("Either upload_id or run_id must be specified")

        payload = {
            "id": id,
            "name": name,
        }

        if description is not None:
            payload["description"] = description
        if upload_id is not None:
            payload["upload_id"] = upload_id
        if run_id is not None:
            payload["run_id"] = run_id

        if format is not None:
            payload["format"] = format.to_dict() if isinstance(format, Format) else format
        else:
            payload["format"] = Format(format_input=FormatInput(input_type=InputFormat.JSON)).to_dict()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/inputs",
            payload=payload,
        )

        return ManagedInput.from_dict(response.json())

    def new_run(  # noqa: C901 # Refactor this function at some point.
        self,
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        instance_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        upload_id: Optional[str] = None,
        options: Optional[Union[Options, dict[str, str]]] = None,
        configuration: Optional[Union[RunConfiguration, dict[str, any]]] = None,
        batch_experiment_id: Optional[str] = None,
        external_result: Optional[Union[ExternalRunResult, dict[str, any]]] = None,
    ) -> str:
        """
        Submit an input to start a new run of the application. Returns the
        `run_id` of the submitted run.

        Parameters
        ----------
        input: Union[Input, dict[str, Any], BaseModel, str]
            Input to use for the run. This can be a `nextmv.Input` object,
            `dict`, `BaseModel` or `str`. If `nextmv.Input` is used, then the
            input is extracted from the `.data` property. Note that for now,
            `InputFormat.CSV_ARCHIVE` is not supported as an
            `input.input_format`. If an input is too large, it will be uploaded
            with the `upload_large_input` method.
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
        configuration: Optional[Union[RunConfiguration, dict[str, any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.
        batch_experiment_id: Optional[str]
            ID of a batch experiment to associate the run with. This is used
            when the run is part of a batch experiment.
        external_result: Optional[Union[ExternalRunResult, dict[str, any]]]
            External result to use for the run. This can be a
            `cloud.ExternalRunResult` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration. This is used when the run is an external run. We
            suggest that instead of specifying this parameter, you use the
            `track_run` method of the class.

        Returns
        ----------
        str
            ID (`run_id`) of the run that was submitted.

        Raises
        ----------
            requests.HTTPError: If the response status code is not 2xx.
            ValueError:
                If the `input` is of type `nextmv.Input` and the
                `.input_format` is not `JSON`. If the final `options` are not
                of type `dict[str,str]`.
        """

        input_data = None
        if isinstance(input, BaseModel):
            input_data = input.to_dict()
        elif isinstance(input, dict) or isinstance(input, str):
            input_data = input
        elif isinstance(input, Input):
            if input.input_format == InputFormat.CSV_ARCHIVE:
                raise ValueError("csv-archive is not supported")
            input_data = input.data

        input_size = 0
        if input_data is not None:
            input_size = get_size(input_data)

        upload_url_required = input_size > _MAX_RUN_SIZE
        upload_id_used = upload_id is not None

        if not upload_id_used and upload_url_required:
            upload_url = self.upload_url()
            self.upload_large_input(input=input_data, upload_url=upload_url)
            upload_id = upload_url.upload_id
            upload_id_used = True

        options_dict = {}
        if isinstance(input, Input) and input.options is not None:
            options_dict = input.options.to_dict_cloud()

        if options is not None:
            if isinstance(options, Options):
                options_dict = options.to_dict_cloud()
            elif isinstance(options, dict):
                for k, v in options.items():
                    if isinstance(v, str):
                        options_dict[k] = v
                    else:
                        options_dict[k] = json.dumps(v)

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
        if configuration is not None:
            configuration_dict = (
                configuration.to_dict() if isinstance(configuration, RunConfiguration) else configuration
            )
            payload["configuration"] = configuration_dict
        if batch_experiment_id is not None:
            payload["batch_experiment_id"] = batch_experiment_id
        if external_result is not None:
            external_dict = (
                external_result.to_dict() if isinstance(external_result, ExternalRunResult) else external_result
            )
            payload["result"] = external_dict

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
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        instance_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        upload_id: Optional[str] = None,
        run_options: Optional[Union[Options, dict[str, str]]] = None,
        polling_options: PollingOptions = _DEFAULT_POLLING_OPTIONS,
        configuration: Optional[Union[RunConfiguration, dict[str, any]]] = None,
        batch_experiment_id: Optional[str] = None,
        external_result: Optional[Union[ExternalRunResult, dict[str, any]]] = None,
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
            `dict`, `BaseModel` or `str`. If `nextmv.Input` is used, then the
            input is extracted from the `.data` property. Note that for now,
            `InputFormat.CSV_ARCHIVE` is not supported as an
            `input.input_format`. If an input is too large, it will be uploaded
            with the `upload_large_input` method.
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
        configuration: Optional[Union[RunConfiguration, dict[str, any]]]
            Configuration to use for the run. This can be a
            `cloud.RunConfiguration` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration.
        batch_experiment_id: Optional[str]
            ID of a batch experiment to associate the run with. This is used
            when the run is part of a batch experiment.
        external_result: Optional[Union[ExternalRunResult, dict[str, any]]]
            External result to use for the run. This can be a
            `cloud.ExternalRunResult` object or a dict. If the object is used,
            then the `.to_dict()` method is applied to extract the
            configuration. This is used when the run is an external run. We
            suggest that instead of specifying this parameter, you use the
            `track_run_with_result` method of the class.

        Returns
        ----------
        RunResult
            Result of the run.

        Raises
        ----------
            ValueError:
                If the `input` is of type `nextmv.Input` and the
                `.input_format` is not `JSON`.
                If the final `options` are not of type `dict[str,str]`.
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
            configuration=configuration,
            batch_experiment_id=batch_experiment_id,
            external_result=external_result,
        )

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
        )

    def new_scenario_test(
        self,
        id: str,
        name: str,
        scenarios: list[Scenario],
        description: Optional[str] = None,
        repetitions: Optional[int] = 0,
    ) -> str:
        """
        Create a new scenario test. The test is based on `scenarios` and you
        may specify `repetitions` to run the test multiple times. 0 repetitions
        means that the tests will be executed once. 1 repetition means that the
        test will be repeated once, i.e.: it will be executed twice. 2
        repetitions equals 3 executions, so on, and so forth.

        For each scenario, consider the `scenario_input` and `configuration`.
        The `scenario_input.scenario_input_type` allows you to specify the data
        that will be used for that scenario.

        - `ScenarioInputType.INPUT_SET`: the data should be taken from an
          existing input set.
        - `ScenarioInputType.INPUT`: the data should be taken from a list of
          existing inputs. When using this type, an input set will be created
          from this set of managed inputs.
        - `ScenarioInputType.New`: a new set of data will be uploaded as a set
          of managed inputs. A new input set will be created from this set of
          managed inputs.

        On the other hand, the `configuration` allows you to specify multiple
        option variations for the scenario. Please see the
        `ScenarioConfiguration` class for more information.

        The scenario tests uses the batch experiments API under the hood.

        Parameters
        ----------
        id: str
            ID of the scenario test.
        name: str
            Name of the scenario test.
        scenarios: list[Scenario]
            List of scenarios to use for the scenario test. At least one
            scenario should be provided.
        description: Optional[str]
            Optional description of the scenario test.
        repetitions: Optional[int]
            Number of repetitions to use for the scenario test. 0
            repetitions means that the tests will be executed once. 1
            repetition means that the test will be repeated once, i.e.: it
            will be executed twice. 2 repetitions equals 3 executions, so on,
            and so forth.

        Returns
        -------
        str
            ID of the scenario test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If no scenarios are provided.
        """

        if len(scenarios) < 1:
            raise ValueError("At least one scenario must be provided")

        scenarios_by_id = _scenarios_by_id(scenarios)

        # Save all the information needed by scenario.
        input_sets = {}
        instances = {}
        for scenario_id, scenario in scenarios_by_id.items():
            instance = self.instance(instance_id=scenario.instance_id)

            # Each scenario is associated to an input set, so we must either
            # get it or create it.
            input_set = self.__input_set_for_scenario(scenario, scenario_id)

            instances[scenario_id] = instance
            input_sets[scenario_id] = input_set

        # Calculate the combinations of all the option sets across scenarios.
        opt_sets_by_scenario = _option_sets(scenarios)

        # The scenario tests results in multiple individual runs.
        runs = []
        run_counter = 0
        opt_sets = {}
        for scenario_id, scenario_opt_sets in opt_sets_by_scenario.items():
            opt_sets = {**opt_sets, **scenario_opt_sets}
            input_set = input_sets[scenario_id]
            scenario = scenarios_by_id[scenario_id]

            for set_key in scenario_opt_sets.keys():
                inputs = input_set.input_ids if len(input_set.input_ids) > 0 else input_set.inputs
                for input in inputs:
                    input_id = input.id if isinstance(input, ManagedInput) else input
                    for repetition in range(repetitions + 1):
                        run_counter += 1
                        run = BatchExperimentRun(
                            input_id=input_id,
                            input_set_id=input_set.id,
                            instance_id=scenario.instance_id,
                            option_set=set_key,
                            scenario_id=scenario_id,
                            repetition=repetition,
                            run_number=f"{run_counter}",
                        )
                        runs.append(run)

        return self.new_batch_experiment(
            id=id,
            name=name,
            description=description,
            type="scenario",
            option_sets=opt_sets,
            runs=runs,
        )

    def new_secrets_collection(
        self,
        secrets: list[Secret],
        id: str,
        name: str,
        description: Optional[str] = None,
    ) -> SecretsCollectionSummary:
        """
        Create a new secrets collection. If no secrets are provided, a
        ValueError is raised.

        Args:
            secrets: List of secrets to use for the secrets collection. id: ID
            of the secrets collection. Will be generated if not provided.
            name: Name of the secrets collection. Will be generated if not
                provided.
            description: Description of the secrets collection. Will be
                generated if not provided.

        Returns:
            SecretsCollectionSummary: Summary of the secrets collection.

        Raises:
            ValueError: If no secrets are provided. requests.HTTPError: If the
            response status code is not 2xx.
        """

        if len(secrets) == 0:
            raise ValueError("secrets must be provided")

        payload = {
            "secrets": [secret.to_dict() for secret in secrets],
        }

        if id is not None:
            payload["id"] = id
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/secrets",
            payload=payload,
        )

        return SecretsCollectionSummary.from_dict(response.json())

    def new_version(
        self,
        id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        exist_ok: bool = False,
    ) -> Version:
        """
        Create a new version using the current dev binary.

        Args:
            id: ID of the version. Will be generated if not provided.
            name: Name of the version. Will be generated if not provided.
            description: Description of the version. Will be generated if not provided.
            exist_ok: If True and a version with the same ID already exists,
                return the existing version instead of creating a new one.

        Returns:
            Version.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        if exist_ok and id is None:
            raise ValueError("If exist_ok is True, id must be provided")

        if exist_ok and self.version_exists(version_id=id):
            return self.version(version_id=id)

        payload = {}

        if id is not None:
            payload["id"] = id
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/versions",
            payload=payload,
        )

        return Version.from_dict(response.json())

    def push(
        self,
        manifest: Optional[Manifest] = None,
        app_dir: Optional[str] = None,
        verbose: bool = False,
        model: Optional[Model] = None,
        model_configuration: Optional[ModelConfiguration] = None,
    ) -> None:
        """
        Push an app to Nextmv Cloud.

        If the manifest is not provided, an `app.yaml` file will be searched
        for in the provided path. If there is no manifest file found, an
        exception will be raised.

        There are two ways to push an app to Nextmv Cloud:
        1. Specifying `app_dir`, which is the path to an app’s root directory.
        This acts as an external strategy, where the app is composed of files
        in a directory and those apps are packaged and pushed to Nextmv Cloud.
        2. Specifying a `model` and `model_configuration`. This acts as an
        internal (or Python-native) strategy, where the app is actually a
        `nextmv.Model`. The model is encoded, some dependencies and
        accompanying files are packaged, and the app is pushed to Nextmv Cloud.

        Examples
        -------

        1. Push an app using an external strategy, i.e., specifying the app’s
        directory:
        ```python
        import os

        from nextmv import cloud

        client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        app.push()  # Use verbose=True for step-by-step output.
        ```

        2. Push an app using an internal strategy, i.e., specifying the model
        and model configuration:
        ```python
        import os

        import nextroute

        import nextmv
        import nextmv.cloud


        # Define the model that makes decisions. This model uses the Nextroute
        # library to solve a vehicle routing problem.
        class DecisionModel(nextmv.Model):
            def solve(self, input: nextmv.Input) -> nextmv.Output:
                nextroute_input = nextroute.schema.Input.from_dict(input.data)
                nextroute_options = nextroute.Options.extract_from_dict(input.options.to_dict())
                nextroute_output = nextroute.solve(nextroute_input, nextroute_options)

                return nextmv.Output(
                    options=input.options,
                    solution=nextroute_output.solutions[0].to_dict(),
                    statistics=nextroute_output.statistics.to_dict(),
                )


        # Define the options that the model needs.
        opt = []
        default_options = nextroute.Options()
        for name, default_value in default_options.to_dict().items():
            opt.append(nextmv.Option(name.lower(), type(default_value), default_value, name, False))

        options = nextmv.Options(*opt)

        # Instantiate the model and model configuration.
        model = DecisionModel()
        model_configuration = nextmv.ModelConfiguration(
            name="python_nextroute_model",
            requirements=[
                "nextroute==1.8.1",
                "nextmv==0.14.0.dev1",
            ],
            options=options,
        )

        # Define the Nextmv application and push the model to the cloud.
        client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        manifest = nextmv.cloud.default_python_manifest()
        app.push(
            manifest=manifest,
            verbose=True,
            model=model,
            model_configuration=model_configuration,
        )
        ```

        Parameters
        ----------
        manifest : Optional[Manifest], optional
            The manifest for the app, by default None.
        app_dir : Optional[str], optional
            The path to the app’s directory, by default None.
        verbose : bool, optional
            Whether to print verbose output, by default False.
        """

        if verbose:
            log("💽 Starting build for Nextmv application.")

        if app_dir is None or app_dir == "":
            app_dir = "."

        if manifest is None:
            manifest = Manifest.from_yaml(app_dir)

        if model is not None and not isinstance(model, Model):
            raise TypeError("model must be an instance of nextmv.Model")

        if model_configuration is not None and not isinstance(model_configuration, ModelConfiguration):
            raise TypeError("model_configuration must be an instance of nextmv.ModelConfiguration")

        if (model is None and model_configuration is not None) or (model is not None and model_configuration is None):
            raise ValueError("model and model_configuration must be provided together")

        package._run_build_command(app_dir, manifest.build, verbose)
        package._run_pre_push_command(app_dir, manifest.pre_push, verbose)
        tar_file, output_dir = package._package(app_dir, manifest, model, model_configuration, verbose)
        self.__update_app_binary(tar_file, manifest, verbose)

        try:
            shutil.rmtree(output_dir)
        except OSError as e:
            raise Exception(f"error deleting output directory: {e}") from e

    def run_input(self, run_id: str) -> dict[str, Any]:
        """
        Get the input of a run.

        Args:
            run_id: ID of the run.

        Returns:
            Input of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """
        run_information = self.run_metadata(run_id=run_id)

        query_params = None
        large = False
        if run_information.metadata.input_size > _MAX_RUN_SIZE:
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

        return download_response.json()

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

        info = RunInformation.from_dict(response.json())
        info.console_url = self.__console_url(info.id)

        return info

    def run_logs(self, run_id: str) -> RunLog:
        """
        Get the logs of a run.

        Args:
            run_id: ID of the run.

        Returns:
            Logs of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """
        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/runs/{run_id}/logs",
        )
        return RunLog.from_dict(response.json())

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

        return self.__run_result(run_id=run_id, run_information=run_information)

    def run_result_with_polling(
        self,
        run_id: str,
        polling_options: PollingOptions = _DEFAULT_POLLING_OPTIONS,
    ) -> RunResult:
        """
        Get the result of a run. The result includes the run output. This
        method polls for the result until the run finishes executing or the
        polling strategy is exhausted.

        Args:
            run_id: ID of the run.
            polling_options: Options to use when polling for the run result.

        Returns:
            Result of the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        def polling_func() -> tuple[any, bool]:
            run_information = self.run_metadata(run_id=run_id)
            if run_information.metadata.status_v2 in {
                StatusV2.succeeded,
                StatusV2.failed,
                StatusV2.canceled,
            }:
                return run_information, True

            return None, False

        run_information = poll(polling_options=polling_options, polling_func=polling_func)

        return self.__run_result(run_id=run_id, run_information=run_information)

    def scenario_test(self, scenario_test_id: str) -> BatchExperiment:
        """
        Get the scenario test. Scenario tests are based on batch experiments,
        so this function will return the corresponding batch experiment
        associated to the scenario test.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test.

        Returns
        -------
        BatchExperiment
            The scenario test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        return self.batch_experiment(batch_id=scenario_test_id)

    def track_run(self, tracked_run: TrackedRun, instance_id: Optional[str] = None) -> str:
        """
        Track an external run.

        This method allows you to register in Nextmv a run that happened
        elsewhere, as though it were executed in the Nextmv platform. Having
        information about a run in Nextmv is useful for things like
        experimenting and testing.

        Parameters
        ----------
        tracked_run : TrackedRun
            The run to track.
        instance_id: Optional[str]
            Optional instance ID if you want to associate your tracked run with
            an instance.

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
        """
        url_input = self.upload_url()

        upload_input = tracked_run.input
        if isinstance(tracked_run.input, Input):
            upload_input = tracked_run.input.data

        self.upload_large_input(input=upload_input, upload_url=url_input)

        url_output = self.upload_url()

        upload_output = tracked_run.output
        if isinstance(tracked_run.output, Output):
            upload_output = tracked_run.output.to_dict()

        self.upload_large_input(input=upload_output, upload_url=url_output)

        external_result = ExternalRunResult(
            output_upload_id=url_output.upload_id,
            status=tracked_run.status.value,
            execution_duration=tracked_run.duration,
        )

        if tracked_run.logs is not None:
            url_stderr = self.upload_url()
            self.upload_large_input(input=tracked_run.logs_text(), upload_url=url_stderr)
            external_result.error_upload_id = url_stderr.upload_id

        if tracked_run.error is not None and tracked_run.error != "":
            external_result.error_message = tracked_run.error

        return self.new_run(
            upload_id=url_input.upload_id,
            external_result=external_result,
            instance_id=instance_id,
        )

    def track_run_with_result(
        self,
        tracked_run: TrackedRun,
        polling_options: PollingOptions = _DEFAULT_POLLING_OPTIONS,
        instance_id: Optional[str] = None,
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
        run_id = self.track_run(tracked_run=tracked_run, instance_id=instance_id)

        return self.run_result_with_polling(
            run_id=run_id,
            polling_options=polling_options,
        )

    def update_instance(
        self,
        id: str,
        name: str,
        version_id: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[InstanceConfiguration] = None,
    ) -> Instance:
        """
        Update an instance.

        Args:
            id: ID of the instance to update.
            version_id: ID of the version to associate the instance with.
            name: Name of the instance.
            description: Description of the instance.
            configuration: Configuration to use for the instance.

        Returns:
            Instance.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        payload = {}

        if version_id is not None:
            payload["version_id"] = version_id
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if configuration is not None:
            payload["configuration"] = configuration.to_dict()

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/instances/{id}",
            payload=payload,
        )

        return Instance.from_dict(response.json())

    def update_batch_experiment(
        self,
        batch_experiment_id: str,
        name: str,
        description: str,
    ) -> BatchExperimentInformation:
        """
        Update a batch experiment.

        Parameters
        ----------
        batch_experiment_id : str
            ID of the batch experiment to update.
        name : str
            Name of the batch experiment.
        description : str
            Description of the batch experiment.

        Returns
        -------
        BatchExperimentInformation
            The information with the updated batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {
            "name": name,
            "description": description,
        }
        response = self.client.request(
            method="PATCH",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_experiment_id}",
            payload=payload,
        )

        return BatchExperimentInformation.from_dict(response.json())

    def update_managed_input(
        self,
        managed_input_id: str,
        name: str,
        description: str,
    ) -> None:
        """
        Update a managed input.

        Parameters
        ----------
        managed_input_id : str
            ID of the managed input to update.
        name : str
            Name of the managed input.
        description : str
            Description of the managed input.

        Returns
        -------
        None
            No return value.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {
            "name": name,
            "description": description,
        }
        _ = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
            payload=payload,
        )

    def update_scenario_test(
        self,
        scenario_test_id: str,
        name: str,
        description: str,
    ) -> BatchExperimentInformation:
        """
        Update a scenario test. Scenario tests use the batch experiments API,
        so this method calls the `update_batch_experiment` method, and thus the
        return type is the same.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to update.
        name : str
            Name of the scenario test.
        description : str
            Description of the scenario test.

        Returns
        -------
        BatchExperimentInformation
            The information with the updated scenario test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        return self.update_batch_experiment(
            batch_experiment_id=scenario_test_id,
            name=name,
            description=description,
        )

    def update_secrets_collection(
        self,
        secrets_collection_id: str,
        name: str,
        description: str,
        secrets: list[Secret],
    ) -> SecretsCollectionSummary:
        """
        Update a secrets collection.

        Args:
            secrets_collection_id: ID of the secrets collection.
            name: Name of the secrets collection.
            description: Description of the secrets collection.
            secrets: List of secrets to update.

        Returns:
            SecretsCollection.

        Raises:
            ValueError: If no secrets are provided.
            requests.HTTPError: If the response status code is not 2xx.
        """

        if len(secrets) == 0:
            raise ValueError("secrets must be provided")

        payload = {
            "name": name,
            "description": description,
            "secrets": [secret.to_dict() for secret in secrets],
        }
        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
            payload=payload,
        )

        return SecretsCollectionSummary.from_dict(response.json())

    def upload_large_input(
        self,
        input: Union[dict[str, Any], str],
        upload_url: UploadURL,
    ) -> None:
        """
        Upload the file located at the given path to the provided upload URL.

        Args:
            upload_url: Upload URL to use for uploading the file.
            input: Input to use for the run.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        if isinstance(input, dict):
            input = json.dumps(input)

        self.client.upload_to_presigned_url(
            url=upload_url.upload_url,
            data=input,
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

    def secrets_collection(self, secrets_collection_id: str) -> SecretsCollection:
        """
        Get a secrets collection.

        Args:
            secrets_collection_id: ID of the secrets collection.

        Returns:
            SecretsCollection.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

        return SecretsCollection.from_dict(response.json())

    def version(self, version_id: str) -> Version:
        """
        Get a version.

        Args:
            version_id: ID of the version.

        Returns:
            Version.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions/{version_id}",
        )

        return Version.from_dict(response.json())

    def version_exists(self, version_id: str) -> bool:
        """
        Check if a version exists.

        Args:
            version_id: ID of the version.

        Returns:
            bool: True if the version exists, False otherwise.
        """

        try:
            self.version(version_id=version_id)
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            raise e

    def __run_result(
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
        result = RunResult.from_dict(response.json())
        result.console_url = self.__console_url(result.id)

        if not large_output:
            return result

        download_url = DownloadURL.from_dict(response.json()["output"])
        download_response = self.client.request(
            method="GET",
            endpoint=download_url.url,
            headers={"Content-Type": "application/json"},
        )
        result.output = download_response.json()

        return result

    def __update_app_binary(
        self,
        tar_file: str,
        manifest: Manifest,
        verbose: bool = False,
    ) -> None:
        """Updates the application binary in Cloud."""

        if verbose:
            log(f'🌟 Pushing to application: "{self.id}".')

        endpoint = f"{self.endpoint}/binary"
        response = self.client.request(
            method="GET",
            endpoint=endpoint,
        )
        upload_url = response.json()["upload_url"]

        with open(tar_file, "rb") as f:
            response = self.client.request(
                method="PUT",
                endpoint=upload_url,
                data=f,
                headers={"Content-Type": "application/octet-stream"},
            )

        activation_request = {
            "requirements": {
                "executable_type": manifest.type,
                "runtime": manifest.runtime,
            },
        }
        response = self.client.request(
            method="PUT",
            endpoint=endpoint,
            payload=activation_request,
        )

        if verbose:
            log(f'💥️ Successfully pushed to application: "{self.id}".')
            log(
                json.dumps(
                    {
                        "app_id": self.id,
                        "endpoint": self.client.url,
                        "instance_url": f"{self.endpoint}/runs?instance_id=devint",
                    },
                    indent=2,
                )
            )

    def __console_url(self, run_id: str) -> str:
        """Auxiliary method to get the console URL for a run."""

        return f"{self.client.console_url}/app/{self.id}/run/{run_id}?view=details"

    def __input_set_for_scenario(self, scenario: Scenario, scenario_id: str) -> InputSet:
        # If working with an input set, there is no need to create one.
        if scenario.scenario_input.scenario_input_type == ScenarioInputType.INPUT_SET:
            input_set = self.input_set(input_set_id=scenario.scenario_input.scenario_input_data)
            return input_set

        # If working with a list of managed inputs, we need to create an
        # input set.
        if scenario.scenario_input.scenario_input_type == ScenarioInputType.INPUT:
            name, id = name_and_id(prefix="inpset", entity_id=scenario_id)
            input_set = self.new_input_set(
                id=id,
                name=name,
                description=f"Automatically created from scenario test: {id}",
                maximum_runs=20,
                inputs=[
                    ManagedInput.from_dict(data={"id": input_id})
                    for input_id in scenario.scenario_input.scenario_input_data
                ],
            )
            return input_set

        # If working with new data, we need to create managed inputs, and then,
        # an input set.
        if scenario.scenario_input.scenario_input_type == ScenarioInputType.NEW:
            managed_inputs = []
            for data in scenario.scenario_input.scenario_input_data:
                upload_url = self.upload_url()
                self.upload_large_input(input=data, upload_url=upload_url)
                name, id = name_and_id(prefix="man-input", entity_id=scenario_id)
                managed_input = self.new_managed_input(
                    id=id,
                    name=name,
                    description=f"Automatically created from scenario test: {id}",
                    upload_id=upload_url.upload_id,
                )
                managed_inputs.append(managed_input)

            name, id = name_and_id(prefix="inpset", entity_id=scenario_id)
            input_set = self.new_input_set(
                id=id,
                name=name,
                description=f"Automatically created from scenario test: {id}",
                maximum_runs=20,
                inputs=managed_inputs,
            )
            return input_set

        raise ValueError(f"Unknown scenario input type: {scenario.scenario_input.scenario_input_type}")


def poll(polling_options: PollingOptions, polling_func: Callable[[], tuple[any, bool]]) -> any:
    """
    Auxiliary function for polling.

    The `polling_func` is a callable that must return a `tuple[any, bool]`
    where the first element is the result of the polling and the second
    element is a boolean indicating if the polling was successful or should be
    retried.

    This function will return the result of the `polling_func` if the polling
    process is successful, otherwise it will raise a `TimeoutError` or
    `RuntimeError` depending on the situation.

    Parameters
    ----------
    polling_options : PollingOptions
        Options for the polling process.
    polling_func : callable
        Function to call to check if the polling was successful.

    Returns
    -------
    any
        Result of the polling function.
    """

    # Start by sleeping for the duration specified as initial delay.
    if polling_options.verbose:
        log(f"polling | sleeping for initial delay: {polling_options.initial_delay}")

    time.sleep(polling_options.initial_delay)

    start_time = time.time()
    stopped = False

    # Begin the polling process.
    for ix in range(polling_options.max_tries):
        # Check is we should stop polling according to the stop callback.
        if polling_options.stop is not None and polling_options.stop():
            stopped = True

            break

        # We check if we can stop polling.
        result, ok = polling_func()
        if polling_options.verbose:
            log(f"polling | try # {ix + 1}, ok: {ok}")

        if ok:
            return result

        # An exit condition happens if we exceed the allowed duration.
        passed = time.time() - start_time
        if polling_options.verbose:
            log(f"polling | elapsed time: {passed}")

        if passed >= polling_options.max_duration:
            raise TimeoutError(
                f"polling did not succeed after {passed} seconds, exceeds max duration: {polling_options.max_duration}",
            )

        # Calculate the delay.
        delay = polling_options.delay  # Base
        delay += polling_options.backoff * (2**ix)  # Add exponential backoff.
        delay += random.uniform(0, polling_options.jitter)  # Add jitter.

        # Sleep for the calculated delay. We cannot exceed the max delay.
        sleep_duration = min(delay, polling_options.max_delay)
        if polling_options.verbose:
            log(f"polling | sleeping for duration: {sleep_duration}")

        time.sleep(sleep_duration)

    if stopped:
        log("polling | stop condition met, stopping polling")

        return None

    raise RuntimeError(
        f"polling did not succeed after {polling_options.max_tries} tries",
    )


def _is_not_exist_error(e: requests.HTTPError) -> bool:
    """
    Check if the error is a known 404 Not Found error.

    Args:
        e: HTTPError to check.

    Returns:
        True if the error is a 404 Not Found error, False otherwise.
    """
    if (
        # Check whether the error is caused by a 404 status code - meaning the app does not exist.
        (hasattr(e, "response") and hasattr(e.response, "status_code") and e.response.status_code == 404)
        or
        # Check a possibly nested exception as well.
        (
            hasattr(e, "__cause__")
            and hasattr(e.__cause__, "response")
            and hasattr(e.__cause__.response, "status_code")
            and e.__cause__.response.status_code == 404
        )
    ):
        return True
    return False
