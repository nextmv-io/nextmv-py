"""
This module defines the cloud switchback stop command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, SwitchbackTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def stop(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Stops a Nextmv Cloud switchback test.

    Before stopping a switchback test, it must be in a started state. You may
    use the [code]nextmv cloud switchback start[/code] command to start a
    switchback test. Alternatively, define a [code]--start[/code] when using
    the [code]nextmv cloud switchback create[/code] command to have the
    switchback test start automatically at a specific time.

    [bold][underline]Examples[/underline][/bold]

    - Stop the switchback test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [green]nextmv cloud switchback stop --app-id hare-app --switchback-test-id hop-analysis[/green]
    """

    in_progress(msg="Stopping switchback test...")
    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.stop_switchback_test(switchback_test_id=switchback_test_id)
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
