"""This module contains the declarations for secrets management."""

from datetime import datetime
from enum import Enum

from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel


class SecretsCollectionSummary(BaseModel):
    """The summary of a secrets collection, which is a mechanism for hosting
    secrets securely in the Nextmv Cloud."""

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
    """Type of the secret that is stored in the Nextmv Cloud."""

    ENV = "env"
    """Environment variable secret type."""
    FILE = "file"
    """File secret type."""


class Secret(BaseModel):
    """A secret is a piece of sensitive information that is stored securely in
    the Nextmv Cloud."""

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
    Nextmv Cloud."""

    secrets: list[Secret]
    """List of secrets in the collection."""
