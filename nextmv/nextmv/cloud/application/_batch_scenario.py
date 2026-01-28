"""
Application mixin for managing batch experiments.
"""

from typing import TYPE_CHECKING, Any

from nextmv.cloud.batch_experiment import (
    BatchExperiment,
    BatchExperimentInformation,
    BatchExperimentMetadata,
    BatchExperimentRun,
    ExperimentStatus,
)
from nextmv.cloud.input_set import InputSet, ManagedInput
from nextmv.cloud.scenario import Scenario, ScenarioInputType, _option_sets, _scenarios_by_id
from nextmv.polling import DEFAULT_POLLING_OPTIONS, PollingOptions, poll
from nextmv.run import Run
from nextmv.safe import safe_id, safe_name_and_id

if TYPE_CHECKING:
    from . import Application


class ApplicationBatchMixin:
    """
    Mixin class for managing batch experiments within an application.
    """

    def batch_experiment(self: "Application", batch_id: str) -> BatchExperiment:
        """
        Get a batch experiment. This method also returns the runs of the batch
        experiment under the `.runs` attribute.

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

        exp = BatchExperiment.from_dict(response.json())

        runs_response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/batch/{batch_id}/runs",
        )

        runs = [Run.from_dict(run) for run in runs_response.json().get("runs", [])]
        exp.runs = runs

        return exp

    def batch_experiment_metadata(self: "Application", batch_id: str) -> BatchExperimentMetadata:
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
        self: "Application",
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

    def delete_batch_experiment(self: "Application", batch_id: str) -> None:
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

    def delete_scenario_test(self: "Application", scenario_test_id: str) -> None:
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

    def list_batch_experiments(self: "Application") -> list[BatchExperimentMetadata]:
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

    def list_scenario_tests(self: "Application") -> list[BatchExperimentMetadata]:
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

    def new_batch_experiment(  # noqa: C901
        self: "Application",
        name: str | None = None,
        input_set_id: str | None = None,
        description: str | None = None,
        id: str | None = None,
        option_sets: dict[str, dict[str, str]] | None = None,
        runs: list[BatchExperimentRun | dict[str, Any]] | None = None,
        type: str | None = "batch",
    ) -> str:
        """
        Create a new batch experiment.

        Parameters
        ----------
        name: Optional[str]
            Name of the batch experiment. If not provided, the ID will be used as the name.
        input_set_id: str | None
            ID of the input set to use for the batch experiment.
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

        # Generate ID if not provided
        if id is None or id == "":
            id = safe_id("batch")

        # Use ID as name if name not provided
        if name is None or name == "":
            name = id

        payload = {
            "id": id,
            "name": name,
        }
        if input_set_id is not None:
            payload["input_set_id"] = input_set_id
        if description is not None:
            payload["description"] = description
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
        self: "Application",
        name: str | None = None,
        input_set_id: str | None = None,
        description: str | None = None,
        id: str | None = None,
        option_sets: dict[str, dict[str, str]] | None = None,
        runs: list[BatchExperimentRun | dict[str, Any]] | None = None,
        type: str | None = "batch",
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
        name: Optional[str]
            Name of the batch experiment. If not provided, the ID will be used as the name.
        input_set_id: str
            ID of the input set to use for the batch experiment.
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
        polling_options : PollingOptions, default=DEFAULT_POLLING_OPTIONS
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
            description=description,
            id=id,
            option_sets=option_sets,
            runs=runs,
            type=type,
        )

        return self.batch_experiment_with_polling(batch_id=batch_id, polling_options=polling_options)

    def new_scenario_test(
        self: "Application",
        scenarios: list[Scenario],
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        repetitions: int | None = 0,
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
        scenarios: list[Scenario]
            List of scenarios to use for the scenario test. At least one
            scenario should be provided.
        id: Optional[str]
            ID of the scenario test. Will be generated if not provided.
        name: Optional[str]
            Name of the scenario test. If not provided, the ID will be used as the name.
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

        # Generate ID if not provided
        if id is None or id == "":
            id = safe_id("scenario")

        # Use ID as name if name not provided
        if name is None or name == "":
            name = id

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
        self: "Application",
        scenarios: list[Scenario],
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        repetitions: int | None = 0,
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
        scenarios: list[Scenario]
            List of scenarios to use for the scenario test. At least one
            scenario should be provided.
        id: Optional[str]
            ID of the scenario test. Will be generated if not provided.
        name: Optional[str]
            Name of the scenario test. If not provided, the ID will be used as the name.
        description: Optional[str]
            Optional description of the scenario test.
        repetitions: Optional[int]
            Number of repetitions to use for the scenario test. 0
            repetitions means that the tests will be executed once. 1
            repetition means that the test will be repeated once, i.e.: it
            will be executed twice. 2 repetitions equals 3 executions, so on,
            and so forth.
        polling_options : PollingOptions, default=DEFAULT_POLLING_OPTIONS
            Options to use when polling for the scenario test result.

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
            scenarios=scenarios,
            id=id,
            name=name,
            description=description,
            repetitions=repetitions,
        )

        return self.scenario_test_with_polling(
            scenario_test_id=test_id,
            polling_options=polling_options,
        )

    def scenario_test(self: "Application", scenario_test_id: str) -> BatchExperiment:
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

    def scenario_test_metadata(self: "Application", scenario_test_id: str) -> BatchExperimentMetadata:
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
        self: "Application",
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
        polling_options : PollingOptions, default=DEFAULT_POLLING_OPTIONS
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

    def update_batch_experiment(
        self: "Application",
        batch_experiment_id: str,
        name: str | None = None,
        description: str | None = None,
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

    def update_scenario_test(
        self: "Application",
        scenario_test_id: str,
        name: str | None = None,
        description: str | None = None,
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

    def __input_set_for_scenario(self: "Application", scenario: Scenario, scenario_id: str) -> InputSet:
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
                self.upload_data(data=data, upload_url=upload_url)
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
