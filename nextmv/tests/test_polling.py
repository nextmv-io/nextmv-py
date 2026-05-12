import unittest
from typing import Any

from nextmv.polling import PollingOptions, poll


# This is a dummy function to avoid actually sleeping during tests.
def no_sleep(value: float) -> None:
    return


class TestPolling(unittest.TestCase):
    def test_poll(self):
        counter = 0

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < 4:
                return "result", False

            return "result", True

        polling_options = PollingOptions()

        result = poll(polling_options, polling_func, no_sleep)

        self.assertEqual(result, "result")

    def test_poll_stop_callback(self):
        counter = 0

        # The polling func would stop after 9 calls.
        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < 10:
                return "result", False

            return "result", True

        # The stop callback makes sure that the polling stops sooner, after 3
        # calls.
        def stop() -> bool:
            if counter == 3:
                return True

        polling_options = PollingOptions(stop=stop)

        result = poll(polling_options, polling_func, no_sleep)

        self.assertIsNone(result)

    def test_poll_long(self):
        counter = 0
        max_tries = 1000000

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < max_tries:
                return "result", False

            return "result", True

        polling_options = PollingOptions(
            max_tries=max_tries + 1,
        )

        result = poll(polling_options, polling_func, no_sleep)

        self.assertEqual(result, "result")
