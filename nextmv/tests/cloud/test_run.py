import datetime
import time
import unittest

from nextmv.cloud.run import run_duration


class TestRunDuration(unittest.TestCase):
    def test_run_duration_convenience_func(self):
        before_t, before_dt = time.time(), datetime.datetime.now()
        time.sleep(0.25)
        after_t, after_dt = time.time(), datetime.datetime.now()
        duration_t = run_duration(before_t, after_t)
        duration_dt = run_duration(before_dt, after_dt)
        self.assertAlmostEqual(duration_t, 250.0, delta=20.0)
        self.assertAlmostEqual(duration_dt, 250.0, delta=20.0)
