"""
Application mixin for managing app secrets.
"""

from typing import TYPE_CHECKING, Any

from nextmv.cloud.secrets import (
    Secret,
    SecretOperation,
    SecretOperationType,
    SecretsCollection,
    SecretsCollectionSummary,
)
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

    def list_secrets_collections(self: "Application", no_pagination: bool = False) -> list[SecretsCollectionSummary]:
        """
        List all secrets collections.

        Pagination is enabled by default, but you can disable it with the
        `no_pagination` argument. With pagination enabled, this function will make
        multiple API calls if necessary to retrieve all entities.

        Parameters
        ----------
        no_pagination : bool, default=False
            Whether to disable pagination when listing entities.

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

        func = self.client.request if no_pagination else self.client.request_with_pagination
        response = func(
            method="GET",
            endpoint=f"{self.endpoint}/secrets",
        )
        response_secrets = response.json().get("items", []) if no_pagination else response

        return [SecretsCollectionSummary.from_dict(secrets) for secrets in response_secrets]

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

    def patch_secrets_collection(
        self: "Application",
        secrets_collection_id: str,
        name: str | None = None,
        description: str | None = None,
        operations: list[SecretOperation | dict[str, Any]] | None = None,
    ) -> SecretsCollection:
        """
        Partially update a secrets collection.

        This method updates the name and/or description of a secrets
        collection, and/or creates, updates, or deletes individual secrets,
        without resending the values of the secrets that are not being
        changed. Secrets are identified by their `(type, location)` pair. The
        request is applied completely or not at all.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to update.
        name : Optional[str], default=None
            Optional new name for the secrets collection.
        description : Optional[str], default=None
            Optional new description for the secrets collection.
        operations : Optional[list[SecretOperation | dict[str, Any]]], default=None
            Optional list of operations to apply to individual secrets. Each
            operation should be an instance of the SecretOperation class, or a
            dict with the same fields.

        Returns
        -------
        SecretsCollection
            The updated secrets collection. Secret values are masked in the
            response.

        Raises
        ------
        ValueError
            If there is nothing to update, if `operations` is an empty list,
            if an operation is not a SecretOperation or dict, or if more than
            one operation targets the same secret.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> from nextmv.cloud import SecretOperation, SecretOperationType, SecretType
        >>> # Rename a collection without touching its secrets
        >>> collection = app.patch_secrets_collection("api-secrets", name="API Secrets")
        >>> # Rotate one secret and remove another
        >>> collection = app.patch_secrets_collection(
        ...     secrets_collection_id="api-secrets",
        ...     operations=[
        ...         SecretOperation(
        ...             op=SecretOperationType.UPDATE,
        ...             secret_type=SecretType.ENV,
        ...             location="API_KEY",
        ...             value="new-api-key",
        ...         ),
        ...         SecretOperation(
        ...             op=SecretOperationType.DELETE,
        ...             secret_type=SecretType.ENV,
        ...             location="OLD_API_KEY",
        ...         ),
        ...     ],
        ... )
        """

        if name is None and description is None and operations is None:
            raise ValueError("at least one of name, description, or operations must be provided")

        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        if operations is not None:
            if len(operations) == 0:
                raise ValueError("operations must not be an empty list")

            operations_dicts = []
            seen = set()
            for ix, operation in enumerate(operations):
                if isinstance(operation, dict):
                    operation = SecretOperation.from_dict(operation)
                elif not isinstance(operation, SecretOperation):
                    raise ValueError(f"operation at index {ix} must be either a SecretOperation or dict object")

                key = (operation.secret_type, operation.location)
                if key in seen:
                    raise ValueError(f"operation at index {ix} targets the same secret as a previous operation")
                seen.add(key)

                operations_dicts.append(operation.to_dict())

            payload["operations"] = operations_dicts

        response = self.client.request(
            method="PATCH",
            endpoint=f"{self.endpoint}/secrets/{secrets_collection_id}",
            payload=payload,
        )

        return SecretsCollection.from_dict(response.json())

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

        The update is done through the partial-update (PATCH) endpoint, so
        previously fetched secret values are never sent back to the server.
        If `secrets` is not provided, only the name and/or description are
        updated, and the secrets in the collection are left untouched. If
        `secrets` is provided, all the existing secrets in the collection are
        replaced with the given ones: secrets with a matching type and
        location are updated, new ones are created, and the rest are deleted.
        To create, update, or delete individual secrets without resending the
        values of the others, use `patch_secrets_collection` instead.

        Parameters
        ----------
        secrets_collection_id : str
            ID of the secrets collection to update.
        name : Optional[str], default=None
            Optional new name for the secrets collection.
        description : Optional[str], default=None
            Optional new description for the secrets collection.
        secrets : Optional[list[Secret | dict[str, Any]]], default=None
            Optional list of secrets that replaces all the existing secrets in
            the collection. Each secret should be an instance of the Secret
            class containing a type, location, and value.

        Returns
        -------
        SecretsCollectionSummary
            Summary of the updated secrets collection including its metadata.

        Raises
        ------
        ValueError
            If there is nothing to update, or if a secret is not a Secret or
            dict object.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Rename a secrets collection, keeping its secrets as they are
        >>> updated_collection = app.update_secrets_collection(
        ...     secrets_collection_id="api-secrets",
        ...     name="Updated API Secrets",
        ... )
        >>> # Replace all the secrets in a collection
        >>> from nextmv.cloud import Secret, SecretType
        >>> updated_secrets = [
        ...     Secret(secret_type=SecretType.ENV, location="API_KEY", value="new-api-key"),
        ...     Secret(secret_type=SecretType.ENV, location="DATABASE_URL", value="new-database-url"),
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

        if secrets is None or len(secrets) == 0:
            if name is None and description is None:
                raise ValueError("at least one of name, description, or secrets must be provided")

            return self.patch_secrets_collection(
                secrets_collection_id=secrets_collection_id,
                name=name,
                description=description,
            )

        new_secrets: list[Secret] = []
        for ix, secret in enumerate(secrets):
            if isinstance(secret, dict):
                new_secrets.append(Secret.from_dict(secret))
            elif isinstance(secret, Secret):
                new_secrets.append(secret)
            else:
                raise ValueError(f"secret at index {ix} must be either a Secret or dict object")

        # Replacing all the secrets is expressed as partial-update operations
        # against the keys of the existing secrets. Only the keys of the
        # fetched secrets are used: their values, which may be masked, are
        # never sent back to the server.
        collection = self.secrets_collection(secrets_collection_id)
        existing_keys = {(secret.secret_type, secret.location) for secret in collection.secrets}
        new_keys = {(secret.secret_type, secret.location) for secret in new_secrets}

        operations = [
            SecretOperation(
                op=SecretOperationType.UPDATE
                if (secret.secret_type, secret.location) in existing_keys
                else SecretOperationType.CREATE,
                secret_type=secret.secret_type,
                location=secret.location,
                value=secret.value,
            )
            for secret in new_secrets
        ]
        operations.extend(
            SecretOperation(op=SecretOperationType.DELETE, secret_type=secret_type, location=location)
            for secret_type, location in sorted(existing_keys - new_keys)
        )

        return self.patch_secrets_collection(
            secrets_collection_id=secrets_collection_id,
            name=name,
            description=description,
            operations=operations,
        )
