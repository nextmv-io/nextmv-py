import sys
import time
from functools import wraps
from typing import Dict, List

from nextmv.cloud import Application, RunResult, StatusV2


def log(message: str) -> None:
    """Logs a message using stderr."""

    print(message, file=sys.stderr)


def wrap_func(function):
    """
    Wraps the given function in a new function that unpacks the arguments given as a tuple.
    """

    @wraps(function)
    def func_wrapper(args):
        return function(*args[0], **args[1])

    return func_wrapper


def convert_to_string_values(input_dict: Dict[str, any]) -> Dict[str, str]:
    """
    Converts all values of the given dictionary to strings.
    """
    return {key: str(value) for key, value in input_dict.items()}


_INFINITE_TIMEOUT = sys.maxsize


def wait_for_runs(
    app: Application,
    run_ids: List[str],
    timeout: int = _INFINITE_TIMEOUT,
    max_backoff: int = 30,
) -> List[RunResult]:
    """
    Wait until all runs with the given IDs are finished.
    """
    # Wait until all runs are finished or the timeout is reached
    missing = set(run_ids)
    backoff = 1
    start_time = time.time()
    while missing and time.time() - start_time < timeout:
        for run_id in missing.copy():
            run_info = app.run_metadata(run_id=run_id)
            if run_info.metadata.status_v2 == StatusV2.succeeded:
                missing.remove(run_id)
                continue
            if run_info.metadata.status_v2 in [
                StatusV2.failed,
                StatusV2.canceled,
            ]:
                raise RuntimeError(f"Run {run_id} {run_info.metadata.status_v2}")

        time.sleep(backoff)
        backoff = min(backoff * 2, max_backoff)

    if missing:
        raise TimeoutError(f"Timeout of {timeout} seconds reached while waiting.")

    return [app.run_result(run_id=run_id) for run_id in run_ids]
