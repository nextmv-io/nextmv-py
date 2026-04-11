"""Cloud marketplace app command tree for the Nextmv CLI.

All four commands (list, get, create, update) wrap pure action
functions in ``nextmv.cli.actions.marketplace`` via ``cli.command()``.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.actions.marketplace import (
    create_marketplace_app,
    get_marketplace_app,
    list_marketplace_apps,
    update_marketplace_app,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Create and manage Nextmv Marketplace applications.

    Unlike the [code]nextmv cloud app[/code] command set, this one can be used
    to manage Marketplace applications instances explicitly.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "List all marketplace applications.",
        "nextmv cloud marketplace app list",
    ),
    (
        "List all applications for a specific partner.",
        "nextmv cloud marketplace app list --partner-id my-partner",
    ),
    (
        "List all applications and save the information to an [magenta]apps.json[/magenta] file.",
        "nextmv cloud marketplace app list --output apps.json",
    ),
)

GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the marketplace application with the ID [magenta]marketplace-hare[/magenta].",
        "nextmv cloud marketplace app get --partner-id my-partner \\\n"
        "    --app-id marketplace-hare",
    ),
    (
        "Get the marketplace application and save the information to an "
        "[magenta]app.json[/magenta] file.",
        "nextmv cloud marketplace app get --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --output app.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create a marketplace application with the title [magenta]Hare Routing[/magenta]. "
        "A random ID will be generated.",
        "nextmv cloud marketplace app create --partner-id fluffy-comrade \\\n"
        '    --reference-app-id hare-app --title "Hare Routing"',
    ),
    (
        "Create a marketplace application with a specific ID [magenta]marketplace-hare[/magenta].",
        "nextmv cloud marketplace app create --partner-id fluffy-comrade \\\n"
        '    --reference-app-id hare-app --title "Hare Routing" --app-id marketplace-hare',
    ),
    (
        "Create a marketplace application with a description.",
        "nextmv cloud marketplace app create --partner-id fluffy-comrade \\\n"
        '    --reference-app-id hare-app --title "Hare Routing" \\\n'
        '    --description "Advanced routing solution for hare logistics"',
    ),
    (
        "Create a marketplace application with categories and features.",
        "nextmv cloud marketplace app create --partner-id fluffy-comrade \\\n"
        '    --reference-app-id hare-app --title "Hare Routing" \\\n'
        "    --categories routing --categories logistics \\\n"
        '    --features "real-time optimization"',
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the title of a marketplace application.",
        "nextmv cloud marketplace app update --partner-id my-partner \\\n"
        '    --app-id marketplace-hare --title "Advanced Hare Routing"',
    ),
    (
        "Update the description of a marketplace application.",
        "nextmv cloud marketplace app update --partner-id my-partner \\\n"
        '    --app-id marketplace-hare \\\n'
        '    --description "Enterprise-grade routing solution"',
    ),
    (
        "Update categories and features.",
        "nextmv cloud marketplace app update --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --categories routing --categories logistics \\\n"
        '    --features "real-time optimization"',
    ),
    (
        "Update the state of a marketplace application.",
        "nextmv cloud marketplace app update --partner-id my-partner \\\n"
        "    --app-id marketplace-hare --state released",
    ),
    (
        "Update multiple fields and save the result to a file.",
        "nextmv cloud marketplace app update --partner-id my-partner \\\n"
        '    --app-id marketplace-hare --title "New Title" --state released \\\n'
        "    --output app.json",
    ),
)


list = cli.command(  # noqa: A001
    app,
    list_marketplace_apps,
    name="list",
    progress="Listing applications...",
    output_flag=True,
    saved_noun="Application list information",
    examples=LIST_EXAMPLES,
)

get = cli.command(
    app,
    get_marketplace_app,
    name="get",
    progress="Getting application...",
    output_flag=True,
    saved_noun="Application information",
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    create_marketplace_app,
    name="create",
    progress="Creating application...",
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    update_marketplace_app,
    name="update",
    progress="Updating application...",
    output_flag=True,
    saved_noun="Updated application information",
    examples=UPDATE_EXAMPLES,
)
