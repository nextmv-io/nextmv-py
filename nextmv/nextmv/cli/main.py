"""
The Nextmv Command Line Interface (CLI).

This module is the main entry point for the Nextmv CLI application. The Nextmv
CLI is built with [Typer](https://typer.tiangolo.com/) and provides various
commands to interact with Nextmv services. You should visit the "Learn" section
of the Typer documentation to learn about the features that are used here.

The Nextmv CLI also uses [Rich](https://rich.readthedocs.io/en/stable/) for
rich text and formatting in the terminal. The command documentation is created
using Rich markup. You should also visit the Rich documentation to learn more
about the features used here. An example of Rich markup can be found in the
epilog of the Typer application defined below.
"""

import typer
from rich import print

from nextmv.cli.configure import GO_CLI_PATH, go_cli_exists, load_config, remove_go_cli
from nextmv.cli.configure import app as configure_app
from nextmv.cli.error import error
from nextmv.cli.version import app as version_app

# Main CLI application.
app = typer.Typer(
    help="The Nextmv Command Line Interface (CLI).",
    epilog="[dim]\n---\n\n[italic]:rabbit: Made by Nextmv with :heart:[/italic][/dim]",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["--help", "-h"]},
    no_args_is_help=True,
)

# Register subcommands.
app.add_typer(configure_app)
app.add_typer(version_app)


@app.callback()
def callback(ctx: typer.Context) -> None:
    """
    Callback function that runs before any command. Useful for checks on the
    environment.
    """

    handle_go_cli()
    handle_config_existence(ctx)


def handle_go_cli() -> None:
    """
    Handle the presence of the deprecated Go CLI by notifying the user.

    This function checks if the Go CLI is installed and prompts the user to
    remove it to avoid conflicts with the Python CLI.
    """

    exists = go_cli_exists()
    if exists:
        delete = typer.confirm(
            f"Do you want to delete the deprecated Nextmv CLI at {GO_CLI_PATH} now?",
            default=True,
        )
        if delete:
            remove_go_cli()
        else:
            print(
                ":bulb: You can delete the [italic red]deprecated[/italic red] Nextmv CLI "
                f"later by removing [italic]{GO_CLI_PATH}[/italic]. Make sure you also clean up your [code]PATH[/code]."
            )


def handle_config_existence(ctx: typer.Context) -> None:
    """
    Check if configuration exists and show an error if it does not.

    Parameters
    ----------
    ctx : typer.Context
        The Typer context object.
    """

    ignored_commands = {"configure", "version"}
    if ctx.invoked_subcommand in ignored_commands:
        return

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configure[/code].")
