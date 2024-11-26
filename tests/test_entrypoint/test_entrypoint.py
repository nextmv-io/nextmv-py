import json
import os
import shutil
import subprocess
import time
import unittest


class TestEntrypoint(unittest.TestCase):
    def setUp(self):
        """Copies the entrypoint script as the main script in the root of an
        app."""

        # Copy the entrypoint.
        src = self._file_name("__entrypoint__.py", "../../nextmv")
        dst = self._file_name("main.py", "../..")
        shutil.copy(src, dst)

        # Copy app files.
        for file in ["input.json", "app.yaml"]:
            src = self._file_name(file, ".")
            dst = self._file_name(file, "../..")
            shutil.copy(src, dst)

        # Copy mlflow dir.
        src = self._file_name("nextroute_model", ".")
        dst = self._file_name("nextroute_model", "../..")
        shutil.copytree(src, dst, dirs_exist_ok=True)

        time.sleep(10)

    def tearDown(self):
        """Removes the newly created main script elements."""

        filenames = [
            self._file_name("main.py", "../.."),
            self._file_name("input.json", "../.."),
            self._file_name("app.yaml", "../.."),
        ]

        for filename in filenames:
            os.remove(filename)

        shutil.rmtree(self._file_name("nextroute_model", "../.."))
        shutil.rmtree(self._file_name("mlruns", "../.."))

    def test_entrypoint(self):
        """
        Test that the __entrypoint__.py script runs successfully by mimicking
        the unpacking of an app and running the main script. We are using a
        sample nextroute app that is already pickled with mlflow in the
        "nextroute_model" directory.
        """

        input_file = self._file_name("input.json", "../..")
        with open(input_file) as f:
            input_data = json.load(f)

        input_stream = json.dumps(input_data)

        main_file = self._file_name("main.py", "../..")
        args = ["python", main_file]
        result = subprocess.run(
            args,
            env=os.environ,
            check=True,
            text=True,
            capture_output=True,
            input=input_stream,
        )

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
