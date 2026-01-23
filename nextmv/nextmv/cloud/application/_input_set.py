"""
Application mixin for managing app input sets.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from nextmv.cloud.input_set import InputSet, ManagedInput

if TYPE_CHECKING:
    from . import Application


class ApplicationInputSetMixin:
    """
    Mixin class for managing app input sets within an application.
    """

    def input_set(self: "Application", input_set_id: str) -> InputSet:
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

    def list_input_sets(self: "Application") -> list[InputSet]:
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

    def new_input_set(
        self: "Application",
        id: str,
        name: str,
        description: str | None = None,
        end_time: datetime | None = None,
        instance_id: str | None = None,
        maximum_runs: int | None = None,
        run_ids: list[str] | None = None,
        start_time: datetime | None = None,
        inputs: list[ManagedInput] | None = None,
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
        inputs: Optional[list[ManagedInput]]
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

    def update_input_set(
        self: "Application",
        id: str,
        name: str | None = None,
        description: str | None = None,
        inputs: list[ManagedInput] | None = None,
    ) -> InputSet:
        """
        Update an input set.

        Parameters
        ----------
        id : str
            ID of the input set to update.
        name : Optional[str], default=None
            Optional name of the input set.
        description : Optional[str], default=None
            Optional description of the input set.
        inputs: Optional[list[ManagedInput]]
            List of inputs to use for the input set. This is used to create
            the input set from a list of inputs that are already available in
            the application.

        Returns
        -------
        Instance
            The updated instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        # Get the input set as it currently exsits.
        input_set = self.input_set(id)
        input_set_dict = input_set.to_dict()
        payload = input_set_dict.copy()

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if inputs is not None:
            payload["inputs"] = [input.to_dict() for input in inputs]

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.experiments_endpoint}/inputsets/{id}",
            payload=payload,
        )

        return InputSet.from_dict(response.json())
