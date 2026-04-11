"""Cloud app command tree for the Nextmv CLI.

All seven commands are built by ``cli.command()`` from pure action functions
in ``nextmv.cli.actions.app`` (or ``run_push_workflow`` for the interactive
push flow). Parameter types, help text, and defaults come from the action
signatures -- this file carries only the per-command wiring (Typer
registration, progress messages, example blocks, save-noun, and
success-message overrides).
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.app import (
    app_exists,
    create_app,
    delete_app,
    get_app,
    list_apps,
    update_app,
)
from nextmv.cli.cloud.app._workflows import run_push_workflow

# Set up subcommand application.
app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create, manage, and push Nextmv Cloud applications.

    A Nextmv application is an entity that contains a decision model as
    executable code. An application can make a run by taking an input,
    executing the decision model, and producing an output.
    """
    pass


# ---------------------------------------------------------------------------
# Rich example blocks -- data tuples rendered to Rich markup by cli.command().
# Inline [magenta]...[/magenta] highlights inside descriptions are preserved.
# ---------------------------------------------------------------------------

LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all applications.",
        "nextmv cloud app list",
    ),
    (
        "List all applications using the profile named [magenta]hare[/magenta].",
        "nextmv cloud app list --profile hare",
    ),
    (
        "List all applications and save the information to an [magenta]apps.json[/magenta] file.",
        "nextmv cloud app list --output apps.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create an application with the name [magenta]Hare App[/magenta]. A random ID will be generated.",
        'nextmv cloud app create --name "Hare App"',
    ),
    (
        "Create an application with the specific ID [magenta]hare-app[/magenta].",
        'nextmv cloud app create --name "Hare App" --app-id hare-app',
    ),
    (
        "Create an application with an ID and description.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        '    --description "An application for routing hares"',
    ),
    (
        "Create an application, or get it if it already exists.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app --exist-ok',
    ),
    (
        "Create a workflow application.",
        'nextmv cloud app create --name "Hare Workflow" --app-id hare-workflow --is-workflow',
    ),
    (
        "Create an application with a default instance ID.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        "    --default-instance-id burrow",
    ),
    (
        "Create an application with a default experiment instance.",
        'nextmv cloud app create --name "Hare App" --app-id hare-app \\\n'
        "    --default-experiment-instance experiment-v1",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the application with the ID [magenta]hare-app[/magenta].",
        "nextmv cloud app get --app-id hare-app",
    ),
    (
        "Get the application with the ID [magenta]hare-app[/magenta] and save the information to an "
        "[magenta]app.json[/magenta] file.",
        "nextmv cloud app get --app-id hare-app --output app.json",
    ),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete the application with the ID [magenta]hare-app[/magenta].",
        "nextmv cloud app delete --app-id hare-app",
    ),
    (
        "Delete the application with the ID [magenta]hare-app[/magenta] without confirmation prompt.",
        "nextmv cloud app delete --app-id hare-app --yes",
    ),
)

EXISTS_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Check if the application with the ID [magenta]hare-app[/magenta] exists.",
        "nextmv cloud app exists --app-id hare-app",
    ),
    (
        "Check if the application with the ID [magenta]hare-app[/magenta] exists. "
        "Use the profile named [magenta]hare[/magenta].",
        "nextmv cloud app exists --app-id hare-app --profile hare",
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update an application's name.",
        'nextmv cloud app update --app-id hare-app --name "New Hare App"',
    ),
    (
        "Update an application's description.",
        'nextmv cloud app update --app-id hare-app --name "Hare App" \\\n'
        '    --description "An updated description for routing hares"',
    ),
    (
        "Update an application's default instance ID.",
        'nextmv cloud app update --app-id hare-app --name "Hare App" \\\n'
        "    --default-instance-id burrow",
    ),
    (
        "Update an application's default experiment instance.",
        'nextmv cloud app update --app-id hare-app --name "Hare App" \\\n'
        "    --default-experiment-instance experiment-v1",
    ),
    (
        "Update multiple application properties at once.",
        'nextmv cloud app update --app-id hare-app --name "Hare App" \\\n'
        '    --description "Updated description" --default-instance-id burrow \\\n'
        "    --default-experiment-instance experiment-v1",
    ),
    (
        "Update an application and save the updated information to an "
        "[magenta]updated_app.json[/magenta] file.",
        'nextmv cloud app update --app-id hare-app --name "New Hare App" --output updated_app.json',
    ),
)

PUSH_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Push an application, with ID [magenta]hare-app[/magenta], from the current directory.",
        "nextmv cloud app push --app-id hare-app",
    ),
    (
        "Push an application, with ID [magenta]hare-app[/magenta], from the [magenta]./my-app[/magenta] directory.",
        "nextmv cloud app push --app-id hare-app --app-dir ./my-app",
    ),
    (
        "Push an application, with ID [magenta]hare-app[/magenta], using a custom manifest file.",
        "nextmv cloud app push --app-id hare-app --manifest ./custom-manifest.yaml",
    ),
    (
        "Push and automatically create a new version (no prompt).",
        "nextmv cloud app push --app-id hare-app --version-yes",
    ),
    (
        "Push and create a new version with a custom version ID (no prompt).",
        "nextmv cloud app push --app-id hare-app --version-id v1.0.0",
    ),
    (
        "Push and create a new version, then link it to a new instance with a specific ID (no prompt).",
        "nextmv cloud app push --app-id hare-app --version-yes --create-instance-id inst-1",
    ),
    (
        "Push and create a new version, then link it to an existing instance (no prompt).",
        "nextmv cloud app push --app-id hare-app --version-yes --update-instance-id inst-1",
    ),
)


# ---------------------------------------------------------------------------
# Command registration -- one cli.command() call per operation.
# ---------------------------------------------------------------------------

list = cli.command(  # noqa: A001 -- shadows the builtin intentionally
    app,
    list_apps,
    name="list",
    progress="Listing applications...",
    output_flag=True,
    saved_noun="Application list information",
    examples=LIST_EXAMPLES,
)

create = cli.command(
    app,
    create_app,
    name="create",
    progress="Creating application...",
    examples=CREATE_EXAMPLES,
)

get = cli.command(
    app,
    get_app,
    name="get",
    progress="Getting application...",
    output_flag=True,
    saved_noun="Application information",
    examples=GET_EXAMPLES,
)

delete = cli.command(
    app,
    delete_app,
    name="delete",
    progress="Deleting application...",
    on_success="Deleted application [magenta]{app_id}[/magenta].",
    examples=DELETE_EXAMPLES,
)

exists = cli.command(
    app,
    app_exists,
    name="exists",
    examples=EXISTS_EXAMPLES,
)

update = cli.command(
    app,
    update_app,
    name="update",
    progress="Updating application...",
    output_flag=True,
    saved_noun="Updated application information",
    examples=UPDATE_EXAMPLES,
)

# push uses handles_own_output=True because run_push_workflow manages its
# own status messages (confirmation prompts, version creation progress,
# instance linking). The action layer's thin push_app is used by MCP;
# the CLI uses this richer workflow instead.
push = cli.command(
    app,
    run_push_workflow,
    name="push",
    handles_own_output=True,
    progress="Pushing application...",
    examples=PUSH_EXAMPLES,
)
