"""Cloud ensemble command tree for the Nextmv CLI.

``list``, ``get``, and ``delete`` wrap the thin actions in
``nextmv.cli.actions.ensemble``. ``create`` and ``update`` route
through ``_workflows.py`` because they parse repeatable JSON
``--run-groups`` / ``--rules`` flags and handle the ``--output`` file
save.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.ensemble import (
    delete_ensemble,
    get_ensemble,
    list_ensembles,
)
from nextmv.cli.cloud.ensemble._workflows import (
    run_create_ensemble,
    run_update_ensemble,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud ensemble definitions.

    An ensemble definition defines how to coordinate and execute
    multiple child runs for an application, and how to determine the
    optimal result from those runs. You can configure run groups to
    specify which instances to run on and with what options, as well as
    evaluation rules to determine the best result based on specified
    metrics.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all ensemble definitions for application [magenta]hare-app[/magenta].",
        "nextmv cloud ensemble list --app-id hare-app",
    ),
    (
        "List all ensemble definitions and save to a file.",
        "nextmv cloud ensemble list --app-id hare-app --output ensembles.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the ensemble definition [magenta]prod-ensemble[/magenta].",
        "nextmv cloud ensemble get --app-id hare-app \\\n"
        "    --ensemble-definition-id prod-ensemble",
    ),
    (
        "Get an ensemble definition and save the information to a file.",
        "nextmv cloud ensemble get --app-id hare-app \\\n"
        "    --ensemble-definition-id prod-ensemble --output ensemble.json",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the name of an ensemble definition.",
        "nextmv cloud ensemble update --app-id hare-app \\\n"
        '    --ensemble-definition-id prod-ensemble --name "Updated Production Ensemble"',
    ),
    (
        "Update name and description.",
        "nextmv cloud ensemble update --app-id hare-app \\\n"
        '    --ensemble-definition-id prod-ensemble --name "Prod v2" \\\n'
        '    --description "Enhanced ensemble"',
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete an ensemble definition.",
        "nextmv cloud ensemble delete --app-id hare-app \\\n"
        "    --ensemble-definition-id prod-ensemble",
    ),
    (
        "Delete an ensemble definition without the confirmation prompt.",
        "nextmv cloud ensemble delete --app-id hare-app \\\n"
        "    --ensemble-definition-id prod-ensemble --yes",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_ensembles,
    name="list",
    progress="Listing ensemble definitions...",
    output_flag=True,
    saved_noun="Ensemble definitions list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_ensemble,
    name="get",
    progress="Getting ensemble definition...",
    output_flag=True,
    saved_noun="Ensemble definition information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_ensemble,
    name="create",
    handles_own_output=True,
)

update = cli.command(
    app,
    run_update_ensemble,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_ensemble,
    name="delete",
    progress="Deleting ensemble definition...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete ensemble definition "
            "[magenta]{ensemble_definition_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline=(
            "Ensemble definition [magenta]{ensemble_definition_id}[/magenta] "
            "will not be deleted."
        ),
        succeeded=(
            "Ensemble definition [magenta]{ensemble_definition_id}[/magenta] deleted "
            "successfully from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)
