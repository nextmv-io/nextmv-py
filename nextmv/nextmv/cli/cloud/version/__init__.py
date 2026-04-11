"""Cloud version command tree for the Nextmv CLI.

All commands are built by ``cli.command()`` from pure action functions in
``nextmv.cli.actions.version``. The ``exists`` command wraps the thin
``version_exists`` action in a CLI workflow that prints a JSON dict and
exits with code 1 if the version is missing.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.version import (
    create_version,
    delete_version,
    get_version,
    list_versions,
    update_version,
)
from nextmv.cli.cloud.version._workflows import run_version_exists_check

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Cloud application versions.

    A version represents a snapshot of an application's code at a specific
    point in time. Versions are used to track changes to the decision model.
    You can think of versions as Git tags for your Nextmv Cloud applications.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    ("List all versions of application [magenta]hare-app[/magenta].",
        "nextmv cloud version list --app-id hare-app"),
    ("List all versions and save the information to a file.",
        "nextmv cloud version list --app-id hare-app --output versions.json"),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    ("Get details for version [magenta]v1[/magenta] of application [magenta]hare-app[/magenta].",
        "nextmv cloud version get --app-id hare-app --version-id v1"),
    ("Get version details and save them to a file.",
        "nextmv cloud version get --app-id hare-app --version-id v1 --output version.json"),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Create a version for application [magenta]hare-app[/magenta]. A random ID will be generated.",
        "nextmv cloud version create --app-id hare-app"),
    ("Create a version with a specific name.",
        'nextmv cloud version create --app-id hare-app --name "v1.0.0"'),
    ("Create a version with a specific ID.",
        "nextmv cloud version create --app-id hare-app --version-id v1"),
    ("Create a version with a name and description.",
        'nextmv cloud version create --app-id hare-app --name "v1.0.0" \\\n'
        '    --description "Initial release with routing optimization"'),
    ("Create a version, or get it if it already exists.",
        "nextmv cloud version create --app-id hare-app --version-id v1 --exist-ok"),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Update a version's name.",
        'nextmv cloud version update --app-id hare-app --version-id v1 --name "New Name"'),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Delete a version.",
        "nextmv cloud version delete --app-id hare-app --version-id v1"),
)

EXISTS_EXAMPLES: tuple[cli.Example, ...] = (
    ("Check if version [magenta]v1[/magenta] exists in application [magenta]hare-app[/magenta].",
        "nextmv cloud version exists --app-id hare-app --version-id v1"),
    ("Check if the version exists using the profile named [magenta]hare[/magenta].",
        "nextmv cloud version exists --app-id hare-app --version-id v1 --profile hare"),
)


list = cli.command(  # noqa: A001 — shadows the builtin intentionally
    app,
    list_versions,
    name="list",
    progress="Listing versions...",
    output_flag=True,
    saved_noun="Version list",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_version,
    name="get",
    progress="Getting version...",
    output_flag=True,
    saved_noun="Version information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    create_version,
    name="create",
    progress="Creating version...",
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    update_version,
    name="update",
    progress="Updating version...",
    output_flag=True,
    saved_noun="Updated version information",
    examples=UPDATE_EXAMPLES,
)

delete = cli.command(
    app,
    delete_version,
    name="delete",
    progress="Deleting version...",
    delete_confirm=cli.DeleteConfirmation(
        confirm=(
            "Are you sure you want to delete version "
            "[magenta]{version_id}[/magenta] from application "
            "[magenta]{app_id}[/magenta]? This action cannot be undone."
        ),
        decline="Version [magenta]{version_id}[/magenta] will not be deleted.",
        succeeded=(
            "Version [magenta]{version_id}[/magenta] deleted successfully "
            "from application [magenta]{app_id}[/magenta]."
        ),
    ),
    examples=DELETE_EXAMPLES,
)

# `exists` uses handles_own_output=True because it needs to print a JSON
# dict and exit with code 1 when the version does not exist.
exists = cli.command(
    app,
    run_version_exists_check,
    name="exists",
    progress="Checking if version exists...",
    handles_own_output=True,
    examples=EXISTS_EXAMPLES,
)
