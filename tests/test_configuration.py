import os
import shutil
import subprocess
import unittest

import nextmv


class TestConfiguration(unittest.TestCase):
    """ "
    Tests for the `Configuration` class.

    This test suite will first copy the `configurationX.py` scripts one level
    up: to the root directory. This happens in the `setUp` method. This is
    necessary because those scripts contain an `import nextmv` statement. If
    the path to `nextmv` is not in the same path as the test scripts, the
    `import nextmv` statement will fail.

    After the test suite is executed, the `tearDown` method will remove the
    `configurationX.py` scripts from the root directory.

    All the test methods that rely on a `configurationX.py` script, need to
    assume that the script is one level up.
    """

    test_scripts = [1, 2, 3]
    """These are auxiliary scripts that are used to test different scenarios of
    instantiating a `Configuration` object."""

    def setUp(self):
        """Copies the configuration scripts to the root directory before the
        tests are executed."""

        for file in self.test_scripts:
            name = f"configuration{file}.py"
            src = self._file_name(name)
            dst = self._file_name(name, "..")
            shutil.copy(src, dst)

    def tearDown(self):
        """Removes the configuration scripts from the root directory after the
        tests are executed."""

        for file in self.test_scripts:
            name = f"configuration{file}.py"
            filename = self._file_name(name, "..")
            os.remove(filename)

    def test_defaults(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "{'duration': '30s', 'threads': 4}\n")

    def test_env_vars(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "60s", "THREADS": "8"},
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "{'duration': '60s', 'threads': 8}\n")

    def test_command_line_args_two_dashes(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "90s", "--threads", "12"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "{'duration': '90s', 'threads': 12}\n")

    def test_command_line_args_one_dash(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file, "-duration", "120s", "-threads", "16"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "{'duration': '120s', 'threads': 16}\n")

    def test_command_line_args_precede_env_vars(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "90s", "--threads", "12"],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "60s", "THREADS": "8"},
        )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "{'duration': '90s', 'threads': 12}\n")

    def test_no_values(self):
        file = self._file_name("configuration2.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn('parameter "duration" is required', result.stderr)

    def test_no_parameters(self):
        # The test passes if no exception is raised.
        nextmv.Configuration()

    def test_bad_parameter_type(self):
        with self.assertRaises(TypeError):
            nextmv.Configuration("I am not a valid parameter")

    def test_bad_type_command_line_arg(self):
        file = self._file_name("configuration2.py", "..")
        result = subprocess.run(
            ["python3", file, "--duration", "30s", "--threads", "four"],
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid int value", result.stderr)

    def test_bad_type_env_var(self):
        file = self._file_name("configuration2.py", "..")
        result = subprocess.run(
            ["python3", file],
            capture_output=True,
            text=True,
            env={**os.environ, "DURATION": "30s", "THREADS": "four"},
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("not of type <class 'int'>", result.stderr)

    def test_full_help_message(self):
        file = self._file_name("configuration1.py", "..")
        result = subprocess.run(
            ["python3", file, "-h"],
            capture_output=True,
            text=True,
        )

        self.maxDiff = None
        self.assertEqual(result.returncode, 0)
        self.assertIn("[env var: DURATION] (required) (default: 30s)", result.stdout)

    def test_minimal_help_message(self):
        file = self._file_name("configuration3.py", "..")
        result = subprocess.run(
            ["python3", file, "-h"],
            capture_output=True,
            text=True,
        )

        self.maxDiff = None
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("[env var: DURATION] (required) (default: 30s)", result.stdout)

    @staticmethod
    def _file_name(name: str, relative_location: str = ".") -> str:
        """
        Returns the full path to a file in the current testing directory.

        Parameters
        ----------
        name : str
            The name of the file.
        relative_location : str, optional
            The relative location of the file. The default is ".".

        Returns
        -------
        str
            The full path to the file.
        """

        return os.path.join(os.path.dirname(__file__), relative_location, name)
