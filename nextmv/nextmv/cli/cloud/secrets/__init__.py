"""Cloud secrets command tree for the Nextmv CLI.

``list``, ``get``, and ``delete`` are thin wrappers around the actions in
``nextmv.cli.actions.secrets``. ``create`` and ``update`` route through
``run_create_secrets_collection`` / ``run_update_secrets_collection`` in
``_workflows.py`` because they parse a repeatable ``--secrets`` JSON flag
into SDK ``Secret`` instances before calling the action.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.secrets import (
    delete_secrets_collection,
    get_secrets_collection,
    list_secrets_collections,
)
from nextmv.cli.cloud.secrets._workflows import (
    run_create_secrets_collection,
    run_update_secrets_collection,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud secrets collections.

    A secret collection defines one or more secrets used by your optimization
    model during execution. You can reference a secret collection either in an
    application instance configuration, or directly when starting a run. The
    platform then injects the secrets into the container during the
    optimization run as environment variables and files.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all secrets collections of application [magenta]hare-app[/magenta].",
        "nextmv cloud secrets list --app-id hare-app",
    ),
    (
        "List all secrets collections and save the information to a file.",
        "nextmv cloud secrets list --app-id hare-app --output secrets.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the secrets collection [magenta]api-keys[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud secrets get --app-id hare-app --secrets-collection-id api-keys",
    ),
    (
        "Get a secrets collection and save the information to a file.",
        "nextmv cloud secrets get --app-id hare-app --secrets-collection-id api-keys \\\n"
        "    --output secrets.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create a secrets collection with a single environment variable secret.",
        "nextmv cloud secrets create --app-id hare-app \\\n"
        "    --secrets '{\"type\": \"env\", \"location\": \"API_KEY\", \"value\": \"secret-value\"}'",
    ),
    (
        "Create a secrets collection with multiple secrets by repeating the flag.",
        "nextmv cloud secrets create --app-id hare-app \\\n"
        "    --secrets '{\"type\": \"env\", \"location\": \"API_KEY\", \"value\": \"secret-value\"}' \\\n"
        "    --secrets '{\"type\": \"env\", \"location\": \"DATABASE_URL\", \"value\": \"postgres://localhost\"}'",
    ),
    (
        "Create a secrets collection with custom ID, name, and description.",
        "nextmv cloud secrets create --app-id hare-app \\\n"
        "    --secrets-collection-id db-creds --name \"Database Credentials\" \\\n"
        "    --description \"Production database credentials\" \\\n"
        "    --secrets '{\"type\": \"env\", \"location\": \"DB_USER\", \"value\": \"admin\"}'",
    ),
    (
        "Create a secrets collection with file-based secrets.",
        "nextmv cloud secrets create --app-id hare-app \\\n"
        "    --secrets-collection-id certs --name \"Certificates\" \\\n"
        "    --secrets '{\"type\": \"file\", \"location\": \"licenses/acme.lic\", "
        "\"value\": \"LICENSE_CONTENT_HERE\"}'",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of a secrets collection.",
        "nextmv cloud secrets update --app-id hare-app \\\n"
        "    --secrets-collection-id api-keys --name \"Updated API Keys\"",
    ),
    (
        "Replace all secrets in a collection with new secrets.",
        "nextmv cloud secrets update --app-id hare-app \\\n"
        "    --secrets-collection-id api-keys \\\n"
        "    --secrets '{\"type\": \"env\", \"location\": \"API_KEY\", \"value\": \"new-value\"}'",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete the secrets collection [magenta]api-keys[/magenta] from application [magenta]hare-app[/magenta].",
        "nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys",
    ),
    (
        "Delete the secrets collection without the confirmation prompt.",
        "nextmv cloud secrets delete --app-id hare-app --secrets-collection-id api-keys --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_secrets_collections,
    name="list",
    progress="Listing secrets collections...",
    output_flag=True,
    saved_noun="Secrets collections list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_secrets_collection,
    name="get",
    progress="Getting secrets collection...",
    output_flag=True,
    saved_noun="Secrets collection information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_secrets_collection,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    run_update_secrets_collection,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_secrets_collection,
    name="delete",
    progress="Deleting secrets collection...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete secrets collection "
            "[magenta]{secrets_collection_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline=(
            "Secrets collection [magenta]{secrets_collection_id}[/magenta] "
            "will not be deleted."
        ),
        succeeded=(
            "Secrets collection [magenta]{secrets_collection_id}[/magenta] "
            "deleted successfully from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
