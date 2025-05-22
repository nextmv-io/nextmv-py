import unittest
from typing import Any

from nextmv.cloud.application import PollingOptions, poll


class TestApplication(unittest.TestCase):
    def test_poll(self):
        counter = 0

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1

            if counter < 4:
                return "result", False

            return "result", True

        polling_options = PollingOptions(verbose=True)

        result = poll(polling_options, polling_func)

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

        polling_options = PollingOptions(verbose=True, stop=stop)

        result = poll(polling_options, polling_func)

        self.assertIsNone(result)
