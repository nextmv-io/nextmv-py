"""
Application mixin for managing app secrets.
"""

from typing import TYPE_CHECKING, Any

from nextmv.cloud.secrets import Secret, SecretsCollection, SecretsCollectionSummary
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationSecretsMixin:
    """
    Mixin class for managing app secrets within an application.
    """

    def delete_secrets_collection(self: "Application", secrets_collection_id: str) -> None:
        """
        Delete a secrets collection.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_secrets_collection("secrets-123")
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

    def list_secrets_collections(self: "Application") -> list[SecretsCollectionSummary]:
        """
        List all secrets collections.

        Returns
        -------
        list[SecretsCollectionSummary]
            List of all secrets collections associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> collections = app.list_secrets_collections()
        >>> for collection in collections:
        ...     print(collection.name)
        'API Keys'
        'Database Credentials'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets",
        )

        return [SecretsCollectionSummary.from_dict(secrets) for secrets in response.json()["items"]]

    def new_secrets_collection(
        self: "Application",
        secrets: list[Secret],
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
    ) -> SecretsCollectionSummary:
        """
        Create a new secrets collection.

        This method creates a new secrets collection with the provided secrets.
        A secrets collection is a group of key-value pairs that can be used by
        your application instances during execution. If no secrets are
        provided, a ValueError is raised. If the `id` or `name` parameters are
        not provided, they will be generated based on a unique ID.

        Parameters
        ----------
        secrets : list[Secret]
            List of secrets to use for the secrets collection. Each secret
            should be an instance of the Secret class containing a key and
            value.
        id : str | None, default=None
            ID of the secrets collection. If not provided, a unique ID will be
            generated.
        name : str | None, default=None
            Name of the secrets collection. If not provided, the ID will be
            used.
        description : Optional[str], default=None
            Description of the secrets collection.

        Returns
        -------
        SecretsCollectionSummary
            Summary of the secrets collection including its metadata.

        Raises
        ------
        ValueError
            If no secrets are provided.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Create a new secrets collection with API keys
        >>> from nextmv.cloud import Secret
        >>> secrets = [
        ...     Secret(
        ...          location="API_KEY",
        ...          value="your-api-key",
        ...          secret_type=SecretType.ENV,
        ...     ),
        ...     Secret(
        ...          location="DATABASE_URL",
        ...          value="your-database-url",
        ...          secret_type=SecretType.ENV,
        ...     ),
        ... ]
        >>> collection = app.new_secrets_collection(
        ...     secrets=secrets,
        ...     id="api-secrets",
        ...     name="API Secrets",
        ...     description="Collection of API secrets for external services"
        ... )
        >>> print(collection.id)
        'api-secrets'
        """

        if len(secrets) == 0:
            raise ValueError("secrets must be provided")

        if id is None or id == "":
            id = safe_id(prefix="secrets")
        if name is None or name == "":
            name = id

        payload = {
            "id": id,
            "name": name,
            "secrets": [secret.to_dict() for secret in secrets],
        }

        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/secrets",
            payload=payload,
        )

        return SecretsCollectionSummary.from_dict(response.json())

    def secrets_collection(self: "Application", secrets_collection_id: str) -> SecretsCollection:
        """
        Get a secrets collection.

        This method retrieves a secrets collection by its ID. A secrets collection
        is a group of key-value pairs that can be used by your application
        instances during execution.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to retrieve.

        Returns
        -------
        SecretsCollection
            The requested secrets collection, including all secret values
            and metadata.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Retrieve a secrets collection
        >>> collection = app.secrets_collection("api-secrets")
        >>> print(collection.name)
        'API Secrets'
        >>> print(len(collection.secrets))
        2
        >>> for secret in collection.secrets:
        ...     print(secret.location)
        'API_KEY'
        'DATABASE_URL'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
        )

        return SecretsCollection.from_dict(response.json())

    def update_secrets_collection(
        self: "Application",
        secrets_collection_id: str,
        name: str | None = None,
        description: str | None = None,
        secrets: list[Secret | dict[str, Any]] | None = None,
    ) -> SecretsCollectionSummary:
        """
        Update a secrets collection.

        This method updates an existing secrets collection with new values for name,
        description, and secrets. A secrets collection is a group of key-value pairs
        that can be used by your application instances during execution.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to update.
        name : Optional[str], default=None
            Optional new name for the secrets collection.
        description : Optional[str], default=None
            Optional new description for the secrets collection.
        secrets : Optional[list[Secret | dict[str, Any]]], default=None
            Optional list of secrets to update. Each secret should be an
            instance of the Secret class containing a key and value.

        Returns
        -------
        SecretsCollectionSummary
            Summary of the updated secrets collection including its metadata.

        Raises
        ------
        ValueError
            If no secrets are provided.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Update an existing secrets collection
        >>> from nextmv.cloud import Secret
        >>> updated_secrets = [
        ...     Secret(key="API_KEY", value="new-api-key"),
        ...     Secret(key="DATABASE_URL", value="new-database-url")
        ... ]
        >>> updated_collection = app.update_secrets_collection(
        ...     secrets_collection_id="api-secrets",
        ...     name="Updated API Secrets",
        ...     description="Updated collection of API secrets",
        ...     secrets=updated_secrets
        ... )
        >>> print(updated_collection.id)
        'api-secrets'
        """

        collection = self.secrets_collection(secrets_collection_id)
        collection_dict = collection.to_dict()
        payload = collection_dict.copy()

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if secrets is not None and len(secrets) > 0:
            secrets_dicts = []
            for ix, secret in enumerate(secrets):
                if isinstance(secret, dict):
                    secrets_dicts.append(secret)
                elif isinstance(secret, Secret):
                    secrets_dicts.append(secret.to_dict())
                else:
                    raise ValueError(f"secret at index {ix} must be either a Secret or dict object")

            payload["secrets"] = secrets_dicts

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
            payload=payload,
        )

        return SecretsCollectionSummary.from_dict(response.json())
