"""
Integration module for interacting with Nextmv Cloud integrations.

This module provides functionality to interact with integrations in Nextmv
Cloud, including integration management.

Classes
-------
IntegrationType
    Enum representing the type of an integration.
IntegrationProvider
    Enum representing the provider of an integration.
Integration
    Class representing an integration in Nextmv Cloud.

Functions
---------
list_integrations
    Function to list all integrations in Nextmv Cloud.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.manifest import ManifestType
from nextmv.safe import safe_id


class IntegrationType(str, Enum):
    """
    The type of an integration.

    You can import the `IntegrationType` class directly from `cloud`:

    ```python
    from nextmv.cloud import IntegrationType
    ```

    Attributes
    ----------
    RUNTIME : str
        Indicates a runtime integration.
    DATA : str
        Indicates a data integration.
    """

    RUNTIME = "runtime"
    """Indicates a runtime integration."""
    DATA = "data"
    """Indicates a data integration."""


class IntegrationProvider(str, Enum):
    """
    The provider of an integration.

    You can import the `IntegrationProvider` class directly from `cloud`:

    ```python
    from nextmv.cloud import IntegrationProvider
    ```

    Attributes
    ----------
    DBX : str
        Indicates a Databricks integration.
    UNKNOWN : str
        Indicates an unknown integration provider.
    """

    DBX = "dbx"
    """Indicates a Databricks integration."""
    UNKNOWN = "unknown"
    """Indicates an unknown integration provider."""


class Integration(BaseModel):
    """
    Represents an integration in Nextmv Cloud. An integration allows Nextmv
    Cloud to communicate with external systems or services.

    You can import the `Integration` class directly from `cloud`:

    ```python
    from nextmv.cloud import Integration
    ```

    You can use the `Integration.get` class method to retrieve an existing
    integration from Nextmv Cloud, to ensure that all fields are properly
    populated.

    Parameters
    ----------
    integration_id : str
        The unique identifier of the integration.
    client : Client
        Client to use for interacting with the Nextmv Cloud API.
    name : str, optional
        The name of the integration.
    description : str, optional
        An optional description of the integration.
    is_global : bool, optional
        Indicates whether the integration is global (available to all
        applications in the account).
    application_ids : list[str], optional
        List of application IDs that have access to this integration.
    integration_type : IntegrationType, optional
        The type of the integration (runtime or data).
    exec_types : list[ManifestType], optional
        List of execution types supported by the integration.
    provider : IntegrationProvider, optional
        The provider of the integration.
    provider_config : dict[str, Any], optional
        Configuration specific to the integration provider.
    created_at : datetime, optional
        The timestamp when the integration was created.
    updated_at : datetime, optional
        The timestamp when the integration was last updated.
    """

    integration_id: str = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "integration_id"),
    )
    """The unique identifier of the integration."""
    client: Client = Field(exclude=True)
    """Client to use for interacting with the Nextmv Cloud API."""

    name: str | None = None
    """The name of the integration."""
    description: str | None = None
    """An optional description of the integration."""
    is_global: bool = Field(
        serialization_alias="global",
        validation_alias=AliasChoices("global", "is_global"),
        default=False,
    )
    """
    Indicates whether the integration is global (available to all
    applications in the account).
    """
    application_ids: list[str] | None = None
    """
    List of application IDs that have access to this integration.
    """
    integration_type: IntegrationType | None = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "integration_type"),
        default=None,
    )
    """The type of the integration (runtime or data)."""
    exec_types: list[ManifestType] | None = None
    """List of execution types supported by the integration."""
    provider: IntegrationProvider | None = None
    """The provider of the integration."""
    provider_config: dict[str, Any] | None = None
    """Configuration specific to the integration provider."""
    created_at: datetime | None = None
    """The timestamp when the integration was created."""
    updated_at: datetime | None = None
    """The timestamp when the integration was last updated."""
    endpoint: str = Field(
        exclude=True,
        default="v1/integrations/{id}",
    )
    """Base endpoint for the integration."""

    def model_post_init(self, __context) -> None:
        """
        Validations done after model initialization.
        """

        self.endpoint = self.endpoint.format(id=self.integration_id)

    @classmethod
    def get(cls, client: Client, integration_id: str) -> "Integration":
        """
        Retrieve an existing integration from Nextmv Cloud.

        This method should be used for validating that the integration exists,
        and not rely simply on instantiating the `Integration` class. Using
        this method ensures that all the fields of the `Integration` class are
        properly populated.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        integration_id : str
            The unique identifier of the integration to retrieve.

        Returns
        -------
        Integration
            The retrieved integration instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import Client, Integration
        >>> client = Client(api_key="your_api_key")
        >>> integration = Integration.get(client=client, integration_id="your_integration_id")
        >>> print(integration.to_dict())
        """

        response = client.request(
            method="GET",
            endpoint=f"v1/integrations/{integration_id}",
        )
        response_dict = response.json()
        response_dict["client"] = client

        return cls.from_dict(response_dict)

    @classmethod
    def new(  # noqa: C901
        cls,
        client: Client,
        integration_type: IntegrationType | str,
        exec_types: list[ManifestType | str],
        provider: IntegrationProvider | str,
        provider_config: dict[str, Any],
        integration_id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        is_global: bool = False,
        application_ids: list[str] | None = None,
        exist_ok: bool = False,
    ) -> "Integration":
        """
        Create a new integration directly in Nextmv Cloud.

        Parameters
        ----------
        client : Client
            Client to use for interacting with the Nextmv Cloud API.
        integration_type : IntegrationType | str
            The type of the integration. Please refer to the `IntegrationType`
            enum for possible values.
        exec_types : list[ManifestType | str]
            List of execution types supported by the integration. Please refer
            to the `ManifestType` enum for possible values.
        provider : IntegrationProvider | str
            The provider of the integration. Please refer to the
            `IntegrationProvider` enum for possible values.
        provider_config : dict[str, Any]
            Configuration specific to the integration provider.
        integration_id : str, optional
            The unique identifier of the integration. If not provided,
            it will be generated automatically.
        name : str | None, optional
            The name of the integration. If not provided, the integration ID
            will be used as the name.
        description : str, optional
            An optional description of the integration.
        is_global : bool, optional, default=False
            Indicates whether the integration is global (available to all
            applications in the account). Default is False.
        application_ids : list[str], optional
            List of application IDs that have access to this integration.
        exist_ok : bool, default=False
            If True and an integration with the same ID already exists,
            return the existing integration instead of creating a new one.

        Returns
        -------
        Integration
            The created integration instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If both `is_global` is True and `application_ids` is provided.

        Examples
        --------
        >>> from nextmv.cloud import Client, Integration, IntegrationType, IntegrationProvider, ManifestType
        >>> client = Client(api_key="your_api_key")
        >>> integration = Integration.new(
        ...     client=client,
        ...     name="my_integration",
        ...     integration_type=IntegrationType.RUNTIME,
        ...     exec_types=[ManifestType.PYTHON],
        ...     provider=IntegrationProvider.DBX,
        ...     provider_config={"config_key": "config_value"},
        ... )
        >>> print(integration.to_dict())
        """

        if is_global and application_ids is not None:
            raise ValueError("An integration cannot be global and have specific application IDs.")
        elif not is_global and application_ids is None:
            raise ValueError("A non-global integration must have specific application IDs.")

        if integration_id is None or integration_id == "":
            integration_id = safe_id("integration")
        if name is None or name == "":
            name = integration_id

        if exist_ok:
            try:
                integration = cls.get(client=client, integration_id=integration_id)
                return integration
            except Exception:
                pass

        if not isinstance(integration_type, IntegrationType):
            integration_type = IntegrationType(integration_type)

        if not all(isinstance(exec_type, ManifestType) for exec_type in exec_types):
            exec_types = [ManifestType(exec_type) for exec_type in exec_types]

        if not isinstance(provider, IntegrationProvider):
            provider = IntegrationProvider(provider)

        payload = {
            "id": integration_id,
            "name": name,
            "global": is_global,
            "type": integration_type.value,
            "exec_types": [exec_type.value for exec_type in exec_types],
            "provider": provider.value,
            "provider_config": provider_config,
        }

        if description is not None:
            payload["description"] = description

        if application_ids is not None:
            payload["application_ids"] = application_ids

        response = client.request(
            method="POST",
            endpoint="v1/integrations",
            payload=payload,
        )
        response_dict = response.json()
        response_dict["client"] = client
        integration = cls.from_dict(response_dict)

        return integration

    def delete(self) -> None:
        """
        Deletes the integration from Nextmv Cloud.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import Client, Integration
        >>> client = Client(api_key="your_api_key")
        >>> integration = Integration.get(client=client, integration_id="your_integration_id")
        >>> integration.delete()
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=self.endpoint,
        )

    def update(  # noqa: C901
        self,
        name: str | None = None,
        integration_type: IntegrationType | str | None = None,
        exec_types: list[ManifestType | str] | None = None,
        provider: IntegrationProvider | str | None = None,
        provider_config: dict[str, Any] | None = None,
        description: str | None = None,
        is_global: bool | None = None,
        application_ids: list[str] | None = None,
    ) -> "Integration":
        """
        Updates the integration in Nextmv Cloud.

        Parameters
        ----------
        name : str, optional
            The new name of the integration.
        integration_type : IntegrationType | str, optional
            The new type of the integration. Please refer to the `IntegrationType`
            enum for possible values.
        exec_types : list[ManifestType | str], optional
            New list of execution types supported by the integration. Please refer
            to the `ManifestType` enum for possible values.
        provider : IntegrationProvider | str, optional
            The new provider of the integration. Please refer to the
            `IntegrationProvider` enum for possible values.
        provider_config : dict[str, Any], optional
            New configuration specific to the integration provider.
        description : str, optional
            The new description of the integration.
        is_global : bool, optional
            Indicates whether the integration is global (available to all
            applications in the account). If not provided, the current value
            is preserved.
        application_ids : list[str], optional
            New list of application IDs that have access to this integration.

        Returns
        -------
        Integration
            The updated integration instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import Client, Integration
        >>> client = Client(api_key="your_api_key")
        >>> integration = Integration.get(client=client, integration_id="your_integration_id")
        >>> updated_integration = integration.update(name="new_name")
        >>> print(updated_integration.to_dict())
        """

        integration = self.get(client=self.client, integration_id=self.integration_id)
        integration_dict = integration.to_dict()
        payload = integration_dict.copy()

        if name is not None:
            payload["name"] = name

        if integration_type is not None:
            if not isinstance(integration_type, IntegrationType):
                integration_type = IntegrationType(integration_type)
            payload["type"] = integration_type.value

        if exec_types is not None:
            if not all(isinstance(exec_type, ManifestType) for exec_type in exec_types):
                exec_types = [ManifestType(exec_type) for exec_type in exec_types]
            payload["exec_types"] = [exec_type.value for exec_type in exec_types]

        if provider is not None:
            if not isinstance(provider, IntegrationProvider):
                provider = IntegrationProvider(provider)
            payload["provider"] = provider.value

        if provider_config is not None:
            payload["provider_config"] = provider_config

        if description is not None:
            payload["description"] = description

        if is_global is not None:
            payload["global"] = is_global

        if application_ids is not None:
            payload["application_ids"] = application_ids

        # Final validation: ensure invariants are met.
        if payload["global"] is True and payload.get("application_ids"):
            raise ValueError(
                "An integration cannot be global and have application_ids. "
                "To make an integration global, call update(is_global=True, application_ids=[])."
            )
        if payload["global"] is False and not payload.get("application_ids"):
            raise ValueError(
                "A non-global integration must have specific application IDs. "
                "Provide application_ids with at least one ID, or set is_global=True."
            )

        response = self.client.request(
            method="PUT",
            endpoint=self.endpoint,
            payload=payload,
        )
        response_dict = response.json()
        response_dict["client"] = self.client
        integration = self.from_dict(response_dict)

        return integration


def list_integrations(client: Client) -> list[Integration]:
    """
    List all integrations in Nextmv Cloud for the given client.

    You can import the `list_integrations` method directly from `cloud`:

    ```python
    from nextmv.cloud import list_integrations
    ```

    Parameters
    ----------
    client : Client
        Client to use for interacting with the Nextmv Cloud API.

    Returns
    -------
    list[Integration]
        List of integrations.

    Raises
    ------
    requests.HTTPError
        If the response status code is not 2xx.

    Examples
    --------
    >>> from nextmv.cloud import Client, list_integrations
    >>> client = Client(api_key="your_api_key")
    >>> integrations = list_integrations(client=client)
    >>> for integration in integrations:
    ...     print(integration.to_dict())
    """

    response = client.request(
        method="GET",
        endpoint="v1/integrations",
    )
    response_dict = response.json()
    integrations = []
    for integration_data in response_dict.get("items", []):
        integration_data["client"] = client
        integration = Integration.from_dict(integration_data)
        integrations.append(integration)

    return integrations
