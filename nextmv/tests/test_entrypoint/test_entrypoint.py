import json
import os
import shutil
import subprocess
import sys
import unittest

import nextmv.cloud

import nextmv


class SimpleDecisionModel(nextmv.Model):
    def solve(self, input: nextmv.Input) -> nextmv.Output:
        return nextmv.Output(
            solution={"foo": "bar"},
            statistics={"baz": "qux"},
        )


class TestEntrypoint(unittest.TestCase):
    TWO_DIRS_UP = os.path.join("..", "..")
    MODEL_NAME = "simple_decision_model"

    def setUp(self):
        """Copies the entrypoint script as the main script in the root of an
        app."""

        # Copy the entrypoint.
        src = self._file_name("__entrypoint__.py", os.path.join(self.TWO_DIRS_UP, "nextmv"))
        dst = self._file_name("main.py", self.TWO_DIRS_UP)
        shutil.copy(src, dst)

    def tearDown(self):
        """Removes the newly created main script elements."""

        filenames = [
            self._file_name("main.py", self.TWO_DIRS_UP),
            self._file_name("app.yaml", self.TWO_DIRS_UP),
        ]

        for filename in filenames:
            os.remove(filename)

        shutil.rmtree(self._file_name(self.MODEL_NAME, self.TWO_DIRS_UP))
        shutil.rmtree(self._file_name("mlruns", self.TWO_DIRS_UP))

    def test_entrypoint(self):
        """
        Test that the __entrypoint__.py script runs successfully by mimicking
        the unpacking of an app and running the main script. We are using a
        sample nextroute app that is already pickled with mlflow in the
        "nextroute_model" directory.
        """

        model = SimpleDecisionModel()
        options = nextmv.Options(nextmv.Option("param1", str, ""))

        model_configuration = nextmv.ModelConfiguration(
            name=self.MODEL_NAME,
            options=options,
        )
        destination = os.path.join(os.path.dirname(__file__), self.TWO_DIRS_UP)
        model.save(destination, model_configuration)

        manifest = nextmv.cloud.Manifest.from_model_configuration(model_configuration)
        manifest.to_yaml(dirpath=destination)

        main_file = self._file_name("main.py", self.TWO_DIRS_UP)

        args = [sys.executable, main_file]
        try:
            result = subprocess.run(
                args,
                env=os.environ,
                check=True,
                text=True,
                capture_output=True,
                input=json.dumps({}),
            )
        except subprocess.CalledProcessError as e:
            print("stderr:\n", e.stderr)
            print("stdout:\n", e.stdout)
            print("output:\n", e.output)
            raise e

        output = result.stdout

        self.assertEqual(result.returncode, 0, result.stderr)

        self.assertNotEqual(output.strip(), "")

        output_data = json.loads(output)
        self.assertIn("statistics", output_data)

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
