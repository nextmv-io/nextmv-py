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

import os
from typing import Annotated

import typer
from rich.prompt import Confirm

from nextmv.cli.cloud import app as cloud_app
from nextmv.cli.community import app as community_app
from nextmv.cli.configuration import app as configuration_app
from nextmv.cli.configuration.config import CONFIG_DIR, GO_CLI_PATH, load_config
from nextmv.cli.message import error, info, success, warning
from nextmv.cli.version import app as version_app
from nextmv.cli.version import version_callback

# Main CLI application.
app = typer.Typer(
    help="The Nextmv Command Line Interface (CLI).",
    epilog="[dim]\n---\n\n[italic]:rabbit: Made by Nextmv with :heart:[/italic][/dim]",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["--help", "-h"]},
    no_args_is_help=True,
    invoke_without_command=True,
)

# Register subcommands. The `name` parameter is required when the subcommand
# module has a callback function defined.
app.add_typer(cloud_app, name="cloud")
app.add_typer(community_app, name="community")
app.add_typer(configuration_app, name="configuration")
app.add_typer(version_app)


@app.callback()
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show the current version of the Nextmv CLI.",
            callback=version_callback,
        ),
    ] = None,
) -> None:
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
        delete = Confirm.ask(
            "Do you want to delete the [italic red]deprecated[/italic red] Nextmv CLI "
            f"at [magenta]{GO_CLI_PATH}[/magenta] now?",
            default=True,
        )
        if delete:
            remove_go_cli()
        else:
            info(
                msg="You can delete the [italic red]deprecated[/italic red] Nextmv CLI later by removing "
                f"[italic]{GO_CLI_PATH}[/italic]. Make sure you also clean up your [code]PATH[/code].",
                emoji=":bulb:",
            )


def handle_config_existence(ctx: typer.Context) -> None:
    """
    Check if configuration exists and show an error if it does not.

    Parameters
    ----------
    ctx : typer.Context
        The Typer context object.
    """

    ignored_commands = {"configuration", "version"}
    if ctx.invoked_subcommand in ignored_commands:
        return

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configuration create[/code].")


def go_cli_exists() -> bool:
    """
    Check if the Go CLI is installed by looking for the 'nextmv' executable
    under the config dir.

    Returns
    -------
    bool
        True if the Go CLI is installed, False otherwise.
    """

    # Check if the Go CLI executable exists
    exists = GO_CLI_PATH.exists()
    if exists:
        warning(
            "A [italic red]deprecated[/italic red] Nextmv CLI is installed at "
            f"[italic]{GO_CLI_PATH}[/italic]. You must delete it to avoid conflicts."
        )

    check_config_in_path()

    return exists


def remove_go_cli() -> None:
    """
    Remove the Go CLI executable if it exists and notify about PATH cleanup.
    """

    if GO_CLI_PATH.exists():
        GO_CLI_PATH.unlink()
        success(f"Deleted deprecated [magenta]{GO_CLI_PATH}[/magenta].")

    check_config_in_path()


def check_config_in_path() -> None:
    """
    Check if the configuration directory is in the PATH and notify the user.
    """

    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    config_dir_str = str(CONFIG_DIR)

    if config_dir_str in path_dirs:
        warning(
            f"[italic]{CONFIG_DIR}[/italic] was found in your [code]PATH[/code]. "
            f"You should remove any entries related to [italic]{CONFIG_DIR}[/italic] from your [code]PATH[/code]."
        )
