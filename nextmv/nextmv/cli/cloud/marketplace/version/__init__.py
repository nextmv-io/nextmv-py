"""Cloud marketplace version command tree for the Nextmv CLI.

All four commands (list, get, create, update) wrap pure action
functions in ``nextmv.cli.actions.marketplace`` via ``cli.command()``.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.marketplace import (
    create_marketplace_version,
    get_marketplace_version,
    list_marketplace_versions,
    update_marketplace_version,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Marketplace application versions.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all marketplace versions for an application.",
        "nextmv cloud marketplace version list --partner-id my-partner \\\n"
        "    --app-id marketplace-hare",
    ),
    (
        "List all versions and save the information to a "
        "[magenta]versions.json[/magenta] file.",
        "nextmv cloud marketplace version list --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --output versions.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the marketplace version with the ID [magenta]mkt-v1[/magenta].",
        "nextmv cloud marketplace version get --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --version-id mkt-v1",
    ),
    (
        "Get the marketplace version and save the information to a file.",
        "nextmv cloud marketplace version get --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --version-id mkt-v1 --output version.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create a marketplace version with change log entries. A random ID will be generated.",
        "nextmv cloud marketplace version create --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --reference-version-id v1.0.0 \\\n"
        '    --change-log "Improved performance" --change-log "Fixed bug in routing"',
    ),
    (
        "Create a marketplace version with a specific version ID.",
        "nextmv cloud marketplace version create --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --reference-version-id v1.0.0 \\\n"
        '    --version-id mkt-v1 --change-log "Initial marketplace release"',
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update a version's change log with a single entry.",
        "nextmv cloud marketplace version update --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --version-id mkt-v1 \\\n"
        '    --change-log "Fixed critical bug in routing algorithm"',
    ),
    (
        "Update a version's change log with multiple entries.",
        "nextmv cloud marketplace version update --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --version-id mkt-v1 \\\n"
        '    --change-log "Performance improvements" --change-log "Added new features"',
    ),
    (
        "Update a version and save the updated information to a file.",
        "nextmv cloud marketplace version update --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --version-id mkt-v1 \\\n"
        '    --change-log "Bug fixes" --output updated_version.json',
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_marketplace_versions,
    name="list",
    progress="Listing versions...",
    output_flag=True,
    saved_noun="Version list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_marketplace_version,
    name="get",
    progress="Getting version...",
    output_flag=True,
    saved_noun="Version information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    create_marketplace_version,
    name="create",
    progress="Creating version...",
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    update_marketplace_version,
    name="update",
    progress="Updating version...",
    output_flag=True,
    saved_noun="Updated version information",
    examples=UPDATE_EXAMPLES,
)
