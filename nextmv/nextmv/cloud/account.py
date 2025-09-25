"""
Account management functionality for the Nextmv Cloud API.

This module provides classes for interacting with account-level resources
in the Nextmv Platform, particularly for accessing and managing the queue
of runs.

Classes
-------
QueuedRun
    A run that is pending to be executed in the account.
Queue
    A list of runs that are pending or currently being executed.
Account
    The Nextmv Platform account with API access methods.
"""

from dataclasses import dataclass
from datetime import datetime

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.status import Status, StatusV2


class QueuedRun(BaseModel):
    """A run that is pending to be executed in the account.

    You can import the `QueuedRun` class directly from `cloud`:

    ```python
    from nextmv.cloud import QueuedRun
    ```

    Represents details of a run in the queue, including its status and metadata.
    QueuedRun objects are typically obtained through the Account.queue() method.

    Attributes
    ----------
    id : str
        ID of the run.
    user_email : str
        Email of the user who created the run.
    name : str
        Name of the run.
    description : str
        Description of the run.
    created_at : datetime
        Creation date of the run.
    application_id : str
        ID of the application used for the run.
    application_instance_id : str
        ID of the application instance used for the run.
    application_version_id : str
        ID of the application version used for the run.
    execution_class : str
        Execution class used for the run.
    status : Status
        Deprecated: use status_v2.
    status_v2 : StatusV2
        Status of the run.

    Examples
    --------
    >>> queued_run = QueuedRun.from_dict({
    ...     "id": "run-123456",
    ...     "user_email": "user@example.com",
    ...     "name": "My Run",
    ...     "description": "Test run",
    ...     "created_at": "2023-01-01T12:00:00Z",
    ...     "application_id": "app-123456",
    ...     "application_instance_id": "appins-123456",
    ...     "application_version_id": "appver-123456",
    ...     "execution_class": "standard",
    ...     "status": "RUNNING",
    ...     "status_v2": "RUNNING"
    ... })
    >>> print(queued_run.name)
    My Run
    """

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
    being executed, in the account.

    You can import the `Queue` class directly from `cloud`:

    ```python
    from nextmv.cloud import Queue
    ```

    The Queue object provides access to a list of queued runs in a Nextmv account.
    It is typically obtained through the Account.queue() method.

    Attributes
    ----------
    runs : list[QueuedRun]
        List of runs in the queue.

    Examples
    --------
    >>> account = Account(client=Client(api_key="your-api-key"))
    >>> queue = account.queue()
    >>> print(f"Number of runs in queue: {len(queue.runs)}")
    Number of runs in queue: 5
    >>> # Accessing the first run in the queue
    >>> if queue.runs:
    ...     print(f"First run: {queue.runs[0].name}")
    First run: My Priority Run
    """

    runs: list[QueuedRun]
    """List of runs in the queue."""


@dataclass
class Account:
    """The Nextmv Platform account.

    You can import the `Account` class directly from `cloud`:

    ```python
    from nextmv.cloud import Account
    ```

    This class provides access to account-level operations in the Nextmv Platform,
    such as retrieving the queue of runs.

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    endpoint : str, optional
        Base endpoint for the account, by default "v1/account"

    Attributes
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    endpoint : str
        Base endpoint for the account.

    Examples
    --------
    >>> from nextmv.cloud import Client, Account
    >>> client = Client(api_key="your-api-key")
    >>> account = Account(client=client)
    >>> queue = account.queue()
    >>> print(f"Number of runs in queue: {len(queue.runs)}")
    Number of runs in queue: 3
    """

    client: Client
    """Client to use for interacting with the Nextmv Cloud API."""

    endpoint: str = "v1/account"
    """Base endpoint for the account."""

    def queue(self) -> Queue:
        """Get the queue of runs in the account.

        Retrieves the current list of runs that are pending or being executed
        in the Nextmv account.

        Returns
        -------
        Queue
            Queue of runs in the account.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> account = Account(client=Client(api_key="your-api-key"))
        >>> queue = account.queue()
        >>> for run in queue.runs:
        ...     print(f"Run {run.id}: {run.name} - Status: {run.status_v2}")
        Run run-123: Daily Optimization - Status: RUNNING
        Run run-456: Weekly Planning - Status: QUEUED
        """
        response = self.client.request(
            method="GET",
            endpoint=self.endpoint + "/queue",
        )

        return Queue.from_dict(response.json())
