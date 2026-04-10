"""Dual-purpose ``Annotated`` option aliases shared by CLI and MCP frontends.

Each alias carries two metadata entries:

* ``typer.Option(...)`` — consumed by Typer when building CLI commands.
* ``pydantic.Field(description=...)`` — consumed by FastMCP's Pydantic layer
  when building MCP tool schemas.

Python's ``Annotated`` accepts multiple metadata entries; Typer walks them
looking for ``ParameterInfo`` and Pydantic walks them looking for
``FieldInfo``. They coexist without conflict. See the feasibility spike
(historical) and ``tests/cli/framework/test_options.py`` for the permanent
regression guard.

The help text for each option is defined once as a module-level constant and
referenced twice inside the alias (once by ``typer.Option(help=...)`` and once
by ``Field(description=...)``) so it stays in sync.

Framework-internal aliases (e.g. ``_OutputOption``) omit the ``Field(...)``
entry because they have no MCP counterpart. They are injected automatically
by ``cli.command(output_flag=True, ...)`` and are not imported by domain
connector files.
"""

from typing import Annotated, TypeAlias

import typer
from pydantic import Field

# ---------------------------------------------------------------------------
# App domain — dual-purpose aliases used by cli/actions/app.py
# ---------------------------------------------------------------------------

_APP_ID_HELP = (
    "An optional ID for the Nextmv Cloud application. "
    "If not provided, a random ID will be generated."
)
AppIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--app-id",
        "-a",
        help=_APP_ID_HELP,
        metavar="APP_ID",
        envvar="NEXTMV_APP_ID",
    ),
    Field(description=_APP_ID_HELP),
]

_APP_ID_REQUIRED_HELP = "The Nextmv Cloud application ID."
AppIdRequiredOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--app-id",
        "-a",
        help=_APP_ID_REQUIRED_HELP,
        metavar="APP_ID",
        envvar="NEXTMV_APP_ID",
    ),
    Field(description=_APP_ID_REQUIRED_HELP),
]

_NAME_HELP = (
    "A name for the application. If not provided, the application ID will be "
    "used as the name."
)
NameOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--name", "-n", help=_NAME_HELP, metavar="NAME"),
    Field(description=_NAME_HELP),
]

_DESCRIPTION_HELP = "An optional description for the application."
DescriptionOption: TypeAlias = Annotated[
    str | None,
    typer.Option("--description", "-d", help=_DESCRIPTION_HELP, metavar="DESCRIPTION"),
    Field(description=_DESCRIPTION_HELP),
]

_DEFAULT_INSTANCE_ID_HELP = "An optional default instance ID for the application."
DefaultInstanceIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--default-instance-id",
        "-i",
        help=_DEFAULT_INSTANCE_ID_HELP,
        metavar="DEFAULT_INSTANCE_ID",
    ),
    Field(description=_DEFAULT_INSTANCE_ID_HELP),
]

_DEFAULT_EXPERIMENT_INSTANCE_HELP = (
    "An optional default experiment instance ID for the application."
)
DefaultExperimentInstanceOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--default-experiment-instance",
        "-x",
        help=_DEFAULT_EXPERIMENT_INSTANCE_HELP,
        metavar="DEFAULT_EXPERIMENT_INSTANCE",
    ),
    Field(description=_DEFAULT_EXPERIMENT_INSTANCE_HELP),
]

_IS_WORKFLOW_HELP = "Whether the application is a workflow."
IsWorkflowOption: TypeAlias = Annotated[
    bool,
    typer.Option("--is-workflow", "-w", help=_IS_WORKFLOW_HELP),
    Field(description=_IS_WORKFLOW_HELP),
]

_EXIST_OK_HELP = (
    "If an application with the given ID already exists, do not raise an "
    "error, and simply return it."
)
ExistOkOption: TypeAlias = Annotated[
    bool,
    typer.Option("--exist-ok", "-e", help=_EXIST_OK_HELP),
    Field(description=_EXIST_OK_HELP),
]

_APP_DIR_HELP = (
    "Absolute path to the local directory containing the application code "
    "and ``app.yaml`` manifest."
)
AppDirOption: TypeAlias = Annotated[
    str,
    typer.Option("--app-dir", "-D", help=_APP_DIR_HELP, metavar="APP_DIR"),
    Field(description=_APP_DIR_HELP),
]


# ---------------------------------------------------------------------------
# Framework-internal CLI-only aliases — NOT imported by domain connector files.
# These are injected automatically by ``cli.command()`` when flags like
# ``output_flag=True`` are set.
# ---------------------------------------------------------------------------

_OUTPUT_HELP = "Save the result as JSON to this file path."
_OutputOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--output",
        "-o",
        help=_OUTPUT_HELP,
        metavar="OUTPUT_PATH",
    ),
]
