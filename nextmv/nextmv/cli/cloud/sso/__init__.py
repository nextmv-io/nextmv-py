"""Cloud sso command tree for the Nextmv CLI.

All SSO commands route through ``_workflows.py`` because they all need
CLI-specific behavior (stdin fallbacks, confirmation prompts, --output
saves, or plain success messages with no data return). Domain deletion
lives in a nested ``domain`` subcommand tree for historical reasons.
"""

import typer

from nextmv.cli import framework as cli
from nextmv.cli.cloud.sso._workflows import (
    run_create_sso_configuration,
    run_delete_domain,
    run_delete_sso_configuration,
    run_disable_sso_configuration,
    run_enable_sso_configuration,
    run_get_sso_configuration,
    run_update_sso_configuration,
)

app = typer.Typer()

# Nested `domain` subcommand tree.
domain_app = typer.Typer()
app.add_typer(domain_app, name="domain")


@app.callback()
def callback() -> None:
    """
    Manage SSO for your Nextmv Cloud organization (account).

    Please contact Nextmv support for assistance configuring SSO for
    your organization.
    """
    pass


@domain_app.callback()
def domain_callback() -> None:
    """
    Manage SSO mapped domains for your Nextmv Cloud organization (account).

    Mapped domains redirect additional domains to your IDP for federated
    authentication.

    Please contact Nextmv support for assistance configuring SSO for
    your organization.
    """
    pass


GET_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Get the SSO configuration.",
        "nextmv cloud sso get",
    ),
    (
        "Get the SSO configuration and save the information to a file.",
        "nextmv cloud sso get --output sso_config.json",
    ),
)

CREATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Create an SSO configuration using a metadata URL.",
        'nextmv cloud sso create --metadata-url "https://sso.carrotexpress.com/saml/metadata"',
    ),
    (
        "Create and enable SSO configuration immediately.",
        'nextmv cloud sso create \\\n'
        '    --metadata-url "https://sso.bunnylogistics.io/metadata" --enabled',
    ),
    (
        "Create SSO configuration using a metadata document file.",
        'nextmv cloud sso create --metadata-document "/path/to/metadata_document.xml"',
    ),
)

UPDATE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Update the SSO configuration with a new metadata URL.",
        'nextmv cloud sso update --metadata-url "https://example.com/metadata.xml"',
    ),
)

ENABLE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Enable the SSO configuration.", "nextmv cloud sso enable"),
    ("Enable without confirmation prompt.", "nextmv cloud sso enable --yes"),
)

DISABLE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Disable the SSO configuration.", "nextmv cloud sso disable"),
    ("Disable without confirmation prompt.", "nextmv cloud sso disable --yes"),
)

DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    ("Delete the SSO configuration.", "nextmv cloud sso delete"),
    ("Delete without confirmation prompt.", "nextmv cloud sso delete --yes"),
)

DOMAIN_DELETE_EXAMPLES: tuple[cli.Example, ...] = (
    (
        "Delete a mapped domain from the SSO configuration.",
        'nextmv cloud sso domain delete --domain "example.com"',
    ),
)


get = cli.command(
    app,
    run_get_sso_configuration,
    name="get",
    handles_own_output=True,
    examples=GET_EXAMPLES,
)

create = cli.command(
    app,
    run_create_sso_configuration,
    name="create",
    handles_own_output=True,
    examples=CREATE_EXAMPLES,
)

update = cli.command(
    app,
    run_update_sso_configuration,
    name="update",
    handles_own_output=True,
    examples=UPDATE_EXAMPLES,
)

enable = cli.command(
    app,
    run_enable_sso_configuration,
    name="enable",
    handles_own_output=True,
    examples=ENABLE_EXAMPLES,
)

disable = cli.command(
    app,
    run_disable_sso_configuration,
    name="disable",
    handles_own_output=True,
    examples=DISABLE_EXAMPLES,
)

delete = cli.command(
    app,
    run_delete_sso_configuration,
    name="delete",
    handles_own_output=True,
    examples=DELETE_EXAMPLES,
)

domain_delete = cli.command(
    domain_app,
    run_delete_domain,
    name="delete",
    handles_own_output=True,
    examples=DOMAIN_DELETE_EXAMPLES,
)
