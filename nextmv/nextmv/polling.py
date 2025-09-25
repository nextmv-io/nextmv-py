"""
Polling module containing logic to poll for a run result.

Polling can be used with both Cloud and local applications.

Classes
-------
PollingOptions
    Options to use when polling for a run result.

Functions
---------
poll
    Function to poll a function until it succeeds or the polling strategy is
    exhausted.
"""

import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Optional

from nextmv.logger import log


@dataclass
class PollingOptions:
    """
    Options to use when polling for a run result.

    You can import the `PollingOptions` class directly from `nextmv`:

    ```python
    from nextmv import PollingOptions
    ```

    The Cloud API will be polled for the result. The polling stops if:

    * The maximum number of polls (tries) are exhausted. This is specified by
      the `max_tries` parameter.
    * The maximum duration of the polling strategy is reached. This is
      specified by the `max_duration` parameter.

    Before conducting the first poll, the `initial_delay` is used to sleep.
    After each poll, a sleep duration is calculated using the following
    strategy, based on exponential backoff with jitter:

    ```
    sleep_duration = min(`max_delay`, `delay` + `backoff` * 2 ** i + Uniform(0, `jitter`))
    ```

    Where:
    * i is the retry (poll) number.
    * Uniform is the uniform distribution.

    Note that the sleep duration is capped by the `max_delay` parameter.

    Parameters
    ----------
    backoff : float, default=0.9
        Exponential backoff factor, in seconds, to use between polls.
    delay : float, default=0.1
        Base delay to use between polls, in seconds.
    initial_delay : float, default=1.0
        Initial delay to use before starting the polling strategy, in seconds.
    max_delay : float, default=20.0
        Maximum delay to use between polls, in seconds.
    max_duration : float, default=300.0
        Maximum duration of the polling strategy, in seconds.
    max_tries : int, default=100
        Maximum number of tries to use.
    jitter : float, default=1.0
        Jitter to use for the polling strategy. A uniform distribution is sampled
        between 0 and this number. The resulting random number is added to the
        delay for each poll, adding a random noise. Set this to 0 to avoid using
        random jitter.
    verbose : bool, default=False
        Whether to log the polling strategy. This is useful for debugging.
    stop : callable, default=None
        Function to call to check if the polling should stop. This is useful for
        stopping the polling based on external conditions. The function should
        return True to stop the polling and False to continue. The function does
        not receive any arguments. The function is called before each poll.

    Examples
    --------
    >>> from nextmv.cloud import PollingOptions
    >>> # Create polling options with custom settings
    >>> polling_options = PollingOptions(
    ...     max_tries=50,
    ...     max_duration=600,
    ...     verbose=True
    ... )
    """

    backoff: float = 0.9
    """
    Exponential backoff factor, in seconds, to use between polls.
    """
    delay: float = 0.1
    """Base delay to use between polls, in seconds."""
    initial_delay: float = 1
    """
    Initial delay to use before starting the polling strategy, in seconds.
    """
    max_delay: float = 20
    """Maximum delay to use between polls, in seconds."""
    max_duration: float = -1
    """
    Maximum duration of the polling strategy, in seconds. A negative value means no limit.
    """
    max_tries: int = -1
    """Maximum number of tries to use. A negative value means no limit."""
    jitter: float = 1
    """
    Jitter to use for the polling strategy. A uniform distribution is sampled
    between 0 and this number. The resulting random number is added to the
    delay for each poll, adding a random noise. Set this to 0 to avoid using
    random jitter.
    """
    verbose: bool = False
    """Whether to log the polling strategy. This is useful for debugging."""
    stop: Optional[Callable[[], bool]] = None
    """
    Function to call to check if the polling should stop. This is useful for
    stopping the polling based on external conditions. The function should
    return True to stop the polling and False to continue. The function does
    not receive any arguments. The function is called before each poll.
    """


DEFAULT_POLLING_OPTIONS: PollingOptions = PollingOptions()
"""
Default polling options to use when polling for a run result. This constant
provides the default values for `PollingOptions` used across the module.
Using these defaults is recommended for most use cases unless specific timing
needs are required.
"""


def poll(  # noqa: C901
    polling_options: PollingOptions,
    polling_func: Callable[[], tuple[Any, bool]],
    __sleep_func: Callable[[float], None] = time.sleep,
) -> Any:
    """
    Poll a function until it succeeds or the polling strategy is exhausted.

    You can import the `poll` function directly from `nextmv`:

    ```python
    from nextmv import poll
    ```

    This function implements a flexible polling strategy with exponential backoff
    and jitter. It calls the provided polling function repeatedly until it indicates
    success, the maximum number of tries is reached, or the maximum duration is exceeded.

    The `polling_func` is a callable that must return a `tuple[Any, bool]`
    where the first element is the result of the polling and the second
    element is a boolean indicating if the polling was successful or should be
    retried.

    Parameters
    ----------
    polling_options : PollingOptions
        Options for configuring the polling behavior, including retry counts,
        delays, timeouts, and verbosity settings.
    polling_func : callable
        Function to call to check if the polling was successful. Must return a tuple
        where the first element is the result value and the second is a boolean
        indicating success (True) or need to retry (False).

    Returns
    -------
    Any
        Result value from the polling function when successful.

    Raises
    ------
    TimeoutError
        If the polling exceeds the maximum duration specified in polling_options.
    RuntimeError
        If the maximum number of tries is exhausted without success.

    Examples
    --------
    >>> from nextmv.cloud import PollingOptions, poll
    >>> import time
    >>>
    >>> # Define a polling function that succeeds after 3 tries
    >>> counter = 0
    >>> def check_completion() -> tuple[str, bool]:
    ...     global counter
    ...     counter += 1
    ...     if counter >= 3:
    ...         return "Success", True
    ...     return None, False
    ...
    >>> # Configure polling options
    >>> options = PollingOptions(
    ...     max_tries=5,
    ...     delay=0.1,
    ...     backoff=0.2,
    ...     verbose=True
    ... )
    >>>
    >>> # Poll until the function succeeds
    >>> result = poll(options, check_completion)
    >>> print(result)
    'Success'
    """

    # Start by sleeping for the duration specified as initial delay.
    if polling_options.verbose:
        log(f"polling | sleeping for initial delay: {polling_options.initial_delay}")

    __sleep_func(polling_options.initial_delay)

    start_time = time.time()
    stopped = False

    # Begin the polling process.
    max_reached = False
    ix = 0
    while True:
        # Check if we reached the maximum number of tries. Break if so.
        if ix >= polling_options.max_tries and polling_options.max_tries >= 0:
            break
        ix += 1

        # Check is we should stop polling according to the stop callback.
        if polling_options.stop is not None and polling_options.stop():
            stopped = True

            break

        # We check if we can stop polling.
        result, ok = polling_func()
        if polling_options.verbose:
            log(f"polling | try # {ix + 1}, ok: {ok}")

        if ok:
            return result

        # An exit condition happens if we exceed the allowed duration.
        passed = time.time() - start_time
        if polling_options.verbose:
            log(f"polling | elapsed time: {passed}")

        if passed >= polling_options.max_duration and polling_options.max_duration >= 0:
            raise TimeoutError(
                f"polling did not succeed after {passed} seconds, exceeds max duration: {polling_options.max_duration}",
            )

        # Calculate the delay.
        if max_reached:
            # If we already reached the maximum, we don't want to further calculate the
            # delay to avoid overflows.
            delay = polling_options.max_delay
            delay += random.uniform(0, polling_options.jitter)  # Add jitter.
        else:
            delay = polling_options.delay  # Base
            delay += polling_options.backoff * (2**ix)  # Add exponential backoff.
            delay += random.uniform(0, polling_options.jitter)  # Add jitter.

        # We cannot exceed the max delay.
        if delay >= polling_options.max_delay:
            max_reached = True
            delay = polling_options.max_delay

        # Sleep for the calculated delay.
        sleep_duration = delay
        if polling_options.verbose:
            log(f"polling | sleeping for duration: {sleep_duration}")

        __sleep_func(sleep_duration)

    if stopped:
        log("polling | stop condition met, stopping polling")

        return None

    raise RuntimeError(
        f"polling did not succeed after {polling_options.max_tries} tries",
    )
