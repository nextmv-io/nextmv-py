"""Core batch experiment actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

A batch experiment executes multiple runs across an input set, optionally
comparing several option sets side by side. Each run is defined by an
input, an instance or version, and optional configuration. The SDK
returns typed objects which these actions flatten to dicts for generic
consumption by either frontend.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppIdRequiredOption,
    BatchExperimentIdOption,
    DescriptionOption,
    NameOption,
)
from nextmv.cloud import Application, Client


def list_batches(
    client: Client,
    app_id: AppIdRequiredOption,
) -> list[dict[str, Any]]:
    """List all Nextmv Cloud batch experiments for an application.

    Returns a list of batch experiment summary dicts including ID,
    name, status, and creation timestamp.
    """
    app = Application(client=client, id=app_id)
    batches = app.list_batch_experiments()
    return [b.to_dict() for b in batches]


def get_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
) -> dict[str, Any]:
    """Get details and per-run results of a Nextmv Cloud batch experiment.

    Returns the batch experiment status along with individual run
    results (if the experiment has completed).
    """
    app = Application(client=client, id=app_id)
    batch = app.batch_experiment(batch_id=batch_experiment_id)
    return batch.to_dict()


def batch_metadata(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
) -> dict[str, Any]:
    """Get metadata for a Nextmv Cloud batch experiment.

    Returns experiment-level metadata only — status, run counts, and
    timing — without the full per-run details. This is a faster
    alternative to :func:`get_batch` when per-run results are not
    needed.
    """
    app = Application(client=client, id=app_id)
    metadata = app.batch_experiment_metadata(batch_id=batch_experiment_id)
    return metadata.to_dict()


def create_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    input_set_id: str | None = None,
    name: NameOption = None,
    description: DescriptionOption = None,
    option_sets: dict[str, dict[str, str]] | None = None,
    runs: list[Any] | None = None,
) -> str:
    """Create a new Nextmv Cloud batch experiment.

    A batch experiment runs the application against an input set,
    optionally with multiple option sets to compare different solver
    configurations side by side. The ``runs`` parameter accepts a list
    of run dicts that the SDK converts into ``BatchExperimentRun``
    objects internally.

    Returns the new batch experiment ID.
    """
    app = Application(client=client, id=app_id)
    return app.new_batch_experiment(
        input_set_id=input_set_id,
        name=name,
        description=description,
        option_sets=option_sets,
        runs=runs,
    )


def update_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
    name: NameOption = None,
    description: DescriptionOption = None,
) -> dict[str, Any]:
    """Update a Nextmv Cloud batch experiment.

    Only the provided fields are updated; omitted fields remain
    unchanged. Returns the updated batch experiment dict.
    """
    app = Application(client=client, id=app_id)
    return app.update_batch_experiment(
        batch_experiment_id=batch_experiment_id,
        name=name,
        description=description,
    ).to_dict()


def delete_batch(
    client: Client,
    app_id: AppIdRequiredOption,
    batch_experiment_id: BatchExperimentIdOption,
) -> None:
    """Delete a Nextmv Cloud batch experiment permanently.

    This action cannot be undone. All associated data, including
    run results, will be deleted.
    """
    app = Application(client=client, id=app_id)
    app.delete_batch_experiment(batch_id=batch_experiment_id)
