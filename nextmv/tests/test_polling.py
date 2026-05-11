import unittest
from typing import Any
from unittest.mock import patch

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

    def test_default_max_tries_prevents_infinite_loop(self):
        """Default max_tries (100) causes RuntimeError when polling never succeeds."""

        def polling_func() -> tuple[Any, bool]:
            return None, False  # never succeeds

        with self.assertRaises(RuntimeError):
            poll(PollingOptions(), polling_func, no_sleep)

    def test_default_max_duration_prevents_infinite_loop(self):
        """max_duration limit causes TimeoutError when polling never succeeds."""

        def polling_func() -> tuple[Any, bool]:
            return None, False  # never succeeds

        # Patch time.time so elapsed always exceeds max_duration after the first poll.
        with patch("nextmv.polling.time.time", side_effect=[0.0, 1.0]):
            with self.assertRaises(TimeoutError):
                poll(PollingOptions(max_tries=-1, max_duration=0.5), polling_func, no_sleep)

    def test_negative_max_tries_means_no_limit(self):
        """max_tries=-1 disables the tries cap; polling succeeds after many attempts."""
        counter = 0
        target = 200  # more than the default 100

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1
            return "done", counter >= target

        result = poll(PollingOptions(max_tries=-1, max_duration=-1), polling_func, no_sleep)
        self.assertEqual(result, "done")
        self.assertEqual(counter, target)

    def test_negative_max_duration_means_no_limit(self):
        """max_duration=-1 disables the duration cap."""
        counter = 0

        def polling_func() -> tuple[Any, bool]:
            nonlocal counter
            counter += 1
            return "done", counter >= 5

        result = poll(PollingOptions(max_tries=-1, max_duration=-1), polling_func, no_sleep)
        self.assertEqual(result, "done")
