"""
This module defines the cloud shadow stop command for the Nextmv CLI.
"""

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import AppIDOption, ProfileOption, ShadowTestIDOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def stop(
    app_id: AppIDOption,
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
    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.stop_shadow_test(shadow_test_id=shadow_test_id)
    success(
        f"Shadow test [magenta]{shadow_test_id}[/magenta] stopped successfully "
        f"in application [magenta]{app_id}[/magenta]."
    )
