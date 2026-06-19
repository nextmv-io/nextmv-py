"""
The Nextmv Command Line Interface (CLI).

This module is the main entry point for the Nextmv CLI application. The Nextmv
CLI is built with [Typer](https://typer.tiangolo.com/) and provides various
commands to interact with Nextmv services. You should visit the "Learn" section
of the Typer documentation to learn about the features that are used here.

The Nextmv CLI also uses [Rich](https://rich.readthedocs.io/en/stable/) for
rich text and formatting in the terminal. The command documentation is created
using Rich markup. You should also visit the Rich documentation to learn more
about the features used here. An example of Rich markup can be found in the
epilog of the Typer application defined below.
"""

import io
import os
import runpy
import sys
import warnings
from typing import Annotated

import requests
import typer
from typer import rich_utils

from nextmv._uv_handler import _find_uv_binary
from nextmv.cli.auth import app as auth_app
from nextmv.cli.cache import app as cache_app
from nextmv.cli.cloud import app as cloud_app
from nextmv.cli.community import app as community_app
from nextmv.cli.configuration import app as configuration_app
from nextmv.cli.configuration.config import GO_CLI_PATH
from nextmv.cli.init import app as init_app
from nextmv.cli.local import app as local_app
from nextmv.cli.manifest import app as manifest_app
from nextmv.cli.message import confirmation, error, info, success, warning
from nextmv.cli.version import app as version_app
from nextmv.cli.version import version_callback
from nextmv.cloud.client import retrieve_endpoint_from_config, retrieve_key_from_config
from nextmv.config import CONFIG_DIR, load_config
from nextmv.deprecated import NextmvDeprecationWarning

# Disable dim text for the extended help of commands.
rich_utils.STYLE_HELPTEXT = ""

# Main CLI application.
app = typer.Typer(
    help="The Nextmv Command Line Interface (CLI).",
    epilog="[dim]\n---\n\n[italic]:rabbit: Made by Nextmv with :heart:[/italic][/dim]",
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["--help", "-h"]},
    no_args_is_help=True,
    invoke_without_command=True,
    pretty_exceptions_show_locals=False,
)

# Register subcommands. The `name` parameter is required when the subcommand
# module has a callback function defined.
# We want to keep the subcommands in alphabetical order.
app.add_typer(auth_app, name="auth")
app.add_typer(cache_app, name="cache")
app.add_typer(cloud_app, name="cloud")
app.add_typer(community_app, name="community")
app.add_typer(configuration_app, name="configuration")
app.add_typer(init_app)
app.add_typer(local_app, name="local")
app.add_typer(manifest_app, name="manifest")
app.add_typer(version_app)

# Register the MCP subcommand only if the mcp extra is installed.
try:
    from nextmv.cli.mcp import app as mcp_app

    app.add_typer(mcp_app, name="mcp")
except ImportError:
    pass


@app.callback()
def callback(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            help="Show the current version of the Nextmv CLI.",
            callback=version_callback,
        ),
    ] = None,
) -> None:
    """
    Callback function that runs before any command. Useful for checks on the
    environment.
    """

    # Skip checks for help commands.
    if "--help" in sys.argv or "-h" in sys.argv:
        return

    # Skip checks for certain commands entirely.
    ignored_commands = {"configuration", "auth", "mcp", "manifest", "version"}
    if ctx.invoked_subcommand in ignored_commands:
        return

    # 'init' and 'local' don't require the go CLI or config checks.
    if ctx.invoked_subcommand not in {"init", "local"}:
        _handle_go_cli()
        _handle_config_existence(ctx)

    _handle_env_vars_and_profile(ctx)


def _handle_go_cli() -> None:
    """
    Handle the presence of the deprecated Go CLI by notifying the user.

    This function checks if the Go CLI is installed and prompts the user to
    remove it to avoid conflicts with the Python CLI.
    """

    exists = _go_cli_exists()
    if exists:
        delete = confirmation(
            "Do you want to delete the [italic red]deprecated[/italic red] Nextmv CLI "
            f"at [magenta]{GO_CLI_PATH}[/magenta] now?"
        )
        if delete:
            _remove_go_cli()
            return

        info(
            "You can delete the [italic red]deprecated[/italic red] Nextmv CLI later by removing "
            f"[magenta]{GO_CLI_PATH}[/magenta]. "
            "Make sure you also clean up your [code]PATH[/code], "
            f"by removing references to [magenta]{CONFIG_DIR}[/magenta] from it."
        )


def _handle_config_existence(ctx: typer.Context) -> None:
    """
    Check if configuration exists and show an error if it does not.

    Parameters
    ----------
    ctx : typer.Context
        The Typer context object.
    """

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configuration create[/code].")


def _handle_env_vars_and_profile(ctx: typer.Context) -> None:  # noqa: C901 # At the edge, breaking it reduces readability.
    """
    Warn when environment variables conflict with profile settings.

    Checks NEXTMV_API_KEY, NEXTMV_ENDPOINT, and NEXTMV_PROFILE against the
    active profile (from --profile/-p or NEXTMV_PROFILE) and emits warnings
    when values differ or both a profile env var and flag are set simultaneously.

    Parameters
    ----------
    ctx : typer.Context
        The Typer context object.
    """

    # Only applies to: 'cloud ...', 'community ...', 'init', and 'local app sync'.
    if ctx.invoked_subcommand == "local" and "sync" not in sys.argv:
        return

    api_key = os.getenv("NEXTMV_API_KEY")
    api_key_set = api_key is not None

    endpoint_var = os.getenv("NEXTMV_ENDPOINT")
    endpoint_set = endpoint_var is not None

    profile_var = os.getenv("NEXTMV_PROFILE")
    profile_var_set = profile_var is not None

    profile_opts = {"--profile", "-p"}
    profile_opt_set = not profile_opts.isdisjoint(sys.argv)

    # First, check if we don't have to warn or inform of anything.
    override_not_used = not api_key_set and not endpoint_set
    if override_not_used and not profile_var_set and not profile_opt_set:
        return

    # Get the value of the profile option, if set.
    profile_from_opt = None
    if profile_opt_set:
        profile_from_opt = next(
            (sys.argv[i + 1] for i, arg in enumerate(sys.argv[:-1]) if arg in profile_opts),
            None,
        )

    # Determine the profile to use based on the environment variable and option.
    profile = None
    profile_name = "default"
    if profile_var_set:
        profile = profile_var
        profile_name = profile_var
    elif profile_opt_set:
        profile = profile_from_opt
        profile_name = profile_from_opt

    # Warn if conflicting profile specifications are found.
    if profile_var_set and profile_opt_set and profile_var != profile_from_opt:
        warning(
            "Both the [magenta]NEXTMV_PROFILE[/magenta] environment variable and the [magenta]--profile/-p[/magenta] "
            "option are set with [italic]different[/italic] values. This may cause an unexpected behavior. "
            "The env var takes precedence."
        )

    # Warn if API key specs are conflicting.
    if api_key_set:
        conf_key = retrieve_key_from_config(profile=profile)
        if conf_key != api_key:
            warning(
                "The [magenta]NEXTMV_API_KEY[/magenta] environment variable is set, "
                "and its value [italic]differs[/italic] "
                f"from the API key of the [magenta]{profile_name}[/magenta] profile. "
                "This may cause an unexpected behavior. The env var takes precedence."
            )

    # Warn if endpoint specs are conflicting.
    if endpoint_set:
        if not endpoint_var.startswith("https://") and not endpoint_var.startswith("http://"):
            endpoint = f"https://{endpoint_var}"

        conf_endpoint = retrieve_endpoint_from_config(profile=profile)
        if conf_endpoint != endpoint:
            warning(
                "The [magenta]NEXTMV_ENDPOINT[/magenta] environment variable is set, "
                "and its value [italic]differs[/italic] "
                f"from the endpoint of the [magenta]{profile_name}[/magenta] profile. "
                "This may cause an unexpected behavior. The env var takes precedence."
            )


def _go_cli_exists() -> bool:
    """
    Check if the Go CLI is installed by looking for the 'nextmv' executable
    under the config dir.

    Returns
    -------
    bool
        True if the Go CLI is installed, False otherwise.
    """

    # Check if the Go CLI executable exists
    exists = GO_CLI_PATH.exists()
    if exists:
        warning(
            "A [italic red]deprecated[/italic red] Nextmv CLI is installed at "
            f"[magenta]{GO_CLI_PATH}[/magenta]. You should delete it to avoid conflicts."
        )

    return exists


def _remove_go_cli() -> None:
    """
    Remove the Go CLI executable if it exists and notify about PATH cleanup.
    """

    if GO_CLI_PATH.exists():
        GO_CLI_PATH.unlink()
        success(f"Deleted [italic red]deprecated[/italic red] [magenta]{GO_CLI_PATH}[/magenta].")


def _setup_encoding() -> None:
    """
    Configure UTF-8 encoding for Windows platforms to make sure emojis and rich text do
    not cause encoding errors.
    """
    # Only force UTF-8 encoding on Windows where the default encoding is not already UTF-8
    # and where sys.stdout has a buffer attribute (indicating it's a real stream and not a
    # mock).
    if (
        sys.platform == "win32"
        and getattr(sys.stdout, "encoding", "").lower() != "utf-8"
        and hasattr(sys.stdout, "buffer")
    ):
        try:
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer,
                encoding="utf-8",
                errors="replace",  # Don't crash on bad chars
                line_buffering=True,
            )
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer,
                encoding="utf-8",
                errors="replace",
                line_buffering=True,
            )
        except Exception:
            # If wrapping fails (e.g. in some CI environments),
            # fall back to the original stream rather than crashing.
            pass


def _handle_http_exception(e: requests.HTTPError) -> None:
    """
    Handle HTTP exceptions by showing user-friendly error messages based on the
    status code.

    Parameters
    ----------
    e : requests.HTTPError
        The HTTP error to handle.
    """
    if e.response.status_code == 401:
        # This means that you are authenticated and your role gives you
        # permission to access, but you fail an additional check like a
        # paid account check.
        error(
            msg="You are not authorized to perform this action. "
            "Please contact [link=https://www.nextmv.io/contact][bold]Nextmv support[/bold][/link].",
            should_exit=False,
        )
    elif e.response.status_code == 403:
        # Can mean one of two things: either you are not authenticated, or
        # your role does not permit you to perform the action.
        error(msg="You are not authorized or do not have permission to perform this action.", should_exit=False)
    elif e.response.status_code == 400:
        # This means that the request was malformed. The error message from
        # the server should give more details on what was wrong with the
        # request.
        error(msg=f"You made a bad request: {e.response.text}", should_exit=False)
    elif e.response.status_code == 404:
        error(msg="The requested resource was not found. It may have been deleted.", should_exit=False)
    elif e.response.status_code == 429:
        error(msg="You have hit a rate limit. Please wait a moment before trying again.", should_exit=False)
    elif e.response.status_code >= 500:
        error(msg="There was an unexpected error in Nextmv Cloud. Please try again later.", should_exit=False)
    else:
        error(msg=str(e).rstrip("\n"), should_exit=False)

    # Exit here to avoid printing more of the traceback.
    sys.exit(1)


def main() -> None:
    """
    Entry point for the CLI with global exception handling.

    Catches all exceptions except Typer/Click exceptions (which handle their
    own exit codes) and displays a clean error message instead of a traceback.
    """

    # Improve compatibility with Windows terminals.
    _setup_encoding()

    # Suppress SDK-level DeprecationWarnings so only CLI warnings are shown.
    warnings.filterwarnings("ignore", category=NextmvDeprecationWarning)

    # Handle --run-script and --run-uv for running scripts with the bundled Python
    # interpreter or via uv. These are used internally in case of frozen PyInstaller
    # distributions.
    if len(sys.argv) > 1 and sys.argv[1] == "--run-script":
        if len(sys.argv) < 3:
            error("--run-script requires a script path.", should_exit=False)
            sys.exit(1)

        script_path = sys.argv[2]
        sys.argv = sys.argv[2:]  # script becomes argv[0]; its own args follow
        runpy.run_path(script_path, run_name="__main__")
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == "--run-uv":
        if len(sys.argv) < 3:
            error("--run-uv requires arguments for 'uv run'.", should_exit=False)
            sys.exit(1)

        uv_bin = _find_uv_binary()
        uv_args = [uv_bin, "run"] + sys.argv[2:]
        os.execv(uv_bin, uv_args)

    # This is where we actually launch the CLI (the Typer app defined above).
    # If debug mode is active, we want to print the raw Python traceback for
    # easier debugging. Otherwise, we catch exceptions and process them to
    # print out nice error messages.
    should_debug = "--debug" in sys.argv
    if should_debug:
        app()
        return

    try:
        app()
    # Capture "special" HTTP errors to enrich them.
    except requests.HTTPError as e:
        _handle_http_exception(e)
    except (typer.Exit, typer.Abort, SystemExit):
        raise
    except Exception as e:
        # We do not exit to avoid a Typer exception, which would print a traceback.
        error(msg=str(e).rstrip("\n"), should_exit=False)
        sys.exit(1)


if __name__ == "__main__":
    main()
