"""Community command tree for the Nextmv CLI.

Both ``list`` and ``clone`` route through ``_workflows.py`` because they
render Rich tables / call the SDK's verbose+rich cloning path directly
— neither fits the framework's default JSON-emit flow.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.community._workflows import (
    run_clone_community_app,
    run_list_community_apps,
)

app = typer.Typer()


@app.callback()
def callback() -> None:
    """
    Interact with community apps, which are pre-built decision models.

    Community apps are maintained in the nextmv-io/community-apps GitHub
    repository.
    """
    pass


LIST_EXAMPLES: tuple[cli.Example, ...] = (
    ("List the available community apps.", "nextmv community list"),
    (
        "List the available versions of the [magenta]go-nextroute[/magenta] community app.",
        "nextmv community list --app go-nextroute",
    ),
    ("List the names of the available community apps as a flat list.", "nextmv community list --flat"),
)

CLONE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Clone the [magenta]go-nextroute[/magenta] community app at the latest version.",
        "nextmv community clone --app go-nextroute",
    ),
    (
        "Clone a community app to a specific directory.",
        "nextmv community clone --app go-nextroute --directory ~/sample/my_app",
    ),
    (
        "Clone a specific version of a community app.",
        "nextmv community clone --app go-nextroute --version v1.2.0",
    ),
)


list = cli.command(  # noqa: A001
    app,
    run_list_community_apps,
    name="list",
    handles_own_output=True,
    examples=LIST_EXAMPLES,
)

clone = cli.command(
    app,
    run_clone_community_app,
    name="clone",
    handles_own_output=True,
    examples=CLONE_EXAMPLES,
)
