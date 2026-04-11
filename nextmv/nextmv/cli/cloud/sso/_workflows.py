"""CLI-only workflows for the cloud sso domain.

SSO commands combine stdin-piped metadata documents, interactive
confirmation prompts for enable/disable/delete, and --output file saves
for get — none of which fit the framework's default flow.
"""

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from nextmv.cli.actions.sso import (
    create_sso_configuration,
    delete_domain,
    delete_sso_configuration,
    disable_sso_configuration,
    enable_sso_configuration,
    get_sso_configuration,
    update_sso_configuration,
)
from nextmv.cli.framework.options import YesOption
from nextmv.cli.message import confirmation, in_progress, info, print_json, success
from nextmv.cloud.client import Client


def run_get_sso_configuration(
    client: Client,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the SSO configuration information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
) -> None:
    """Get the information of a Nextmv Cloud SSO configuration.

    This command is useful to get the attributes of an existing Nextmv
    Cloud SSO configuration.
    """

    in_progress(msg="Getting SSO configuration...")
    sso_config_dict = get_sso_configuration(client)

    if output is not None and output != "":
        Path(output).write_text(json.dumps(sso_config_dict, indent=2))
        success(f"SSO configuration information saved to [magenta]{output}[/magenta].")
        return

    print_json(sso_config_dict)


def run_create_sso_configuration(
    client: Client,
    allow_non_domain_users: Annotated[
        bool,
        typer.Option(
            "--allow-non-domain-users",
            "-a",
            help=(
                "Allow users who are not part of the SSO domain to access the "
                "Nextmv Cloud organization (account)."
            ),
        ),
    ] = False,
    enabled: Annotated[
        bool,
        typer.Option(
            "--enabled",
            "-e",
            help=(
                "Enable SSO for the Nextmv Cloud organization (account) at the "
                "time of creation. Run [code]nextmv cloud sso enable[/code] to "
                "enable SSO after creation."
            ),
        ),
    ] = False,
    metadata_url: Annotated[
        str | None,
        typer.Option(
            "--metadata-url",
            "-u",
            help="The URL to the SSO metadata document.",
            metavar="METADATA_URL",
        ),
    ] = None,
    metadata_document: Annotated[
        str | None,
        typer.Option(
            "--metadata-document",
            "-d",
            help=(
                "The SSO metadata document as a string or a path to a file "
                "containing the document."
            ),
            metavar="METADATA_DOCUMENT",
        ),
    ] = None,
) -> None:
    """Create a new SSO configuration for your Nextmv Cloud organization.

    SSO must be configured to enable managed accounts in your organization.
    Please contact Nextmv support for assistance.

    You must use either the ``--metadata-url`` or ``--metadata-document``
    option. When working with the metadata document, you have three options:

    * Pipe the document into the command via stdin.
    * Provide the document as a string with ``--metadata-document``.
    * Provide a path to a file containing the document with ``--metadata-document``.

    You can use ``nextmv cloud sso get`` to view the newly-created
    configuration after running this command.
    """

    # Stdin fallback for the metadata document.
    stdin_input = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin_input:
        metadata_document = stdin_input

    in_progress(msg="Creating configuration...")
    create_sso_configuration(
        client,
        allow_non_domain_users=allow_non_domain_users,
        enabled=enabled,
        metadata_url=metadata_url,
        metadata_document=metadata_document,
    )
    success("SSO configuration created successfully.")


def run_update_sso_configuration(
    client: Client,
    metadata_url: Annotated[
        str | None,
        typer.Option(
            "--metadata-url",
            "-u",
            help="The URL to the SSO metadata document to update.",
            metavar="METADATA_URL",
        ),
    ] = None,
    metadata_document: Annotated[
        str | None,
        typer.Option(
            "--metadata-document",
            "-d",
            help="The SSO metadata document as a string to update.",
            metavar="METADATA_DOCUMENT",
        ),
    ] = None,
) -> None:
    """Update information of a Nextmv Cloud SSO configuration.

    This command allows you to update the metadata URL or metadata
    document of an existing SSO configuration. You can use
    ``nextmv cloud sso get`` to view the updated configuration.
    """

    in_progress(msg="Updating SSO configuration...")
    update_sso_configuration(
        client,
        metadata_url=metadata_url,
        metadata_document=metadata_document,
    )
    success("SSO configuration updated successfully.")


def run_enable_sso_configuration(
    client: Client,
    yes: YesOption = False,
) -> None:
    """Enables the SSO configuration.

    Use the ``--yes`` flag to skip the confirmation prompt. Use
    ``nextmv cloud sso disable`` to disable SSO.
    """

    if not yes:
        if not confirmation("Are you sure you want to enable the SSO configuration?"):
            info("SSO configuration will not be enabled.")
            return

    enable_sso_configuration(client)
    success("SSO configuration has been enabled.")


def run_disable_sso_configuration(
    client: Client,
    yes: YesOption = False,
) -> None:
    """Disables the SSO configuration.

    Use the ``--yes`` flag to skip the confirmation prompt. Use
    ``nextmv cloud sso enable`` to re-enable SSO.
    """

    if not yes:
        if not confirmation("Are you sure you want to disable the SSO configuration?"):
            info("SSO configuration will not be disabled.")
            return

    disable_sso_configuration(client)
    success("SSO configuration has been disabled.")


def run_delete_sso_configuration(
    client: Client,
    yes: YesOption = False,
) -> None:
    """Deletes the SSO configuration.

    You must have the administrator role on the organization to delete
    it. Use the ``--yes`` flag to skip the confirmation prompt. You can
    create a new SSO configuration with ``nextmv cloud sso create``.
    """

    if not yes:
        if not confirmation(
            "Are you sure you want to delete the SSO configuration? "
            "You can create it again with [code]nextmv cloud sso create[/code]."
        ):
            info("SSO configuration will not be deleted.")
            return

    delete_sso_configuration(client)
    success(
        "SSO configuration has been deleted. You can create it again with "
        "[code]nextmv cloud sso create[/code]."
    )


def run_delete_domain(
    client: Client,
    domain: Annotated[
        str,
        typer.Option(
            "--domain",
            "-d",
            help="The domain to delete from the SSO configuration.",
            metavar="DOMAIN",
        ),
    ],
    yes: YesOption = False,
) -> None:
    """Delete a mapped domain from a Nextmv Cloud SSO configuration.

    This action will prevent users from the deleted domain from
    accessing your account using SSO. Use the ``--yes`` flag to skip the
    confirmation prompt.

    You can use ``nextmv cloud sso get`` to view all mapped domains in
    your SSO configuration.
    """

    if not yes:
        if not confirmation(
            f"Are you sure you want to delete the [magenta]{domain}[/magenta] domain? "
            "You must contact Nextmv support to re-add it."
        ):
            info("SSO mapped domain will not be deleted.")
            return

    in_progress(msg="Deleting SSO mapped domain from configuration...")
    delete_domain(client, domain=domain)
    success("SSO mapped domain deleted successfully.")
