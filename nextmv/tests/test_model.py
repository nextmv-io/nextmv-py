import os
import unittest

from nextmv.model import _cleanup_python_model

import nextmv


class ModelForTesting(nextmv.Model):
    """Dummy decision model for testing purposes."""

    def solve(self, input: nextmv.Input) -> nextmv.Output:
        return nextmv.Output()


class TestModel(unittest.TestCase):
    def tearDown(self):
        """Removes the newly created mlflow elements, while also testing the
        "private" cleanup function."""

        model_configuration = nextmv.ModelConfiguration(
            name="test_model",
        )
        _cleanup_python_model(model_dir=".", model_configuration=model_configuration)

    def test_save(self):
        model = ModelForTesting()
        model_configuration = nextmv.ModelConfiguration(
            name="test_model",
        )
        model.save(model_dir=".", configuration=model_configuration)

        # Assert that the "test_model" directory was created
        model_path = os.path.join(".", model_configuration.name)
        self.assertTrue(os.path.isdir(model_path))

        # Assert that the "test_model" directory is not empty
        self.assertTrue(len(os.listdir(model_path)) > 0)

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
