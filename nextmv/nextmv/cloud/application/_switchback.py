"""
Application mixin for managing switchback tests.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from nextmv.cloud.switchback import SwitchbackTest, SwitchbackTestMetadata, TestComparisonSingle
from nextmv.run import Run
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationSwitchbackMixin:
    """
    Mixin class for managing switchback tests within an application.
    """

    def switchback_test(self: "Application", switchback_test_id: str) -> SwitchbackTest:
        """
        Get a switchback test. This method also returns the runs of the switchback
        test under the `.runs` attribute.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test.

        Returns
        -------
        SwitchbackTest
            The requested switchback test details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> switchback_test = app.switchback_test("switchback-123")
        >>> print(switchback_test.name)
        'My Switchback Test'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}",
        )

        exp = SwitchbackTest.from_dict(response.json())

        runs_response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}/runs",
        )

        runs = [Run.from_dict(run) for run in runs_response.json().get("runs", [])]
        exp.runs = runs

        return exp

    def switchback_test_metadata(self: "Application", switchback_test_id: str) -> SwitchbackTestMetadata:
        """
        Get metadata for a switchback test.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test.

        Returns
        -------
        SwitchbackTestMetadata
            The requested switchback test metadata.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> metadata = app.switchback_test_metadata("switchback-123")
        >>> print(metadata.name)
        'My Switchback Test'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}/metadata",
        )

        return SwitchbackTestMetadata.from_dict(response.json())

    def delete_switchback_test(self: "Application", switchback_test_id: str) -> None:
        """
        Delete a switchback test.

        Deletes a switchback test along with all the associated information,
        such as its runs.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_switchback_test("switchback-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}",
        )

    def list_switchback_tests(self: "Application") -> list[SwitchbackTest]:
        """
        List all switchback tests.

        Returns
        -------
        list[SwitchbackTest]
            List of switchback tests.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/switchback",
        )

        return [SwitchbackTest.from_dict(switchback_test) for switchback_test in response.json().get("items", [])]

    def new_switchback_test(
        self: "Application",
        comparison: TestComparisonSingle,
        unit_duration_minutes: float,
        units: int,
        switchback_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        start: datetime | None = None,
    ) -> SwitchbackTest:
        """
        Create a new switchback test in draft mode. Switchback tests are
        experiments that alternate between different instances over specified
        time intervals.

        Use the `comparison` parameter to define how to set up the instance
        comparison. The test will alternate between the baseline and candidate
        instances defined in the comparison.

        You may specify `start` to make the switchback test start at a
        specific time. Alternatively, you may use the `start_switchback_test`
        method to start the test.

        Parameters
        ----------
        comparison : TestComparisonSingle
            Comparison defining the baseline and candidate instances.
        unit_duration_minutes : float
            Duration of each interval in minutes. The value must be between 1
            and 10080.
        units : int
            Total number of intervals in the switchback test. The value must be
            between 1 and 1000.
        switchback_test_id : Optional[str], default=None
            Optional ID for the switchback test. Will be generated if not
            provided.
        name : Optional[str], default=None
            Optional name of the switchback test. If not provided, the ID will
            be used as the name.
        description : Optional[str], default=None
            Optional description of the switchback test.
        start : Optional[datetime], default=None
            Optional scheduled start time for the switchback test.

        Returns
        -------
        SwitchbackTest
            The created switchback test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        if unit_duration_minutes < 1 or unit_duration_minutes > 10080:
            raise ValueError("unit_duration_minutes must be between 1 and 10080")

        if units < 1 or units > 1000:
            raise ValueError("units must be between 1 and 1000")

        # Generate ID if not provided
        if switchback_test_id is None:
            switchback_test_id = safe_id("switchback")

        # Use ID as name if name not provided
        if name is None or name == "":
            name = switchback_test_id

        payload = {
            "id": switchback_test_id,
            "name": name,
            "comparison": comparison,
            "generate_random_plan": {
                "unit_duration_minutes": unit_duration_minutes,
                "units": units,
            },
        }

        if description is not None:
            payload["description"] = description
        if start is not None:
            payload["generate_random_plan"]["start"] = start.isoformat()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/switchback",
            payload=payload,
        )

        return SwitchbackTest.from_dict(response.json())

    def start_switchback_test(self: "Application", switchback_test_id: str) -> None:
        """
        Start a switchback test. Create a switchback test in draft mode using the
        `new_switchback_test` method, then use this method to start the test.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test to start.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PUT",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}/start",
        )

    def stop_switchback_test(self: "Application", switchback_test_id: str) -> None:
        """
        Stop a switchback test. The test should already have started before using
        this method.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test to stop.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PUT",
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}/stop",
        )

    def update_switchback_test(
        self: "Application",
        switchback_test_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> SwitchbackTest:
        """
        Update a switchback test.

        Parameters
        ----------
        switchback_test_id : str
            ID of the switchback test to update.
        name : Optional[str], default=None
            Optional name of the switchback test.
        description : Optional[str], default=None
            Optional description of the switchback test.

        Returns
        -------
        SwitchbackTest
            The information with the updated switchback test.

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
            endpoint=f"{self.experiments_endpoint}/switchback/{switchback_test_id}",
            payload=payload,
        )

        return SwitchbackTest.from_dict(response.json())
