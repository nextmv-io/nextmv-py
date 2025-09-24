"""
Application module for interacting with Nextmv Cloud applications.

This module provides functionality to interact with applications in Nextmv Cloud,
including application management, running applications, and managing experiments
and inputs.

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
import tarfile
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Union

import requests

from nextmv._serialization import deflated_serialize_json
from nextmv.base_model import BaseModel
from nextmv.cloud import package
from nextmv.cloud.acceptance_test import AcceptanceTest, Metric
from nextmv.cloud.batch_experiment import (
    BatchExperiment,
    BatchExperimentInformation,
    BatchExperimentMetadata,
    BatchExperimentRun,
    ExperimentStatus,
    to_runs,
)
from nextmv.cloud.client import Client, get_size
from nextmv.cloud.input_set import InputSet, ManagedInput
from nextmv.cloud.instance import Instance, InstanceConfiguration
from nextmv.cloud.scenario import Scenario, ScenarioInputType, _option_sets, _scenarios_by_id
from nextmv.cloud.secrets import Secret, SecretsCollection, SecretsCollectionSummary
from nextmv.cloud.url import DownloadURL, UploadURL
from nextmv.cloud.version import Version
from nextmv.input import Input, InputFormat
from nextmv.logger import log
from nextmv.manifest import Manifest
from nextmv.model import Model, ModelConfiguration
from nextmv.options import Options
from nextmv.output import Output, OutputFormat
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.run import (
    ExternalRunResult,
    Format,
    FormatInput,
    FormatOutput,
    RunConfiguration,
    RunInformation,
    RunLog,
    RunResult,
    TrackedRun,
)
from nextmv.safe import safe_id, safe_name_and_id
from nextmv.status import StatusV2

# Maximum size of the run input/output in bytes. This constant defines the
# maximum allowed size for run inputs and outputs. When the size exceeds this
# value, the system will automatically use the large input upload and/or large
# result download endpoints.
_MAX_RUN_SIZE: int = 5 * 1024 * 1024


@dataclass
class Application:
    """
    A published decision model that can be executed.

    You can import the `Application` class directly from `cloud`:

    ```python
    from nextmv.cloud import Application
    ```

    This class represents an application in Nextmv Cloud, providing methods to
    interact with the application, run it with different inputs, manage versions,
    instances, experiments, and more.

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    id : str
        ID of the application.
    default_instance_id : str, default=None
        Default instance ID to use for submitting runs.
    endpoint : str, default="v1/applications/{id}"
        Base endpoint for the application.
    experiments_endpoint : str, default="{base}/experiments"
        Base endpoint for the experiments in the application.

    Examples
    --------
    >>> from nextmv.cloud import Client, Application
    >>> client = Client(api_key="your-api-key")
    >>> app = Application(client=client, id="your-app-id")
    >>> # Retrieve app information
    >>> instances = app.list_instances()
    """

    client: Client
    """Client to use for interacting with the Nextmv Cloud API."""
    id: str
    """ID of the application."""

    default_instance_id: str = None
    """Default instance ID to use for submitting runs."""
    endpoint: str = "v1/applications/{id}"
    """Base endpoint for the application."""
    experiments_endpoint: str = "{base}/experiments"
    """Base endpoint for the experiments in the application."""

    def __post_init__(self):
        """Initialize the endpoint and experiments_endpoint attributes.

        This method is automatically called after class initialization to
        format the endpoint and experiments_endpoint URLs with the application ID.
        """
        self.endpoint = self.endpoint.format(id=self.id)
        self.experiments_endpoint = self.experiments_endpoint.format(base=self.endpoint)

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
        Create a new application directly in Nextmv Cloud.

        The application is created as an empty shell, and executable code must
        be pushed to the app before running it remotely.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        name : str
            Name of the application.
        id : str, optional
            ID of the application. Will be generated if not provided.
        description : str, optional
            Description of the application.
        is_workflow : bool, optional
            Whether the application is a Decision Workflow.
        exist_ok : bool, default=False
            If True and an application with the same ID already exists,
            return the existing application instead of creating a new one.

        Returns
        -------
        Application
            The newly created (or existing) application.

        Examples
        --------
        >>> from nextmv.cloud import Client
        >>> client = Client(api_key="your-api-key")
        >>> app = Application.new(client=client, name="My New App", id="my-app")
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

    def acceptance_test(self, acceptance_test_id: str) -> AcceptanceTest:
        """
        Retrieve details of an acceptance test.

        Parameters
        ----------
        acceptance_test_id : str
            ID of the acceptance test to retrieve.

        Returns
        -------
        AcceptanceTest
            The requested acceptance test details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> test = app.acceptance_test("test-123")
        >>> print(test.name)
        'My Test'
        """
        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/acceptance/{acceptance_test_id}",
        )

        return AcceptanceTest.from_dict(response.json())

    def acceptance_test_with_polling(
        self,
        acceptance_test_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> AcceptanceTest:
        """
        Retrieve details of an acceptance test using polling.

        Retrieves the result of an acceptance test. This method polls for the
        result until the test finishes executing or the polling strategy is
        exhausted.

        Parameters
        ----------
        acceptance_test_id : str
            ID of the acceptance test to retrieve.

        Returns
        -------
        AcceptanceTest
            The requested acceptance test details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> test = app.acceptance_test_with_polling("test-123")
        >>> print(test.name)
        'My Test'
        """

        def polling_func() -> tuple[Any, bool]:
            acceptance_test_result = self.acceptance_test(acceptance_test_id=acceptance_test_id)
            if acceptance_test_result.status in {
                ExperimentStatus.COMPLETED,
                ExperimentStatus.FAILED,
                ExperimentStatus.DRAFT,
                ExperimentStatus.CANCELED,
                ExperimentStatus.DELETE_FAILED,
            }:
                return acceptance_test_result, True

            return None, False

        acceptance_test = poll(polling_options=polling_options, polling_func=polling_func)

        return self.acceptance_test(acceptance_test_id=acceptance_test.id)

    def batch_experiment(self, batch_id: str) -> BatchExperiment:
        """
        Get a batch experiment.

        Parameters
        ----------
        batch_id : str
            ID of the batch experiment.

        Returns
        -------
        BatchExperiment
            The requested batch experiment details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> batch_exp = app.batch_experiment("batch-123")
        >>> print(batch_exp.name)
        'My Batch Experiment'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}",
        )

        return BatchExperiment.from_dict(response.json())

    def batch_experiment_metadata(self, batch_id: str) -> BatchExperimentMetadata:
        """
        Get metadata for a batch experiment.

        Parameters
        ----------
        batch_id : str
            ID of the batch experiment.

        Returns
        -------
        BatchExperimentMetadata
            The requested batch experiment metadata.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> metadata = app.batch_experiment_metadata("batch-123")
        >>> print(metadata.name)
        'My Batch Experiment'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}/metadata",
        )

        return BatchExperimentMetadata.from_dict(response.json())

    def batch_experiment_with_polling(
        self,
        batch_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> BatchExperiment:
        """
        Get a batch experiment with polling.

        Retrieves the result of an experiment. This method polls for the result
        until the experiment finishes executing or the polling strategy is
        exhausted.

        Parameters
        ----------
        batch_id : str
            ID of the batch experiment.

        Returns
        -------
        BatchExperiment
            The requested batch experiment details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> batch_exp = app.batch_experiment_with_polling("batch-123")
        >>> print(batch_exp.name)
        'My Batch Experiment'
        """

        def polling_func() -> tuple[Any, bool]:
            batch_metadata = self.batch_experiment_metadata(batch_id=batch_id)
            if batch_metadata.status in {
                ExperimentStatus.COMPLETED,
                ExperimentStatus.FAILED,
                ExperimentStatus.DRAFT,
                ExperimentStatus.CANCELED,
                ExperimentStatus.DELETE_FAILED,
            }:
                return batch_metadata, True

            return None, False

        batch_information = poll(polling_options=polling_options, polling_func=polling_func)

        return self.batch_experiment(batch_id=batch_information.id)

    def cancel_run(self, run_id: str) -> None:
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

    def delete(self) -> None:
        """
        Delete the application.

        Permanently removes the application from Nextmv Cloud.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete()  # Permanently deletes the application
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=self.endpoint,
        )

    def delete_acceptance_test(self, acceptance_test_id: str) -> None:
        """
        Delete an acceptance test.

        Deletes an acceptance test along with all the associated information
        such as the underlying batch experiment.

        Parameters
        ----------
        acceptance_test_id : str
            ID of the acceptance test to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_acceptance_test("test-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/acceptance/{acceptance_test_id}",
        )

    def delete_batch_experiment(self, batch_id: str) -> None:
        """
        Delete a batch experiment.

        Deletes a batch experiment along with all the associated information,
        such as its runs.

        Parameters
        ----------
        batch_id : str
            ID of the batch experiment to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_batch_experiment("batch-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}",
        )

    def delete_scenario_test(self, scenario_test_id: str) -> None:
        """
        Delete a scenario test.

        Deletes a scenario test. Scenario tests are based on the batch
        experiments API, so this function summons `delete_batch_experiment`.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_scenario_test("scenario-123")
        """

        self.delete_batch_experiment(batch_id=scenario_test_id)

    def delete_secrets_collection(self, secrets_collection_id: str) -> None:
        """
        Delete a secrets collection.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_secrets_collection("secrets-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

    @staticmethod
    def exists(client: Client, id: str) -> bool:
        """
        Check if an application exists.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        id : str
            ID of the application to check.

        Returns
        -------
        bool
            True if the application exists, False otherwise.

        Examples
        --------
        >>> from nextmv.cloud import Client
        >>> client = Client(api_key="your-api-key")
        >>> Application.exists(client, "app-123")
        True
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

        Parameters
        ----------
        input_set_id : str
            ID of the input set to retrieve.

        Returns
        -------
        InputSet
            The requested input set.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> input_set = app.input_set("input-set-123")
        >>> print(input_set.name)
        'My Input Set'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/inputsets/{input_set_id}",
        )

        return InputSet.from_dict(response.json())

    def instance(self, instance_id: str) -> Instance:
        """
        Get an instance.

        Parameters
        ----------
        instance_id : str
            ID of the instance to retrieve.

        Returns
        -------
        Instance
            The requested instance details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> instance = app.instance("instance-123")
        >>> print(instance.name)
        'Production Instance'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/instances/{instance_id}",
        )

        return Instance.from_dict(response.json())

    def instance_exists(self, instance_id: str) -> bool:
        """
        Check if an instance exists.

        Parameters
        ----------
        instance_id : str
            ID of the instance to check.

        Returns
        -------
        bool
            True if the instance exists, False otherwise.

        Examples
        --------
        >>> app.instance_exists("instance-123")
        True
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

        Returns
        -------
        list[AcceptanceTest]
            List of all acceptance tests associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> tests = app.list_acceptance_tests()
        >>> for test in tests:
        ...     print(test.name)
        'Test 1'
        'Test 2'
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

        Returns
        -------
        list[InputSet]
            List of all input sets associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> input_sets = app.list_input_sets()
        >>> for input_set in input_sets:
        ...     print(input_set.name)
        'Input Set 1'
        'Input Set 2'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/inputsets",
        )

        return [InputSet.from_dict(input_set) for input_set in response.json()]

    def list_instances(self) -> list[Instance]:
        """
        List all instances.

        Returns
        -------
        list[Instance]
            List of all instances associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> instances = app.list_instances()
        >>> for instance in instances:
        ...     print(instance.name)
        'Development Instance'
        'Production Instance'
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

        Returns
        -------
        list[SecretsCollectionSummary]
            List of all secrets collections associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> collections = app.list_secrets_collections()
        >>> for collection in collections:
        ...     print(collection.name)
        'API Keys'
        'Database Credentials'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets",
        )

        return [SecretsCollectionSummary.from_dict(secrets) for secrets in response.json()["items"]]

    def list_versions(self) -> list[Version]:
        """
        List all versions.

        Returns
        -------
        list[Version]
            List of all versions associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> versions = app.list_versions()
        >>> for version in versions:
        ...     print(version.name)
        'v1.0.0'
        'v1.1.0'
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
        Create a new acceptance test.

        The acceptance test is based on a batch experiment. If you already
        started a batch experiment, you don't need to provide the input_set_id
        parameter. In that case, the ID of the acceptance test and the batch
        experiment must be the same. If the batch experiment does not exist,
        you can provide the input_set_id parameter and a new batch experiment
        will be created for you.

        Parameters
        ----------
        candidate_instance_id : str
            ID of the candidate instance.
        baseline_instance_id : str
            ID of the baseline instance.
        id : str
            ID of the acceptance test.
        metrics : list[Union[Metric, dict[str, Any]]]
            List of metrics to use for the acceptance test.
        name : str
            Name of the acceptance test.
        input_set_id : Optional[str], default=None
            ID of the input set to use for the underlying batch experiment,
            in case it hasn't been started.
        description : Optional[str], default=None
            Description of the acceptance test.

        Returns
        -------
        AcceptanceTest
            The created acceptance test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If the batch experiment ID does not match the acceptance test ID.
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
            # Get all input IDs from the input set.
            input_set = self.input_set(input_set_id=input_set_id)
            if not input_set.input_ids:
                raise ValueError(f"input set {input_set_id} does not contain any inputs")
            runs = []
            for input_id in input_set.input_ids:
                runs.append(
                    BatchExperimentRun(
                        instance_id=candidate_instance_id,
                        input_set_id=input_set_id,
                        input_id=input_id,
                    )
                )
                runs.append(
                    BatchExperimentRun(
                        instance_id=baseline_instance_id,
                        input_set_id=input_set_id,
                        input_id=input_id,
                    )
                )
            batch_experiment_id = self.new_batch_experiment(
                name=name,
                description=description,
                id=id,
                runs=runs,
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
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> AcceptanceTest:
        """
        Create a new acceptance test and poll for the result.

        This is a convenience method that combines the new_acceptance_test with polling
        logic to check when the acceptance test is done.

        Parameters
        ----------
        candidate_instance_id : str
            ID of the candidate instance.
        baseline_instance_id : str
            ID of the baseline instance.
        id : str
            ID of the acceptance test.
        metrics : list[Union[Metric, dict[str, Any]]]
            List of metrics to use for the acceptance test.
        name : str
            Name of the acceptance test.
        input_set_id : Optional[str], default=None
            ID of the input set to use for the underlying batch experiment,
            in case it hasn't been started.
        description : Optional[str], default=None
            Description of the acceptance test.
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the acceptance test result.

        Returns
        -------
        AcceptanceTest
            The completed acceptance test with results.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        TimeoutError
            If the acceptance test does not succeed after the
            polling strategy is exhausted based on time duration.
        RuntimeError
            If the acceptance test does not succeed after the
            polling strategy is exhausted based on number of tries.

        Examples
        --------
        >>> test = app.new_acceptance_test_with_result(
        ...     candidate_instance_id="candidate-123",
        ...     baseline_instance_id="baseline-456",
        ...     id="test-789",
        ...     metrics=[Metric(name="objective", type="numeric")],
        ...     name="Performance Test",
        ...     input_set_id="input-set-123"
        ... )
        >>> print(test.status)
        'completed'
        """

        acceptance_test = self.new_acceptance_test(
            candidate_instance_id=candidate_instance_id,
            baseline_instance_id=baseline_instance_id,
            id=id,
            metrics=metrics,
            name=name,
            input_set_id=input_set_id,
            description=description,
        )

        return self.acceptance_test_with_polling(
            acceptance_test_id=acceptance_test.id,
            polling_options=polling_options,
        )

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
            This argument is deprecated, use `runs` instead.
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
            input_set = self.input_set(input_set_id)
            runs = to_runs(instance_ids, input_set)
            payload_runs = [run.to_dict() for run in runs]
            payload["runs"] = payload_runs
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

    def new_batch_experiment_with_result(
        self,
        name: str,
        input_set_id: Optional[str] = None,
        instance_ids: Optional[list[str]] = None,
        description: Optional[str] = None,
        id: Optional[str] = None,
        option_sets: Optional[dict[str, dict[str, str]]] = None,
        runs: Optional[list[Union[BatchExperimentRun, dict[str, Any]]]] = None,
        type: Optional[str] = "batch",
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> BatchExperiment:
        """
        Convenience method to create a new batch experiment and poll for the
        result.

        This method combines the `new_batch_experiment` and
        `batch_experiment_with_polling` methods, applying polling logic to
        check when the experiment succeeded.

        Parameters
        ----------
        name: str
            Name of the batch experiment.
        input_set_id: str
            ID of the input set to use for the batch experiment.
        instance_ids: list[str]
            List of instance IDs to use for the batch experiment. This argument
            is deprecated, use `runs` instead.
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
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the batch experiment result.

        Returns
        -------
        BatchExperiment
            The completed batch experiment with results.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        batch_id = self.new_batch_experiment(
            name=name,
            input_set_id=input_set_id,
            instance_ids=instance_ids,
            description=description,
            id=id,
            option_sets=option_sets,
            runs=runs,
            type=type,
        )

        return self.batch_experiment_with_polling(batch_id=batch_id, polling_options=polling_options)

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
            the application's `default_instance_id` is used.
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

        This method creates a new instance associated with a specific version of the application.
        Instances are configurations of an application version that can be executed.

        Parameters
        ----------
        version_id : str
            ID of the version to associate the instance with.
        id : str
            ID of the instance. Will be generated if not provided.
        name : str
            Name of the instance. Will be generated if not provided.
        description : Optional[str], default=None
            Description of the instance.
        configuration : Optional[InstanceConfiguration], default=None
            Configuration to use for the instance. This can include resources,
            timeouts, and other execution parameters.
        exist_ok : bool, default=False
            If True and an instance with the same ID already exists,
            return the existing instance instead of creating a new one.

        Returns
        -------
        Instance
            The newly created (or existing) instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If exist_ok is True and id is None.

        Examples
        --------
        >>> # Create a new instance for a specific version
        >>> instance = app.new_instance(
        ...     version_id="version-123",
        ...     id="prod-instance",
        ...     name="Production Instance",
        ...     description="Instance for production use"
        ... )
        >>> print(instance.name)
        'Production Instance'
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
        format: Optional[Union[Format, dict[str, Any]]] = None,
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
            payload["format"] = Format(
                format_input=FormatInput(input_type=InputFormat.JSON),
                format_output=FormatOutput(output_type=OutputFormat.JSON),
            ).to_dict()

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
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
        batch_experiment_id: Optional[str] = None,
        external_result: Optional[Union[ExternalRunResult, dict[str, Any]]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
        input_dir_path: Optional[str] = None,
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
            `upload_large_input` method. If both the `input_dir_path` and `input`
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
            `upload_large_input` method.
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
            `cloud.ExternalRunResult` object or a dict. If the object is used,
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

        self.__validate_input_dir_path_and_configuration(input_dir_path, configuration)

        tar_file = ""
        if input_dir_path is not None and input_dir_path != "":
            if not os.path.exists(input_dir_path):
                raise ValueError(f"Directory {input_dir_path} does not exist.")

            if not os.path.isdir(input_dir_path):
                raise ValueError(f"Path {input_dir_path} is not a directory.")

            tar_file = self.__package_inputs(input_dir_path)

        input_data = self.__extract_input_data(input)

        input_size = 0
        if input_data is not None:
            input_size = get_size(input_data)

        upload_id_used = upload_id is not None
        if self.__upload_url_required(upload_id_used, input_size, tar_file, input):
            upload_url = self.upload_url()
            self.upload_large_input(input=input_data, upload_url=upload_url, tar_file=tar_file)
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
        self,
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
        instance_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        upload_id: Optional[str] = None,
        run_options: Optional[Union[Options, dict[str, str]]] = None,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
        batch_experiment_id: Optional[str] = None,
        external_result: Optional[Union[ExternalRunResult, dict[str, Any]]] = None,
        json_configurations: Optional[dict[str, Any]] = None,
        input_dir_path: Optional[str] = None,
        output_dir_path: Optional[str] = ".",
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
            `upload_large_input` method. If both the `input_dir_path` and `input`
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
            `upload_large_input` method.
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

    def new_scenario_test_with_result(
        self,
        id: str,
        name: str,
        scenarios: list[Scenario],
        description: Optional[str] = None,
        repetitions: Optional[int] = 0,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> BatchExperiment:
        """
        Convenience method to create a new scenario test and poll for the
        result.

        This method combines the `new_scenario_test` and
        `scenario_test_with_polling` methods, applying polling logic to
        check when the test succeeded.

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
        BatchExperiment
            The completed scenario test as a BatchExperiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If no scenarios are provided.
        """

        test_id = self.new_scenario_test(
            id=id,
            name=name,
            scenarios=scenarios,
            description=description,
            repetitions=repetitions,
        )

        return self.scenario_test_with_polling(
            scenario_test_id=test_id,
            polling_options=polling_options,
        )

    def new_secrets_collection(
        self,
        secrets: list[Secret],
        id: str,
        name: str,
        description: Optional[str] = None,
    ) -> SecretsCollectionSummary:
        """
        Create a new secrets collection.

        This method creates a new secrets collection with the provided secrets.
        A secrets collection is a group of key-value pairs that can be used by
        your application instances during execution. If no secrets are provided,
        a ValueError is raised.

        Parameters
        ----------
        secrets : list[Secret]
            List of secrets to use for the secrets collection. Each secret
            should be an instance of the Secret class containing a key and value.
        id : str
            ID of the secrets collection.
        name : str
            Name of the secrets collection.
        description : Optional[str], default=None
            Description of the secrets collection.

        Returns
        -------
        SecretsCollectionSummary
            Summary of the secrets collection including its metadata.

        Raises
        ------
        ValueError
            If no secrets are provided.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Create a new secrets collection with API keys
        >>> from nextmv.cloud import Secret
        >>> secrets = [
        ...     Secret(
        ...          location="API_KEY",
        ...          value="your-api-key",
        ...          secret_type=SecretType.ENV,
        ...     ),
        ...     Secret(
        ...          location="DATABASE_URL",
        ...          value="your-database-url",
        ...          secret_type=SecretType.ENV,
        ...     ),
        ... ]
        >>> collection = app.new_secrets_collection(
        ...     secrets=secrets,
        ...     id="api-secrets",
        ...     name="API Secrets",
        ...     description="Collection of API secrets for external services"
        ... )
        >>> print(collection.id)
        'api-secrets'
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

        This method creates a new version of the application using the current development
        binary. Application versions represent different iterations of your application's
        code and configuration that can be deployed.

        Parameters
        ----------
        id : Optional[str], default=None
            ID of the version. If not provided, a unique ID will be generated.
        name : Optional[str], default=None
            Name of the version. If not provided, a name will be generated.
        description : Optional[str], default=None
            Description of the version. If not provided, a description will be generated.
        exist_ok : bool, default=False
            If True and a version with the same ID already exists,
            return the existing version instead of creating a new one.
            If True, the 'id' parameter must be provided.

        Returns
        -------
        Version
            The newly created (or existing) version.

        Raises
        ------
        ValueError
            If exist_ok is True and id is None.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Create a new version
        >>> version = app.new_version(
        ...     id="v1.0.0",
        ...     name="Initial Release",
        ...     description="First stable version"
        ... )
        >>> print(version.id)
        'v1.0.0'

        >>> # Get or create a version with exist_ok
        >>> version = app.new_version(
        ...     id="v1.0.0",
        ...     exist_ok=True
        ... )
        """

        if exist_ok and id is None:
            raise ValueError("If exist_ok is True, id must be provided")

        if exist_ok and self.version_exists(version_id=id):
            return self.version(version_id=id)

        if id is None:
            id = safe_id(prefix="version")

        payload = {
            "id": id,
        }

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
        1. Specifying `app_dir`, which is the path to an app's root directory.
        This acts as an external strategy, where the app is composed of files
        in a directory and those apps are packaged and pushed to Nextmv Cloud.
        2. Specifying a `model` and `model_configuration`. This acts as an
        internal (or Python-native) strategy, where the app is actually a
        `nextmv.Model`. The model is encoded, some dependencies and
        accompanying files are packaged, and the app is pushed to Nextmv Cloud.

        Parameters
        ----------
        manifest : Optional[Manifest], default=None
            The manifest for the app. If None, an `app.yaml` file in the provided
            app directory will be used.
        app_dir : Optional[str], default=None
            The path to the app's root directory. If None, the current directory
            will be used. This is for the external strategy approach.
        verbose : bool, default=False
            Whether to print verbose output during the push process.
        model : Optional[Model], default=None
            The Python-native model to push. Must be specified together with
            `model_configuration`. This is for the internal strategy approach.
        model_configuration : Optional[ModelConfiguration], default=None
            Configuration for the Python-native model. Must be specified together
            with `model`.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If neither app_dir nor model/model_configuration is provided correctly,
            or if only one of model and model_configuration is provided.
        TypeError
            If model is not an instance of nextmv.Model or if model_configuration
            is not an instance of nextmv.ModelConfiguration.
        Exception
            If there's an error in the build, packaging, or cleanup process.

        Examples
        --------
        1. Push an app using an external strategy (directory-based):

        >>> import os
        >>> from nextmv import cloud
        >>> client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        >>> app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        >>> app.push()  # Use verbose=True for step-by-step output.

        2. Push an app using an internal strategy (Python-native model):

        >>> import os
        >>> import nextroute
        >>> import nextmv
        >>> import nextmv.cloud
        >>>
        >>> # Define the model that makes decisions
        >>> class DecisionModel(nextmv.Model):
        ...     def solve(self, input: nextmv.Input) -> nextmv.Output:
        ...         nextroute_input = nextroute.schema.Input.from_dict(input.data)
        ...         nextroute_options = nextroute.Options.extract_from_dict(input.options.to_dict())
        ...         nextroute_output = nextroute.solve(nextroute_input, nextroute_options)
        ...
        ...         return nextmv.Output(
        ...             options=input.options,
        ...             solution=nextroute_output.solutions[0].to_dict(),
        ...             statistics=nextroute_output.statistics.to_dict(),
        ...         )
        >>>
        >>> # Define the options that the model needs
        >>> opt = []
        >>> default_options = nextroute.Options()
        >>> for name, default_value in default_options.to_dict().items():
        ...     opt.append(nextmv.Option(name.lower(), type(default_value), default_value, name, False))
        >>> options = nextmv.Options(*opt)
        >>>
        >>> # Instantiate the model and model configuration
        >>> model = DecisionModel()
        >>> model_configuration = nextmv.ModelConfiguration(
        ...     name="python_nextroute_model",
        ...     requirements=[
        ...         "nextroute==1.8.1",
        ...         "nextmv==0.14.0.dev1",
        ...     ],
        ...     options=options,
        ... )
        >>>
        >>> # Push the model to Nextmv Cloud
        >>> client = cloud.Client(api_key=os.getenv("NEXTMV_API_KEY"))
        >>> app = cloud.Application(client=client, id="<YOUR-APP-ID>")
        >>> manifest = nextmv.cloud.default_python_manifest()
        >>> app.push(
        ...     manifest=manifest,
        ...     verbose=True,
        ...     model=model,
        ...     model_configuration=model_configuration,
        ... )
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

        Retrieves the input data that was used for a specific run. This method
        handles both small and large inputs automatically - if the input size
        exceeds the maximum allowed size, it will fetch the input from a
        download URL.

        Parameters
        ----------
        run_id : str
            ID of the run to retrieve the input for.

        Returns
        -------
        dict[str, Any]
            Input data of the run as a dictionary.

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

    def run_logs(self, run_id: str) -> RunLog:
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

    def run_result(self, run_id: str, output_dir_path: Optional[str] = ".") -> RunResult:
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
        self,
        run_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        output_dir_path: Optional[str] = ".",
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

    def scenario_test(self, scenario_test_id: str) -> BatchExperiment:
        """
        Get a scenario test.

        Retrieves a scenario test by ID. Scenario tests are based on batch
        experiments, so this function returns the corresponding batch
        experiment associated with the scenario test.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to retrieve.

        Returns
        -------
        BatchExperiment
            The scenario test details as a batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> test = app.scenario_test("scenario-123")
        >>> print(test.name)
        'My Scenario Test'
        >>> print(test.type)
        'scenario'
        """

        return self.batch_experiment(batch_id=scenario_test_id)

    def scenario_test_metadata(self, scenario_test_id: str) -> BatchExperimentMetadata:
        """
        Get the metadata for a scenario test, given its ID.

        Scenario tests are based on batch experiments, so this function returns
        the corresponding batch experiment metadata associated with the
        scenario test.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to retrieve.

        Returns
        -------
        BatchExperimentMetadata
            The scenario test metadata as a batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> metadata = app.scenario_test_metadata("scenario-123")
        >>> print(metadata.name)
        'My Scenario Test'
        >>> print(metadata.type)
        'scenario'
        """

        return self.batch_experiment_metadata(batch_id=scenario_test_id)

    def scenario_test_with_polling(
        self,
        scenario_test_id: str,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
    ) -> BatchExperiment:
        """
        Get a scenario test with polling.

        Retrieves the result of a scenario test. This method polls for the
        result until the test finishes executing or the polling strategy is
        exhausted.

        The scenario tests uses the batch experiments API under the hood.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to retrieve.
        polling_options : PollingOptions, default=_DEFAULT_POLLING_OPTIONS
            Options to use when polling for the scenario test result.

        Returns
        -------
        BatchExperiment
            The scenario test details as a batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> test = app.scenario_test_with_polling("scenario-123")
        >>> print(test.name)
        'My Scenario Test'
        >>> print(test.type)
        'scenario'
        """

        return self.batch_experiment_with_polling(batch_id=scenario_test_id, polling_options=polling_options)

    def track_run(  # noqa: C901
        self,
        tracked_run: TrackedRun,
        instance_id: Optional[str] = None,
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
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
        >>> from nextmv.cloud.run import TrackedRun
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

            input_tar_file = self.__package_inputs(input_dir_path)

        # Handle the case where the input is uploaded as Input or a dict.
        upload_input = tracked_run.input
        if upload_input is not None and isinstance(tracked_run.input, Input):
            upload_input = tracked_run.input.data

        # Actually uploads de input.
        self.upload_large_input(input=upload_input, upload_url=url_input, tar_file=input_tar_file)

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

            output_tar_file = self.__package_inputs(output_dir_path)

        # Handle the case where the output is uploaded as Output or a dict.
        upload_output = tracked_run.output
        if upload_output is not None and isinstance(tracked_run.output, Output):
            upload_output = tracked_run.output.to_dict()

        # Actually uploads the output.
        self.upload_large_input(input=upload_output, upload_url=url_output, tar_file=output_tar_file)

        # Create the external run result and appends logs if required.
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
            name=tracked_run.name,
            description=tracked_run.description,
            configuration=configuration,
        )

    def track_run_with_result(
        self,
        tracked_run: TrackedRun,
        polling_options: PollingOptions = DEFAULT_POLLING_OPTIONS,
        instance_id: Optional[str] = None,
        output_dir_path: Optional[str] = ".",
        configuration: Optional[Union[RunConfiguration, dict[str, Any]]] = None,
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

    def update_instance(
        self,
        id: str,
        name: Optional[str] = None,
        version_id: Optional[str] = None,
        description: Optional[str] = None,
        configuration: Optional[InstanceConfiguration] = None,
    ) -> Instance:
        """
        Update an instance.

        Parameters
        ----------
        id : str
            ID of the instance to update.
        name : Optional[str], default=None
            Optional name of the instance.
        version_id : Optional[str], default=None
            Optional ID of the version to associate the instance with.
        description : Optional[str], default=None
            Optional description of the instance.
        configuration : Optional[InstanceConfiguration], default=None
            Optional configuration to use for the instance.

        Returns
        -------
        Instance
            The updated instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        # Get the instance as it currently exsits.
        instance = self.instance(id)
        instance_dict = instance.to_dict()

        payload = {
            "name": instance_dict["name"],
            "version_id": instance_dict["version_id"],
            "description": instance_dict["description"],
            "configuration": instance_dict["configuration"],
        }

        if name is not None:
            payload["name"] = name
        if version_id is not None:
            payload["version_id"] = version_id
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
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> BatchExperimentInformation:
        """
        Update a batch experiment.

        Parameters
        ----------
        batch_experiment_id : str
            ID of the batch experiment to update.
        name : Optional[str], default=None
            Optional name of the batch experiment.
        description : Optional[str], default=None
            Optional description of the batch experiment.

        Returns
        -------
        BatchExperimentInformation
            The information with the updated batch experiment.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PATCH",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_experiment_id}",
            payload=payload,
        )

        return BatchExperimentInformation.from_dict(response.json())

    def update_managed_input(
        self,
        managed_input_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> ManagedInput:
        """
        Update a managed input.

        Parameters
        ----------
        managed_input_id : str
            ID of the managed input to update.
        name : Optional[str], default=None
            Optional new name for the managed input.
        description : Optional[str], default=None
            Optional new description for the managed input.

        Returns
        -------
        ManagedInput
            The updated managed input.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        managed_input = self.managed_input(managed_input_id)
        managed_input_dict = managed_input.to_dict()

        payload = {
            "name": managed_input_dict["name"],
            "description": managed_input_dict["description"],
        }

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/inputs/{managed_input_id}",
            payload=payload,
        )

        return ManagedInput.from_dict(response.json())

    def update_scenario_test(
        self,
        scenario_test_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> BatchExperimentInformation:
        """
        Update a scenario test.

        Updates a scenario test with new name and description. Scenario tests
        use the batch experiments API, so this method calls the
        `update_batch_experiment` method, and thus the return type is the same.

        Parameters
        ----------
        scenario_test_id : str
            ID of the scenario test to update.
        name : Optional[str], default=None
            Optional new name for the scenario test.
        description : Optional[str], default=None
            Optional new description for the scenario test.

        Returns
        -------
        BatchExperimentInformation
            The information about the updated scenario test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> info = app.update_scenario_test(
        ...     scenario_test_id="scenario-123",
        ...     name="Updated Test Name",
        ...     description="Updated description for this test"
        ... )
        >>> print(info.name)
        'Updated Test Name'
        """

        return self.update_batch_experiment(
            batch_experiment_id=scenario_test_id,
            name=name,
            description=description,
        )

    def update_secrets_collection(
        self,
        secrets_collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        secrets: Optional[list[Secret]] = None,
    ) -> SecretsCollectionSummary:
        """
        Update a secrets collection.

        This method updates an existing secrets collection with new values for name,
        description, and secrets. A secrets collection is a group of key-value pairs
        that can be used by your application instances during execution.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to update.
        name : Optional[str], default=None
            Optional new name for the secrets collection.
        description : Optional[str], default=None
            Optional new description for the secrets collection.
        secrets : Optional[list[Secret]], default=None
            Optional list of secrets to update. Each secret should be an
            instance of the Secret class containing a key and value.

        Returns
        -------
        SecretsCollectionSummary
            Summary of the updated secrets collection including its metadata.

        Raises
        ------
        ValueError
            If no secrets are provided.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Update an existing secrets collection
        >>> from nextmv.cloud import Secret
        >>> updated_secrets = [
        ...     Secret(key="API_KEY", value="new-api-key"),
        ...     Secret(key="DATABASE_URL", value="new-database-url")
        ... ]
        >>> updated_collection = app.update_secrets_collection(
        ...     secrets_collection_id="api-secrets",
        ...     name="Updated API Secrets",
        ...     description="Updated collection of API secrets",
        ...     secrets=updated_secrets
        ... )
        >>> print(updated_collection.id)
        'api-secrets'
        """

        collection = self.secrets_collection(secrets_collection_id)
        collection_dict = collection.to_dict()

        payload = {
            "name": collection_dict["name"],
            "description": collection_dict["description"],
            "secrets": collection_dict["secrets"],
        }

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if secrets is not None and len(secrets) > 0:
            payload["secrets"] = [secret.to_dict() for secret in secrets]

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
            payload=payload,
        )

        return SecretsCollectionSummary.from_dict(response.json())

    def upload_large_input(
        self,
        input: Optional[Union[dict[str, Any], str]],
        upload_url: UploadURL,
        json_configurations: Optional[dict[str, Any]] = None,
        tar_file: Optional[str] = None,
    ) -> None:
        """
        Upload large input data to the provided upload URL.

        This method allows uploading large input data (either a dictionary or string)
        to a pre-signed URL. If the input is a dictionary, it will be converted to
        a JSON string before upload.

        Parameters
        ----------
        input : Optional[Union[dict[str, Any], str]]
            Input data to upload. Can be either a dictionary that will be
            converted to JSON, or a pre-formatted JSON string.
        upload_url : UploadURL
            Upload URL object containing the pre-signed URL to use for uploading.
        json_configurations : Optional[dict[str, Any]], default=None
            Optional configurations for JSON serialization. If provided, these
            configurations will be used when serializing the data via
            `json.dumps`.
        tar_file : Optional[str], default=None
            If provided, this will be used to upload a tar file instead of
            a JSON string or dictionary. This is useful for uploading large
            files that are already packaged as a tarball.

        Returns
        -------
        None
            This method doesn't return anything.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Upload a dictionary as JSON
        >>> data = {"locations": [...], "vehicles": [...]}
        >>> url = app.upload_url()
        >>> app.upload_large_input(input=data, upload_url=url)
        >>>
        >>> # Upload a pre-formatted JSON string
        >>> json_str = '{"locations": [...], "vehicles": [...]}'
        >>> app.upload_large_input(input=json_str, upload_url=url)
        """

        if input is not None and isinstance(input, dict):
            input = deflated_serialize_json(input, json_configurations=json_configurations)

        self.client.upload_to_presigned_url(
            url=upload_url.upload_url,
            data=input,
            tar_file=tar_file,
        )

    def upload_url(self) -> UploadURL:
        """
        Get an upload URL to use for uploading a file.

        This method generates a pre-signed URL that can be used to upload large files
        to Nextmv Cloud. It's primarily used for uploading large input data, output
        results, or log files that exceed the size limits for direct API calls.

        Returns
        -------
        UploadURL
            An object containing both the upload URL and an upload ID for reference.
            The upload URL is a pre-signed URL that allows temporary write access.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Get an upload URL and upload large input data
        >>> upload_url = app.upload_url()
        >>> large_input = {"locations": [...], "vehicles": [...]}
        >>> app.upload_large_input(input=large_input, upload_url=upload_url)
        """

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/runs/uploadurl",
        )

        return UploadURL.from_dict(response.json())

    def secrets_collection(self, secrets_collection_id: str) -> SecretsCollection:
        """
        Get a secrets collection.

        This method retrieves a secrets collection by its ID. A secrets collection
        is a group of key-value pairs that can be used by your application
        instances during execution.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to retrieve.

        Returns
        -------
        SecretsCollection
            The requested secrets collection, including all secret values
            and metadata.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Retrieve a secrets collection
        >>> collection = app.secrets_collection("api-secrets")
        >>> print(collection.name)
        'API Secrets'
        >>> print(len(collection.secrets))
        2
        >>> for secret in collection.secrets:
        ...     print(secret.location)
        'API_KEY'
        'DATABASE_URL'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

        return SecretsCollection.from_dict(response.json())

    def version(self, version_id: str) -> Version:
        """
        Get a version.

        Retrieves a specific version of the application by its ID. Application versions
        represent different iterations of your application's code and configuration.

        Parameters
        ----------
        version_id : str
            ID of the version to retrieve.

        Returns
        -------
        Version
            The version object containing details about the requested application version.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Retrieve a specific version
        >>> version = app.version("v1.0.0")
        >>> print(version.id)
        'v1.0.0'
        >>> print(version.name)
        'Initial Release'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions/{version_id}",
        )

        return Version.from_dict(response.json())

    def version_exists(self, version_id: str) -> bool:
        """
        Check if a version exists.

        This method checks if a specific version of the application exists by
        attempting to retrieve it. It handles HTTP errors for non-existent versions
        and returns a boolean indicating existence.

        Parameters
        ----------
        version_id : str
            ID of the version to check for existence.

        Returns
        -------
        bool
            True if the version exists, False otherwise.

        Raises
        ------
        requests.HTTPError
            If an HTTP error occurs that is not related to the non-existence
            of the version.

        Examples
        --------
        >>> # Check if a version exists
        >>> exists = app.version_exists("v1.0.0")
        >>> if exists:
        ...     print("Version exists!")
        ... else:
        ...     print("Version does not exist.")
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
        output_dir_path: Optional[str] = ".",
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
                shutil.unpack_archive(temp_tar_path, output_dir_path)
        else:
            result.output = download_response.json()

        return result

    @staticmethod
    def __convert_manifest_to_payload(manifest: Manifest) -> dict[str, Any]:
        """Converts a manifest to a payload dictionary for the API."""

        activation_request = {
            "requirements": {
                "executable_type": manifest.type,
                "runtime": manifest.runtime,
            },
        }

        if manifest.configuration is not None and manifest.configuration.content is not None:
            content = manifest.configuration.content
            io_config = {
                "format": content.format,
            }
            if content.multi_file is not None:
                multi_config = io_config["multi_file"] = {}
                if content.multi_file.input is not None:
                    multi_config["input_path"] = content.multi_file.input.path
                if content.multi_file.output is not None:
                    output_config = multi_config["output_configuration"] = {}
                    if content.multi_file.output.statistics:
                        output_config["statistics_path"] = content.multi_file.output.statistics
                    if content.multi_file.output.assets:
                        output_config["assets_path"] = content.multi_file.output.assets
                    if content.multi_file.output.solutions:
                        output_config["solutions_path"] = content.multi_file.output.solutions
            activation_request["requirements"]["io_configuration"] = io_config

        if manifest.configuration is not None and manifest.configuration.options is not None:
            options = manifest.configuration.options.to_dict()
            if "format" in options and isinstance(options["format"], list):
                # the endpoint expects a dictionary with a template key having a list of strings
                # the app.yaml however defines format as a list of strings, so we need to convert it here
                options["format"] = {
                    "template": options["format"],
                }
            activation_request["requirements"]["options"] = options
        return activation_request

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

        response = self.client.request(
            method="PUT",
            endpoint=endpoint,
            payload=Application.__convert_manifest_to_payload(manifest=manifest),
        )

        if verbose:
            log(f'💥️ Successfully pushed to application: "{self.id}".')
            log(
                json.dumps(
                    {
                        "app_id": self.id,
                        "endpoint": self.client.url,
                        "instance_url": f"{self.endpoint}/runs?instance_id=latest",
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
            name, id = safe_name_and_id(prefix="inpset", entity_id=scenario_id)
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
                name, id = safe_name_and_id(prefix="man-input", entity_id=scenario_id)
                managed_input = self.new_managed_input(
                    id=id,
                    name=name,
                    description=f"Automatically created from scenario test: {id}",
                    upload_id=upload_url.upload_id,
                )
                managed_inputs.append(managed_input)

            name, id = safe_name_and_id(prefix="inpset", entity_id=scenario_id)
            input_set = self.new_input_set(
                id=id,
                name=name,
                description=f"Automatically created from scenario test: {id}",
                maximum_runs=20,
                inputs=managed_inputs,
            )
            return input_set

        raise ValueError(f"Unknown scenario input type: {scenario.scenario_input.scenario_input_type}")

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

    def __package_inputs(self, dir_path: str) -> str:
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

    def __upload_url_required(
        self,
        upload_id_used: bool,
        input_size: int,
        tar_file: str,
        input: Union[Input, dict[str, Any], BaseModel, str] = None,
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
                        continue

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


def _is_not_exist_error(e: requests.HTTPError) -> bool:
    """
    Check if the error is a known 404 Not Found error.

    This is an internal helper function that examines HTTPError objects to determine
    if they represent a "Not Found" (404) condition, either directly or through a
    nested exception.

    Parameters
    ----------
    e : requests.HTTPError
        The HTTP error to check.

    Returns
    -------
    bool
        True if the error is a 404 Not Found error, False otherwise.

    Examples
    --------
    >>> try:
    ...     response = requests.get('https://api.example.com/nonexistent')
    ...     response.raise_for_status()
    ... except requests.HTTPError as err:
    ...     if _is_not_exist_error(err):
    ...         print("Resource does not exist")
    ...     else:
    ...         print("Another error occurred")
    Resource does not exist
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
