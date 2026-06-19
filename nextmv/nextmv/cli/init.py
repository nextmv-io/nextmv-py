"""
This module defines the init command for the Nextmv CLI.
"""

import json
import os
import subprocess
import sys
import threading
from dataclasses import dataclass

import questionary
import rich
import rich.markup
import typer
from rich.prompt import Prompt

from nextmv import cloud, local
from nextmv.cli.cloud.app.push import handle_push
from nextmv.cli.configuration.config import build_cloud_app, obscure_api_key
from nextmv.cli.message import choice, confirmation, directory_path, error, in_progress, info, message, rule, success
from nextmv.cli.options import DebugOption
from nextmv.cloud.community import _get_valid_path
from nextmv.config import load_config
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
def init(_: DebugOption = False) -> None:
    """
    Get started with the Nextmv CLI.

    [bold][underline]Examples[/underline][/bold]

    - Start the tutorial.

        $ [dim]nextmv init[/dim]
    """

    begin = str(rich.markup.render(":rocket: Let's go!"))
    starting_choice = choice(
        msg="Welcome to the Nextmv CLI! This tutorial will guide you through your first steps with Nextmv.",
        choices=[begin, "Maybe later."],
        default=begin,
    )
    if starting_choice != begin:
        info("You can run [code]nextmv init[/code] at any time to get started.")
        raise typer.Exit()
    rule()

    manifest_type = _manifest_type_question()
    rule()

    template = _template_question(manifest_type)
    rule()

    content_format = _content_format_question()
    rule()

    dirpath = _path_question(template)

    local_app = _handle_files_initialization(template, dirpath, manifest_type, content_format)
    rule()

    if manifest_type == ManifestType.PYTHON and template == "demand-alloc":
        message(
            msg="This template is a complex, real-world example of a demand-forecast allocation workflow. "
            "Please navigate to the directory and read the [magenta]README.md[/magenta] files for more information.",
            emoji=":sparkles:",
        )
        rule()
        message(
            msg="Congratulations! You've completed the Nextmv CLI tutorial.",
            emoji=":rocket:",
        )

    else:
        commands = []
        try:
            local_run_id, cmds1 = _handle_local_run_create(local_app, template)
            commands.extend(cmds1)
            rule()

            cmd2 = _handle_local_run_get(local_run_id)
            commands.append(cmd2)
            rule()

            cmd3 = _handle_configuration()
            commands.append(cmd3)
            rule()

            cloud_app, cmds4 = _handle_app_sync()
            commands.extend(cmds4)
            rule()

            instance_id, cmd5 = _handle_app_push(cloud_app)
            commands.append(cmd5)
            rule()

            cloud_run_id, cmd6 = _handle_cloud_run_create(cloud_app, local_app, template, instance_id)
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
        except Exception:
            rule()
            message(
                msg="The tutorial was not completed! You can run [code]nextmv init[/code] any time.", emoji=":rabbit:"
            )
            if len(commands) > 0:
                message(
                    msg="Here are the commands that were run so far:",
                    emoji=":rocket:",
                )

        for cmd in commands:
            if cmd is not None:
                message(msg=f"- {cmd.explanation}: [code]{cmd.cmd}[/code]", indents=1)

    print("", file=sys.stderr)
    message(msg="[yellow]Happy optimizing![/yellow]", emoji=":sparkles:")


def _manifest_type_question() -> ManifestType:
    """
    Ask the user which language they want to use for their manifest.

    Returns
    -------
    ManifestType
        The type of manifest to initialize, based on the user's choice.
    """

    manifest_type = choice(
        msg="Which type (language) do you want to work with?",
        choices=[member.value for member in ManifestType],
        default=ManifestType.PYTHON.value,
    )

    return ManifestType(manifest_type)


def _template_question(manifest_type: ManifestType) -> str:
    """
    Ask the user how they want to start working with Nextmv.

    Returns
    -------
    str
        The user's choice for how to start working with Nextmv. If the user
        chooses to start with an example template, the value will be the name
        of the example. If they choose to start with an existing model, the
        value will be "existing".
    """

    hello_world = questionary.Choice(
        title="Example - hello world",
        description="A simple, beginner-friendly example to get you started with the basics of Nextmv.",
        value="hello-world",
    )
    existing_model = questionary.Choice(
        title="Existing model",
        description="I already have a model and want to make it work with Nextmv.",
        value="existing",
    )
    if manifest_type == ManifestType.PYTHON:
        choices = [
            hello_world,
            questionary.Choice(
                title="Example - class-room assignment",
                description="A more complete, real-world example to see Nextmv in action.",
                value="class-assign",
            ),
            questionary.Choice(
                title="Example - demand allocation workflow",
                description="A complex example showcasing a decision workflow with multiple steps and a sub-app.",
                value="demand-alloc",
            ),
            existing_model,
        ]
    else:
        choices = [hello_world, existing_model]

    init_type = choice(
        msg="How do you want to start working with Nextmv?",
        choices=choices,
        default=hello_world.value,
    )

    return init_type


def _content_format_question() -> ContentFormat:
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

    content_format = choice(
        msg="Which type of I/O (input/output) content format do you prefer for your app?",
        choices=choices,
        default=ContentFormat.JSON.value,
    )
    content_format = ContentFormat(content_format)

    return content_format


def _path_question(template: str) -> str:
    """
    Ask the user for the path to their existing model or where they want to
    initialize their template.

    Parameters
    ----------
    template : str
        The name of the template or "existing" if the user is working with an existing model.

    Returns
    -------
    str
        The path to the user's existing model or the path where they want to
        initialize their template.
    """

    msg = "What is the path to your existing model?"
    if template != "existing":
        msg = "Where would you like to initialize your Nextmv application template?"

    dirpath = directory_path(
        msg=msg,
        default=".",
    )
    dirpath = dirpath or "."

    return dirpath


def _handle_files_initialization(
    template: str,
    dirpath: str,
    manifest_type: ManifestType,
    content_format: ContentFormat,
) -> local.Application:
    """
    Handle the file initialization for a new Nextmv application.

    Depending on whether the user is starting from a template or an existing
    model, this function either scaffolds a full application from a template or
    initializes only the manifest file.

    Parameters
    ----------
    template : str
        The name of the template or "existing" if the user is working with an existing model.
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

    if template != "existing":
        template_dst = f"{manifest_type.value}_{content_format.value}_{template}"
        resolved_template = _get_valid_path(template_dst, os.stat)
        local_app = local.Application.initialize(
            src=resolved_template,
            description="Sample Nextmv application initialized with the CLI.",
            manifest_type=manifest_type,
            content_format=content_format,
            example=template,
            destination=dirpath,
            should_register=False,
        )
        success(
            f"[magenta]{manifest_type.value}[/magenta], [magenta]{content_format.value}[/magenta] template "
            f"initialized at [magenta]{local_app.src}[/magenta]."
        )

    else:
        manifest_path = initialize_manifest(manifest_type=manifest_type, content_format=content_format, dirpath=dirpath)
        success(
            f"[magenta]{manifest_type.value}[/magenta], [magenta]{content_format.value}[/magenta] manifest "
            f"initialized at [magenta]{manifest_path}[/magenta]."
        )
        local_app = local.Application(src=os.path.dirname(manifest_path))

    return local_app


def _handle_local_run_create(local_app: local.Application, template: str) -> tuple[str, list[ExecutedCommand]]:
    """
    Prompt the user to start a local run for the initialized application.

    Asks whether to immediately start a local run. If confirmed, changes the
    working directory to the application source, prompts for an input path,
    and invokes ``nextmv local run create``. Exits early if the user declines.

    Parameters
    ----------
    local_app : Application
        The registered local application for which the run will be started.
    template : str
        The name of the template or "existing" if the user is working with an existing model.

    Returns
    -------
    tuple[str, list[ExecutedCommand]]
        The run ID returned by the local run command and the list of commands
        that were executed.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to start a run.
    """

    # Ask if the user wants to start the local run or exit immedaitely.
    create_run = confirmation(
        msg=f"Do you want to start a run for local app at [magenta]{local_app.src}[/magenta] now?",
        default=True,
    )
    if not create_run:
        info("You can start a local run for this application at any time with [code]nextmv local run create[/code]")
        raise typer.Exit()

    # Handle changing directories to the src of the local application.
    commands = []
    cmd_str = f"cd {local_app.src}"
    in_progress(f"Changing working directory with command: [code]{cmd_str}[/code]")
    os.chdir(local_app.src)
    success(f"Working directory is now [magenta]{os.getcwd()}[/magenta].")
    cmd = ExecutedCommand(cmd=cmd_str, explanation="Change working directory to the application source")
    commands.append(cmd)

    # Depending on the type, we might need to execute an additional command.
    man_type = local_app.manifest.type
    if man_type != ManifestType.PYTHON:
        cmd_str = Prompt.ask(
            prompt=f"This application is of type [magenta]{man_type.value}[/magenta]. "
            "Please type the command needed to compile/build the application. Leave blank to omit",
            default="",
        )
        if cmd_str != "":
            result = _cli_call(cmd_str.split())
            cmd = ExecutedCommand(cmd=cmd_str, explanation="Compile/build the application")
            commands.append(cmd)

    # Select the input path to run the local app.
    default = "."
    if template != "existing" and local_app.content_format == ContentFormat.JSON:
        default = "input.json"
    elif template != "existing" and local_app.content_format == ContentFormat.MULTI_FILE:
        default = "inputs"

    dirpath = directory_path(
        msg="Please select a directory or file to use as input for the local run",
        default=default,
        only_directories=False,
    )

    # Actually execute the command to start the local run.
    command = ["nextmv", "local", "run", "create", "--input", dirpath]
    str_cmd = " ".join(command)
    in_progress(f"Starting local run with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors and parsing the run ID from the output.
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

    # If we got here, the run started successfully and we have a run ID.
    success(f"[italic]Local[/italic] run started successfully with run ID: [magenta]{run_id}[/magenta].")
    cmd = ExecutedCommand(cmd=str_cmd, explanation="Start a [italic]local[/italic] run")
    commands.append(cmd)

    return run_id, commands


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

    # Ask if the user wants to get the results of the local run or exit
    # immediately.
    get_result = confirmation(
        msg=f"Do you want to get the results of the local run with ID [magenta]{run_id}[/magenta] now?",
        default=True,
    )
    if not get_result:
        info("You can get the results of this local run at any time with [code]nextmv local run get[/code]")
        raise typer.Exit()

    # Actually execute the command to get the local run results.
    command = ["nextmv", "local", "run", "get", "--run-id", run_id, "--wait"]
    str_cmd = " ".join(command)
    in_progress(f"Getting local run results with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors.
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

    # Check if a configuration already exists. If it does, skip the
    # configuration step.
    config = load_config()
    if config != {}:
        success("Nextmv CLI is already configured. Skipping configuration step.")
        return None

    # If we got here, the CLI is not configured. Ask the user if they want to
    # configure it now.
    should_configure = confirmation(
        "The Nextmv CLI is not configured yet. Do you want to configure it now?",
        default=True,
    )
    if not should_configure:
        info("You can configure the Nextmv CLI at any time with [code]nextmv configuration create[/code]")
        raise typer.Exit()

    # If we got here, the user wants to configure the CLI. Guide them through
    # the process of obtaining an API key and creating the configuration.
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

    # Actually execute the command to create the configuration with the
    # provided API key.
    command = ["nextmv", "configuration", "create", "--api-key", api_key]
    obfuscated = command.copy()
    api_key = obscure_api_key(api_key)
    obfuscated[-1] = api_key
    str_cmd = " ".join(obfuscated)
    in_progress(f"Creating configuration with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors.
    if result.returncode != 0:
        error(
            f"Failed to create configuration. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    return ExecutedCommand(cmd=str_cmd, explanation="Configure the Nextmv CLI")


def _handle_app_sync() -> tuple[cloud.Application, list[ExecutedCommand]]:
    """
    Prompt the user to sync their local application with Nextmv Cloud.

    Asks whether to sync the local application with a Cloud app. If confirmed,
    prompts for a target Cloud app ID (generating one if left blank) and
    invokes ``nextmv local app sync``. Exits early if the user declines or if
    the command fails.

    Returns
    -------
    tuple[cloud.Application, list[ExecutedCommand]]
        The Cloud application that the local app was synced with and the
        commands that were executed to perform the sync.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to sync or if the command fails.
    """

    # Ask the user if they have an active Nextmv Plan, which is required to sync
    # an app to Nextmv Cloud. If they don't, provide guidance and exit.
    has_premium = confirmation(
        "For the next step, you need an active Nextmv Plan. Do you have an active plan with Nextmv?",
        default=True,
    )
    if not has_premium:
        info(
            "You can activate your Nextmv Plan by contacting "
            "[link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link]."
        )
        raise typer.Exit()

    # Ask the user if they want to sync their local application with Nextmv
    # Cloud or exit immediately.
    should_sync = confirmation(
        "Do you want to sync your local application with Nextmv Cloud?",
        default=True,
    )
    if not should_sync:
        info(
            "You can sync your local application with Nextmv Cloud at any time with [code]nextmv local app sync[/code]"
        )
        raise typer.Exit()

    # If we got here, the user wants to sync. Prompt for the target Cloud app
    # ID or generate one if left blank.
    target_app_id = Prompt.ask(
        "Please enter the ID of the Cloud app you want to sync to, or leave blank to sync with a new app",
        case_sensitive=False,
    )
    if target_app_id == "":
        target_app_id = safe_id("cloud-app")

    info(f"Your local application will be synced with Cloud app ID [magenta]{target_app_id}[/magenta].")

    # If the target Cloud app does not exist, a command is recorded.
    commands = []
    cloud_app, created = build_cloud_app(app_id=target_app_id)
    if created:
        str_cmd = f"nextmv cloud app create --app-id {cloud_app.id}"
        info(f"Cloud app was created with the following command: [code]{str_cmd}[/code]")
        cmd = ExecutedCommand(
            cmd=str_cmd,
            explanation="Create a new Cloud application",
        )
        commands.append(cmd)

    # Actually execute the command to sync the local application with the
    # target Cloud app.
    command = ["nextmv", "local", "app", "sync", "--target-app-id", cloud_app.id]
    str_cmd = " ".join(command)
    in_progress(f"Syncing local application with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors.
    if result.returncode != 0:
        error(
            f"Failed to sync application. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    # If we got here, the sync was successful. Inform the user.
    runs_url = f"https://cloud.nextmv.io/app/{cloud_app.id}/runs"
    success(
        "You can see the synced runs in the Nextmv Cloud Console at "
        f"[link={runs_url}][magenta]{runs_url}[/magenta][/link]."
    )
    cmd = ExecutedCommand(cmd=str_cmd, explanation="Sync the local application with Nextmv Cloud")
    commands.append(cmd)

    return cloud_app, commands


def _handle_app_push(cloud_app: cloud.Application) -> tuple[str, ExecutedCommand]:
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
    tuple[str, ExecutedCommand]
        The instance ID returned by the push command and the command that was
        executed to perform the push.

    Raises
    ------
    typer.Exit
        Exits the program if the user declines to push the app.
    """

    # If we got here, the user has an active Nextmv Plan. Ask if they want to
    # push their app to Nextmv Cloud or exit immediately.
    should_push = confirmation(
        "Do you want to push (deploy) your app to Nextmv Cloud now?",
        default=True,
    )
    if not should_push:
        info("You can push your app to Nextmv Cloud at any time with [code]nextmv cloud app push[/code]")
        raise typer.Exit()

    # Actually execute the command to push the app to Nextmv Cloud.
    str_cmd = f"nextmv cloud app push --app-id {cloud_app.id}"
    in_progress(f"Pushing application with command: [code]{str_cmd}[/code]")
    instance_id = handle_push(
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

    return instance_id, ExecutedCommand(cmd=str_cmd, explanation="Push the application to Nextmv Cloud")


def _handle_cloud_run_create(
    cloud_app: cloud.Application,
    local_app: local.Application,
    is_template: bool,
    instance_id: str,
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
    instance_id : str
        The instance ID returned by the push command, which can be used as
        input for the run.

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

    # Ask the user if they want to start a run for their Cloud app or exit
    # immediately.
    create_run = confirmation(
        msg=f"Do you want to start a [italic]remote[/italic] run for Cloud app [magenta]{cloud_app.id}[/magenta] now?",
        default=True,
    )
    if not create_run:
        info(
            "You can start a [italic]remote[/italic] run for the Cloud app at any time with "
            "[code]nextmv cloud run create[/code]"
        )
        raise typer.Exit()

    # Select the input path to run the Cloud app, defaulting to the same path
    # as the local run if it was a template.
    default = "."
    if is_template and local_app.content_format == ContentFormat.JSON:
        default = "input.json"
    elif is_template and local_app.content_format == ContentFormat.MULTI_FILE:
        default = "inputs"

    dirpath = directory_path(
        msg="Please select a directory or file to use as input for the [italic]remote[/italic] run",
        default=default,
        only_directories=False,
    )

    # Actually execute the command to start the Cloud run.
    command = ["nextmv", "cloud", "run", "create", "--app-id", cloud_app.id, "--input", dirpath]
    if instance_id:
        command.extend(["--instance-id", instance_id])

    str_cmd = " ".join(command)
    in_progress(f"Starting [italic]remote[/italic] run with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors and parsing the run ID from the output.
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

    # If we got here, the run started successfully and we have a run ID. Inform
    # the user.
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

    # Ask the user if they want to get the results of the Cloud run or exit
    # immediately.
    get_result = confirmation(
        msg=f"Do you want to get the results of the [italic]remote[/italic] run with ID [magenta]{run_id}[/magenta]?",
        default=True,
    )
    if not get_result:
        info(
            "You can get the results of this [italic]remote[/italic] run at any time with "
            "[code]nextmv cloud run get[/code]"
        )
        raise typer.Exit()

    # Actually execute the command to get the Cloud run results.
    command = ["nextmv", "cloud", "run", "get", "--app-id", cloud_app.id, "--run-id", run_id, "--wait"]
    str_cmd = " ".join(command)
    in_progress(f"Getting [italic]remote[/italic] run results with command: [code]{str_cmd}[/code]")
    result = _cli_call(command)

    # Handle the result, checking for errors.
    if result.returncode != 0:
        error(
            f"Failed to get [italic]remote[/italic] run results. Command exited with code {result.returncode}.\n"
            f"Standard output: {result.stdout}\n"
            f"Standard error: {result.stderr}"
        )

    # Show the user the URL for the completed run.
    raw_output = result.stdout.strip()
    output = json.loads(raw_output)
    console_url = output.get("console_url")
    if console_url is not None:
        success(
            f"You can see the details of the [magenta]{run_id}[/magenta] run in the Nextmv Cloud Console at "
            f"[link={console_url}][magenta]{console_url}[/magenta][/link]."
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
        # Use binary mode so we can apply different decoding strategies to each
        # stream: stdout is machine-readable (JSON) and must be decoded strictly
        # so corruption surfaces as a clear UnicodeDecodeError rather than a
        # confusing JSONDecodeError; stderr is human-facing and uses
        # errors="replace" so stray non-UTF-8 bytes (common on Windows with
        # codepage cp1252) never crash the thread.
        process = subprocess.Popen(
            command,
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout_lines = []
        stderr_lines = []
        stdout_exc: list[BaseException] = []

        def stream_stderr():
            for raw_line in process.stderr:
                line = raw_line.decode("utf-8", errors="replace")
                rich.print(line, end="", file=sys.stderr)
                stderr_lines.append(line)

        def stream_stdout():
            try:
                for raw_line in process.stdout:
                    line = raw_line.decode("utf-8")
                    rich.print(line, end="")
                    stdout_lines.append(line)
            except Exception as exc:
                # Capture so we can re-raise on the main thread after joining.
                stdout_exc.append(exc)

        # Use threads to read both streams concurrently without deadlocking
        stderr_thread = threading.Thread(target=stream_stderr)
        stdout_thread = threading.Thread(target=stream_stdout)

        stderr_thread.start()
        stdout_thread.start()

        stderr_thread.join()
        stdout_thread.join()
        process.wait()

        # Re-raise any decoding error from stdout on the calling thread so it
        # surfaces as a clear UnicodeDecodeError rather than being swallowed.
        if stdout_exc:
            raise stdout_exc[0]

        result = subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout="".join(stdout_lines),
            stderr="".join(stderr_lines),
        )
    except Exception as e:
        error(f"An error occurred while running command '{' '.join(command)}': {e}")

    return result
