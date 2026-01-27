"""
Application mixin for managing shadow tests.
"""

from typing import TYPE_CHECKING

from nextmv.cloud.shadow import ShadowTest, ShadowTestMetadata, StartEvents, TerminationEvents
from nextmv.run import Run
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationShadowMixin:
    """
    Mixin class for managing shadow tests within an application.
    """

    def shadow_test(self: "Application", shadow_test_id: str) -> ShadowTest:
        """
        Get a shadow test. This method also returns the runs of the shadow
        test under the `.runs` attribute.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test.

        Returns
        -------
        ShadowTest
            The requested shadow test details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> shadow_test = app.shadow_test("shadow-123")
        >>> print(shadow_test.name)
        'My Shadow Test'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}",
        )

        exp = ShadowTest.from_dict(response.json())

        runs_response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}/runs",
        )

        runs = [Run.from_dict(run) for run in runs_response.json().get("runs", [])]
        exp.runs = runs

        return exp

    def shadow_test_metadata(self: "Application", shadow_test_id: str) -> ShadowTestMetadata:
        """
        Get metadata for a shadow test.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test.

        Returns
        -------
        ShadowTestMetadata
            The requested shadow test metadata.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> metadata = app.shadow_test_metadata("shadow-123")
        >>> print(metadata.name)
        'My Shadow Test'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}/metadata",
        )

        return ShadowTestMetadata.from_dict(response.json())

    def delete_shadow_test(self: "Application", shadow_test_id: str) -> None:
        """
        Delete a shadow test.

        Deletes a shadow test along with all the associated information,
        such as its runs.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_shadow_test("shadow-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}",
        )

    def list_shadow_tests(self: "Application") -> list[ShadowTest]:
        """
        List all shadow tests.

        Returns
        -------
        list[ShadowTest]
            List of shadow tests.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.experiments_endpoint}/shadow",
        )

        return [ShadowTest.from_dict(shadow_test) for shadow_test in response.json()]

    def new_shadow_test(
        self: "Application",
        comparisons: dict[str, list[str]],
        termination_events: TerminationEvents,
        shadow_test_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        start_events: StartEvents | None = None,
    ) -> ShadowTest:
        """
        Create a new shadow test in draft mode. Shadow tests are experiments
        that run instances in parallel to compare their results.

        Use the `comparisons` parameter to define how to set up instance
        comparisons. The keys of the `comparisons` dictionary are the baseline
        instance IDs, and the values are the candidate lists of instance IDs to
        compare against the respective baseline.

        You may specify `start_events` to make the shadow test start at a
        specific time. Alternatively, you may use the `start_shadow_test`
        method to start the test.

        The `termination_events` parameter is required and provides control
        over when the shadow test should terminate. Alternatively, you may use
        the `stop_shadow_test` method to stop the test.

        Parameters
        ----------
        comparisons : dict[str, list[str]]
            Dictionary defining the baseline and candidate instance IDs for
            comparison. The keys are baseline instance IDs, and the values are
            lists of candidate instance IDs to compare against the respective
            baseline.
        termination_events : TerminationEvents
            Termination events for the shadow test.
        shadow_test_id : Optional[str]
            ID of the shadow test. Will be generated if not provided.
        name : Optional[str]
            Name of the shadow test. If not provided, the ID will be used as
            the name.
        description : Optional[str]
            Optional description of the shadow test.
        start_events : Optional[StartEvents]
            Start events for the shadow test.

        Returns
        -------
        ShadowTest
            The created shadow test.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        # Generate ID if not provided
        if shadow_test_id is None:
            shadow_test_id = safe_id("shadow")

        # Use ID as name if name not provided
        if name is None or name == "":
            name = shadow_test_id

        payload = {
            "id": shadow_test_id,
            "name": name,
            "comparisons": comparisons,
            "termination_events": termination_events.to_dict(),
        }

        if description is not None:
            payload["description"] = description
        if start_events is not None:
            payload["start_events"] = start_events.to_dict()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.experiments_endpoint}/shadow",
            payload=payload,
        )

        return ShadowTest.from_dict(response.json())

    def start_shadow_test(self: "Application", shadow_test_id: str) -> None:
        """
        Start a shadow test. Create a shadow test in draft mode using the
        `new_shadow_test` method, then use this method to start the test.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test to start.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PUT",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}/start",
        )

    def stop_shadow_test(self: "Application", shadow_test_id: str) -> None:
        """
        Stop a shadow test. The test should already have started before using
        this method.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test to stop.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        _ = self.client.request(
            method="PUT",
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}/stop",
        )

    def update_shadow_test(
        self: "Application",
        shadow_test_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> ShadowTest:
        """
        Update a shadow test.

        Parameters
        ----------
        shadow_test_id : str
            ID of the shadow test to update.
        name : Optional[str], default=None
            Optional name of the shadow test.
        description : Optional[str], default=None
            Optional description of the shadow test.

        Returns
        -------
        ShadowTest
            The information with the updated shadow test.

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
            endpoint=f"{self.experiments_endpoint}/shadow/{shadow_test_id}",
            payload=payload,
        )

        return ShadowTest.from_dict(response.json())
