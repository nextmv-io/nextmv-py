"""Core managed input management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Managed inputs are reusable input data objects stored on the platform.
They can be referenced by ID when creating runs or building input sets.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    ManagedInputIdOption,
    NameOption,
    OptionalManagedInputIdOption,
)
from nextmv.cloud import Application, Client


def list_managed_inputs(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all managed inputs for a Nextmv Cloud application.

    Returns a list of managed input dicts including ID, name, and
    description. Does not return the input data itself.
    """
    app = Application(client=client, id=app_id)
    return [i.to_dict() for i in app.list_managed_inputs()]


def get_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    managed_input_id: ManagedInputIdOption,
) -> dict[str, Any]:
    """Get details of a Nextmv Cloud managed input.

    Returns the managed input metadata. Does not return the input data
    itself.
    """
    app = Application(client=client, id=app_id)
    return app.managed_input(managed_input_id=managed_input_id).to_dict()


def create_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    data: dict[str, Any] | None = None,
    managed_input_id: OptionalManagedInputIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    upload_id: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud managed input.

    Provide exactly one of:

    * ``data``: raw input data (JSON object) to upload directly.
    * ``upload_id``: a pre-existing upload ID from ``upload create``.
    * ``run_id``: copy the input from an existing run.

    When ``data`` is provided it is uploaded via a pre-signed URL first,
    and the resulting upload_id is used to create the managed input.

    Returns the created managed input dict.
    """
    app = Application(client=client, id=app_id)

    if data is not None:
        upload_url = app.upload_url()
        app.upload_data(upload_url=upload_url, data=data)
        upload_id = upload_url.upload_id

    return app.new_managed_input(
        id=managed_input_id,
        name=name,
        description=description,
        upload_id=upload_id,
        run_id=run_id,
    ).to_dict()


def update_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    managed_input_id: ManagedInputIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud managed input.

    Only the provided fields are updated; omitted fields remain unchanged.
    Returns the updated managed input dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_managed_input(
        managed_input_id=managed_input_id,
        name=name,
        description=description,
    ).to_dict()


def delete_managed_input(
    client: Client,
    app_id: AppIdRequiredOption,
    managed_input_id: ManagedInputIdOption,
) -> None:
    """Delete a Nextmv Cloud managed input permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_managed_input(managed_input_id=managed_input_id)
