from dataclasses import dataclass
from datetime import datetime
from typing import List

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.cloud.status import Status, StatusV2


class QueuedRun(BaseModel):
    """A run that is pending to be executed in the account."""

    id: str
    """ID of the run."""
    user_email: str
    """Email of the user who created the run."""
    name: str
    """Name of the run."""
    description: str
    """Description of the run."""
    created_at: datetime
    """Creation date of the run."""
    application_id: str
    """ID of the application used for the run."""
    application_instance_id: str
    """ID of the application instance used for the run."""
    application_version_id: str
    """ID of the application version used for the run."""
    execution_class: str
    """Execution class used for the run."""
    status: Status
    """Deprecated: use status_v2."""
    status_v2: StatusV2
    """Status of the run."""


class Queue(BaseModel):
    """A queue is a list of runs that are pending to be executed, or currently
    being executed, in the account."""

    runs: List[QueuedRun]
    """List of runs in the queue."""


@dataclass
class Account:
    """The Nextmv Platform account."""

    client: Client
    """Client to use for interacting with the Nextmv Cloud API."""

    endpoint: str = "v1/account"
    """Base endpoint for the account."""

    def queue(self) -> Queue:
        """Get the queue of runs in the account.

        Returns:
            Queue: Queue of runs in the account.

        Raises:
            requests.HTTPError: If the response status code is not 2xx.
        """
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint + "/queue",
        )

        return Queue.from_dict(response.json())
