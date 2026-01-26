"""
This module defines the configuration list command for the Nextmv CLI.
"""

import typer
from rich.console import Console
from rich.table import Table

from nextmv.cli.configuration.config import API_KEY_KEY, ENDPOINT_KEY, load_config, non_profile_keys, obscure_api_key
from nextmv.cli.message import error

# Set up subcommand application.
app = typer.Typer()
console = Console()


@app.command()
def list() -> None:
    """
    List the current configuration and all profiles.

    [bold][underline]Examples[/underline][/bold]

    - Show current configuration and all profiles.
        $ [dim]nextmv configuration list[/dim]
    """

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configuration[/code].")

    default = {
        "api_key": config.get(API_KEY_KEY),
        "endpoint": config.get(ENDPOINT_KEY),
        "name": "Default",
    }
    profiles = [default]

    for k, v in config.items():
        # Skip default configuration.
        if k in non_profile_keys():
            continue

        profile = {
            "name": k,
            "api_key": v.get(API_KEY_KEY),
            "endpoint": v.get(ENDPOINT_KEY),
        }
        profiles.append(profile)

    table = Table("Profile name", "API Key", "Endpoint")
    not_set = "[italic]Not set[/italic]"
    for profile in profiles:
        if profile["name"] != "Default":
            table.add_row(
                profile["name"],
                obscure_api_key(profile["api_key"]) if profile.get("api_key") is not None else not_set,
                profile["endpoint"] if profile.get("endpoint") is not None else not_set,
            )
            continue

        api_key = not_set
        if profile.get("api_key") is not None:
            api_key = obscure_api_key(profile["api_key"])

        endpoint = not_set
        if profile.get("endpoint") is not None:
            endpoint = profile["endpoint"]

        table.add_row(
            f"[bold yellow]{profile['name']}[/bold yellow]",
            f"[bold yellow]{api_key}[/bold yellow]",
            f"[bold yellow]{endpoint}[/bold yellow]",
        )
        table.add_section()

    console.print(table)
