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

    If you only want to log messages to stderr, and not redirect the stdout
    stream to stderr, you can instead use the `log` function from this same
    module.
    """

    def __init__(self):
        self._logs = []
        self._stdout_set = False

    class _StdoutCapture:
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

        if not self._stdout_set:
            sys.stdout = self._StdoutCapture(self)
            self._stdout_set = True

        self._logs.append(message)

    def flush(self) -> None:
        """
        Flush the logs to stderr and reset the behavior of the stdout and
        stderr streams.
        """

        for log in self._logs:
            print(log, file=sys.stderr)

        self._logs = []
        sys.stdout = sys.__stdout__
        self._stdout_set = False


def log(message: str) -> None:
    """
    Log a message to stderr.

    If you want a special logger that captures all messages and redirects both
    stdout and stderr to stderr, you can instead use the `Logger` class from
    the same module.

    Args:
        message: The message to log.
    """

    logger = Logger()
    logger.log(message)
    logger.flush()
