"""
Local module to hold convenience functions used in the `local` package.

Functions
----------
calculate_files_size
    Function to calculate the total size of files in a directory.

Attributes
----------
OUTPUT_KEY : str
    Output key constant used for identifying output in the run output.
LOGS_KEY : str
    Logs key constant used for identifying logs in the run output.
LOGS_FILE : str
    Constant used for identifying the file used for logging.
DEFAULT_OUTPUT_JSON_FILE : str
    Constant for the default output JSON file name.
RUNS_KEY : str
    Runs key constant used for identifying the runs directory in the nextmv
    location.
NEXTMV_DIR : str
    Constant for the Nextmv directory name.
DEFAULT_INPUT_JSON_FILE : str
    Constant for the default input JSON file name.
"""

import json
import os

OUTPUT_KEY = "output"
"""
Output key constant used for identifying output in the run output.
"""
LOGS_KEY = "logs"
"""
Logs key constant used for identifying logs in the run output.
"""
LOGS_FILE = "logs.log"
"""
Constant used for identifying the file used for logging.
"""
DEFAULT_OUTPUT_JSON_FILE = "solution.json"
"""
Constant for the default output JSON file name.
"""
RUNS_KEY = "runs"
"""
Runs key constant used for identifying the runs directory in the nextmv
location.
"""
NEXTMV_DIR = ".nextmv"
"""
Constant for the Nextmv directory name.
"""
DEFAULT_INPUT_JSON_FILE = "input.json"
"""
Constant for the default input JSON file name.
"""


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
            if os.path.islink(fp):
                continue
            total_size += os.path.getsize(fp)

    info_file = os.path.join(run_dir, f"{run_id}.json")
    with open(info_file, "r+") as f:
        info = json.load(f)
        info["metadata"][metadata_key] = total_size
        f.seek(0)
        json.dump(info, f, indent=2)
        f.truncate()
