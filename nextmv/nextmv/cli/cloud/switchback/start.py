"""
This module defines the cloud switchback start command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, SwitchbackTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def start(
    app_id: AppIDOption,
    switchback_test_id: SwitchbackTestIDOption,
    profile: ProfileOption = None,
) -> None:
    """
    Starts a Nextmv Cloud switchback test.

    Before starting a switchback test, it must be created in draft state. You
    may use the [code]nextmv cloud switchback create[/code] command to create a
    new switchback test. Alternatively, define a --start when using the
    [code]nextmv cloud switchback create[/code] command to have the switchback
    test start automatically at a specific time.

    [bold][underline]Examples[/underline][/bold]

    - Start the switchback test with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud switchback start --app-id hare-app --switchback-test-id hop-analysis[/dim]
    """

    in_progress(msg="Starting switchback test...")
    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.start_switchback_test(switchback_test_id=switchback_test_id)
    success(
        f"Switchback test [magenta]{switchback_test_id}[/magenta] started successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
