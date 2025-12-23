"""
This module defines the configure command for the Nextmv CLI.
"""

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich import print
from rich.console import Console
from rich.table import Table

from nextmv.cli.error import error

# Set up subcommand application.
app = typer.Typer()
console = Console()

# Some useful constants.
API_KEY_KEY = "apikey"
ENDPOINT_KEY = "endpoint"
CONFIG_DIR = Path.home() / ".nextmv"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
DEFAULT_ENDPOINT = "api.cloud.nextmv.io"


@app.command()
def configure(
    api_key: Annotated[
        str | None,
        typer.Argument(
            help="A valid Nextmv Cloud API key. "
            + "Get one from [link=https://cloud.nextmv.io][bold]https://cloud.nextmv.io[/bold][/link].",
            envvar="NEXTMV_API_KEY",
        ),
    ] = None,
    profile: Annotated[  # Similar to nextmv.cli.options.ProfileOption but with different help text.
        str | None,
        typer.Option(
            "--profile",
            "-p",
            help="Profile name to manage.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ] = None,
    endpoint: Annotated[  # Hidden because it is meant for internal use.
        str | None,
        typer.Option(
            "--endpoint",
            "-e",
            hidden=True,
        ),
    ] = DEFAULT_ENDPOINT,
    show: Annotated[
        bool,
        typer.Option("--show", "-s", help="Shows the current configuration and all profiles."),
    ] = False,
    delete: Annotated[
        bool,
        typer.Option(
            "--delete",
            "-d",
            help="Deletes the specified profile from the configuration. Use with [code]--profile[/code].",
        ),
    ] = False,
) -> None:
    """
    Configure the CLI and manage profiles.

    [bold][underline]Examples[/underline][/bold]

    - Default configuration.
        [green]nextmv configure YOUR_API_KEY[/green]

    - Configure a profile named [italic]hare[/italic].
        [green]nextmv configure YOUR_API_KEY --profile hare[/green]

    - Show current configuration and all profiles.
        [green]nextmv configure --show[/green]

    - Delete a profile named [italic]hare[/italic].
        [green]nextmv configure --profile hare --delete[/green]
    """

    if api_key is None and not show and not delete:
        error(
            "Provide an [code]API_KEY[/code], use the [code]--show[/code] option, or the [code]--delete[/code] option."
        )

    if show:
        show_profiles()
        raise typer.Exit()

    if profile is not None and profile.strip().lower() == "default":
        error("[code]default[/code] is a reserved profile name.")

    if "https://" in endpoint:
        endpoint = str(endpoint).replace("https://", "")

    config = load_config()
    if delete:
        delete_profile(config, profile)

    if profile is None:
        config[API_KEY_KEY] = api_key
        config[ENDPOINT_KEY] = endpoint
    else:
        if profile not in config:
            config[profile] = {}

        config[profile][API_KEY_KEY] = api_key
        config[profile][ENDPOINT_KEY] = endpoint

    save_config(config)

    print(":white_check_mark: Configuration saved successfully.")
    print(f"\t[bold]Profile[/bold]: {profile or 'Default'}")
    print(f"\t[bold]API Key[/bold]: {obscure_api_key(api_key)}")
    if endpoint != DEFAULT_ENDPOINT:
        print(f"\t[bold]Endpoint[/bold]: {endpoint}")


def show_profiles() -> None:
    """
    Show the current configuration and all profiles. Prints a table to the
    console.
    """
    config = load_config()

    default = {
        "api_key": config.get(API_KEY_KEY),
        "endpoint": config.get(ENDPOINT_KEY),
        "name": "Default",
    }
    profiles = [default]

    for k, v in config.items():
        # Skip default configuration.
        if k in {API_KEY_KEY, ENDPOINT_KEY}:
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


def load_config() -> dict[str, Any]:
    """
    Load the current configuration from the config file. Returns an empty
    dictionary if no configuration file exists.

    Returns
    -------
    dict[str, Any]
        The current configuration as a dictionary.
    """

    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open() as file:
        config = yaml.safe_load(file)

    return config


def save_config(config: dict[str, Any]) -> None:
    """
    Save the given configuration to the config file.

    Parameters
    ----------
    config : dict[str, Any]
        The configuration to save.
    """

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w") as file:
        yaml.safe_dump(config, file)


def obscure_api_key(api_key: str) -> str:
    """
    Obscure an API key for display purposes.

    Parameters
    ----------
    api_key : str
        The API key to obscure.

    Returns
    -------
    str
        The obscured API key.
    """

    if len(api_key) <= 4:
        return "*" * len(api_key)

    return api_key[:2] + "*" * 4 + api_key[-2:]


def delete_profile(config: dict[str, Any], profile: str | None = None) -> None:
    """
    Delete a profile from the configuration.

    Parameters
    ----------
    config : dict[str, Any]
        The current configuration.
    profile_name : str
        The name of the profile to delete.
    """

    if profile is None:
        error("Specify a profile to delete using the [code]--profile[/code] option.")
    if profile not in config:
        error(f"Profile [bold cyan]{profile}[/bold cyan] does not exist.")

    del config[profile]
    save_config(config)
    print(f":white_check_mark: Profile [bold cyan]{profile}[/bold cyan] deleted successfully.")

    raise typer.Exit()
