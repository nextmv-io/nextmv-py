import unittest

from nextmv.cloud.application import PollingOptions, poll


class TestApplication(unittest.TestCase):
    def test_poll(self):
        counter = 0

        def polling_func() -> tuple[any, bool]:
            nonlocal counter
            counter += 1

            if counter < 4:
                return "result", False

            return "result", True

        polling_options = PollingOptions(verbose=True)

        result = poll(polling_options, polling_func)

        self.assertEqual(result, "result")
