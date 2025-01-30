import csv
import os
import shutil
import unittest
from io import StringIO
from typing import Optional
from unittest.mock import patch

import nextmv


class TestInput(unittest.TestCase):
    """
    Tests for the various classes for loading an input.
    """

    def test_local_loader_json_stdin(self):
        sample_input = '{"empanadas": "are_life"}\n'
        input_loader = nextmv.LocalInputLoader()

        with patch("sys.stdin", new=StringIO(sample_input)):
            input_data = input_loader.load()

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.JSON)
        self.assertEqual(input_data.data, {"empanadas": "are_life"})
        self.assertIsNone(input_data.options)

    def test_local_loader_text_stdin(self):
        sample_input = "empanadas are life\n"
        input_loader = nextmv.LocalInputLoader()

        with patch("sys.stdin", new=StringIO(sample_input)):
            input_data = input_loader.load(input_format=nextmv.InputFormat.TEXT)

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.TEXT)
        self.assertEqual(input_data.data, "empanadas are life")
        self.assertIsNone(input_data.options)

    def test_local_loader_csv_stdin(self):
        sample_input = '"empanadas","are","life"\n1,2,3\n4,5,6'
        input_loader = nextmv.LocalInputLoader()

        with patch("sys.stdin", new=StringIO(sample_input)):
            input_data = input_loader.load(
                input_format=nextmv.InputFormat.CSV,
                csv_configurations={
                    "quoting": csv.QUOTE_NONNUMERIC,
                },
            )

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.CSV)
        self.assertEqual(
            list(input_data.data),
            [
                {"empanadas": 1.0, "are": 2.0, "life": 3.0},
                {"empanadas": 4.0, "are": 5.0, "life": 6.0},
            ],
        )
        self.assertIsNone(input_data.options)

    def test_local_loader_with_options(self):
        sample_input = '{"empanadas": "are_life"}\n'
        options = nextmv.Options(nextmv.Parameter("foo", str, default="bar", required=False))
        input_loader = nextmv.LocalInputLoader()

        with patch("sys.stdin", new=StringIO(sample_input)):
            input_data = input_loader.load(options=options)

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.JSON)
        self.assertEqual(input_data.data, {"empanadas": "are_life"})
        self.assertIsNotNone(input_data.options)
        self.assertDictEqual(input_data.options.to_dict(), options.to_dict())

    def test_local_loader_json_file(self):
        sample_input = '{"empanadas": "are_life"}'
        input_loader = nextmv.LocalInputLoader()

        with patch("builtins.open", return_value=StringIO(sample_input)):
            input_data = input_loader.load(path="input.json")

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.JSON)
        self.assertEqual(input_data.data, {"empanadas": "are_life"})
        self.assertIsNone(input_data.options)

    def test_local_loader_text_file(self):
        sample_input = "empanadas are life"
        input_loader = nextmv.LocalInputLoader()

        with patch("builtins.open", return_value=StringIO(sample_input)):
            input_data = input_loader.load(input_format=nextmv.InputFormat.TEXT, path="input.txt")

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.TEXT)
        self.assertEqual(input_data.data, "empanadas are life")
        self.assertIsNone(input_data.options)

    def test_local_loader_csv_file(self):
        sample_input = '"empanadas","are","life"\n1,2,3\n4,5,6'
        input_loader = nextmv.LocalInputLoader()

        with patch("builtins.open", return_value=StringIO(sample_input)):
            input_data = input_loader.load(
                input_format=nextmv.InputFormat.CSV,
                path="input.csv",
                csv_configurations={
                    "quoting": csv.QUOTE_NONNUMERIC,
                },
            )

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.CSV)
        self.assertEqual(
            list(input_data.data),
            [
                {"empanadas": 1.0, "are": 2.0, "life": 3.0},
                {"empanadas": 4.0, "are": 5.0, "life": 6.0},
            ],
        )
        self.assertIsNone(input_data.options)

    def test_local_loader_csv_archive_default_dir(self):
        """If the path for loading the input is not provided, the path `input`
        is used for the directory."""
        self._test_local_loader_csv_archive(test_dir="input", load_path="")

        # Should also work if not provided at all.
        self._test_local_loader_csv_archive(test_dir="input", load_path=None)

    def test_local_loader_csv_archive_custom_dir(self):
        """If the path for loading the input is provided, the path is used for
        the directory."""
        self._test_local_loader_csv_archive(test_dir="custom_dir", load_path="custom_dir")

    def _test_local_loader_csv_archive(
        self,
        test_dir: str,
        load_path: Optional[str] = None,
    ):
        """This is an auxiliary function that is used to test the flow of the
        CSV archive input loader but with different directories."""

        # Create the directory if it doesn't exist
        os.makedirs(test_dir, exist_ok=True)

        input_loader = nextmv.LocalInputLoader()

        # Write sample CSV files
        sample_input_1 = '"empanadas","are","life"\n1,2,3\n4,5,6'
        sample_input_2 = '"or","are","tacos"\n7,8,9\n10,11,12'
        with open(f"{test_dir}/empanada_declaration_archive.csv", "w") as file_1:
            file_1.write(sample_input_1)
        with open(f"{test_dir}/taco_declaration_archive.csv", "w") as file_2:
            file_2.write(sample_input_2)

        # Load the CSV archive input
        input_data = input_loader.load(
            nextmv.InputFormat.CSV_ARCHIVE,
            path=load_path,
            csv_configurations={
                "quoting": csv.QUOTE_NONNUMERIC,
            },
        )

        # Do the checks
        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.CSV_ARCHIVE)
        self.assertIsNone(input_data.options)

        self.assertIn(
            "empanada_declaration_archive",
            list(input_data.data.keys()),
        )
        self.assertIn(
            "taco_declaration_archive",
            list(input_data.data.keys()),
        )
        self.assertEqual(
            list(input_data.data["empanada_declaration_archive"]),
            [
                {"empanadas": 1.0, "are": 2.0, "life": 3.0},
                {"empanadas": 4.0, "are": 5.0, "life": 6.0},
            ],
        )
        self.assertEqual(
            list(input_data.data["taco_declaration_archive"]),
            [
                {"or": 7.0, "are": 8.0, "tacos": 9.0},
                {"or": 10.0, "are": 11.0, "tacos": 12.0},
            ],
        )

        # Remove the directory.
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()
