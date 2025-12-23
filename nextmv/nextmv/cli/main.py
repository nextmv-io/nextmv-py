"""
The Nextmv Command Line Interface (CLI).

This module is the main entry point for the Nextmv CLI application.
"""

import typer

from nextmv.cli.configure import app as configure_app
from nextmv.cli.version import app as version_app

# Main CLI application.
app = typer.Typer(
    epilog="[dim]\n\n---\n\n[italic]:rabbit: Made by Nextmv with :heart:[/italic][/dim]",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["--help", "-h"]},
    no_args_is_help=True,
)

# Register subcommands.
app.add_typer(configure_app)
app.add_typer(version_app)
