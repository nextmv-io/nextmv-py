"""
This module defines the cloud command tree for the Nextmv CLI.
"""

import typer

from nextmv.cli.cloud.acceptance import app as acceptance_app
from nextmv.cli.cloud.account import app as account_app
from nextmv.cli.cloud.app import app as app_app
from nextmv.cli.cloud.batch import app as batch_app
from nextmv.cli.cloud.data import app as data_app
from nextmv.cli.cloud.ensemble import app as ensemble_app
from nextmv.cli.cloud.input_set import app as input_set_app
from nextmv.cli.cloud.instance import app as instance_app
from nextmv.cli.cloud.managed_input import app as managed_input_app
from nextmv.cli.cloud.run import app as run_app
from nextmv.cli.cloud.scenario import app as scenario_app
from nextmv.cli.cloud.secrets import app as secrets_app
from nextmv.cli.cloud.shadow import app as shadow_app
from nextmv.cli.cloud.switchback import app as switchback_app
from nextmv.cli.cloud.upload import app as upload_app
from nextmv.cli.cloud.version import app as version_app

# Set up subcommand application.
app = typer.Typer()
app.add_typer(acceptance_app, name="acceptance")
app.add_typer(account_app, name="account")
app.add_typer(app_app, name="app")
app.add_typer(batch_app, name="batch")
app.add_typer(data_app, name="data")
app.add_typer(ensemble_app, name="ensemble")
app.add_typer(input_set_app, name="input-set")
app.add_typer(instance_app, name="instance")
app.add_typer(managed_input_app, name="managed-input")
app.add_typer(run_app, name="run")
app.add_typer(scenario_app, name="scenario")
app.add_typer(secrets_app, name="secrets")
app.add_typer(shadow_app, name="shadow")
app.add_typer(switchback_app, name="switchback")
app.add_typer(upload_app, name="upload")
app.add_typer(version_app, name="version")


@app.callback()
def callback() -> None:
    """
    Interact with Nextmv Cloud, a platform for deploying and managing decision models.
    """
    pass
