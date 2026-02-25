"""
This module defines the init command for the Nextmv CLI.
"""

import questionary
import typer

from nextmv.cli.message import choice, directory_path
from nextmv.content_format import ContentFormat
from nextmv.manifest import ManifestType

# Set up subcommand application.
app = typer.Typer()


@app.command()
def init() -> None:
    """
    Get started with the Nextmv CLI.
    """

    is_template = _template_question()
    manifest_type = _manifest_type_question(is_template)
    content_format = _content_format_question(is_template)
    dirpath = _path_question(is_template)


def _template_question() -> bool:
    """
    Ask the user if they want to start with a template or an existing model.

    Returns
    -------
    bool
        True if the user wants to start with a template, False if they want to
        start with an existing model.
    """

    init_type = choice(
        msg="Are you working with an existing model or do you want to start with a template?",
        choices=["Template", "Existing model"],
        default="Template",
    )

    return init_type == "Template"


def _manifest_type_question(is_template: bool) -> ManifestType:
    """
    Ask the user which language they want to use for their manifest.

    Parameters
    ----------
    is_template : bool
        Whether the user is starting with a template or an existing model.

    Returns
    -------
    ManifestType
        The type of manifest to initialize, based on the user's choice.
    """

    msg = "Which language is your existing model written in?"
    if is_template:
        msg = "Which language do you want to use for your Nextmv application template?"

    manifest_type = choice(
        msg=msg,
        choices=[member.value for member in ManifestType],
        default=ManifestType.PYTHON.value,
    )

    manifest_type = ManifestType(manifest_type)

    return manifest_type


def _content_format_question(is_template: bool) -> ContentFormat:
    """
    Ask the user which content format they want to use for their manifest.

    Parameters
    ----------
    is_template : bool
        Whether the user is starting with a template or an existing model.

    Returns
    -------
    ContentFormat
        The content format to use for the manifest, based on the user's choice.
    """
    choices = [None] * len(ContentFormat)
    for ix, member in enumerate(ContentFormat):
        choices[ix] = questionary.Choice(
            title=member.value,
            description=member.description,
        )

    msg = "How does your existing model handle I/O (input/output) data?"
    if is_template:
        msg = "Which type of I/O (input/output) content format do you prefer for your app?"

    content_format = choice(
        msg=msg,
        choices=choices,
        default=ContentFormat.JSON.value,
    )
    content_format = ContentFormat(content_format)

    return content_format


def _path_question(is_template: bool) -> str:
    """
    Ask the user for the path to their existing model or where they want to
    initialize their template.

    Parameters
    ----------
    is_template : bool
        Whether the user is starting with a template or an existing model.

    Returns
    -------
    str
        The path to the user's existing model or the path where they want to
        initialize their template.
    """

    msg = "What is the path to your existing model?"
    if is_template:
        msg = "Where would you like to initialize your Nextmv application template?"

    dirpath = directory_path(
        msg=msg,
        default=".",
    )
    dirpath = dirpath or "."

    return dirpath
