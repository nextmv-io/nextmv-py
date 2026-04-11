"""Core input set management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Input sets are reusable collections of inputs for batch experiments,
scenario tests, and acceptance tests. They can be built from historical
run IDs, from a running instance's recent runs (optionally filtered by
time range), or from managed inputs.
"""

from datetime import datetime
from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    DescriptionOption,
    InputSetIdOption,
    NameOption,
    OptionalInputSetIdOption,
)
from nextmv.cloud import Application, Client


def list_input_sets(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all input sets for a Nextmv Cloud application.

    Returns a list of input set dicts including ID, name, description,
    and the number of inputs each set contains.
    """
    app = Application(client=client, id=app_id)
    return [s.to_dict() for s in app.list_input_sets()]


def get_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: InputSetIdOption,
) -> dict[str, Any]:
    """Get details of a Nextmv Cloud input set.

    Returns the input set metadata and the list of input IDs it
    contains.
    """
    app = Application(client=client, id=app_id)
    return app.input_set(input_set_id=input_set_id).to_dict()


def create_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: OptionalInputSetIdOption = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    instance_id: str | None = None,
    maximum_runs: int | None = None,
    run_ids: list[str] | None = None,
    managed_input_ids: list[str] | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud input set.

    Build the input set from one of three sources:

    * ``run_ids``: a list of specific run IDs.
    * ``managed_input_ids``: existing managed inputs from the application.
    * ``instance_id`` (optionally with ``start_time``/``end_time``): collect
      runs from that instance, filtered by a time range if provided.

    Returns the created input set dict.
    """
    from nextmv.cloud.input_set import ManagedInput

    app = Application(client=client, id=app_id)

    inputs = None
    if managed_input_ids is not None:
        inputs = [ManagedInput(id=mid) for mid in managed_input_ids]

    return app.new_input_set(
        id=input_set_id,
        name=name,
        description=description,
        instance_id=instance_id,
        maximum_runs=maximum_runs,
        run_ids=run_ids,
        start_time=start_time,
        end_time=end_time,
        inputs=inputs,
    ).to_dict()


def update_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: InputSetIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
    managed_input_ids: list[str] | None = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud input set.

    Only the provided fields are updated; omitted fields remain unchanged.
    When ``managed_input_ids`` is provided, the input set's managed inputs
    are replaced with the listed IDs. Returns the updated input set dict.
    """
    from nextmv.cloud.input_set import ManagedInput

    app = Application(client=client, id=app_id)

    inputs = None
    if managed_input_ids is not None:
        inputs = [ManagedInput(id=mid) for mid in managed_input_ids]

    return app.update_input_set(
        id=input_set_id,
        name=name,
        description=description,
        inputs=inputs,
    ).to_dict()


def delete_input_set(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: InputSetIdOption,
) -> None:
    """Delete a Nextmv Cloud input set permanently.

    This action cannot be undone.
    """
    app = Application(client=client, id=app_id)
    app.delete_input_set(input_set_id=input_set_id)
