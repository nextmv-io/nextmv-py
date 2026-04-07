"""
This module defines the cloud shadow start command for the Nextmv CLI.
"""

import typer

from nextmv.cli.actions.shadow import start_shadow_test as _start_shadow_test
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, ShadowTestIDOption
from nextmv.cloud.client import Client

# Set up subcommand application.
app = typer.Typer()


@app.command()
def start(
    app_id: AppIDOption,
    shadow_test_id: ShadowTestIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Starts a Nextmv Cloud shadow test.

    Before starting a shadow test, it must be created in draft state. You may
    use the [code]nextmv cloud shadow create[/code] command to create a new
    shadow test. Alternatively, define a --start-time when using the
    [code]nextmv cloud shadow create[/code] command to have the shadow test
    start automatically at a specific time.

    [bold][underline]Examples[/underline][/bold]

    - Start the shadow test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow start --app-id hare-app --shadow-test-id hop-analysis[/dim]
    """

    in_progress(msg="Starting shadow test...")
    client = Client(profile=profile)
    _start_shadow_test(client, app_id, shadow_test_id)
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] started successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
