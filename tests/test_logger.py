import sys
import unittest
from io import StringIO
from unittest.mock import patch

import nextmv


class TestLogger(unittest.TestCase):
    @patch("sys.stderr", new_callable=StringIO)
    @patch("sys.stdout", new_callable=StringIO)
    def test_log(self, mock_stdout, mock_stderr):
        # Make sure that stdout is not redirected to stderr, this is, it is not
        # affected by the log function.
        print("I print a message to stdout")
        self.assertEqual(
            mock_stdout.getvalue(),
            "I print a message to stdout\n",
        )

        # Test that calling the simple log function is equivalent to printing
        # to stderr.
        nextmv.log("doing this")
        print("is the same as doing this", file=sys.stderr)
        self.assertEqual(
            mock_stderr.getvalue(),
            "doing this\nis the same as doing this\n",
        )

    @patch("sys.stderr", new_callable=StringIO)
    def test_logger(self, mock_stderr):
        logger = nextmv.Logger()

        # I can log to stderr.
        logger.log("0. log directly to stderr")

        # And if I print to stdout, it will actually be redirected to stderr.
        print("1. stdout redirected to stderr")

        # I have to remember to flush the logger to see the messages.
        logger.flush()

        self.assertEqual(
            mock_stderr.getvalue(),
            "0. log directly to stderr\n1. stdout redirected to stderr\n",
        )

    @patch("sys.stderr", new_callable=StringIO)
    def test_logger_no_flush(self, mock_stderr):
        logger = nextmv.Logger()

        # I can log to stderr.
        logger.log("0. log directly to stderr")

        # And if I print to stdout, it will actually be redirected to stderr.
        print("1. stdout redirected to stderr")

        # Note that I didn't flush the logger, so the messages are not shown.
        self.assertEqual(mock_stderr.getvalue(), "")
