"""This module contains the declarations for secrets management.

Classes
-------
SecretsCollectionSummary
    Summary of a secrets collection in Nextmv Cloud.
SecretType
    Enumeration of available secret types.
Secret
    Representation of a sensitive piece of information.
SecretsCollection
    Collection of secrets hosted in the Nextmv Cloud.

"""

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel


class SecretsCollectionSummary(BaseModel):
    """The summary of a secrets collection in the Nextmv Cloud.

    You can import the `SecretsCollectionSummary` class directly from `cloud`:

    ```python
    from nextmv.cloud import SecretsCollectionSummary
    ```

    A secrets collection is a mechanism for hosting secrets securely in the
    Nextmv Cloud. This class provides summary information about such a collection.

    Parameters
    ----------
    collection_id : str
        ID of the secrets collection. This is aliased from `id` for
        serialization and validation.
    application_id : str
        ID of the application to which the secrets collection belongs.
    name : str
        Name of the secrets collection.
    description : str
        Description of the secrets collection.
    created_at : datetime
        Creation date of the secrets collection.
    updated_at : datetime
        Last update date of the secrets collection.

    Examples
    --------
    >>> from datetime import datetime
    >>> collection_summary = SecretsCollectionSummary(
    ...     collection_id="col_123",
    ...     application_id="app_456",
    ...     name="My API Credentials",
    ...     description="Collection of API keys for external services",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now()
    ... )
    >>> print(collection_summary.name)
    My API Credentials

    """

    collection_id: str = Field(
        serialization_alias="id",
        validation_alias=AliasChoices("id", "collection_id"),
    )
    """ID of the secrets collection."""
    application_id: str
    """ID of the application to which the secrets collection belongs."""
    name: str
    """Name of the secrets collection."""
    description: str
    """Description of the secrets collection."""
    created_at: datetime
    """Creation date of the secrets collection."""
    updated_at: datetime
    """Last update date of the secrets collection."""


class SecretType(str, Enum):
    """Type of the secret that is stored in the Nextmv Cloud.

    You can import the `SecretType` class directly from `cloud`:

    ```python
    from nextmv.cloud import SecretType
    ```

    This enumeration defines the types of secrets that can be managed.

    Attributes
    ----------
    ENV : str
        Represents an environment variable secret. The value of the secret
        will be available as an environment variable in the execution
        environment.
    FILE : str
        Represents a file-based secret. The value of the secret will be
        written to a file, and the path to this file will be available
        via the `location` attribute of the `Secret`.

    Examples
    --------
    >>> secret_type_env = SecretType.ENV
    >>> print(secret_type_env.value)
    env
    >>> secret_type_file = SecretType.FILE
    >>> print(secret_type_file.value)
    file

    """

    ENV = "env"
    """Environment variable secret type."""
    FILE = "file"
    """File secret type."""


class Secret(BaseModel):
    """A secret is a piece of sensitive information that is stored securely in
    the Nextmv Cloud.

    You can import the `Secret` class directly from `cloud`:

    ```python
    from nextmv.cloud import Secret
    ```

    This class represents an individual secret, detailing its type, location
    (if applicable), and value.

    Parameters
    ----------
    secret_type : SecretType
        The type of the secret, indicating how it should be handled (e.g.,
        as an environment variable or a file). This is aliased from `type`
        for serialization and validation.
    location : str
        The location where the secret will be made available. For `ENV`
        type secrets, this is the name of the environment variable. For
        `FILE` type secrets, this is the path where the file will be
        created.
    value : str
        The actual content of the secret.

    Examples
    --------
    >>> env_secret = Secret(
    ...     secret_type=SecretType.ENV,
    ...     location="API_KEY",
    ...     value="supersecretapikey123"
    ... )
    >>> print(env_secret.location)
    API_KEY
    >>> file_secret = Secret(
    ...     secret_type=SecretType.FILE,
    ...     location="/mnt/secrets/config.json",
    ...     value=\'\'\'{"user": "admin", "pass": "secure"}\'\'\'
    ... )
    >>> print(file_secret.secret_type)
    SecretType.FILE

    """

    secret_type: SecretType = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "secret_type"),
    )
    """Type of the secret."""
    location: str
    """Location of the secret."""
    value: str
    """Value of the secret."""


class SecretsCollection(SecretsCollectionSummary, BaseModel):
    """A secrets collection is a mechanism for hosting secrets securely in the
    Nextmv Cloud.

    You can import the `SecretsCollection` class directly from `cloud`:

    ```python
    from nextmv.cloud import SecretsCollection
    ```

    This class extends `SecretsCollectionSummary` by including the actual list
    of secrets contained within the collection.

    Parameters
    ----------
    secrets : list[Secret]
        A list of `Secret` objects that are part of this collection.
    *args
        Variable length argument list for `SecretsCollectionSummary`.
    **kwargs
        Arbitrary keyword arguments for `SecretsCollectionSummary`.


    Examples
    --------
    >>> from datetime import datetime
    >>> secret1 = Secret(
    ...     secret_type=SecretType.ENV,
    ...     location="DATABASE_USER",
    ...     value="nextmv_user"
    ... )
    >>> secret2 = Secret(
    ...     secret_type=SecretType.FILE,
    ...     location="/etc/app/license.key",
    ...     value="longlicensekeystring"
    ... )
    >>> full_collection = SecretsCollection(
    ...     collection_id="col_789",
    ...     application_id="app_000",
    ...     name="Full App Secrets",
    ...     description="All secrets required by the main application",
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now(),
    ...     secrets=[secret1, secret2]
    ... )
    >>> print(full_collection.name)
    Full App Secrets
    >>> print(len(full_collection.secrets))
    2

    """

    secrets: list[Secret]
    """List of secrets in the collection."""
