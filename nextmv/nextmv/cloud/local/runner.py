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
"""

import json
import os
import shutil
import subprocess
from typing import Any, Optional, Union

from nextmv.cloud.manifest import Manifest
from nextmv.cloud.safe import safe_id


def run(
    src: str,
    manifest: Manifest,
    run_config: dict[str, Any],
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
    options: Optional[dict[str, Any]] = None,
) -> str:
    """
    Execute a local run.

    You can import the `run` method directly from `local`:

    ```python
    from nextmv.cloud.local import run
    ```

    This method recreates, partially, what the Nextmv Cloud does in the backend
    when running an application. A run ID is generated, a run directory is
    created, and the input data is recorded. Then, a subprocess is started to
    execute the application run in a detached manner. This means that the
    application run is not waited upon.

    Parameters
    ----------
    src : str
        The path to the application source code.
    manifest : Manifest
        The application manifest.
    run_config : dict[str, Any]
        The run configuration.
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

    run_id = safe_id("local")
    run_dir = new_run(src, run_id)
    record_input(run_dir, input_data, inputs_dir_path)

    # Start the process as a daemon (detached) so we don't wait for it to finish
    args = ["python", "executor.py"]
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

    # Send input and close stdin immediately without waiting
    stdin_input = json.dumps(
        {
            "src": os.path.abspath(src),
            "manifest_entrypoint": manifest.entrypoint,
            "run_dir": os.path.abspath(run_dir),
            "run_config": run_config,
            "input_data": input_data,
            "inputs_dir_path": os.path.abspath(inputs_dir_path) if inputs_dir_path is not None else None,
            "options": options,
        }
    )
    process.stdin.write(stdin_input)
    process.stdin.close()

    return run_id


def new_run(src: str, run_id: str) -> str:
    """
    Initializes a new run.

    You can import the `new_run` method directly from `local`:

    ```python
    from nextmv.cloud.local import new_run
    ```

    Parameters
    ----------
    src : str
        The path to the application source code.
    run_id : str
        The ID of the run.

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

    return run_dir


def record_input(
    run_dir: str,
    input_data: Optional[Union[dict[str, Any], str]] = None,
    inputs_dir_path: Optional[str] = None,
) -> None:
    """
    Writes the input to the appropriate location.

    You can import the `record_input` method directly from `local`:

    ```python
    from nextmv.cloud.local import record_input
    ```

    Parameters
    ----------
    run_dir : str
        The path to the run directory.
    input_data : Optional[Union[dict[str, Any], str]], optional
        The input data for the run, by default None. If `inputs_dir_path` is
        provided, this parameter is ignored.
    inputs_dir_path : Optional[str], optional
        The path to the directory containing input files, by default None. If
        provided, this parameter takes precedence over `input_data`.
    """

    # Create the inputs directory.
    run_inputs_dir = os.path.join(run_dir, "inputs")
    os.makedirs(run_inputs_dir, exist_ok=True)

    # If we specify an inputs directory, we ignore the input_data.
    if inputs_dir_path is not None and inputs_dir_path != "":
        # Copy all files from inputs_dir_path to run_inputs_dir
        if os.path.exists(inputs_dir_path) and os.path.isdir(inputs_dir_path):
            shutil.copytree(inputs_dir_path, run_inputs_dir, dirs_exist_ok=True)

        return

    # If no inputs_dir_path is provided, input_data should be available, so we
    # write input_data to a default input file.
    if isinstance(input_data, dict):
        with open(os.path.join(run_inputs_dir, "input.json"), "w") as f:
            json.dump(input_data, f, indent=2)

        return

    if isinstance(input_data, str):
        with open(os.path.join(run_inputs_dir, "input"), "w") as f:
            f.write(input_data)

    return
