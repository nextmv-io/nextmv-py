"""Core application management actions.

Pure functions that wrap SDK calls. No CLI or MCP presentation concerns.

Each action takes ``client: Client`` as its first parameter so the CLI and
MCP frameworks can inject a client at call time. Remaining parameters use
dual-purpose ``Annotated`` aliases from ``nextmv.cli.framework.options`` so
the same metadata drives both Typer's ``--help`` output and FastMCP's tool
input schema.

Docstrings are multi-paragraph: the first line is a short description used
by both frontends as the primary tool/command description, and subsequent
paragraphs provide additional guidance that reads naturally in both
contexts.
"""

from typing import Any

from nextmv.cli.framework.options import (
    AppDirOption,
    AppIdOption,
    AppIdRequiredOption,
    DefaultExperimentInstanceOption,
    DefaultInstanceIdOption,
    DescriptionOption,
    ExistOkOption,
    IsWorkflowOption,
    NameOption,
)
from nextmv.cloud import Application, Client, list_applications


def list_apps(client: Client) -> list[dict[str, Any]]:
    """List all Nextmv Cloud applications in the current account.

    Returns a list of application dictionaries containing each application's
    ID, name, description, and default instance.
    """
    apps = list_applications(client)
    return [a.to_dict() for a in apps]


def create_app(
    client: Client,
    name: NameOption = None,
    app_id: AppIdOption = None,
    description: DescriptionOption = None,
    is_workflow: IsWorkflowOption = False,
    exist_ok: ExistOkOption = False,
    default_instance_id: DefaultInstanceIdOption = None,
    default_experiment_instance: DefaultExperimentInstanceOption = None,
) -> dict[str, Any]:
    """Create a new Nextmv Cloud application.

    Set ``exist_ok`` to avoid errors when an application with the given ID
    already exists; the existing application is returned instead.

    An application can be marked as a workflow via ``is_workflow``. Workflows
    leverage Nextpipe to orchestrate multiple decision models.

    Returns the created (or existing) application object. A version and
    default instance are automatically provisioned for new applications.
    """
    return Application.new(
        client=client,
        name=name,
        id=app_id,
        description=description,
        is_workflow=is_workflow,
        exist_ok=exist_ok,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def get_app(client: Client, app_id: AppIdRequiredOption) -> dict[str, Any]:
    """Get details of a specific Nextmv Cloud application.

    Returns the full application object including its name, description,
    default instance, and creation timestamp.
    """
    return Application.get(client=client, id=app_id).to_dict()


def delete_app(client: Client, app_id: AppIdRequiredOption) -> None:
    """Delete a Nextmv Cloud application permanently.

    This action cannot be undone. All versions, instances, and run history
    associated with the application will be removed.
    """
    Application(client=client, id=app_id).delete()


def app_exists(client: Client, app_id: AppIdRequiredOption) -> bool:
    """Check whether a Nextmv Cloud application exists.

    Returns ``True`` if an application with the given ID exists in the
    current account, ``False`` otherwise.
    """
    return Application.exists(client=client, id=app_id)


def update_app(
    client: Client,
    app_id: AppIdRequiredOption,
    name: NameOption = None,
    description: DescriptionOption = None,
    default_instance_id: DefaultInstanceIdOption = None,
    default_experiment_instance: DefaultExperimentInstanceOption = None,
) -> dict[str, Any]:
    """Update attributes of a Nextmv Cloud application.

    Only the provided fields are updated; omitted fields remain unchanged.
    Returns the updated application object.
    """
    app = Application(client=client, id=app_id)
    return app.update(
        name=name,
        description=description,
        default_instance_id=default_instance_id,
        default_experiment_instance=default_experiment_instance,
    ).to_dict()


def push_app(
    client: Client,
    app_id: AppIdRequiredOption,
    app_dir: AppDirOption,
) -> None:
    """Push local application code to a Nextmv Cloud application.

    Uploads the contents of a local directory as a new version of the
    application. The directory must contain an ``app.yaml`` manifest.
    """
    app = Application(client=client, id=app_id)
    app.push(app_dir=app_dir)
