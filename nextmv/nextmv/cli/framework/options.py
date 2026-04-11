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
# Cloud entity ID aliases (required)
#
# Each one identifies a specific entity within the Nextmv Cloud account.
# Used by actions for get/update/delete operations and as foreign keys in
# create operations (e.g. version requires app_id, instance requires both
# app_id and version_id).
# ---------------------------------------------------------------------------

_VERSION_ID_HELP = "The Nextmv Cloud version ID."
VersionIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--version-id",
        "-v",
        help=_VERSION_ID_HELP,
        envvar="NEXTMV_VERSION_ID",
        metavar="VERSION_ID",
    ),
    Field(description=_VERSION_ID_HELP),
]

_INSTANCE_ID_HELP = "The Nextmv Cloud instance ID."
InstanceIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--instance-id",
        "-i",
        help=_INSTANCE_ID_HELP,
        envvar="NEXTMV_INSTANCE_ID",
        metavar="INSTANCE_ID",
    ),
    Field(description=_INSTANCE_ID_HELP),
]

_INPUT_SET_ID_HELP = "The Nextmv Cloud input set ID."
InputSetIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--input-set-id",
        "-s",
        help=_INPUT_SET_ID_HELP,
        envvar="NEXTMV_INPUT_SET_ID",
        metavar="INPUT_SET_ID",
    ),
    Field(description=_INPUT_SET_ID_HELP),
]

_MANAGED_INPUT_ID_HELP = "The Nextmv Cloud managed input ID."
ManagedInputIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--managed-input-id",
        "-m",
        help=_MANAGED_INPUT_ID_HELP,
        envvar="NEXTMV_MANAGED_INPUT_ID",
        metavar="MANAGED_INPUT_ID",
    ),
    Field(description=_MANAGED_INPUT_ID_HELP),
]

_RUN_ID_HELP = "The Nextmv run ID."
RunIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--run-id",
        "-r",
        help=_RUN_ID_HELP,
        envvar="NEXTMV_RUN_ID",
        metavar="RUN_ID",
    ),
    Field(description=_RUN_ID_HELP),
]

_ACCEPTANCE_TEST_ID_HELP = "The Nextmv Cloud acceptance test ID."
AcceptanceTestIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--acceptance-test-id",
        "-t",
        help=_ACCEPTANCE_TEST_ID_HELP,
        envvar="NEXTMV_ACCEPTANCE_TEST_ID",
        metavar="ACCEPTANCE_TEST_ID",
    ),
    Field(description=_ACCEPTANCE_TEST_ID_HELP),
]

_BATCH_EXPERIMENT_ID_HELP = "The Nextmv Cloud batch experiment ID."
BatchExperimentIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--batch-experiment-id",
        "-b",
        help=_BATCH_EXPERIMENT_ID_HELP,
        envvar="NEXTMV_BATCH_EXPERIMENT_ID",
        metavar="BATCH_EXPERIMENT_ID",
    ),
    Field(description=_BATCH_EXPERIMENT_ID_HELP),
]

_SCENARIO_TEST_ID_HELP = "The Nextmv Cloud scenario test ID."
ScenarioTestIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--scenario-test-id",
        help=_SCENARIO_TEST_ID_HELP,
        envvar="NEXTMV_SCENARIO_TEST_ID",
        metavar="SCENARIO_TEST_ID",
    ),
    Field(description=_SCENARIO_TEST_ID_HELP),
]

_SECRETS_COLLECTION_ID_HELP = "The Nextmv Cloud secrets collection ID."
SecretsCollectionIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--secrets-collection-id",
        "-s",
        help=_SECRETS_COLLECTION_ID_HELP,
        envvar="NEXTMV_SECRETS_COLLECTION_ID",
        metavar="SECRETS_COLLECTION_ID",
    ),
    Field(description=_SECRETS_COLLECTION_ID_HELP),
]

_SHADOW_TEST_ID_HELP = "The Nextmv Cloud shadow test ID."
ShadowTestIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--shadow-test-id",
        help=_SHADOW_TEST_ID_HELP,
        envvar="NEXTMV_SHADOW_TEST_ID",
        metavar="SHADOW_TEST_ID",
    ),
    Field(description=_SHADOW_TEST_ID_HELP),
]

_SWITCHBACK_TEST_ID_HELP = "The Nextmv Cloud switchback test ID."
SwitchbackTestIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--switchback-test-id",
        help=_SWITCHBACK_TEST_ID_HELP,
        envvar="NEXTMV_SWITCHBACK_TEST_ID",
        metavar="SWITCHBACK_TEST_ID",
    ),
    Field(description=_SWITCHBACK_TEST_ID_HELP),
]

_ENSEMBLE_DEFINITION_ID_HELP = "The Nextmv Cloud ensemble definition ID."
EnsembleDefinitionIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--ensemble-definition-id",
        "-e",
        help=_ENSEMBLE_DEFINITION_ID_HELP,
        envvar="NEXTMV_ENSEMBLE_DEFINITION_ID",
        metavar="ENSEMBLE_DEFINITION_ID",
    ),
    Field(description=_ENSEMBLE_DEFINITION_ID_HELP),
]

_ACCOUNT_ID_HELP = "The Nextmv Cloud account ID."
AccountIdOption: TypeAlias = Annotated[
    str,
    typer.Option(
        "--account-id",
        help=_ACCOUNT_ID_HELP,
        envvar="NEXTMV_ACCOUNT_ID",
        metavar="ACCOUNT_ID",
    ),
    Field(description=_ACCOUNT_ID_HELP),
]


# ---------------------------------------------------------------------------
# Optional ID aliases
#
# Used when creating a new entity and the ID is optional (auto-generated
# if omitted). The long flag and metavar match the required variant above.
# ---------------------------------------------------------------------------

_OPTIONAL_VERSION_ID_HELP = (
    "An optional ID for the Nextmv Cloud version. "
    "If not provided, a random ID will be generated."
)
OptionalVersionIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--version-id",
        "-v",
        help=_OPTIONAL_VERSION_ID_HELP,
        envvar="NEXTMV_VERSION_ID",
        metavar="VERSION_ID",
    ),
    Field(description=_OPTIONAL_VERSION_ID_HELP),
]

_OPTIONAL_INSTANCE_ID_HELP = (
    "An optional ID for the Nextmv Cloud instance. "
    "If not provided, a random ID will be generated."
)
OptionalInstanceIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--instance-id",
        "-i",
        help=_OPTIONAL_INSTANCE_ID_HELP,
        envvar="NEXTMV_INSTANCE_ID",
        metavar="INSTANCE_ID",
    ),
    Field(description=_OPTIONAL_INSTANCE_ID_HELP),
]

_OPTIONAL_INPUT_SET_ID_HELP = (
    "An optional ID for the Nextmv Cloud input set. "
    "If not provided, a random ID will be generated."
)
OptionalInputSetIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--input-set-id",
        "-s",
        help=_OPTIONAL_INPUT_SET_ID_HELP,
        envvar="NEXTMV_INPUT_SET_ID",
        metavar="INPUT_SET_ID",
    ),
    Field(description=_OPTIONAL_INPUT_SET_ID_HELP),
]

_OPTIONAL_SECRETS_COLLECTION_ID_HELP = (
    "An optional ID for the Nextmv Cloud secrets collection. "
    "If not provided, a random ID will be generated."
)
OptionalSecretsCollectionIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--secrets-collection-id",
        "-s",
        help=_OPTIONAL_SECRETS_COLLECTION_ID_HELP,
        envvar="NEXTMV_SECRETS_COLLECTION_ID",
        metavar="SECRETS_COLLECTION_ID",
    ),
    Field(description=_OPTIONAL_SECRETS_COLLECTION_ID_HELP),
]

_OPTIONAL_MANAGED_INPUT_ID_HELP = (
    "An optional ID for the Nextmv Cloud managed input. "
    "If not provided, a random ID will be generated."
)
OptionalManagedInputIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--managed-input-id",
        "-m",
        help=_OPTIONAL_MANAGED_INPUT_ID_HELP,
        envvar="NEXTMV_MANAGED_INPUT_ID",
        metavar="MANAGED_INPUT_ID",
    ),
    Field(description=_OPTIONAL_MANAGED_INPUT_ID_HELP),
]

_OPTIONAL_ACCEPTANCE_TEST_ID_HELP = (
    "An optional ID for the Nextmv Cloud acceptance test. "
    "If not provided, a random ID will be generated."
)
OptionalAcceptanceTestIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--acceptance-test-id",
        "-t",
        help=_OPTIONAL_ACCEPTANCE_TEST_ID_HELP,
        envvar="NEXTMV_ACCEPTANCE_TEST_ID",
        metavar="ACCEPTANCE_TEST_ID",
    ),
    Field(description=_OPTIONAL_ACCEPTANCE_TEST_ID_HELP),
]

_OPTIONAL_BATCH_EXPERIMENT_ID_HELP = (
    "An optional ID for the Nextmv Cloud batch experiment. "
    "If not provided, a random ID will be generated."
)
OptionalBatchExperimentIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--batch-experiment-id",
        "-b",
        help=_OPTIONAL_BATCH_EXPERIMENT_ID_HELP,
        envvar="NEXTMV_BATCH_EXPERIMENT_ID",
        metavar="BATCH_EXPERIMENT_ID",
    ),
    Field(description=_OPTIONAL_BATCH_EXPERIMENT_ID_HELP),
]

_OPTIONAL_SCENARIO_TEST_ID_HELP = (
    "An optional ID for the Nextmv Cloud scenario test. "
    "If not provided, a random ID will be generated."
)
OptionalScenarioTestIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--scenario-test-id",
        help=_OPTIONAL_SCENARIO_TEST_ID_HELP,
        envvar="NEXTMV_SCENARIO_TEST_ID",
        metavar="SCENARIO_TEST_ID",
    ),
    Field(description=_OPTIONAL_SCENARIO_TEST_ID_HELP),
]

_OPTIONAL_ENSEMBLE_DEFINITION_ID_HELP = (
    "An optional ID for the Nextmv Cloud ensemble definition. "
    "If not provided, a random ID will be generated."
)
OptionalEnsembleDefinitionIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--ensemble-definition-id",
        "-e",
        help=_OPTIONAL_ENSEMBLE_DEFINITION_ID_HELP,
        envvar="NEXTMV_ENSEMBLE_DEFINITION_ID",
        metavar="ENSEMBLE_DEFINITION_ID",
    ),
    Field(description=_OPTIONAL_ENSEMBLE_DEFINITION_ID_HELP),
]

_OPTIONAL_SHADOW_TEST_ID_HELP = (
    "An optional ID for the Nextmv Cloud shadow test. "
    "If not provided, a random ID will be generated."
)
OptionalShadowTestIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--shadow-test-id",
        help=_OPTIONAL_SHADOW_TEST_ID_HELP,
        envvar="NEXTMV_SHADOW_TEST_ID",
        metavar="SHADOW_TEST_ID",
    ),
    Field(description=_OPTIONAL_SHADOW_TEST_ID_HELP),
]

_OPTIONAL_SWITCHBACK_TEST_ID_HELP = (
    "An optional ID for the Nextmv Cloud switchback test. "
    "If not provided, a random ID will be generated."
)
OptionalSwitchbackTestIdOption: TypeAlias = Annotated[
    str | None,
    typer.Option(
        "--switchback-test-id",
        help=_OPTIONAL_SWITCHBACK_TEST_ID_HELP,
        envvar="NEXTMV_SWITCHBACK_TEST_ID",
        metavar="SWITCHBACK_TEST_ID",
    ),
    Field(description=_OPTIONAL_SWITCHBACK_TEST_ID_HELP),
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
