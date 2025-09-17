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
"""

import json
import os
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Any, Optional, Union

from nextmv.input import INPUTS_KEY, InputFormat, load
from nextmv.local.geojson_handler import handle_geojson_visual
from nextmv.local.plotly_handler import handle_plotly_visual
from nextmv.local.runner import calculate_files_size
from nextmv.output import (
    ASSETS_KEY,
    DEFAULT_OUTPUT_JSON_FILE,
    LOGS_FILE,
    LOGS_KEY,
    OUTPUTS_KEY,
    SOLUTIONS_KEY,
    STATISTICS_KEY,
    Asset,
    OutputFormat,
    VisualSchema,
)
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
        manifest_entrypoint=input.data["manifest_entrypoint"],
        run_dir=input.data["run_dir"],
        run_config=input.data["run_config"],
        inputs_dir_path=input.data["inputs_dir_path"],
        options=input.data["options"],
        input_data=input.data["input_data"],
    )


def execute_run(
    run_id: str,
    src: str,
    manifest_entrypoint: str,
    run_dir: str,
    run_config: dict[str, Any],
    inputs_dir_path: Optional[str] = None,
    options: Optional[dict[str, Any]] = None,
    input_data: Optional[Union[dict[str, Any], str]] = None,
) -> None:
    """
    This function actually executes the decision model run, using a
    subprocess to call the entrypoint script with the appropriate input and
    options.

    Parameters
    ----------
    src : str
        The path to the application source code.
    manifest_entrypoint : str
        The entrypoint script as defined in the application manifest.
    run_dir : str
        The path to the run directory.
    run_config : dict[str, Any]
        The run configuration.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.
    options : Optional[dict[str, Any]], optional
        Additional options for the run, by default None.
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
            shutil.copytree(src, temp_src, ignore=shutil.ignore_patterns(".nextmv"))

            stdin_input = process_run_input(
                temp_src=temp_src,
                run_format=run_config["format"]["input"]["type"],
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
            entrypoint = os.path.join(temp_src, manifest_entrypoint)
            args = ["python", entrypoint] + options_args(options)

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
                run_id=run_id,
                temp_src=temp_src,
                result=result,
                run_dir=run_dir,
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
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
) -> str:
    """
    In the temp source, writes the run input according to the run format. If
    the format is `json` or `text`, then the input is not written anywhere,
    rather, it is returned as a string in this function. If the format is
    `csv-archive`, then the input files are written to an `input` directory. If
    the format is `multi-file`, then the input files are written to an `inputs`
    directory.

    Parameters
    ----------
    temp_src : str
        The path to the temporary source directory.
    run_format : str
        The run format, one of `json`, `text`, `csv-archive`, or `multi-file`.
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

    if run_format in (InputFormat.JSON.value, InputFormat.TEXT.value):
        if isinstance(input_data, dict) and run_format == InputFormat.JSON.value:
            return json.dumps(input_data)

        if isinstance(input_data, str) and run_format == InputFormat.TEXT.value:
            return input_data

        raise ValueError(f"invalid input data for format {run_format}")

    if run_format == InputFormat.CSV_ARCHIVE.value:
        if input_data is not None:
            raise ValueError("input data must be None for csv-archive format")

        input_dir = os.path.join(temp_src, "input")
        os.makedirs(input_dir, exist_ok=True)

        if inputs_dir_path is not None and inputs_dir_path != "":
            shutil.copytree(inputs_dir_path, input_dir, dirs_exist_ok=True)

        return ""

    if run_format == InputFormat.MULTI_FILE.value:
        if input_data is not None:
            raise ValueError("input data must be None for multi-file format")

        inputs_dir = os.path.join(temp_src, INPUTS_KEY)
        os.makedirs(inputs_dir, exist_ok=True)

        if inputs_dir_path is not None and inputs_dir_path != "":
            shutil.copytree(inputs_dir_path, inputs_dir, dirs_exist_ok=True)

        return ""


def process_run_output(run_id: str, temp_src: str, result: subprocess.CompletedProcess[str], run_dir: str) -> None:
    """
    Processes the result of the subprocess run. This function is in charge of
    handling the run results, including solutions, statistics, logs, assets,
    etc.

    Parameters
    ----------
    temp_src : str
        The path to the temporary source directory.
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run.
    run_dir : str
        The path to the run directory.
    """

    # Parse stdout as JSON, if possible.
    stdout_output = ""
    raw_output = result.stdout
    if raw_output.strip() != "":
        stdout_output = json.loads(raw_output)

    # Create outputs directory.
    outputs_dir = os.path.join(run_dir, OUTPUTS_KEY)
    os.makedirs(outputs_dir, exist_ok=True)
    temp_run_outputs_dir = os.path.join(temp_src, OUTPUTS_KEY)

    process_run_information(
        run_id=run_id,
        run_dir=run_dir,
        result=result,
    )
    process_run_logs(
        run_dir=run_dir,
        result=result,
    )
    process_run_statistics(
        temp_run_outputs_dir=temp_run_outputs_dir,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
    )
    process_run_assets(
        temp_run_outputs_dir=temp_run_outputs_dir,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
    )
    process_run_solutions(
        run_id=run_id,
        run_dir=run_dir,
        temp_run_outputs_dir=temp_run_outputs_dir,
        temp_src=temp_src,
        outputs_dir=outputs_dir,
        stdout_output=stdout_output,
    )
    process_run_visuals(
        run_dir=run_dir,
        outputs_dir=outputs_dir,
    )


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
        error = result.stderr if result.stderr else "unknown error"

    # Update the run info file.
    info["metadata"]["duration"] = duration
    info["metadata"]["status_v2"] = status
    info["metadata"]["error"] = error

    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)


def process_run_logs(run_dir: str, result: subprocess.CompletedProcess[str]) -> None:
    """
    Processes the logs of the run. Writes the logs to a logs directory.

    Parameters
    ----------
    run_dir : str
        The path to the run directory.
    result : subprocess.CompletedProcess[str]
        The result of the subprocess run.
    """

    logs_dir = os.path.join(run_dir, LOGS_KEY)
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, LOGS_FILE), "w") as f:
        f.write(result.stderr)


def process_run_statistics(temp_run_outputs_dir: str, outputs_dir: str, stdout_output: dict[str, Any]) -> None:
    """
    Processes the statistics of the run. Check for an outputs/statistics folder
    being created by the run. If it exists, copy it to the run directory. If it
    doesn't exist, attempt to get the stats from stdout.

    Parameters
    ----------
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : dict[str, Any]
        The stdout output of the run, parsed as a dictionary.
    """

    stats_src = os.path.join(temp_run_outputs_dir, STATISTICS_KEY)
    stats_dst = os.path.join(outputs_dir, STATISTICS_KEY)
    if os.path.exists(stats_src) and os.path.isdir(stats_src):
        shutil.copytree(stats_src, stats_dst, dirs_exist_ok=True)
        return

    if STATISTICS_KEY not in stdout_output:
        return

    os.makedirs(stats_dst, exist_ok=True)
    with open(os.path.join(stats_dst, f"{STATISTICS_KEY}.json"), "w") as f:
        statistics = {STATISTICS_KEY: stdout_output[STATISTICS_KEY]}
        json.dump(statistics, f, indent=2)


def process_run_assets(temp_run_outputs_dir: str, outputs_dir: str, stdout_output: dict[str, Any]) -> None:
    """
    Processes the assets of the run. Check for an outputs/assets folder being
    created by the run. If it exists, copy it to the run directory. If it
    doesn't exist, attempt to get the assets from stdout.

    Parameters
    ----------
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : dict[str, Any]
        The stdout output of the run, parsed as a dictionary.
    """

    assets_src = os.path.join(temp_run_outputs_dir, ASSETS_KEY)
    assets_dst = os.path.join(outputs_dir, ASSETS_KEY)
    if os.path.exists(assets_src) and os.path.isdir(assets_src):
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
        return

    if ASSETS_KEY not in stdout_output:
        return

    os.makedirs(assets_dst, exist_ok=True)
    with open(os.path.join(assets_dst, f"{ASSETS_KEY}.json"), "w") as f:
        assets = {ASSETS_KEY: stdout_output[ASSETS_KEY]}
        json.dump(assets, f, indent=2)


def process_run_solutions(
    run_id: str,
    run_dir: str,
    temp_run_outputs_dir: str,
    temp_src: str,
    outputs_dir: str,
    stdout_output: dict[str, Any],
) -> None:
    """
    Processes the solutions (output) of the run. This method has the handle all
    the different formats for processing solutions. This includes looking for
    an `output` directory (`csv-archive`), an `outputs/solutions` directory
    (`multi-file`), or looking for solutions in the stdout output (`json` or
    `text`). For flexibility, we copy whatever is in the `output` and
    `outputs/solutions` directories, if they exist. If neither exist, we
    attempt to get the solution from stdout.

    Parameters
    ----------
    temp_run_outputs_dir : str
        The path to the temporary outputs directory.
    temp_src : str
        The path to the temporary source directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
    stdout_output : dict[str, Any]
        The stdout output of the run, parsed as a dictionary.
    """

    info_file = os.path.join(run_dir, f"{run_id}.json")

    with open(info_file) as f:
        info = json.load(f)

    solutions_dst = os.path.join(outputs_dir, SOLUTIONS_KEY)
    os.makedirs(solutions_dst, exist_ok=True)

    output_src = os.path.join(temp_src, "output")
    solutions_src = os.path.join(temp_run_outputs_dir, SOLUTIONS_KEY)
    if os.path.exists(output_src) and os.path.isdir(output_src):
        # For csv-archive, copy everything from output to solutions.
        shutil.copytree(output_src, solutions_dst, dirs_exist_ok=True)
        output_type = OutputFormat.CSV_ARCHIVE.value

    elif os.path.exists(solutions_src) and os.path.isdir(solutions_src):
        # For multi-file, copy everything from outputs/solutions to solutions.
        shutil.copytree(solutions_src, solutions_dst, dirs_exist_ok=True)
        output_type = OutputFormat.MULTI_FILE.value

    else:
        # If we reach here, it means neither output nor outputs/solutions
        # exist, so we simply dump whatever is in stdout as solution.json.
        if stdout_output:
            with open(os.path.join(solutions_dst, DEFAULT_OUTPUT_JSON_FILE), "w") as f:
                json.dump(stdout_output, f, indent=2)

        output_type = OutputFormat.JSON.value

    # Update the run information file with the output size and type.
    calculate_files_size(run_dir, run_id, solutions_dst, metadata_key="output_size")
    info["metadata"]["format"]["output"] = {"type": output_type}
    with open(info_file, "w") as f:
        json.dump(info, f, indent=2)


def process_run_visuals(run_dir: str, outputs_dir: str) -> None:
    """
    Processes the visuals from the assets in the run output. This function looks
    for Plotly assets and generates HTML files for each visual.

    Parameters
    ----------
    run_dir : str
        The path to the run directory.
    outputs_dir : str
        The path to the outputs directory in the run directory.
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


if __name__ == "__main__":
    main()
