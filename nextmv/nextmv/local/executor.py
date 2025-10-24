"""
Executor module for executing local runs.

This module provides functionality to execute local runs. The `main` function
is summoned from the `run` function in the `runner` module.

Functions
---------
main
    Main function to execute a local run.
execute_run
    Function to execute the decision model run.
options_args
    Function to convert options dictionary to command-line arguments.
process_run_input
    Function to process the run input based on the format.
process_run_output
    Function to process the run output and handle results.
resolve_output_format
    Function to determine the output format from manifest or directory structure.
process_run_information
    Function to update run metadata including duration and status.
process_run_logs
    Function to process and save run logs.
process_run_statistics
    Function to process and save run statistics.
process_run_assets
    Function to process and save run assets.
process_run_solutions
    Function to process and save run solutions.
process_run_visuals
    Function to process and save run visuals.
resolve_stdout
    Function to parse subprocess stdout output.
ignore_patterns
    Function to filter files and directories during source code copying.
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Optional, Union

from nextmv.input import INPUTS_KEY, InputFormat, load
from nextmv.local.geojson_handler import handle_geojson_visual
from nextmv.local.local import (
    DEFAULT_OUTPUT_JSON_FILE,
    LOGS_FILE,
    LOGS_KEY,
    NEXTMV_DIR,
    OUTPUT_KEY,
    calculate_files_size,
)
from nextmv.local.plotly_handler import handle_plotly_visual
from nextmv.manifest import Manifest
from nextmv.output import ASSETS_KEY, OUTPUTS_KEY, SOLUTIONS_KEY, STATISTICS_KEY, Asset, OutputFormat, VisualSchema
from nextmv.status import StatusV2


def main() -> None:
    """
    Main function to execute a local run. This function is called when
    executing the script directly. It loads input data (arguments) from stdin
    and orders the execution of the run.
    """

    input = load()
    execute_run(
        run_id=input.data["run_id"],
        src=input.data["src"],
        manifest_dict=input.data["manifest_dict"],
        run_dir=input.data["run_dir"],
        run_config=input.data["run_config"],
        inputs_dir_path=input.data["inputs_dir_path"],
        options=input.data["options"],
        input_data=input.data["input_data"],
    )


def execute_run(
    run_id: str,
    src: str,
    manifest_dict: dict[str, Any],
    run_dir: str,
    run_config: dict[str, Any],
    inputs_dir_path: Optional[str] = None,
    options: Optional[dict[str, Any]] = None,
    input_data: Optional[Union[dict[str, Any], str]] = None,
) -> None:
    """
    Executes the decision model run using a subprocess to call the entrypoint
    script with the appropriate input and options.

    Parameters
    ----------
    run_id : str
        The unique identifier for the run.
    src : str
        The path to the application source code.
    manifest_dict : dict[str, Any]
        The manifest dictionary containing application configuration.
    run_dir : str
        The path to the run directory where outputs will be stored.
    run_config : dict[str, Any]
        The run configuration containing format and other settings.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.
    options : Optional[dict[str, Any]], optional
        Additional command-line options for the run, by default None.
    input_data : Optional[Union[dict[str, Any], str]], optional
        The input data for the run, by default None. If `inputs_dir_path` is
        provided, this parameter is ignored.
    """

    # Create the logs dir to register whatever failure might happen during the
    # execution process.
    logs_dir = os.path.join(run_dir, LOGS_KEY)
    os.makedirs(logs_dir, exist_ok=True)

    # The complete execution is wrapped to capture any errors.
    try:
        # Create a temp dir, and copy the entire src there, to have a transient
        # place to work from, and be cleaned up afterwards.
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_src = os.path.join(temp_dir, "src")
            shutil.copytree(src, temp_src, ignore=ignore_patterns)

            manifest = Manifest.from_dict(manifest_dict)

            stdin_input = process_run_input(
                temp_src=temp_src,
                run_format=run_config["format"]["input"]["type"],
                manifest=manifest,
                input_data=input_data,
                inputs_dir_path=inputs_dir_path,
            )

            # Set the run status to running.
            info_file = os.path.join(run_dir, f"{run_id}.json")
            with open(info_file, "r+") as f:
                info = json.load(f)
                info["metadata"]["status_v2"] = "running"
                f.seek(0)
                json.dump(info, f, indent=2)
                f.truncate()

            # Start a Python subprocess to execute the entrypoint. For now, we are
            # supporting a Python-first experience, so we are not summoning
            # applications that are not Python-based.
            entrypoint = os.path.join(temp_src, manifest.entrypoint)
            args = [sys.executable, entrypoint] + options_args(options)

            result = subprocess.run(
                args,
                env=os.environ,
                check=False,
                text=True,
                capture_output=True,
                input=stdin_input,
                cwd=temp_src,
            )

            process_run_output(
                manifest=manifest,
                run_id=run_id,
                temp_src=temp_src,
                result=result,
                run_dir=run_dir,
                src=src,
            )

    except Exception as e:
        # If we encounter an exception, we log it to the stderr log file.
        with open(os.path.join(logs_dir, LOGS_FILE), "a") as f:
            f.write(f"\nException during run execution: {str(e)}\n")

        # Also, we update the run information file to set the status to failed.
        info_file = os.path.join(run_dir, f"{run_id}.json")
        with open(info_file, "r+") as f:
            info = json.load(f)
            info["metadata"]["status_v2"] = "failed"
            info["metadata"]["error"] = str(e)
            f.seek(0)
            json.dump(info, f, indent=2)
            f.truncate()


def options_args(options: Optional[dict[str, Any]] = None) -> list[str]:
    """
    Converts options dictionary to a list of command-line arguments.

    Parameters
    ----------
    options : Optional[dict[str, Any]], optional
        Additional options for the run, by default None.

    Returns
    -------
    list[str]
        A list of command-line arguments derived from the options.
    """
    option_args = []

    if options is not None:
        for key, value in options.items():
            option_args.append(f"-{key}")
            option_args.append(str(value))

    return option_args


def process_run_input(
    temp_src: str,
    run_format: str,
    manifest: Manifest,
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
) -> str:
    """
    In the temp source, writes the run input according to the run format. If
    the format is `json` or `text`, then the input is not written anywhere,
    rather, it is returned as a string in this function. If the format is
    `csv-archive`, then the input files are written to an `input` directory. If
    the format is `multi-file`, then the input files are written to an `inputs`
    directory or to a custom location specified in the manifest.

    Parameters
    ----------
    temp_src : str
        The path to the temporary source directory.
    run_format : str
        The run format, one of `json`, `text`, `csv-archive`, or `multi-file`.
    manifest : Manifest
        The application manifest.
    input_data : Optional[Union[dict[str, Any], str]], optional
        The input data for the run, by default None. If `inputs_dir_path` is
        provided, this parameter is ignored.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.

    Returns
    -------
    str
        The input data as a string, if the format is `json` or `text`. Otherwise,
        returns an empty string.
    """

    # For JSON and TEXT formats, we return the input data as a string.
    if run_format in (InputFormat.JSON.value, InputFormat.TEXT.value):
        if isinstance(input_data, dict) and run_format == InputFormat.JSON.value:
            return json.dumps(input_data)

        if isinstance(input_data, str) and run_format == InputFormat.TEXT.value:
            return input_data

        raise ValueError(f"invalid input data for format {run_format}")

    if input_data is not None:
        raise ValueError("input data must be None for csv-archive or multi-file format")

    # For CSV-ARCHIVE format, we write the input files to an `input` directory.
    if run_format == InputFormat.CSV_ARCHIVE.value:
        input_dir = os.path.join(temp_src, "input")
        os.makedirs(input_dir, exist_ok=True)

        if inputs_dir_path is not None and inputs_dir_path != "":
            shutil.copytree(inputs_dir_path, input_dir, dirs_exist_ok=True)

        return ""

    # For MULTI-FILE format, we write the input files to an `inputs` directory,
    # or to a custom location specified in the manifest.
    if run_format == InputFormat.MULTI_FILE.value:
        inputs_dir = os.path.join(temp_src, INPUTS_KEY)
        if (
            manifest.configuration is not None
            and manifest.configuration.content is not None
            and manifest.configuration.content.format == InputFormat.MULTI_FILE
            and manifest.configuration.content.multi_file is not None
        ):
            inputs_dir = os.path.join(temp_src, manifest.configuration.content.multi_file.input.path)

        os.makedirs(inputs_dir, exist_ok=True)

        if inputs_dir_path is not None and inputs_dir_path != "":
            shutil.copytree(inputs_dir_path, inputs_dir, dirs_exist_ok=True)

        return ""


def process_run_output(
    manifest: Manifest,
    run_id: str,
    temp_src: str,
    result: subprocess.CompletedProcess[str],
    run_dir: str,
    src: str,
) -> None:
    """
    Processes the result of the subprocess run. This function is in charge of
    handling the run results, including solutions, statistics, logs, assets,
    and visuals.

    Parameters
    ----------
    manifest : Manifest
        The application manifest containing configuration details.
    run_id : str
        The unique identifier for the run.
    temp_src : str
        The path to the temporary source directory.
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run containing stdout, stderr, and return code.
    run_dir : str
        The path to the run directory where outputs will be stored.
    src : str
        The path to the application source code.
    """

    stdout_output = resolve_stdout(result)

    # Create outputs directory.
    outputs_dir = os.path.join(run_dir, OUTPUTS_KEY)
    os.makedirs(outputs_dir, exist_ok=True)
    temp_run_outputs_dir = os.path.join(temp_src, OUTPUTS_KEY)

    output_format = resolve_output_format(
        manifest=manifest,
        temp_run_outputs_dir=temp_run_outputs_dir,
        temp_src=temp_src,
    )
    process_run_information(
        run_id=run_id,
        run_dir=run_dir,
        result=result,
    )
    process_run_logs(
        output_format=output_format,
        run_dir=run_dir,
        result=result,
        stdout_output=stdout_output,
    )
    process_run_statistics(
        temp_run_outputs_dir=temp_run_outputs_dir,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
        temp_src=temp_src,
        manifest=manifest,
        src=src,
    )
    process_run_assets(
        temp_run_outputs_dir=temp_run_outputs_dir,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
        temp_src=temp_src,
        manifest=manifest,
        src=src,
    )
    process_run_solutions(
        run_id=run_id,
        run_dir=run_dir,
        temp_run_outputs_dir=temp_run_outputs_dir,
        temp_src=temp_src,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
        output_format=output_format,
        manifest=manifest,
        src=src,
    )
    process_run_visuals(
        run_dir=run_dir,
        outputs_dir=outputs_dir,
    )


def resolve_output_format(
    manifest: Manifest,
    temp_run_outputs_dir: str,
    temp_src: str,
) -> OutputFormat:
    """
    Resolves the output format of the run. This function checks the manifest
    configuration for the output format. If not specified, it checks for the
    presence of an `output` directory (for `csv-archive`), or an
    `outputs/solutions` directory (for `multi-file`). If neither exist, it
    defaults to `json`.

    Parameters
    ----------
    manifest : Manifest
        The application manifest containing configuration details.
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    temp_src : str
        The path to the temporary source directory.

    Returns
    -------
    OutputFormat
        The determined output format (JSON, CSV_ARCHIVE, or MULTI_FILE).
    """

    if manifest.configuration is not None and manifest.configuration.content is not None:
        return manifest.configuration.content.format

    output_dir = os.path.join(temp_src, OUTPUT_KEY)
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        return OutputFormat.CSV_ARCHIVE

    solutions_dir = os.path.join(temp_run_outputs_dir, SOLUTIONS_KEY)
    if os.path.exists(solutions_dir) and os.path.isdir(solutions_dir):
        return OutputFormat.MULTI_FILE

    return OutputFormat.JSON


def process_run_information(run_id: str, run_dir: str, result: subprocess.CompletedProcess[str]) -> None:
    """
    Processes the run information, updating properties such as duration and
    status.

    Parameters
    ----------
    run_id : str
        The ID of the run.
    run_dir : str
        The path to the run directory.
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run.
    """

    info_file = os.path.join(run_dir, f"{run_id}.json")

    with open(info_file) as f:
        info = json.load(f)

    # Calculate duration.
    created_at_str = info["metadata"]["created_at"]
    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    duration = round((now - created_at).total_seconds() * 1000, 1)

    # Update the status
    status = StatusV2.succeeded.value
    error = ""
    if result.returncode != 0:
        status = StatusV2.failed.value
        # Truncate error message so that Cloud does not complain.
        error = (result.stderr.strip().replace("\n", " ") if result.stderr else "unknown error")[:60]

    # Update the run info file.
    info["metadata"]["duration"] = duration
    info["metadata"]["status_v2"] = status
    info["metadata"]["error"] = error

    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)


def process_run_logs(
    output_format: OutputFormat,
    run_dir: str,
    result: subprocess.CompletedProcess[str],
    stdout_output: Union[str, dict[str, Any]],
) -> None:
    """
    Processes the logs of the run. Writes the logs to a logs directory.
    For multi-file format, stdout is written to logs if present.

    Parameters
    ----------
    output_format : OutputFormat
        The output format of the run (JSON, CSV_ARCHIVE, or MULTI_FILE).
    run_dir : str
        The path to the run directory where logs will be stored.
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run containing stderr output.
    stdout_output : Union[str, dict[str, Any]]
        The stdout output of the run, either as raw string or parsed dictionary.
    """

    logs_dir = os.path.join(run_dir, LOGS_KEY)
    os.makedirs(logs_dir, exist_ok=True)
    std_err = result.stderr
    with open(os.path.join(logs_dir, LOGS_FILE), "w") as f:
        if output_format == OutputFormat.MULTI_FILE and bool(stdout_output):
            if isinstance(stdout_output, dict):
                f.write(json.dumps(stdout_output))
            elif isinstance(stdout_output, str):
                f.write(stdout_output)

            if std_err:
                f.write("\n")

        f.write(std_err)


def process_run_statistics(
    temp_run_outputs_dir: str,
    outputs_dir: str,
    stdout_output: Union[str, dict[str, Any]],
    temp_src: str,
    manifest: Manifest,
    src: str,
) -> None:
    """
    Processes the statistics of the run. Checks for an outputs/statistics folder
    or custom statistics file location from manifest. If found, copies to run
    directory. Otherwise, attempts to extract statistics from stdout.

    Parameters
    ----------
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : Union[str, dict[str, Any]]
        The stdout output of the run, either as raw string or parsed dictionary.
    temp_src : str
        The path to the temporary source directory.
    manifest : Manifest
        The application manifest containing configuration and custom paths.
    src : str
        The path to the original application source code, used to avoid copying
        files that are already part of the source.
    """

    stats_dst = os.path.join(outputs_dir, STATISTICS_KEY)
    os.makedirs(stats_dst, exist_ok=True)
    statistics_file = f"{STATISTICS_KEY}.json"

    # Check for custom location in manifest and override stats_src if needed.
    if (
        manifest.configuration is not None
        and manifest.configuration.content is not None
        and manifest.configuration.content.format == OutputFormat.MULTI_FILE
        and manifest.configuration.content.multi_file is not None
    ):
        stats_src_file = os.path.join(temp_src, manifest.configuration.content.multi_file.output.statistics)

        # If the custom statistics file exists, copy it to the stats destination
        if os.path.exists(stats_src_file) and os.path.isfile(stats_src_file):
            stats_dst_file = os.path.join(stats_dst, statistics_file)
            shutil.copy2(stats_src_file, stats_dst_file)
            return

    stats_src = os.path.join(temp_run_outputs_dir, STATISTICS_KEY)
    if os.path.exists(stats_src) and os.path.isdir(stats_src):
        _copy_new_or_modified_files(stats_src, stats_dst, src)
        return

    if not isinstance(stdout_output, dict):
        return

    if STATISTICS_KEY not in stdout_output:
        return

    with open(os.path.join(stats_dst, statistics_file), "w") as f:
        statistics = {STATISTICS_KEY: stdout_output[STATISTICS_KEY]}
        json.dump(statistics, f, indent=2)


def process_run_assets(
    temp_run_outputs_dir: str,
    outputs_dir: str,
    stdout_output: Union[str, dict[str, Any]],
    temp_src: str,
    manifest: Manifest,
    src: str,
) -> None:
    """
    Processes the assets of the run. Checks for an outputs/assets folder or
    custom assets file location from manifest. If found, copies to run directory.
    Otherwise, attempts to extract assets from stdout.

    Parameters
    ----------
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : Union[str, dict[str, Any]]
        The stdout output of the run, either as raw string or parsed dictionary.
    temp_src : str
        The path to the temporary source directory.
    manifest : Manifest
        The application manifest containing configuration and custom paths.
    src : str
        The path to the original application source code, used to avoid copying
        files that are already part of the source.
    """

    assets_dst = os.path.join(outputs_dir, ASSETS_KEY)
    os.makedirs(assets_dst, exist_ok=True)
    assets_file = f"{ASSETS_KEY}.json"

    # Check for custom location in manifest and override assets_src if needed.
    if (
        manifest.configuration is not None
        and manifest.configuration.content is not None
        and manifest.configuration.content.format == OutputFormat.MULTI_FILE
        and manifest.configuration.content.multi_file is not None
    ):
        assets_src_file = os.path.join(temp_src, manifest.configuration.content.multi_file.output.assets)

        # If the custom assets file exists, copy it to the assets destination
        if os.path.exists(assets_src_file) and os.path.isfile(assets_src_file):
            assets_dst_file = os.path.join(assets_dst, assets_file)
            shutil.copy2(assets_src_file, assets_dst_file)
            return

    assets_src = os.path.join(temp_run_outputs_dir, ASSETS_KEY)
    if os.path.exists(assets_src) and os.path.isdir(assets_src):
        _copy_new_or_modified_files(assets_src, assets_dst, src)
        return

    if not isinstance(stdout_output, dict):
        return

    if ASSETS_KEY not in stdout_output:
        return

    with open(os.path.join(assets_dst, assets_file), "w") as f:
        assets = {ASSETS_KEY: stdout_output[ASSETS_KEY]}
        json.dump(assets, f, indent=2)


def process_run_solutions(
    run_id: str,
    run_dir: str,
    temp_run_outputs_dir: str,
    temp_src: str,
    outputs_dir: str,
    stdout_output: Union[str, dict[str, Any]],
    output_format: OutputFormat,
    manifest: Manifest,
    src: str,
) -> None:
    """
    Processes the solutions (output) of the run. Handles all different output
    formats including CSV-archive, multi-file, JSON, and text. Looks for
    `output` directory (csv-archive), `outputs/solutions` directory (multi-file),
    or custom solutions path from manifest. Falls back to stdout for JSON/text.
    Updates run metadata with output size and format information.

    Only copies files that are truly new outputs, excluding files that already
    exist in the original source code, inputs, statistics, or assets directories
    to prevent copying application data as solutions.

    Parameters
    ----------
    run_id : str
        The unique identifier of the run.
    run_dir : str
        The path to the run directory where outputs are stored.
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    temp_src : str
        The path to the temporary source directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : Union[str, dict[str, Any]]
        The stdout output of the run, either as raw string or parsed dictionary.
    output_format : OutputFormat
        The determined output format (JSON, CSV_ARCHIVE, MULTI_FILE, or TEXT).
    manifest : Manifest
        The application manifest containing configuration and custom paths.
    src : str
        The path to the application source code.
    """

    info_file = os.path.join(run_dir, f"{run_id}.json")

    with open(info_file) as f:
        info = json.load(f)

    solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
    os.makedirs(solutions_dst, exist_ok=True)

    # Build list of directories to exclude from copying
    exclusion_dirs = _build_exclusion_directories(src, manifest, outputs_dir, run_dir)

    if output_format == OutputFormat.CSV_ARCHIVE:
        output_src = os.path.join(temp_src, OUTPUT_KEY)
        _copy_new_or_modified_files(output_src, solutions_dst, src, exclusion_dirs)
    elif output_format == OutputFormat.MULTI_FILE:
        solutions_src = os.path.join(temp_run_outputs_dir, SOLUTIONS_KEY)
        if (
            manifest.configuration is not None
            and manifest.configuration.content is not None
            and manifest.configuration.content.format == OutputFormat.MULTI_FILE
            and manifest.configuration.content.multi_file is not None
        ):
            solutions_src = os.path.join(temp_src, manifest.configuration.content.multi_file.output.solutions)

        _copy_new_or_modified_files(solutions_src, solutions_dst, src, exclusion_dirs)
    else:
        if bool(stdout_output):
            with open(os.path.join(solutions_dst, DEFAULT_OUTPUT_JSON_FILE), "w") as f:
                if isinstance(stdout_output, dict):
                    json.dump(stdout_output, f, indent=2)
                elif isinstance(stdout_output, str):
                    f.write(stdout_output)

    # Update the run information file with the output size and type.
    calculate_files_size(run_dir, run_id, solutions_dst, metadata_key="output_size")
    info["metadata"]["format"]["output"] = {"type": output_format.value}
    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)


def process_run_visuals(run_dir: str, outputs_dir: str) -> None:
    """
    Processes the visuals from the assets in the run output. This function looks
    for visual assets (Plotly and GeoJSON) in the assets.json file and generates
    HTML files for each visual. ChartJS visuals are ignored for local runs.

    Parameters
    ----------
    run_dir : str
        The path to the run directory where visuals will be stored.
    outputs_dir : str
        The path to the outputs directory in the run directory containing assets.
    """

    # Get the assets.
    assets_dir = os.path.join(outputs_dir, ASSETS_KEY)
    if not os.path.exists(assets_dir):
        return

    assets_file = os.path.join(assets_dir, f"{ASSETS_KEY}.json")
    if not os.path.exists(assets_file):
        return

    with open(assets_file) as f:
        assets = json.load(f)

    # Create visuals directory.
    visuals_dir = os.path.join(run_dir, "visuals")
    os.makedirs(visuals_dir, exist_ok=True)

    # Loop over all the assets to find visual assets.
    for asset_dict in assets.get(ASSETS_KEY, []):
        asset = Asset.from_dict(asset_dict)
        if asset.visual is None:
            continue

        if asset.visual.visual_schema == VisualSchema.PLOTLY:
            handle_plotly_visual(asset, visuals_dir)
        elif asset.visual.visual_schema == VisualSchema.GEOJSON:
            handle_geojson_visual(asset, visuals_dir)

        # ChartJS is not easily supported directly from Python in local runs,
        # so we ignore it for now.


def resolve_stdout(result: subprocess.CompletedProcess[str]) -> Union[str, dict[str, Any]]:
    """
    Resolves the stdout output of the subprocess run. If the stdout is valid
    JSON, it returns the parsed dictionary. Otherwise, it returns the raw
    string output.

    Parameters
    ----------
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run.

    Returns
    -------
    Union[str, dict[str, Any]]
        The parsed stdout output as a dictionary if valid JSON, otherwise the
        raw string output.
    """
    raw_output = result.stdout
    if raw_output.strip() == "":
        return ""

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        return raw_output


def ignore_patterns(dir_path: str, names: list[str]) -> list[str]:
    """
    Custom ignore function for copytree that filters files and directories
    during source code copying. Excludes virtual environments, cache files,
    the nextmv directory, and non-essential files while preserving Python
    source files and application manifests.

    Parameters
    ----------
    dir_path : str
        The path to the directory being processed.
    names : list[str]
        A list of file and directory names in the current directory.

    Returns
    -------
    list[str]
        A list of names to ignore during the copy operation.
    """
    ignored = []
    for name in names:
        full_path = os.path.join(dir_path, name)

        # Ignore nextmv directory
        if name == NEXTMV_DIR:
            ignored.append(name)
            continue

        # Ignore virtual environment directories
        if name in ("venv", ".venv", "env", ".env", "virtualenv", ".virtualenv"):
            ignored.append(name)
            continue

        # Ignore __pycache__ directories
        if name == "__pycache__":
            ignored.append(name)
            continue

        # If it's a file, only keep Python files and app.yaml
        if os.path.isfile(full_path):
            if not (name.endswith(".py") or name == "app.yaml"):
                ignored.append(name)
                continue

        # Ignore .pyc files explicitly
        if name.endswith(".pyc"):
            ignored.append(name)
            continue

    return ignored


def _build_exclusion_directories(src: str, manifest: Manifest, outputs_dir: str, run_dir: str) -> list[str]:
    """
    Build a list of directories to exclude when copying solution files.

    Parameters
    ----------
    src : str
        The path to the original application source code.
    manifest : Manifest
        The application manifest containing configuration.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    run_dir : str
        The path to the run directory.

    Returns
    -------
    list[str]
        List of directory paths to exclude from copying.
    """
    exclusion_dirs = []

    # Add inputs directory from original source
    inputs_dir_original = os.path.join(src, INPUTS_KEY)
    if os.path.exists(inputs_dir_original):
        exclusion_dirs.append(inputs_dir_original)

    # Add custom inputs directory if specified in manifest
    if (
        manifest.configuration is not None
        and manifest.configuration.content is not None
        and manifest.configuration.content.format == InputFormat.MULTI_FILE
        and manifest.configuration.content.multi_file is not None
    ):
        custom_inputs_dir = os.path.join(src, manifest.configuration.content.multi_file.input.path)
        if os.path.exists(custom_inputs_dir):
            exclusion_dirs.append(custom_inputs_dir)

    # Add inputs directory from run directory
    inputs_dir_run = os.path.join(run_dir, INPUTS_KEY)
    if os.path.exists(inputs_dir_run):
        exclusion_dirs.append(inputs_dir_run)

    # Add statistics and assets directories from run outputs
    stats_dir = os.path.join(outputs_dir, STATISTICS_KEY)
    if os.path.exists(stats_dir):
        exclusion_dirs.append(stats_dir)

    assets_dir = os.path.join(outputs_dir, ASSETS_KEY)
    if os.path.exists(assets_dir):
        exclusion_dirs.append(assets_dir)

    return exclusion_dirs


def _copy_new_or_modified_files(
    src_dir: str, dst_dir: str, original_src_dir: Optional[str] = None, exclusion_dirs: Optional[list[str]] = None
) -> None:
    """
    Copy files from source to destination only if they meet specific criteria.

    This function ensures that only files that are either:
    1. New files (not present in destination)
    2. Existing files with different content (based on checksum comparison)
    3. Files that are NOT present in the original source directory (if provided)
    4. Files that are NOT present in any of the exclusion directories (if provided)

    Empty directories are not created or are removed after copying to avoid
    cluttering the output with empty folders.

    Parameters
    ----------
    src_dir : str
        The source directory path to copy from.
    dst_dir : str
        The destination directory path to copy to.
    original_src_dir : Optional[str], optional
        The original source directory to check against. Files present in this
        directory will NOT be copied, by default None.
    exclusion_dirs : Optional[list[str]], optional
        Additional directories to check against. Files present in any of these
        directories will NOT be copied, by default None.
    """
    # Build list of all exclusion directories
    exclusion_directories = []
    if original_src_dir is not None:
        exclusion_directories.append(original_src_dir)
    if exclusion_dirs is not None:
        exclusion_directories.extend(exclusion_dirs)

    files_copied = False
    for root, _dirs, files in os.walk(src_dir):
        rel_root = os.path.relpath(root, src_dir)
        dst_root = dst_dir if rel_root == "." else os.path.join(dst_dir, rel_root)

        files_to_copy = []
        for file in files:
            # Skip if file exists in any exclusion directory
            if exclusion_directories and _file_exists_in_exclusion_dirs(file, rel_root, exclusion_directories):
                continue

            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst_root, file)

            if _should_copy_file(src_file, dst_file):
                files_to_copy.append((src_file, dst_file))

        # Only create directory if there are files to copy
        if files_to_copy:
            os.makedirs(dst_root, exist_ok=True)
            for src_file, dst_file in files_to_copy:
                shutil.copy2(src_file, dst_file)
                files_copied = True

    # Clean up empty directories after copying
    if files_copied:
        _remove_empty_directories(dst_dir)


def _remove_empty_directories(directory: str) -> None:
    """
    Recursively remove empty directories starting from the given directory.

    This function walks the directory tree bottom-up and removes any directories
    that are empty after all files have been processed. It preserves the root
    directory even if it's empty.

    Parameters
    ----------
    directory : str
        The root directory path to start cleaning from.
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        # Skip the root directory itself
        if root == directory:
            continue

        # If directory is empty (no files and no subdirectories), remove it
        if not files and not dirs:
            try:
                os.rmdir(root)
            except OSError:
                # Directory might not be empty due to hidden files or permissions
                pass


def _should_copy_file(src_file: str, dst_file: str) -> bool:
    """
    Determine if a file should be copied based on existence and content.

    Parameters
    ----------
    src_file : str
        Path to the source file.
    dst_file : str
        Path to the destination file.

    Returns
    -------
    bool
        True if the file should be copied, False otherwise.
    """
    if not os.path.exists(dst_file):
        return True

    try:
        src_checksum = _calculate_file_checksum(src_file)
        dst_checksum = _calculate_file_checksum(dst_file)
        return src_checksum != dst_checksum
    except OSError:
        return True


def _calculate_file_checksum(file_path: str) -> str:
    """
    Calculate MD5 checksum of a file.

    Parameters
    ----------
    file_path : str
        The path to the file.

    Returns
    -------
    str
        The MD5 checksum of the file.
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def _file_exists_in_exclusion_dirs(file_name: str, rel_root: str, exclusion_dirs: list[str]) -> bool:
    """
    Check if a file exists in any of the exclusion directories.

    Parameters
    ----------
    file_name : str
        The name of the file to check.
    rel_root : str
        The relative root path from the source directory.
    exclusion_dirs : list[str]
        List of directories to check against.

    Returns
    -------
    bool
        True if the file exists in any exclusion directory, False otherwise.
    """
    for exclusion_dir in exclusion_dirs:
        if rel_root != ".":
            exclusion_file = os.path.join(exclusion_dir, rel_root, file_name)
        else:
            exclusion_file = os.path.join(exclusion_dir, file_name)

        if os.path.exists(exclusion_file):
            return True
    return False


if __name__ == "__main__":
    main()
