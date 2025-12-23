"""
The Nextmv Command Line Interface (CLI).

This module is the main entry point for the Nextmv CLI application.
"""

import typer

from nextmv.cli.configure import app as configure_app
from nextmv.cli.configure import load_config
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
    # Check that configuration exists for all commands except configure.
    if ctx.invoked_subcommand == "configure":
        return

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configure[/code].")
