"""
Application mixin for managing acceptance tests.
"""

from typing import TYPE_CHECKING, Any

import requests

from nextmv.cloud.acceptance_test import AcceptanceTest, Metric
from nextmv.cloud.batch_experiment import BatchExperimentRun, ExperimentStatus
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationAcceptanceMixin:
    """
    Mixin class providing acceptance test methods for Application.
    """

    def acceptance_test(self: "Application", acceptance_test_id: str) -> AcceptanceTest:
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
        self: "Application",
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

    def delete_acceptance_test(self: "Application", acceptance_test_id: str) -> None:
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

    def list_acceptance_tests(self: "Application") -> list[AcceptanceTest]:
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

    def new_acceptance_test(  # noqa: C901
        self: "Application",
        candidate_instance_id: str,
        baseline_instance_id: str,
        metrics: list[Metric | dict[str, Any]],
        id: str | None = None,
        name: str | None = None,
        input_set_id: str | None = None,
        description: str | None = None,
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
        id : str | None, default=None
            ID of the acceptance test. Will be generated if not provided.
        metrics : list[Union[Metric, dict[str, Any]]]
            List of metrics to use for the acceptance test.
        name : Optional[str], default=None
            Name of the acceptance test. If not provided, the ID will be used as the name.
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

        # Generate ID if not provided
        if id is None or id == "":
            id = safe_id("acceptance")

        # Use ID as name if name not provided
        if name is None or name == "":
            name = id

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
            "id": id,
        }
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/acceptance",
            payload=payload,
        )

        return AcceptanceTest.from_dict(response.json())

    def new_acceptance_test_with_result(
        self: "Application",
        candidate_instance_id: str,
        baseline_instance_id: str,
        metrics: list[Metric | dict[str, Any]],
        id: str | None = None,
        name: str | None = None,
        input_set_id: str | None = None,
        description: str | None = None,
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
        id : str | None, default=None
            ID of the acceptance test. Will be generated if not provided.
        metrics : list[Union[Metric, dict[str, Any]]]
            List of metrics to use for the acceptance test.
        name : Optional[str], default=None
            Name of the acceptance test. If not provided, the ID will be used as the name.
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

    def update_acceptance_test(
        self: "Application",
        acceptance_test_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> AcceptanceTest:
        """
        Update an acceptance test.

        Parameters
        ----------
        acceptance_test_id : str
            ID of the acceptance test to update.
        name : Optional[str], default=None
            Optional name of the acceptance test.
        description : Optional[str], default=None
            Optional description of the acceptance test.

        Returns
        -------
        AcceptanceTest
            The updated acceptance test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> test = app.update_acceptance_test(
        ...     acceptance_test_id="test-123",
        ...     name="Updated Test Name",
        ...     description="Updated description"
        ... )
        >>> print(test.name)
        'Updated Test Name'
        """

        if (name is None or name == "") and (description is None or description == ""):
            raise ValueError("at least one of name or description must be provided for update")

        payload = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PATCH",
            endpoint=f"{self.experiments_endpoint}/acceptance/{acceptance_test_id}",
            payload=payload,
        )

        return AcceptanceTest.from_dict(response.json())
