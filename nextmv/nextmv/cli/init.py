"""
This module defines the init command for the Nextmv CLI.
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass

import questionary
import rich
import rich.markup
import typer
from rich.prompt import Prompt

from nextmv import cloud, local
from nextmv.cli.cloud.app.push import handle_push
from nextmv.cli.configuration.config import build_cloud_app, load_config, obscure_api_key
from nextmv.cli.message import choice, confirmation, directory_path, error, in_progress, info, message, rule, success
from nextmv.cloud.community import _get_valid_path
from nextmv.content_format import ContentFormat
from nextmv.manifest import ManifestType, initialize_manifest
from nextmv.safe import safe_id

# Set up subcommand application.
app = typer.Typer()


@dataclass
class ExecutedCommand:
    """
    Simple class to track a command that was executed in the tutorial.

    Attributes
    ----------
    cmd : str
        The command that was executed.
    explanation : str
        A brief explanation of what the command does.
    """

    cmd: str
    """
    The command that was executed.
    """
    explanation: str
    """
    A brief explanation of what the command does.
    """


@app.command()
def init() -> None:
    """
    Get started with the Nextmv CLI.
    """

    begin = str(rich.markup.render(":rocket: Let's go!"))
    starting_choice = choice(
        msg="Welcome to the Nextmv CLI! This command will guide you through your first steps with Nextmv.",
        choices=[begin, "Maybe later."],
        default=begin,
    )
    if starting_choice != begin:
        info("You can run [code]nextmv init[/code] at any time to get started.")
        raise typer.Exit()
    rule()

    is_template = _template_question()
    rule()

    manifest_type = _manifest_type_question(is_template)
    rule()

    content_format = _content_format_question(is_template)
    rule()

    dirpath = _path_question(is_template)
    rule()

    local_app = _handle_files_initialization(is_template, dirpath, manifest_type, content_format)
    rule()

    commands = []
    local_run_id, cmd1 = _handle_local_run_create(local_app, is_template)
    commands.append(cmd1)
    rule()

    cmd2 = _handle_local_run_get(local_run_id)
    commands.append(cmd2)
    rule()

    cmd3 = _handle_configuration()
    commands.append(cmd3)
    rule()

    cloud_app, cmd4 = _handle_app_sync()
    commands.append(cmd4)
    rule()

    cmd5 = _handle_app_push(cloud_app)
    commands.append(cmd5)
    rule()

    cloud_run_id, cmd6 = _handle_cloud_run_create(cloud_app, local_app, is_template)
    commands.append(cmd6)
    rule()

    cmd7 = _handle_cloud_run_get(cloud_app, cloud_run_id)
    commands.append(cmd7)
    rule()

    message(
        msg="Congratulations! You've completed the Nextmv CLI tutorial. "
        "This is a summary of the commands that were executed during the tutorial:",
        emoji=":rocket:",
    )
    for cmd in commands:
        if cmd is not None:
            message(msg=f"- {cmd.explanation}: [code]{cmd.cmd}[/code]", indents=1)

    print("", file=sys.stderr)
    message(msg="[yellow]Happy optimizing![/yellow]", emoji=":sparkles:")


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


def _handle_files_initialization(
    is_template: bool,
    dirpath: str,
    manifest_type: ManifestType,
    content_format: ContentFormat,
) -> local.Application:
    """
    Handle the file initialization for a new Nextmv application.

    Depending on whether the user is starting from a template or an existing
    model, this function either scaffolds a full application from a template or
    initializes only the manifest file. In both cases, it prompts the user for
    an app ID and registers the application in the local registry.

    Parameters
    ----------
    is_template : bool
        If True, a full application template is scaffolded under `dirpath`. If
        False, only the manifest (`app.yaml`) is initialized in the existing
        model directory.
    dirpath : str
        Path to the directory where the application or manifest will be
        initialized.
    manifest_type : ManifestType
        Language/runtime type of the manifest to initialize.
    content_format : ContentFormat
        Content format (e.g. JSON, multi-file) to use for the application's
        input and output.

    Returns
    -------
    Application
        The initialized Nextmv application, which is also registered in the
        local registry.
    """
    if is_template:
        template = f"{manifest_type.value}_{content_format.value}_template"
        resolved_template = _get_valid_path(template, os.stat)
        local_app = local.Application.initialize(
            src=resolved_template,
            description="Sample Nextmv application initialized with the CLI.",
            manifest_type=manifest_type,
            content_format=content_format,
            destination=dirpath,
            should_register=False,
        )
        success(
            f"[magenta]{manifest_type.value}[/magenta], [magenta]{content_format.value}[/magenta] template "
            f"initialized at [magenta]{local_app.src}[/magenta]."
        )

    else:
        dst = initialize_manifest(manifest_type=manifest_type, content_format=content_format, dirpath=dirpath)
        success(
            f"[magenta]{manifest_type.value}[/magenta], [magenta]{content_format.value}[/magenta] manifest "
            f"initialized at [magenta]{dst}[/magenta]."
        )
        local_app = local.Application(src=dst)

    return local_app


def _handle_local_run_create(local_app: local.Application, is_template: bool) -> tuple[str, ExecutedCommand]:
    """
    Prompt the user to start a local run for the initialized application.

    Asks whether to immediately start a local run. If confirmed, changes the
    working directory to the application source, prompts for an input path,
    and invokes ``nextmv local run create``. Exits early if the user declines.

    Parameters
    ----------
    local_app : Application
        The registered local application for which the run will be started.
    is_template : bool
        Indicates whether the application was initialized from a template.

    Returns
    -------
    tuple[str, ExecutedCommand]
        The run ID returned by the local run command and the command that was
        executed.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to start a run.
    """
    create_run = confirmation(
        msg=f"Do you want to start a run for local app at [magenta]{local_app.src}[/magenta] now?",
        default=True,
    )
    if not create_run:
        info("You can start a local run for this application at any time with [code]nextmv local run create[/code].")
        raise typer.Exit()

    cwd = os.getcwd()
    in_progress(f"Changing working directory from [magenta]{cwd}[/magenta] to [magenta]{local_app.src}[/magenta].")
    os.chdir(local_app.src)
    success(f"Working directory is now [magenta]{os.getcwd()}[/magenta].")

    default = "."
    if is_template and local_app.content_format == ContentFormat.JSON:
        default = "input.json"
    elif is_template and local_app.content_format == ContentFormat.MULTI_FILE:
        default = "inputs/"

    dirpath = directory_path(
        msg="Please select a directory or file to use as input for the local run",
        default=default,
        only_directories=False,
    )
    command = ["nextmv", "local", "run", "create", "--input", dirpath]
    str_cmd = " ".join(command)
    in_progress(f"Starting local run with command: [code]{str_cmd}[/code]")

    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to start local run. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    raw_output = result.stdout.strip()
    output = json.loads(raw_output)
    run_id = output.get("run_id")
    if not run_id:
        error(
            f"Local run started but no run ID was returned. Please check the output below for details.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    success(f"Local run started successfully with run ID: [magenta]{run_id}[/magenta].")

    return run_id, ExecutedCommand(cmd=str_cmd, explanation="Start a [italic]local[/italic] run")


def _handle_local_run_get(run_id: str) -> ExecutedCommand:
    """
    Prompt the user to retrieve the results of a completed local run.

    Asks whether to fetch the run results immediately. If confirmed, prompts
    for an output path and invokes ``nextmv local run get`` to save the
    results. Exits early if the user declines.

    Parameters
    ----------
    run_id : str
        The ID of the local run whose results should be retrieved.

    Returns
    -------
    ExecutedCommand
        The command that was executed to retrieve the local run results.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to retrieve results or if the
        command fails.
    """
    get_result = confirmation(
        msg=f"Do you want to get the results of the local run with ID [magenta]{run_id}[/magenta] now?",
        default=True,
    )
    if not get_result:
        info("You can get the results of this local run at any time with [code]nextmv local run get[/code].")
        raise typer.Exit()

    command = [
        "nextmv",
        "local",
        "run",
        "get",
        "--run-id",
        run_id,
    ]
    str_cmd = " ".join(command)
    in_progress(f"Getting local run results with command: [code]{str_cmd}[/code]")

    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to get local run results. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    return ExecutedCommand(cmd=str_cmd, explanation="Get the results of a [italic]local[/italic] run")


def _handle_configuration() -> ExecutedCommand | None:
    """
    Prompt the user to configure the Nextmv CLI if not already configured.

    Checks whether a configuration already exists. If not, asks the user
    whether to configure the CLI now. If confirmed, guides them through
    obtaining an API key and invokes ``nextmv configuration create`` to
    store it. Exits early if the user declines or if the command fails.

    Returns
    -------
    ExecutedCommand | None
        The command that was executed to create the configuration.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to configure the CLI.
    """
    config = load_config()
    if config != {}:
        success("Nextmv CLI is already configured. Skipping configuration step.")
        return None

    should_configure = confirmation(
        "The Nextmv CLI is not configured yet. Do you want to configure it now?",
        default=True,
    )
    if not should_configure:
        info("You can configure the Nextmv CLI at any time with [code]nextmv configuration create[/code].")
        raise typer.Exit()

    info("To configure the Nextmv CLI, you need an API key. Follow these steps to create one:")
    message(
        msg="Go to the [link=https://cloud.nextmv.io]Nextmv Cloud Console[/link]. Sign in or create an account.",
        emoji=":sparkles:",
        indents=1,
    )
    message(
        msg="Verify your account (if you haven't already). You'll receive an e-mail with a verification link.",
        emoji=":sparkles:",
        indents=1,
    )
    message(
        msg="Go to [magenta]Team Settings[/magenta] :point_right: [magenta]API Keys[/magenta].",
        emoji=":sparkles:",
        indents=1,
    )

    while True:
        api_key = Prompt.ask(
            "Please enter your Nextmv API key to complete the configuration",
            case_sensitive=True,
            password=True,
        )
        if api_key != "":
            break

        error("API key cannot be empty. Please enter a valid API key to complete the configuration.")

    command = ["nextmv", "configuration", "create", "--api-key", api_key]
    obfuscated = command.copy()

    api_key = obscure_api_key(api_key)
    obfuscated[-1] = api_key
    str_cmd = " ".join(obfuscated)

    in_progress(f"Creating configuration with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to create configuration. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    return ExecutedCommand(cmd=str_cmd, explanation="Configure the Nextmv CLI")


def _handle_app_sync() -> tuple[cloud.Application, ExecutedCommand]:
    """
    Prompt the user to sync their local application with Nextmv Cloud.

    Asks whether to sync the local application with a Cloud app. If confirmed,
    prompts for a target Cloud app ID (generating one if left blank) and
    invokes ``nextmv local app sync``. Exits early if the user declines or if
    the command fails.

    Returns
    -------
    tuple[cloud.Application, ExecutedCommand]
        The Cloud application that the local app was synced with and the command
        that was executed to perform the sync.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to sync or if the command fails.
    """
    should_sync = confirmation(
        "Do you want to sync your local application with Nextmv Cloud?",
        default=True,
    )
    if not should_sync:
        info(
            "You can sync your local application with Nextmv Cloud at any time with [code]nextmv local app sync[/code]."
        )
        raise typer.Exit()

    target_app_id = Prompt.ask(
        "Please enter the ID of the Cloud app you want to sync to, or leave blank to sync with a new app",
        case_sensitive=False,
    )
    if target_app_id == "":
        target_app_id = safe_id("cloud-app")

    info(f"Your local application will be synced with Cloud app ID [magenta]{target_app_id}[/magenta].")

    cloud_app = build_cloud_app(app_id=target_app_id)

    command = ["nextmv", "local", "app", "sync", "--target-app-id", cloud_app.id]
    str_cmd = " ".join(command)
    in_progress(f"Syncing local application with command: [code]{str_cmd}[/code]")

    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to sync application. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    runs_url = f"https://cloud.nextmv.io/app/{cloud_app.id}/runs"
    success(
        "You can see the synced runs in the Nextmv Cloud Console at "
        f"[link={runs_url}][magenta]{runs_url}[/magenta][/link]."
    )

    return cloud_app, ExecutedCommand(cmd=str_cmd, explanation="Sync the local application with Nextmv Cloud")


def _handle_app_push(cloud_app: cloud.Application) -> ExecutedCommand:
    """
    Prompt the user to push their application to Nextmv Cloud.

    First confirms whether the user has an active Nextmv Plan, providing
    guidance to activate one if not. Then asks whether to push (deploy) the
    app to Nextmv Cloud. If confirmed, invokes ``cloud_app.push``. Exits early
    if the user declines to push.

    Parameters
    ----------
    cloud_app : cloud.Application
        The Cloud application to push.

    Returns
    -------
    ExecutedCommand
        The command that was executed to push the app to Nextmv Cloud.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to push the app.
    """
    has_premium = confirmation(
        "For the next step, you need an active Nextmv Plan. Do you have an active plan with Nextmv?",
        default=True,
    )
    if not has_premium:
        info(
            "You can activate your Nextmv Plan from the [magenta]Team Settings[/magenta] page in "
            "the [link=https://cloud.nextmv.io]Nextmv Cloud Console[/link]."
        )
        raise typer.Exit()

    should_push = confirmation(
        "Do you want to push (deploy) your app to Nextmv Cloud now?",
        default=True,
    )
    if not should_push:
        info("You can push your app to Nextmv Cloud at any time with [code]nextmv cloud app push[/code].")
        raise typer.Exit()

    str_cmd = f"[code]nextmv cloud app push --app-id {cloud_app.id}[/code]"
    in_progress(f"Pushing application with command: [code]{str_cmd}[/code]")
    handle_push(
        cloud_app=cloud_app,
        app_id=cloud_app.id,
        app_dir=None,
        manifest=None,
        version_id=None,
        version_yes=False,
        version_no=False,
        update_defined=False,
        update_instance_id=None,
        create_defined=False,
        create_instance_id=None,
    )

    return ExecutedCommand(cmd=str_cmd, explanation="Push the application to Nextmv Cloud")


def _handle_cloud_run_create(
    cloud_app: cloud.Application,
    local_app: local.Application,
    is_template: bool,
) -> tuple[str, ExecutedCommand]:
    """
    Prompt the user to start a run for their Cloud application.

    Asks whether to immediately start a run for the Cloud app. If confirmed,
    prompts for an input path, and invokes `cloud_app.run` to start the run.
    Exits early if the user declines.

    Parameters
    ----------
    cloud_app : cloud.Application
        The Cloud application to run.
    local_app : local.Application
        The local application to use as input for the run.
    is_template : bool
        Whether the local application is a template.

    Returns
    -------
    tuple[str, ExecutedCommand]
        The run ID returned by the Cloud run command and the command that was
        executed.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to start a run.
    """

    create_run = confirmation(
        msg=f"Do you want to start a [italic]remote[/italic] run for Cloud app [magenta]{cloud_app.id}[/magenta] now?",
        default=True,
    )
    if not create_run:
        info(
            "You can start a [italic]remote[/italic] run for the Cloud app at any time with "
            "[code]nextmv cloud run create[/code]."
        )
        raise typer.Exit()

    default = "."
    if is_template and local_app.content_format == ContentFormat.JSON:
        default = "input.json"
    elif is_template and local_app.content_format == ContentFormat.MULTI_FILE:
        default = "inputs/"

    dirpath = directory_path(
        msg="Please select a directory or file to use as input for the [italic]remote[/italic] run",
        default=default,
        only_directories=False,
    )
    command = ["nextmv", "cloud", "run", "create", "--app-id", cloud_app.id, "--input", dirpath]
    str_cmd = " ".join(command)
    in_progress(f"Starting [italic]remote[/italic] run with command: [code]{str_cmd}[/code]")

    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to start [italic]remote[/italic] run. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    raw_output = result.stdout.strip()
    output = json.loads(raw_output)
    run_id = output.get("run_id")
    if not run_id:
        error(
            f"[italic]Remote[/italic] run started but no run ID was returned. Please check the output for details.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    success(f"[italic]Remote[/italic] run started successfully with run ID: [magenta]{run_id}[/magenta].")

    return run_id, ExecutedCommand(cmd=str_cmd, explanation="Start a [italic]remote[/italic] run for the Cloud app")


def _handle_cloud_run_get(cloud_app: cloud.Application, run_id: str) -> ExecutedCommand:
    """
    Prompt the user to retrieve the results of a completed Cloud run.

    Asks whether to fetch the run results immediately. If confirmed, prompts
    for an output path and invokes `cloud_app.run_get` to save the results.
    Exits early if the user declines.

    Parameters
    ----------
    cloud_app : cloud.Application
        The Cloud application whose run should be retrieved.
    run_id : str
        The ID of the Cloud run whose results should be retrieved.

    Returns
    -------
    ExecutedCommand
        The command that was executed to retrieve the Cloud run results.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to retrieve results or if the
        command fails.
    """
    get_result = confirmation(
        msg=f"Do you want to get the results of the [italic]remote[/italic] run with ID [magenta]{run_id}[/magenta]?",
        default=True,
    )
    if not get_result:
        info(
            "You can get the results of this [italic]remote[/italic] run at any time with "
            "[code]nextmv cloud run get[/code]."
        )
        raise typer.Exit()

    command = [
        "nextmv",
        "cloud",
        "run",
        "get",
        "--app-id",
        cloud_app.id,
        "--run-id",
        run_id,
    ]
    str_cmd = " ".join(command)
    in_progress(f"Getting [italic]remote[/italic] run results with command: [code]{str_cmd}[/code]")

    result = _cli_call(command)

    if result.returncode != 0:
        error(
            f"Failed to get [italic]remote[/italic] run results. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    return ExecutedCommand(cmd=str_cmd, explanation="Get the results of a [italic]remote[/italic] run")


def _cli_call(command: list[str]) -> subprocess.CompletedProcess:
    """
    Execute a CLI command as a subprocess and return the result.

    Parameters
    ----------
    command : list[str]
        The command and its arguments to execute.

    Returns
    -------
    subprocess.CompletedProcess
        The result of the subprocess call, including return code, stdout, and
        stderr.

    Raises
    ------
    typer.Exit
        Exits the program with code 1 if the subprocess raises an exception.
    """
    try:
        result = subprocess.run(
            command,
            env=os.environ,
            check=False,
            text=True,
            capture_output=True,
        )
    except Exception as e:
        error(f"An error occurred while running command '{' '.join(command)}': {e}")

    rich.print(result.stdout)
    rich.print(result.stderr, file=sys.stderr)

    return result
