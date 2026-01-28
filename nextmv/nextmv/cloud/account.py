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

from datetime import datetime

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.status import StatusV2


class QueuedRun(BaseModel):
    """
    A run that is pending to be executed in the account.

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
    status_v2: StatusV2
    """Status of the run."""


class Queue(BaseModel):
    """
    A queue is a list of runs that are pending to be executed, or currently
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
    >>> from nextmv.cloud import Client, Account
    >>> client = Client(api_key="your-api-key")
    >>> account = Account.get(client=client, account_id="your-account-id")
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


class AccountMember(BaseModel):
    """
    A member of a Nextmv Cloud account (organization).

    You can import the `AccountMember` class directly from `cloud`:

    ```python
    from nextmv.cloud import AccountMember
    ```

    Represents an individual member of an organization in Nextmv Cloud,
    including their role and invitation status.

    Attributes
    ----------
    email : str | None
        Email of the account member.
    role : str | None
        Role of the account member.
    pending_invite : bool | None
        Whether the member has a pending invite.

    Examples
    --------
    >>> member = AccountMember.from_dict({
    ...     "email": "peter.rabbit@carrotexpress.com",
    ...     "role": "admin",
    ...     "pending_invite": False
    ... })
    >>> print(f"{member.email} - {member.role}")
    peter.rabbit@carrotexpress.com - admin
    """

    email: str | None = None
    """Email of the account member."""
    role: str | None = None
    """Role of the account member."""
    pending_invite: bool | None = None
    """Whether the member has a pending invite."""


class Account(BaseModel):
    """
    The Nextmv Cloud account (organization).

    To handle managed accounts, SSO must be configured for your organization.
    Please contact [Nextmv support](https://www.nextmv.io/contact) for
    assistance.

    You can import the `Account` class directly from `cloud`:

    ```python
    from nextmv.cloud import Account
    ```

    This class provides access to account-level operations in the Nextmv Cloud,
    such as retrieving the queue of runs.

    Note: It is recommended to use `Account.get()` or `Account.new()`
    instead of direct initialization to ensure proper setup.

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    account_id : str, optional
        ID of the account (organization).
    name : str, optional
        Name of the account (organization).
    members : list[AccountMember], optional
        List of members in the account (organization).
    account_endpoint : str, default="v1/account"
        Base endpoint for the account (SDK-specific).
    organization_endpoint : str, default="v1/organization/{organization_id}"
        Base endpoint for organization operations (SDK-specific).

    Examples
    --------
    >>> from nextmv.cloud import Client, Account
    >>> client = Client(api_key="your-api-key")
    >>> # Retrieve an existing account
    >>> account = Account.get(client=client, account_id="your-account-id")
    >>> print(f"Account name: {account.name}")
    Account name: Bunny Logistics
    >>> # Create a new account
    >>> new_account = Account.new(client=client, name="Hare Delivery Co", admins=["admin@example.com"])
    >>> # Get the queue of runs
    >>> queue = account.queue()
    >>> print(f"Number of runs in queue: {len(queue.runs)}")
    Number of runs in queue: 3
    """

    # Actual API attributes of an account.
    account_id: str | None = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "account_id"),
        default=None,
    )
    """ID of the account (organization)."""
    name: str | None = None
    """Name of the account (organization)."""
    members: list[AccountMember] | None = None
    """List of members in the account (organization)."""

    # SDK-specific attributes for convenience when using methods.
    client: Client = Field(exclude=True)
    """Client to use for interacting with the Nextmv Cloud API."""
    account_endpoint: str = Field(exclude=True, default="v1/account")
    """Base endpoint for the account."""
    organization_endpoint: str = Field(exclude=True, default="v1/organization/{organization_id}")

    def model_post_init(self, __context) -> None:
        """
        Initialize the organization_endpoint attribute.

        This method is automatically called after class initialization to
        format the organization_endpoint URL with the account ID.
        """

        self.organization_endpoint = self.organization_endpoint.format(organization_id=self.account_id)

    @classmethod
    def get(cls, client: Client, account_id: str) -> "Account":
        """
        Retrieve an account directly from Nextmv Cloud.

        This function is useful if you want to populate an `Account` class
        by fetching the attributes directly from Nextmv Cloud.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        account_id : str
            ID of the account to retrieve.

        Returns
        -------
        Account
            The requested account.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import Client, Account
        >>> client = Client(api_key="your-api-key")
        >>> account = Account.get(client=client, account_id="bunny-logistics")
        >>> print(f"Account: {account.name}")
        Account: Bunny Logistics
        >>> print(f"Members: {len(account.members)}")
        Members: 3
        """

        response = client.request(
            method="GET",
            endpoint=f"v1/organization/{account_id}",
        )

        return cls.from_dict({"client": client} | response.json())

    @classmethod
    def new(
        cls,
        client: Client,
        name: str,
        admins: list[str],
    ) -> "Account":
        """
        Create a new account (organization) directly in Nextmv Cloud.

        To create managed accounts, SSO must be configured for your
        organization. Please contact [Nextmv
        support](https://www.nextmv.io/contact) for assistance.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        name : str
            Name of the new account.
        admins : list[str]
            List of admin user emails for the new account.

        Returns
        -------
        Account
            The newly created account.

        Examples
        --------
        >>> from nextmv.cloud import Client
        >>> client = Client(api_key="your-api-key")
        >>> account = Account.new(client=client, name="My New Account", admins=["admin@example.com"])
        """

        if len(admins) == 0:
            raise ValueError("at least one admin email must be provided to create an account")

        payload = {
            "name": name,
            "admins": admins,
        }

        response = client.request(
            method="POST",
            endpoint="v1/organization",
            payload=payload,
        )

        return cls.from_dict({"client": client} | response.json())

    def delete(self) -> None:
        """
        Delete the account.

        Permanently removes the account (organization) from Nextmv Cloud. You
        must have the administrator role on that account in order to delete it.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> account.delete()  # Permanently deletes the account
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=self.organization_endpoint,
        )

    def queue(self) -> Queue:
        """
        Get the queue of runs in the account.

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
        >>> from nextmv.cloud import Client, Account
        >>> client = Client(api_key="your-api-key")
        >>> account = Account.get(client=client, account_id="your-account-id")
        >>> queue = account.queue()
        >>> for run in queue.runs:
        ...     print(f"Run {run.id}: {run.name} - Status: {run.status_v2}")
        Run run-123: Daily Optimization - Status: RUNNING
        Run run-456: Weekly Planning - Status: QUEUED
        """
        response = self.client.request(
            method="GET",
            endpoint=self.account_endpoint + "/queue",
        )

        return Queue.from_dict(response.json())

    def update(self, name: str) -> "Account":
        """
        Update the account.

        Parameters
        ----------
        name : str
            Name of the account.

        Returns
        -------
        Account
            The updated account.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import Client, Account
        >>> client = Client(api_key="your-api-key")
        >>> account = Account.get(client=client, account_id="bunny-logistics")
        >>> updated_account = account.update(name="Bunny Express Logistics")
        >>> print(updated_account.name)
        Bunny Express Logistics
        """

        account = self.get(client=self.client, account_id=self.account_id)
        account_dict = account.to_dict()
        payload = account_dict.copy()
        payload["name"] = name

        response = self.client.request(
            method="PUT",
            endpoint=self.organization_endpoint,
            payload=payload,
        )

        return Account.from_dict({"client": self.client} | response.json())
