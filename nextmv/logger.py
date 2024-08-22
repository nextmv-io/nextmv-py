"""Logger that writes to stderr."""

import sys


class Logger:
    """
    Logger is a special class that logs _all_ messages to stderr. After it is
    instantiated, it will redirect _all_ messages streamed to both stdout and
    stderr to a buffer. To flush the buffer to stderr, call the `flush` method.
    Once the `flush` method is called, the buffer will be cleared, by streaming
    all the logs stored to stderr, and the behavior of stdout and stderr will
    be restored to their original state.

    If you only want to log messages to stderr, without buffering them, and not
    redirect the stdout stream to stderr, you can instead use the `log`
    function from this same module.

    Examples:

        - Print message "0" to stdout, messages "1" and "2" to stderr, and then "3" to stdout:

        ```python
        import nextmv

        print("0. I do nothing")
        logger = nextmv.Logger()
        logger.log("1. I log a message to stderr")
        print("2. I print a message to stdout, but gets redirected to stderr")
        logger.flush()
        print("3. I print another message to stdout")
        ```
    """

    def __init__(self):
        self._logs = []
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = self._FileCapture(self)
        sys.stderr = self._FileCapture(self)

    class _FileCapture:
        """This custom writer is written to capture anything written to
        stdout. It needs to implement the `write` and `flush` methods."""

        def __init__(self, logger):
            self.logger = logger

        def write(self, message):
            if message.strip():  # Avoid capturing empty messages.
                self.logger._logs.append(message)

        def flush(self):
            pass  # No need to implement flush for this use case.

    def log(self, message: str) -> None:
        """
        Log a message that will be later redirected to stderr.

        Args:
            message: The message to log.
        """

        self._logs.append(message)

    def flush(self) -> None:
        """
        Flush the buffer to stderr and clear the buffer.
        """

        for log in self._logs:
            self._original_stderr.write(log + "\n")

        self._logs = []
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr


def log(message: str) -> None:
    """
    Log a message to stderr.

    If you want a special logger that buffers stdout and stderr messages and
    flushes them to stderr, you can instead use the `Logger` class from the
    same module.

    Args:
        message: The message to log.
    """

    print(message, file=sys.stderr)
