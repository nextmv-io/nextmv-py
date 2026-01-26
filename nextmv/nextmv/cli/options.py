"""
Shared CLI options for the Nextmv CLI.

This module defines reusable option types that can be imported
and used across all CLI commands.
"""

from typing import Annotated

import typer

# profile option - can be used in any command to specify which profile to use.
# Define it as follows in commands or callbacks, as necessary:
# profile: ProfileOption = None
ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile to use for this action. Use [code]nextmv configuration[/code] to manage profiles.",
        envvar="NEXTMV_PROFILE",
        metavar="PROFILE_NAME",
    ),
]

# app_id option - can be used in any command that requires an application ID.
# Define it as follows in commands or callbacks, as necessary:
# app_id: AppIDOption
AppIDOption = Annotated[
    str,
    typer.Option(
        "--app-id",
        "-a",
        help="The Nextmv Cloud application ID to use for this action.",
        envvar="NEXTMV_APP_ID",
        metavar="APP_ID",
    ),
]

# run_id option - can be used in any command that requires a run ID.
# Define it as follows in commands or callbacks, as necessary:
# run_id: RunIDOption
RunIDOption = Annotated[
    str,
    typer.Option(
        "--run-id",
        "-r",
        help="The Nextmv Cloud run ID to use for this action.",
        envvar="NEXTMV_RUN_ID",
        metavar="RUN_ID",
    ),
]

# version_id option - can be used in any command that requires a version ID.
# Define it as follows in commands or callbacks, as necessary:
# version_id: VersionIDOption
VersionIDOption = Annotated[
    str,
    typer.Option(
        "--version-id",
        "-v",
        help="The Nextmv Cloud version ID to use for this action.",
        envvar="NEXTMV_VERSION_ID",
        metavar="VERSION_ID",
    ),
]

# input_set_id option - can be used in any command that requires an input set ID.
# Define it as follows in commands or callbacks, as necessary:
# input_set_id: InputSetIDOption
InputSetIDOption = Annotated[
    str,
    typer.Option(
        "--input-set-id",
        "-s",
        help="The Nextmv Cloud input set ID to use for this action.",
        envvar="NEXTMV_INPUT_SET_ID",
        metavar="INPUT_SET_ID",
    ),
]

# instance_id option - can be used in any command that requires an instance ID.
# Define it as follows in commands or callbacks, as necessary:
# instance_id: InstanceIDOption
InstanceIDOption = Annotated[
    str,
    typer.Option(
        "--instance-id",
        "-i",
        help="The Nextmv Cloud instance ID to use for this action.",
        envvar="NEXTMV_INSTANCE_ID",
        metavar="INSTANCE_ID",
    ),
]

# managed_input_id option - can be used in any command that requires a managed input ID.
# Define it as follows in commands or callbacks, as necessary:
# managed_input_id: ManagedInputIDOption
ManagedInputIDOption = Annotated[
    str,
    typer.Option(
        "--managed-input-id",
        "-m",
        help="The Nextmv Cloud managed input ID to use for this action.",
        envvar="NEXTMV_MANAGED_INPUT_ID",
        metavar="MANAGED_INPUT_ID",
    ),
]

# ensemble_definition_id option - can be used in any command that requires an ensemble definition ID.
# Define it as follows in commands or callbacks, as necessary:
# ensemble_definition_id: EnsembleDefinitionIDOption
EnsembleDefinitionIDOption = Annotated[
    str,
    typer.Option(
        "--ensemble-definition-id",
        "-e",
        help="The Nextmv Cloud ensemble definition ID to use for this action.",
        envvar="NEXTMV_ENSEMBLE_DEFINITION_ID",
        metavar="ENSEMBLE_DEFINITION_ID",
    ),
]

# account_id option - can be used in any command that requires an account ID.
# Define it as follows in commands or callbacks, as necessary:
# account_id: AccountIDOption
AccountIDOption = Annotated[
    str,
    typer.Option(
        "--account-id",
        "-a",
        help="The Nextmv Cloud account ID to use for this action.",
        envvar="NEXTMV_ACCOUNT_ID",
        metavar="ACCOUNT_ID",
    ),
]

# acceptance_test_id option - can be used in any command that requires an acceptance test ID.
# Define it as follows in commands or callbacks, as necessary:
# acceptance_test_id: AcceptanceTestIDOption
AcceptanceTestIDOption = Annotated[
    str,
    typer.Option(
        "--acceptance-test-id",
        "-t",
        help="The Nextmv Cloud acceptance test ID to use for this action.",
        envvar="NEXTMV_ACCEPTANCE_TEST_ID",
        metavar="ACCEPTANCE_TEST_ID",
    ),
]

# batch_experiment_id option - can be used in any command that requires a batch experiment ID.
# Define it as follows in commands or callbacks, as necessary:
# batch_experiment_id: BatchExperimentIDOption
BatchExperimentIDOption = Annotated[
    str,
    typer.Option(
        "--batch-experiment-id",
        "-b",
        help="The Nextmv Cloud batch experiment ID to use for this action.",
        envvar="NEXTMV_BATCH_EXPERIMENT_ID",
        metavar="BATCH_EXPERIMENT_ID",
    ),
]

# scenario_test_id option - can be used in any command that requires a scenario test ID.
# Define it as follows in commands or callbacks, as necessary:
# scenario_test_id: ScenarioTestIDOption
ScenarioTestIDOption = Annotated[
    str,
    typer.Option(
        "--scenario-test-id",
        "-i",
        help="The Nextmv Cloud scenario test ID to use for this action.",
        envvar="NEXTMV_SCENARIO_TEST_ID",
        metavar="SCENARIO_TEST_ID",
    ),
]

# secrets_collection_id option - can be used in any command that requires a secrets collection ID.
# Define it as follows in commands or callbacks, as necessary:
# secrets_collection_id: SecretsCollectionIDOption
SecretsCollectionIDOption = Annotated[
    str,
    typer.Option(
        "--secrets-collection-id",
        "-s",
        help="The Nextmv Cloud secrets collection ID to use for this action.",
        envvar="NEXTMV_SECRETS_COLLECTION_ID",
        metavar="SECRETS_COLLECTION_ID",
    ),
]

# shadow_test_id option - can be used in any command that requires a shadow test ID.
# Define it as follows in commands or callbacks, as necessary:
# shadow_test_id: ShadowTestIDOption
ShadowTestIDOption = Annotated[
    str,
    typer.Option(
        "--shadow-test-id",
        "-s",
        help="The Nextmv Cloud shadow test ID to use for this action.",
        envvar="NEXTMV_SHADOW_TEST_ID",
        metavar="SHADOW_TEST_ID",
    ),
]

# switchback_test_id option - can be used in any command that requires a switchback test ID.
# Define it as follows in commands or callbacks, as necessary:
# switchback_test_id: SwitchbackTestIDOption
SwitchbackTestIDOption = Annotated[
    str,
    typer.Option(
        "--switchback-test-id",
        "-s",
        help="The Nextmv Cloud switchback test ID to use for this action.",
        envvar="NEXTMV_SWITCHBACK_TEST_ID",
        metavar="SWITCHBACK_TEST_ID",
    ),
]
