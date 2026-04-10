"""
This module defines the cloud shadow stop command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.actions.shadow import stop_shadow_test as _stop_shadow_test
from nextmv.cli.message import enum_values, in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, ShadowTestIDOption
from nextmv.cloud.client import Client
from nextmv.cloud.shadow import StopIntent

# Set up subcommand application.
app = typer.Typer()


@app.command()
def stop(
    app_id: AppIDOption,
    intent: Annotated[
        StopIntent,
        typer.Option(
            "--intent",
            "-i",
            help=f"Intent for stopping the shadow test. Allowed values are: {enum_values(StopIntent)}.",
            metavar="INTENT",
        ),
    ],
    shadow_test_id: ShadowTestIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Stops a Nextmv Cloud shadow test.

    Before stopping a shadow test, it must be in a started state. Experiments
    in a [magenta]draft[/magenta] state, that haven't started, can be deleted
    with the [code]nextmv cloud shadow delete[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - Stop the shadow test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud shadow stop --app-id hare-app --shadow-test-id hop-analysis[/dim]
    """

    in_progress(msg="Stopping shadow test...")
    client = Client(profile=profile)
    _stop_shadow_test(client, app_id, shadow_test_id, intent=intent.value)
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
