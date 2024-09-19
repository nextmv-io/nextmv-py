import csv
import json
import os
import shutil
import unittest
from io import StringIO
from typing import Optional
from unittest.mock import patch

import nextmv


class TestOutput(unittest.TestCase):
    """Tests for the various classes for writing an output."""

    def test_local_writer_json_stdout_default(self):
        output = nextmv.Output(
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
                "options": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_default_dict_output(self):
        output = {
            "solution": {"empanadas": "are_life"},
            "statistics": {"foo": "bar"},
        }
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
                "options": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout(self):
        output = nextmv.Output(
            output_format=nextmv.OutputFormat.JSON,
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
                "options": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_with_options(self):
        options = nextmv.Options()
        options.duration = 5
        options.solver = "highs"

        output = nextmv.Output(
            options=options,
            output_format=nextmv.OutputFormat.JSON,
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "options": {
                    "duration": 5,
                    "solver": "highs",
                },
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_with_options_json(self):
        output = nextmv.Output(
            options={"duration": 5, "solver": "highs"},
            output_format=nextmv.OutputFormat.JSON,
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "options": {
                    "duration": 5,
                    "solver": "highs",
                },
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_file(self):
        output = nextmv.Output(
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("builtins.open", create=True) as mock_open:
            output_writer.write(output, "output.json")

            handle = mock_open.return_value.__enter__.return_value
            handle.write.assert_called_once()

            got = json.loads(handle.write.call_args[0][0])
            expected = {
                "options": {},
                "solution": {"empanadas": "are_life"},
                "statistics": {"foo": "bar"},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_csvarchive_default_dir(self):
        """If the path for writing an output is not provided, the path `output`
        is used as the default directory."""
        self._test_local_writer_csvarchive(write_path="output", function_path="")

        # Should also work if not provided at all.
        self._test_local_writer_csvarchive(write_path="output", function_path=None)

    def test_local_writer_csvarchive_custom_dir(self):
        """Tests the flow of a CSV archive output writer but with a custom
        directory."""

        write_path = "KrAzYpAtH"
        self._test_local_writer_csvarchive(
            write_path=write_path,
            function_path=write_path,
        )

    def test_local_writer_csvarchive_wrong_path(self):
        output_writer = nextmv.LocalOutputWriter()
        output = nextmv.Output(
            output_format=nextmv.OutputFormat.CSV_ARCHIVE,
        )

        file_name = "a_file_should_not_be_specified.json"
        with open(file_name, "w") as file:
            file.write("")

        # Using a file that already exists should result in an error.
        with self.assertRaises(ValueError):
            # We patch stdout to avoid printing when executing the test.
            with patch("sys.stdout", new=StringIO()) as mock_stdout:
                output_writer.write(output, file_name, skip_stdout_reset=True)
                _ = mock_stdout.getvalue()

        os.remove(file_name)

        # However, using a file name as a directory should not result in an
        # error. It is kind of weird doing that, but to each their own.
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, file_name, skip_stdout_reset=True)
            _ = mock_stdout.getvalue()

        # Removes the output directory after the test is executed.
        shutil.rmtree(file_name)

    def test_local_writer_csvarchive_dir_overwrite(self):
        output_dir = "empanadas_are_morally_superior_than_pizza"
        os.makedirs(output_dir, exist_ok=True)

        output_writer = nextmv.LocalOutputWriter()
        output = nextmv.Output(
            output_format=nextmv.OutputFormat.CSV_ARCHIVE,
        )

        # We patch stdout to avoid printing when executing the test.
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, output_dir, skip_stdout_reset=True)
            _ = mock_stdout.getvalue()

        self.assertTrue(os.path.exists(output_dir))

        # Removes the output directory after the test is executed.
        shutil.rmtree(output_dir)

    def _test_local_writer_csvarchive(
        self,
        write_path: str,
        function_path: Optional[str] = None,
    ) -> None:
        """Auxiliary function that is used to test the flow of a CSV archive
        output output writer but with different directories."""

        options = nextmv.Options()
        options.duration = 5
        options.solver = "highs"

        solution = {
            "empanadas": [
                {"are": 2.0, "life": 3.0},
                {"are": 5.0, "life": 6.0},
            ],
        }

        output = nextmv.Output(
            options=options,
            output_format=nextmv.OutputFormat.CSV_ARCHIVE,
            solution=solution,
            statistics={"foo": "bar"},
            csv_configurations={"quoting": csv.QUOTE_NONNUMERIC},
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, path=function_path, skip_stdout_reset=True)

            stdout_got = json.loads(mock_stdout.getvalue())
            stdout_expected = {
                "options": {
                    "duration": 5,
                    "solver": "highs",
                },
                "statistics": {"foo": "bar"},
            }

            self.assertDictEqual(stdout_got, stdout_expected)

        with open(f"{write_path}/empanadas.csv") as file:
            csv_got = file.read()

        csv_expected = '"are","life"\n2.0,3.0\n5.0,6.0\n'

        self.assertEqual(csv_got, csv_expected)

        self.assertTrue(os.path.exists(write_path))

        # Removes the output directory after the test is executed.
        shutil.rmtree(write_path)

    def test_local_write_bad_output_type(self):
        output = "I am clearly not an output object."
        with self.assertRaises(TypeError):
            nextmv.write_local(output)
