"""
Marketplace module for interacting with Nextmv Marketplace.

This module provides functionality to interact with the Nextmv Marketplace,
including marketplace application management, versioning, and subscription
management.

Classes
-------
MarketplaceState
    Enumeration of marketplace application states.
MarketplaceVersion
    A marketplace application version in Nextmv Cloud.
MarketplaceApplication
    A marketplace application in Nextmv Cloud.
MarketplaceSubscription
    A marketplace subscription in Nextmv Cloud.

Functions
---------
list_marketplace_applications
    List all marketplace applications.
list_marketplace_subscriptions
    List all marketplace subscriptions.
"""

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.safe import safe_id


class MarketplaceState(str, Enum):
    """
    Enumeration of marketplace application states.

    You can import the `MarketplaceState` class directly from `cloud`:

    ```python
    from nextmv.cloud import MarketplaceState
    ```

    Attributes
    ----------
    RELEASED : str
        The application is released and available in the marketplace.
    PRE_RELEASE : str
        The application is in pre-release state.
    RETRACTED : str
        The application has been retracted from the marketplace.
    """

    RELEASED = "released"
    """The application is released and available in the marketplace."""
    PRE_RELEASE = "pre-release"
    """The application is in pre-release state."""
    RETRACTED = "retracted"
    """The application has been retracted from the marketplace."""


class MarketplaceVersion(BaseModel):
    """
    A marketplace application version in Nextmv Cloud.

    You can import the `MarketplaceVersion` class directly from `cloud`:

    ```python
    from nextmv.cloud import MarketplaceVersion
    ```

    Attributes
    ----------
    version_id : str
        The unique identifier of the marketplace application version.
    change_log : list[str]
        The changelog for the marketplace application version.
    app_id : str
        The unique identifier of the marketplace application.
    partner_id : str
        The unique identifier of the partner that created the marketplace application.
    created_at : datetime | None
        The date and time when the marketplace application version was created.
    updated_at : datetime | None
        The date and time when the marketplace application version was last updated.
    """

    version_id: str = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "version_id"),
    )
    """The unique identifier of the marketplace application version."""
    change_log: list[str]
    """The changelog for the marketplace application version."""
    app_id: str
    """The unique identifier of the marketplace application."""
    partner_id: str
    """The unique identifier of the partner that created the marketplace application."""
    created_at: datetime | None = None
    """The date and time when the marketplace application version was created."""
    updated_at: datetime | None = None
    """The date and time when the marketplace application version was last updated."""


class MarketplaceApplication(BaseModel):
    """
    A marketplace application in Nextmv Cloud.

    You can import the `MarketplaceApplication` class directly from `cloud`:

    ```python
    from nextmv.cloud import MarketplaceApplication
    ```

    Attributes
    ----------
    app_id : str
        The unique identifier of the marketplace application.
    reference_app_id : str
        The unique identifier of the reference application.
    partner_id : str
        The unique identifier of the partner that created the marketplace
        application.
    title : str
        The title of the marketplace application.
    state : MarketplaceState
        The state of the marketplace application.
    description : str | None
        The description of the marketplace application.
    categories : list[str] | None
        The categories of the marketplace application.
    features : list[str] | None
        The features of the marketplace application.
    created_at : datetime | None
        The date and time when the marketplace application was created.
    updated_at : datetime | None
        The date and time when the marketplace application was last updated.
    latest_versions : list[str] | None
        The latest versions of the marketplace application.
    client : Client
        Client to use for interacting with the Nextmv Cloud API. This is an
        SDK-specific attribute and it is not part of the API representation of
        a marketplace application.
    endpoint : str
        Base endpoint for the application. This is an SDK-specific attribute and
        it is not part of the API representation of a marketplace application.
    """

    app_id: str = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "app_id"),
    )
    """The unique identifier of the marketplace application."""
    partner_id: str
    """
    The unique identifier of the partner that created the marketplace
    application.
    """
    title: str
    """The title of the marketplace application."""
    state: MarketplaceState
    """The state of the marketplace application."""
    reference_app_id: str | None = Field(
        serialization_alias="ref_app_id",
        validation_alias=AliasChoices("ref_app_id", "reference_app_id"),
        default=None,
    )
    """The unique identifier of the reference application."""
    description: str | None = None
    """The description of the marketplace application."""
    categories: list[str] | None = None
    """The categories of the marketplace application."""
    features: list[str] | None = None
    """The features of the marketplace application."""
    created_at: datetime | None = None
    """The date and time when the marketplace application was created."""
    updated_at: datetime | None = None
    """The date and time when the marketplace application was last updated."""
    latest_versions: list[str] | None = None
    """The latest versions of the marketplace application."""

    # SDK-specific attributes for convenience when using methods.
    client: Client = Field(exclude=True)
    """
    Client to use for interacting with the Nextmv Cloud API. This is an
    SDK-specific attribute and it is not part of the API representation of a
    marketplace application.
    """
    endpoint: str = Field(exclude=True, default="v1/marketplace/partners/{partner_id}/apps/{app_id}")
    """
    Base endpoint for the application. This is an SDK-specific attribute and it
    is not part of the API representation of a marketplace application.
    """

    def model_post_init(self, __context) -> None:
        """
        Initialize the endpoint attributes.

        This method is called after the model is initialized.
        """
        self.endpoint = self.endpoint.format(partner_id=self.partner_id, app_id=self.app_id)

    @classmethod
    def get(
        cls,
        client: Client,
        partner_id: str,
        app_id: str,
    ) -> "MarketplaceApplication":
        """
        Get a marketplace application by its ID.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        partner_id : str
            The unique identifier of the partner that created the marketplace
            application.
        app_id : str
            The unique identifier of the marketplace application.

        Returns
        -------
        MarketplaceApplication
            The marketplace application with the specified ID.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = client.request(
            method="GET",
            endpoint=f"v1/marketplace/partners/{partner_id}/apps/{app_id}",
        )

        return cls.from_dict({"client": client} | response.json())

    @classmethod
    def new(
        cls,
        client: Client,
        partner_id: str,
        reference_app_id: str,
        title: str,
        app_id: str | None = None,
        description: str | None = None,
        categories: list[str] | None = None,
        features: list[str] | None = None,
    ) -> "MarketplaceApplication":
        """
        Create a new marketplace application.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        partner_id : str
            The unique identifier of the partner that is creating the marketplace
            application.
        reference_app_id : str
            The unique identifier of the reference application.
        title : str
            The title of the marketplace application.
        app_id : str | None, optional
            The unique identifier of the marketplace application. If not provided,
            a safe ID will be generated. (default is None)
        description : str | None, optional
            The description of the marketplace application. (default is None)
        categories : list[str] | None, optional
            The categories of the marketplace application. (default is None)
        features : list[str] | None, optional
            The features of the marketplace application. (default is None)

        Returns
        -------
        MarketplaceApplication
            The newly created marketplace application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        if not app_id:
            app_id = safe_id("marketplace-app")

        payload = {
            "id": app_id,
            "ref_app_id": reference_app_id,
            "title": title,
        }

        if description:
            payload["description"] = description
        if categories:
            payload["categories"] = categories
        if features:
            payload["features"] = features

        response = client.request(
            method="POST",
            endpoint=f"v1/marketplace/partners/{partner_id}/apps",
            payload=payload,
        )

        return cls.from_dict({"client": client} | response.json())

    def list_versions(self) -> list[MarketplaceVersion]:
        """
        List all versions of the marketplace application.

        Returns
        -------
        list[MarketplaceVersion]
            A list of all versions of the marketplace application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions",
        )

        versions = []
        for version_data in response.json() or []:
            version = MarketplaceVersion.from_dict(version_data)
            versions.append(version)

        return versions

    def new_version(
        self,
        change_log: list[str],
        reference_version_id: str,
        version_id: str | None = None,
    ) -> MarketplaceVersion:
        """
        Create a new version of the marketplace application.

        Parameters
        ----------
        change_log : list[str]
            The changelog for the new version of the marketplace application.
        reference_version_id : str
            The unique identifier of the reference version.
        version_id : str | None, optional
            The unique identifier of the new version. If not provided, a safe ID
            will be generated. (default is None)

        Returns
        -------
        MarketplaceVersion
            The newly created marketplace application version.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        if not version_id:
            version_id = safe_id("marketplace-version")

        payload = {
            "id": version_id,
            "change_log": change_log,
            "ref_app_version_id": reference_version_id,
        }

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/versions",
            payload=payload,
        )

        return MarketplaceVersion.from_dict(response.json())

    def update(
        self,
        title: str | None = None,
        description: str | None = None,
        categories: list[str] | None = None,
        features: list[str] | None = None,
        state: MarketplaceState | None = None,
    ) -> "MarketplaceApplication":
        """
        Update the marketplace application.

        Parameters
        ----------
        title : str | None, optional
            The new title of the marketplace application. (default is None)
        description : str | None, optional
            The new description of the marketplace application. (default is None)
        categories : list[str] | None, optional
            The new categories of the marketplace application. (default is None)
        features : list[str] | None, optional
            The new features of the marketplace application. (default is None)
        state : MarketplaceState | None, optional
            The new state of the marketplace application. (default is None)
        Returns
        -------
        MarketplaceApplication
            The updated marketplace application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        app = self.get(client=self.client, partner_id=self.partner_id, app_id=self.app_id)
        app_dict = app.to_dict()
        payload = app_dict.copy()

        if title:
            payload["title"] = title
        if description:
            payload["description"] = description
        if categories:
            payload["categories"] = categories
        if features:
            payload["features"] = features
        if state:
            payload["state"] = state

        response = self.client.request(
            method="PUT",
            endpoint=self.endpoint,
            payload=payload,
        )

        return MarketplaceApplication.from_dict({"client": self.client} | response.json())

    def update_version(
        self,
        version_id: str,
        change_log: list[str],
    ) -> MarketplaceVersion:
        """
        Update a version of the marketplace application.

        Parameters
        ----------
        version_id : str
            The unique identifier of the marketplace application version to update.
        change_log : list[str]
            The new changelog for the marketplace application version.

        Returns
        -------
        MarketplaceVersion
            The updated marketplace application version.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        payload = {
            "change_log": change_log,
        }

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/versions/{version_id}",
            payload=payload,
        )

        return MarketplaceVersion.from_dict(response.json())

    def version(self, version_id: str) -> MarketplaceVersion:
        """
        Get a version of the marketplace application.

        Parameters
        ----------
        version_id : str
            The unique identifier of the marketplace application version to retrieve.

        Returns
        -------
        MarketplaceVersion
            The marketplace application version with the specified ID.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions/{version_id}",
        )

        return MarketplaceVersion.from_dict(response.json())


def list_marketplace_applications(client: Client, partner_id: str | None = None) -> list[MarketplaceApplication]:
    """
    List all marketplace applications.

    You can import the `list_marketplace_applications` function directly from `cloud`:

    ```python
    from nextmv.cloud import list_marketplace_applications
    ```

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    partner_id : str | None, optional
        The unique identifier of the partner to filter marketplace applications
        by. If not provided, all marketplace applications will be listed.
        (default is None)

    Returns
    -------
    list[MarketplaceApplication]
        A list of all marketplace applications.

    Raises
    ------
    requests.HTTPError
        If the response status code is not 2xx.
    """

    endpoint = "v1/marketplace/apps"
    if partner_id:
        endpoint = f"v1/marketplace/partners/{partner_id}/apps"

    response = client.request(
        method="GET",
        endpoint=endpoint,
    )

    apps = []
    for app_data in response.json() or []:
        app = MarketplaceApplication.from_dict({"client": client} | app_data)
        apps.append(app)

    return apps


class MarketplaceSubscription(BaseModel):
    """
    A marketplace subscription in Nextmv Cloud.

    You can import the `MarketplaceSubscription` class directly from `cloud`:

    ```python
    from nextmv.cloud import MarketplaceSubscription
    ```

    Attributes
    ----------
    subscription_id : str
        The unique identifier of the marketplace subscription.
    partner_name : str
        The name of the partner that created the marketplace application.
    app_title : str
        The title of the marketplace application.
    subscription_date : datetime | None
        The date and time when the marketplace subscription was created.
    client : Client
        Client to use for interacting with the Nextmv Cloud API. This is an
        SDK-specific attribute and it is not part of the API representation of a
        marketplace subscription.
    endpoint : str
        Base endpoint for the subscription. This is an SDK-specific attribute and
        it is not part of the API representation of a marketplace subscription.
    """

    subscription_id: str
    """The unique identifier of the marketplace subscription."""
    partner_name: str
    """The name of the partner that created the marketplace application."""
    app_title: str
    """The title of the marketplace application."""
    subscription_date: str | None = None
    """The date and time when the marketplace subscription was created."""

    # SDK-specific attributes for convenience when using methods.
    client: Client = Field(exclude=True)
    """
    Client to use for interacting with the Nextmv Cloud API. This is an
    SDK-specific attribute and it is not part of the API representation of a
    marketplace subscription.
    """
    endpoint: str = Field(exclude=True, default="v1/marketplace/subscriptions/{subscription_id}")
    """
    Base endpoint for the subscription. This is an SDK-specific attribute and it
    is not part of the API representation of a marketplace subscription.
    """

    def model_post_init(self, __context) -> None:
        """
        Initialize the endpoint attributes.

        This method is called after the model is initialized.
        """
        self.endpoint = self.endpoint.format(subscription_id=self.subscription_id)

    @classmethod
    def get(
        cls,
        client: Client,
        subscription_id: str,
    ) -> "MarketplaceSubscription":
        """
        Get a marketplace subscription by its ID.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        subscription_id : str
            The unique identifier of the marketplace subscription.

        Returns
        -------
        MarketplaceSubscription
            The marketplace subscription with the specified ID.
        """
        response = client.request(
            method="GET",
            endpoint=f"v1/marketplace/subscriptions/{subscription_id}",
        )

        return cls.from_dict({"client": client} | response.json())

    @classmethod
    def new(cls, client: Client, subscription_id: str) -> "MarketplaceSubscription":
        """
        Create a new marketplace subscription.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        subscription_id : str
            The unique identifier of the marketplace subscription.

        Returns
        -------
        MarketplaceSubscription
            The newly created marketplace subscription.
        """

        payload = {
            "subscription_id": subscription_id,
        }

        response = client.request(
            method="POST",
            endpoint="v1/marketplace/subscriptions",
            payload=payload,
        )

        return cls.from_dict({"client": client} | response.json())

    def delete(self) -> None:
        """
        Delete the marketplace subscription.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        self.client.request(
            method="DELETE",
            endpoint=self.endpoint,
        )


def list_marketplace_subscriptions(client: Client) -> list[MarketplaceSubscription]:
    """
    List all marketplace subscriptions.

    You can import the `list_marketplace_subscriptions` function directly from `cloud`:

    ```python
    from nextmv.cloud import list_marketplace_subscriptions
    ```

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.

    Returns
    -------
    list[MarketplaceSubscription]
        A list of all marketplace subscriptions.
    """

    response = client.request(
        method="GET",
        endpoint="v1/marketplace/subscriptions",
    )

    subscriptions = []
    for subscription_data in response.json() or []:
        subscription = MarketplaceSubscription.from_dict({"client": client} | subscription_data)
        subscriptions.append(subscription)

    return subscriptions
