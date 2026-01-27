"""
This module defines the cloud batch delete command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_app
from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import info, success
from nextmv.cli.options import AppIDOption, BatchExperimentIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def delete(
    app_id: AppIDOption,
    batch_experiment_id: BatchExperimentIDOption,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Agree to deletion confirmation prompt. Useful for non-interactive sessions.",
        ),
    ] = False,
    profile: ProfileOption = None,
) -> None:
    """
    Deletes a Nextmv Cloud batch experiment.

    This action is permanent and cannot be undone. The batch experiment and all
    associated data, including runs, will be deleted. Use the --yes
    flag to skip the confirmation prompt.

    [bold][underline]Examples[/underline][/bold]

    - Delete the batch experiment with the ID [magenta]hop-analysis[/magenta] from application
      [magenta]hare-app[/magenta].
        $ [dim]nextmv cloud batch delete --app-id hare-app --batch-experiment-id hop-analysis[/dim]

    - Delete the batch experiment without confirmation prompt.
        $ [dim]nextmv cloud batch delete --app-id hare-app --batch-experiment-id carrot-routes --yes[/dim]
    """

    if not yes:
        confirm = get_confirmation(
            f"Are you sure you want to delete batch experiment [magenta]{batch_experiment_id}[/magenta] "
            f"from application [magenta]{app_id}[/magenta]? This action cannot be undone.",
        )

        if not confirm:
            info(
                msg=f"Batch experiment [magenta]{batch_experiment_id}[/magenta] will not be deleted.",
                emoji=":bulb:",
            )
            return

    cloud_app = build_app(app_id=app_id, profile=profile)
    cloud_app.delete_batch_experiment(batch_id=batch_experiment_id)
    success(
        f"Batch experiment [magenta]{batch_experiment_id}[/magenta] deleted successfully "
        f"from application [magenta]{app_id}[/magenta]."
    )
