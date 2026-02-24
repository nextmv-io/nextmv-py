"""
This module defines the cloud sso create command for the Nextmv CLI.
"""

import sys
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, success
from nextmv.cli.options import ProfileOption
from nextmv.cloud.sso import SSOConfiguration

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    allow_non_domain_users: Annotated[
        bool,
        typer.Option(
            "--allow-non-domain-users",
            "-a",
            help="Allow users who are not part of the SSO domain to access the Nextmv Cloud organization (account).",
        ),
    ] = False,
    enabled: Annotated[
        bool,
        typer.Option(
            "--enabled",
            "-e",
            help="Enable SSO for the Nextmv Cloud organization (account) at the time of creation. "
            "Run [code]nextmv cloud sso enable[/code] to enable SSO after creation.",
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
            help="The SSO metadata document as a string or a path to a file containing the document.",
            metavar="METADATA_DOCUMENT",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new SSO configuration for your Nextmv Cloud organization.

    SSO must be configured to enable managed accounts in your organization.
    Please contact [link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link] for assistance.

    You must use either the --metadata-url or --metadata-document option. When
    working with the metadata document, you have three options:

    - Pipe the document into the command via [magenta]stdin[/magenta].
    - Provide the document as a string with --metadata-document.
    - Provide a path to a file containing the document with --metadata-document.

    You can use the [code]nextmv cloud sso get[/code] to get the newly-created
    configuration after running this command.

    [bold][underline]Examples[/underline][/bold]

    - Create an SSO configuration using a metadata URL.
        $ [dim]nextmv cloud sso create --metadata-url "https://sso.carrotexpress.com/saml/metadata"[/dim]

    - Create and enable SSO configuration immediately.
        $ [dim]nextmv cloud sso create --metadata-url "https://sso.bunnylogistics.io/metadata" \\
            --enabled[/dim]

    - Create SSO configuration allowing non-domain users.
        $ [dim]nextmv cloud sso create --metadata-url "https://idp.hopmail.com/saml/metadata" \\
            --allow-non-domain-users[/dim]

    - Create SSO configuration using a metadata document string.
        $ [dim]nextmv cloud sso create --metadata-document "<EntityDescriptor ...</EntityDescriptor>"[/dim]

    - Create SSO configuration using a metadata document file.
        $ [dim]nextmv cloud sso create --metadata-document "/path/to/metadata_document.xml"[/dim]

    - Create SSO configuration using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud sso create --metadata-url "https://sso.cottontailcouriers.net/metadata" \\
            --profile hare[/dim]
    """

    stdin = sys.stdin.read().strip() if sys.stdin.isatty() is False else None
    if stdin is not None:
        metadata_document = stdin

    cloud_client = build_client(profile)
    in_progress(msg="Creating configuration...")

    SSOConfiguration.new(
        client=cloud_client,
        allow_non_domain_users=allow_non_domain_users,
        enabled=enabled,
        metadata_url=metadata_url,
        metadata_document=metadata_document,
        mapped_domains=None,  # mapped_domains cannot be set at creation
    )
    success("SSO configuration created successfully.")
