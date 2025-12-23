"""
The Nextmv Command Line Interface (CLI).

This module is the main entry point for the Nextmv CLI application.
"""

import typer

from nextmv.cli.version import app as version_app

# Main CLI application.
app = typer.Typer(
    help="The Nextmv Command Line Interface (CLI).",
    epilog="[italic]:rabbit: Made with :heart: by Nextmv.[/italic]",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["--help", "-h"]},
)

# Register subcommands.
app.add_typer(version_app)
