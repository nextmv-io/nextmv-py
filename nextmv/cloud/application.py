"""This module contains the application class."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client


class Metadata(BaseModel):
    """Metadata of a run, whether it was successful or not."""

    status: str
    """Status of the run."""
    created_at: datetime
    """Date and time when the run was created."""
    duration: float
    """Duration of the run in milliseconds."""
    input_size: float
    """Size of the input in bytes."""
    output_size: float
    """Size of the output in bytes."""
    error: str
    """Error message if the run failed."""
    application_id: str
    """ID of the application where the run was submitted to."""
    application_instance_id: str
    """ID of the instance where the run was submitted to."""
    application_version_id: str
    """ID of the version of the application where the run was submitted to."""


class RunResult(BaseModel):
    """Result of a run, wheter it was successful or not."""

    id: str
    """ID of the run."""
    user_email: str
    """Email of the user who submitted the run."""
    name: str
    """Name of the run."""
    description: str
    """Description of the run."""
    metadata: Metadata
    """Metadata of the run."""
    output: dict[str, Any]
    """Output of the run."""


@dataclass
class Application:
    """An application is a published decision model that can be executed."""

    client: Client
    """Client to use for interacting with the Nextmv Cloud API."""
    id: str
    """ID of the application."""
    endpoint: str = "v1/applications/{id}"
    """Base endpoint for the application."""
    default_instance_id: str = "devint"
    """Default instance ID to use for submitting runs."""

    def __post_init__(self):
        """Logic to run after the class is initialized."""

        self.endpoint = self.endpoint.format(id=self.id)

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
        """

        payload = {}
        if input is not None:
            payload["input"] = input
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if upload_id is not None:
            payload["upload_id"] = upload_id
        if options is not None:
            payload["options"] = options

        query_params = {
            "instance_id": instance_id if instance_id is not None else self.default_instance_id,
        }
        response = self.client.post(
            endpoint=f"{self.endpoint}/runs",
            payload=payload,
            query_params=query_params,
        )

        return response.json()["run_id"]

    def run_result(
        self,
        run_id: str,
    ) -> RunResult:
        """
        Get the result of a run.

        Args:
            run_id: ID of the run.

        Returns:
            Result of the run.
        """

        response = self.client.get(
            endpoint=f"{self.endpoint}/runs/{run_id}",
        )

        return RunResult.from_dict(response.json())
