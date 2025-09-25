"""
Runner module for executing local runs.

This module provides functionality to execute local runs.

Functions
---------
run
    Function to execute a local run.
new_run
    Function to initialize a new run.
record_input
    Function to write the input to the appropriate location.
calculate_files_size
    Function to calculate the total size of files in a directory.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from typing import Any, Optional, Union

from nextmv.input import DEFAULT_INPUT_JSON_FILE, INPUTS_KEY
from nextmv.manifest import Manifest
from nextmv.run import Format, FormatInput, Metadata, RunInformation, StatusV2
from nextmv.safe import safe_id


def run(
    app_id: str,
    src: str,
    manifest: Manifest,
    run_config: dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
    options: Optional[dict[str, Any]] = None,
) -> str:
    """
    Execute a local run.

    This method recreates, partially, what the Nextmv Cloud does in the backend
    when running an application. A run ID is generated, a run directory is
    created, and the input data is recorded. Then, a subprocess is started to
    execute the application run in a detached manner. This means that the
    application run is not waited upon.

    Parameters
    ----------
    app_id : str
        The ID of the application.
    src : str
        The path to the application source code.
    manifest : Manifest
        The application manifest.
    run_config : dict[str, Any]
        The run configuration.
    name : Optional[str], optional
        The name for the run, by default None.
    description : Optional[str], optional
        The description for the run, by default None.
    input_data : Optional[Union[dict[str, Any], str]], optional
        The input data for the run, by default None. If `inputs_dir_path` is
        provided, this parameter is ignored.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.
    options : Optional[dict[str, Any]], optional
        Additional options for the run, by default None.

    Returns
    -------
    str
        The ID of the created run.
    """

    # Check for required optional dependencies
    missing_deps = []
    if importlib.util.find_spec("folium") is None:
        missing_deps.append("folium")
    if importlib.util.find_spec("plotly") is None:
        missing_deps.append("plotly")

    if missing_deps:
        raise ImportError(
            f"{' and '.join(missing_deps)} {'is' if len(missing_deps) == 1 else 'are'} not installed. "
            "Please install optional dependencies with `pip install nextmv[all]`"
        )

    # Initialize the run: create the ID, dir, and write the input.
    run_id = safe_id("local")
    run_dir = new_run(
        app_id=app_id,
        src=src,
        run_id=run_id,
        run_config=run_config,
        name=name,
        description=description,
    )
    record_input(
        run_dir=run_dir,
        run_id=run_id,
        input_data=input_data,
        inputs_dir_path=inputs_dir_path,
    )

    # Start the process as a daemon (detached) so we don't wait for it to
    # finish. We send the input via stdin and close it immediately without
    # waiting. We call the `executor.py` script to do the actual execution.
    stdin_input = json.dumps(
        {
            "run_id": run_id,
            "src": os.path.abspath(src),
            "manifest_dict": manifest.to_dict(),
            "run_dir": os.path.abspath(run_dir),
            "run_config": run_config,
            "input_data": input_data,
            "inputs_dir_path": os.path.abspath(inputs_dir_path) if inputs_dir_path is not None else None,
            "options": options,
        }
    )
    args = [sys.executable, "executor.py"]
    process = subprocess.Popen(
        args,
        env=os.environ,
        text=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=os.path.dirname(__file__),
        start_new_session=True,  # Detach from parent process
    )
    process.stdin.write(stdin_input)
    process.stdin.close()

    return run_id


def new_run(
    app_id: str,
    src: str,
    run_id: str,
    run_config: dict[str, Any],
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> str:
    """
    Initializes a new run.

    The run information is recorded in a JSON file within the run directory.

    Parameters
    ----------
    app_id : str
        The ID of the application.
    src : str
        The path to the application source code.
    run_id : str
        The ID of the run.
    run_config : dict[str, Any]
        The run configuration.
    name : Optional[str], optional
        The name for the run, by default None.
    description : Optional[str], optional
        The description for the run, by default None.

    Returns
    -------
    str
        The path to the new run directory.
    """

    # First, ensure the runs directory exists.
    runs_dir = os.path.join(src, ".nextmv", "runs")
    os.makedirs(runs_dir, exist_ok=True)

    # Create a new run directory.
    run_dir = os.path.join(runs_dir, run_id)
    os.makedirs(run_dir, exist_ok=True)

    # Create the run information file.
    created_at = datetime.now(timezone.utc)
    metadata = Metadata(
        application_id=app_id,
        application_instance_id="",
        application_version_id="",
        created_at=created_at,
        duration=0.0,
        error="",
        input_size=0.0,
        output_size=0.0,
        format=Format(
            format_input=FormatInput(
                input_type=run_config["format"]["input"]["type"],
            ),
        ),
        status_v2=StatusV2.queued,
    )

    if description is None:
        description = f"Local run created at {created_at.isoformat().replace('+00:00', 'Z')}"

    if name is None:
        name = f"local run {run_id}"

    information = RunInformation(
        description=description,
        id=run_id,
        metadata=metadata,
        name=name,
        user_email="",
    )
    with open(os.path.join(run_dir, f"{run_id}.json"), "w") as f:
        json.dump(information.to_dict(), f, indent=2)

    return run_dir


def record_input(
    run_dir: str,
    run_id: str,
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
) -> None:
    """
    Writes the input to the appropriate location.

    The size of the input is calculated and recorded in the run information.

    Parameters
    ----------
    run_dir : str
        The path to the run directory.
    run_id : str
        The ID of the run.
    input_data : Optional[Union[dict[str, Any], str]], optional
        The input data for the run, by default None. If `inputs_dir_path` is
        provided, this parameter is ignored.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.
    """

    # Create the inputs directory.
    run_inputs_dir = os.path.join(run_dir, INPUTS_KEY)
    os.makedirs(run_inputs_dir, exist_ok=True)

    if inputs_dir_path is not None and inputs_dir_path != "":
        # If we specify an inputs directory, we ignore the input_data.
        # Copy all files from inputs_dir_path to run_inputs_dir
        if os.path.exists(inputs_dir_path) and os.path.isdir(inputs_dir_path):
            shutil.copytree(inputs_dir_path, run_inputs_dir, dirs_exist_ok=True)

    elif isinstance(input_data, dict):
        # If no inputs_dir_path is provided, try a single JSON input.
        with open(os.path.join(run_inputs_dir, DEFAULT_INPUT_JSON_FILE), "w") as f:
            json.dump(input_data, f, indent=2)

    elif isinstance(input_data, str):
        # If no inputs_dir_path is provided, try a single TEXT input.
        with open(os.path.join(run_inputs_dir, "input"), "w") as f:
            f.write(input_data)

    else:
        raise ValueError(
            "Invalid input data type: input_data must be a dict or str, or inputs_dir_path must be provided."
        )

    # Update the input size in the run information file.
    calculate_files_size(run_dir, run_id, run_inputs_dir, metadata_key="input_size")


def calculate_files_size(run_dir: str, run_id: str, dir_path: str, metadata_key: str) -> None:
    """
    Calculates the total size of the files in a directory, in bytes.

    The calculated size is stored in the run information metadata under the
    specified key.

    Parameters
    ----------
    run_dir : str
        The path to the run directory.
    run_id : str
        The ID of the run.
    dir_path : str
        The path to the directory whose size is to be calculated.
    metadata_key : str
        The key under which to store the calculated size in the run information
        metadata.
    """

    total_size = 0
    for dirpath, _, filenames in os.walk(dir_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # Skip if it is a symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    info_file = os.path.join(run_dir, f"{run_id}.json")
    with open(info_file, "r+") as f:
        info = json.load(f)
        info["metadata"][metadata_key] = total_size
        f.seek(0)
        json.dump(info, f, indent=2)
        f.truncate()
