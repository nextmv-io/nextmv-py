"""
This module defines the cloud switchback stop command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import enum_values, in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, SwitchbackTestIDOption
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
            help=f"Intent for stopping the switchback test. Allowed values are: {enum_values(StopIntent)}.",
            metavar="INTENT",
        ),
    ],
    switchback_test_id: SwitchbackTestIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Stops a Nextmv Cloud switchback test.

    Before stopping a switchback test, it must be in a started state. Experiments
    in a [magenta]draft[/magenta] state, that haven't started, can be deleted
    with the [code]nextmv cloud switchback delete[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - Stop the switchback test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback stop --app-id hare-app --switchback-test-id hop-analysis[/dim]
    """

    in_progress(msg="Stopping switchback test...")
    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.stop_switchback_test(switchback_test_id=switchback_test_id, intent=StopIntent(intent))
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
