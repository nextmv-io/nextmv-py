import csv
import json
import os
import shutil
import unittest
from io import StringIO
from typing import Any, Optional
from unittest.mock import patch

import pandas as pd
from nextmv.base_model import BaseModel

import nextmv


class TestOutput(unittest.TestCase):
    """Tests for the various classes for writing an output."""

    def test_post_init_validation(self):
        """Test the validation in __post_init__ for different scenarios."""

        # Test with None solution - should not raise any errors
        output = nextmv.Output()
        self.assertIsNone(output.solution)

        # Test valid JSON serializable object
        output = nextmv.Output(solution={"test": 123})
        self.assertEqual(output.solution, {"test": 123})

        # Test JSON with non-serializable object
        with self.assertRaises(ValueError) as context:

            class NonSerializable:
                pass

            nextmv.Output(solution=NonSerializable())

        self.assertIn("which is not JSON serializable", str(context.exception))

        # Test CSV_ARCHIVE with valid dict
        output = nextmv.Output(
            output_format=nextmv.OutputFormat.CSV_ARCHIVE, solution={"file": [{"col1": 1, "col2": 2}]}
        )
        self.assertEqual(output.solution, {"file": [{"col1": 1, "col2": 2}]})

        # Test CSV_ARCHIVE with non-dict
        with self.assertRaises(ValueError) as context:
            nextmv.Output(output_format=nextmv.OutputFormat.CSV_ARCHIVE, solution=["not a dict"])

        self.assertIn("supported type is `dict`", str(context.exception))

    def test_post_init_options_copied(self):
        """Test that options are deep-copied in __post_init__."""

        options = {"duration": 10}
        output = nextmv.Output(options=options)

        # Modify the original options
        options["duration"] = 20

        # The output's options should not be affected by the modification
        self.assertEqual(output.options["duration"], 10)

    def test_to_dict(self):
        """Test the to_dict method for different cases."""

        # Test with None values for options, statistics, and assets
        output = nextmv.Output()
        expected = {
            "options": {},
            "solution": {},
            "statistics": {},
            "assets": [],
        }
        self.assertDictEqual(output.to_dict(), expected)

        # Test with Options object
        options = nextmv.Options()
        options.duration = 30
        output = nextmv.Output(options=options)
        result = output.to_dict()
        self.assertEqual(result["options"]["duration"], 30)

        # Test with dictionary options
        options_dict = {"duration": 45, "threads": 4}
        output = nextmv.Output(options=options_dict)
        result = output.to_dict()
        self.assertEqual(result["options"]["duration"], 45)
        self.assertEqual(result["options"]["threads"], 4)

        # Test with Statistics object
        run_stats = nextmv.RunStatistics(duration=10.5, iterations=100)
        statistics = nextmv.Statistics(run=run_stats)
        output = nextmv.Output(statistics=statistics)
        result = output.to_dict()
        self.assertEqual(result["statistics"]["run"]["duration"], 10.5)
        self.assertEqual(result["statistics"]["run"]["iterations"], 100)

        # Test with dictionary statistics
        stats_dict = {"custom_metric": 123.45}
        output = nextmv.Output(statistics=stats_dict)
        result = output.to_dict()
        self.assertEqual(result["statistics"]["custom_metric"], 123.45)

        # Test with list of Asset objects
        asset1 = nextmv.Asset(name="asset1", content={"data": [1, 2, 3]}, description="Test asset")
        asset2 = nextmv.Asset(
            name="asset2",
            content={"data": "value"},
        )
        output = nextmv.Output(assets=[asset1, asset2])
        result = output.to_dict()
        self.assertEqual(len(result["assets"]), 2)
        self.assertEqual(result["assets"][0]["name"], "asset1")
        self.assertEqual(result["assets"][1]["name"], "asset2")

        # Test with list of dictionary assets
        asset_dicts = [{"name": "asset3", "content": {"data": [4, 5, 6]}, "content_type": "json"}]
        output = nextmv.Output(assets=asset_dicts)
        result = output.to_dict()
        self.assertEqual(result["assets"][0]["name"], "asset3")

        # Test with CSV configurations
        csv_config = {"delimiter": ";", "quoting": csv.QUOTE_NONNUMERIC}
        output = nextmv.Output(output_format=nextmv.OutputFormat.CSV_ARCHIVE, csv_configurations=csv_config)
        result = output.to_dict()
        self.assertEqual(result["csv_configurations"]["delimiter"], ";")
        self.assertEqual(result["csv_configurations"]["quoting"], csv.QUOTE_NONNUMERIC)

        # Test with invalid options type
        with self.assertRaises(TypeError) as context:
            output = nextmv.Output(options=123)
            output.to_dict()
        self.assertIn("unsupported options type", str(context.exception))

        # Test with invalid statistics type
        with self.assertRaises(TypeError) as context:
            output = nextmv.Output(statistics=123)
            output.to_dict()
        self.assertIn("unsupported statistics type", str(context.exception))

        # Test with invalid assets type
        with self.assertRaises(TypeError) as context:
            output = nextmv.Output(assets=123)
            output.to_dict()
        self.assertIn("unsupported assets type", str(context.exception))

        # Test with invalid asset in assets list
        with self.assertRaises(TypeError) as context:
            output = nextmv.Output(assets=[123])
            output.to_dict()
        self.assertIn("unsupported asset 0, type", str(context.exception))

        # Test with complex nested structure
        options = nextmv.Options()
        options.duration = 30
        run_stats = nextmv.RunStatistics(duration=10.5, iterations=100)
        result_stats = nextmv.ResultStatistics(value=42.0)
        statistics = nextmv.Statistics(run=run_stats, result=result_stats)
        asset = nextmv.Asset(
            name="asset1",
            content={"data": [1, 2, 3]},
            visual=nextmv.Visual(visual_schema=nextmv.VisualSchema.CHARTJS, label="Test Chart"),
        )
        output = nextmv.Output(
            options=options,
            statistics=statistics,
            assets=[asset],
            solution={"value": 42},
            output_format=nextmv.OutputFormat.JSON,
            json_configurations={"indent": 4},
        )

        result = output.to_dict()
        self.assertEqual(result["options"]["duration"], 30)
        self.assertEqual(result["statistics"]["run"]["duration"], 10.5)
        self.assertEqual(result["statistics"]["result"]["value"], 42.0)
        self.assertEqual(result["assets"][0]["name"], "asset1")
        self.assertEqual(result["assets"][0]["visual"]["schema"], "chartjs")
        self.assertEqual(result["solution"]["value"], 42)

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
                "assets": [],
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
                "assets": [],
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_with_configurations(self):
        output = nextmv.Output(
            output_format=nextmv.OutputFormat.JSON,
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
            json_configurations={
                "indent": None,
                "separators": (",", ":"),
                "sort_keys": True,
            },
        )
        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            self.assertEqual(
                mock_stdout.getvalue(),
                '{"assets":[],"options":{},"solution":{"empanadas":"are_life"},"statistics":{"foo":"bar"}}\n',
            )

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
                "assets": [],
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
                "assets": [],
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
                "assets": [],
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

    def test_local_write_bad_output_type(self):
        output = "I am clearly not an output object."
        with self.assertRaises(TypeError):
            nextmv.write(output)

    def test_local_write_passthrough_output(self):
        output = {
            "i_am": "a_crazy_object",
            "with": [
                {"nested": "values"},
                {"and": "more_craziness"},
            ],
        }

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = output

            self.assertDictEqual(got, expected)

    def test_local_write_base_model(self):
        class myClass(BaseModel):
            output: dict[str, Any]

        output = {
            "i_am": "a_crazy_object",
            "with": [
                {"nested": "values"},
                {"and": "more_craziness"},
            ],
        }
        custom_class = myClass(output=output)

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(custom_class, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())

            # We test that the `write` method calls the `.to_dict()` method if
            # it detects the output type to be an instance of `BaseModel`.
            expected = {"output": output}

            self.assertDictEqual(got, expected)

    def test_local_write_empty_output(self):
        output = nextmv.Output()

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = expected = {
                "options": {},
                "solution": {},
                "statistics": {},
                "assets": [],
            }

            self.assertDictEqual(got, expected)

    def test_local_write_valid_assets_from_class(self):
        output = nextmv.Output(
            assets=[
                nextmv.Asset(
                    name="foo",
                    content={"foo": "bar"},
                    content_type="json",
                    description="A foo asset.",
                    visual=nextmv.Visual(
                        visual_schema=nextmv.VisualSchema.CHARTJS,
                        label="A chart",
                        visual_type="custom-tab",
                    ),
                ),
                nextmv.Asset(
                    name="bar",
                    content={"bar": "baz"},
                    content_type="json",
                    description="A bar asset.",
                ),
            ],
        )

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "options": {},
                "solution": {},
                "statistics": {},
                "assets": [
                    {
                        "content": {"foo": "bar"},
                        "content_type": "json",
                        "description": "A foo asset.",
                        "name": "foo",
                        "visual": {
                            "label": "A chart",
                            "schema": "chartjs",
                            "type": "custom-tab",
                        },
                    },
                    {
                        "content": {"bar": "baz"},
                        "content_type": "json",
                        "description": "A bar asset.",
                        "name": "bar",
                    },
                ],
            }

            self.assertDictEqual(got, expected)

    def test_local_write_valid_assets_from_dict(self):
        assets = [
            {
                "name": "foo",
                "content": {"foo": "bar"},
                "content_type": "json",
                "description": "A foo asset.",
                "visual": {
                    "schema": "chartjs",
                    "label": "A chart",
                    "visual_type": "custom-tab",
                },
            },
            {
                "name": "bar",
                "content": {"bar": "baz"},
                "content_type": "json",
                "description": "A bar asset.",
            },
        ]
        output = nextmv.Output(assets=assets)

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "options": {},
                "solution": {},
                "statistics": {},
                "assets": assets,
            }

            self.assertDictEqual(got, expected)

    def test_visual_from_dict(self):
        visual_dict = {
            "schema": "chartjs",
            "label": "A chart",
            "type": "custom-tab",
        }

        visual = nextmv.Visual.from_dict(visual_dict)

        self.assertEqual(visual.visual_schema, nextmv.VisualSchema.CHARTJS)
        self.assertEqual(visual.label, "A chart")
        self.assertEqual(visual.visual_type, "custom-tab")

    def test_visual_from_dict_2(self):
        visual_dict = {
            "visual_schema": "chartjs",
            "label": "A chart",
            "visual_type": "custom-tab",
        }

        visual = nextmv.Visual.from_dict(visual_dict)

        self.assertEqual(visual.visual_schema, nextmv.VisualSchema.CHARTJS)
        self.assertEqual(visual.label, "A chart")
        self.assertEqual(visual.visual_type, "custom-tab")

    def test_visual_direct_instantiation(self):
        visual = nextmv.Visual(
            visual_schema=nextmv.VisualSchema.CHARTJS,
            label="A chart",
            visual_type="custom-tab",
        )

        self.assertEqual(visual.visual_schema, nextmv.VisualSchema.CHARTJS)
        self.assertEqual(visual.label, "A chart")
        self.assertEqual(visual.visual_type, "custom-tab")

    def test_visual_direct_instantiation_2(self):
        visual = nextmv.Visual(
            schema=nextmv.VisualSchema.CHARTJS,
            label="A chart",
            type="custom-tab",
        )

        self.assertEqual(visual.visual_schema, nextmv.VisualSchema.CHARTJS)
        self.assertEqual(visual.label, "A chart")
        self.assertEqual(visual.visual_type, "custom-tab")

    def test_visual_to_dict(self):
        visual = nextmv.Visual(
            visual_schema=nextmv.VisualSchema.CHARTJS,
            label="A chart",
            visual_type="custom-tab",
        )

        visual_dict = visual.to_dict()

        self.assertDictEqual(
            visual_dict,
            {
                "schema": "chartjs",
                "label": "A chart",
                "type": "custom-tab",
            },
        )

    def _test_local_writer_csvarchive(
        self,
        write_path: str,
        function_path: Optional[str] = None,
    ) -> None:
        """Auxiliary function that is used to test the flow of a CSV archive
        output output writer but with different directories."""

        options = nextmv.Options()
        options.parse()
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
                "assets": [],
            }

            self.assertDictEqual(stdout_got, stdout_expected)

        with open(f"{write_path}/empanadas.csv") as file:
            csv_got = file.read()

        csv_expected = '"are","life"\n2.0,3.0\n5.0,6.0\n'

        self.assertEqual(csv_got, csv_expected)

        self.assertTrue(os.path.exists(write_path))

        # Removes the output directory after the test is executed.
        shutil.rmtree(write_path)

    def test_solution_file_creation(self):
        """Test creating SolutionFile instances directly."""

        # Test basic SolutionFile creation
        def simple_writer(file_path: str, data: Any) -> None:
            with open(file_path, "w") as f:
                f.write(str(data))

        solution_file = nextmv.SolutionFile(name="test.txt", data="test data", writer=simple_writer)

        self.assertEqual(solution_file.name, "test.txt")
        self.assertEqual(solution_file.data, "test data")
        self.assertIsNotNone(solution_file.writer)
        self.assertIsNone(solution_file.writer_args)
        self.assertIsNone(solution_file.writer_kwargs)

    def test_solution_file_with_args_kwargs(self):
        """Test SolutionFile with writer arguments and keyword arguments."""

        def writer_with_args(file_path: str, data: Any, *args, **kwargs) -> None:
            with open(file_path, "w") as f:
                f.write(f"{data}-{args}-{kwargs}")

        solution_file = nextmv.SolutionFile(
            name="test.txt",
            data="test data",
            writer=writer_with_args,
            writer_args=["arg1", "arg2"],
            writer_kwargs={"key1": "value1"},
        )

        self.assertEqual(solution_file.writer_args, ["arg1", "arg2"])
        self.assertEqual(solution_file.writer_kwargs, {"key1": "value1"})

    def test_json_solution_file(self):
        """Test json_solution_file convenience function."""

        # Test basic JSON solution file
        data = {"id": 1, "name": "test", "values": [1, 2, 3]}
        solution_file = nextmv.json_solution_file(name="test", data=data)

        self.assertEqual(solution_file.name, "test.json")
        self.assertEqual(solution_file.data, data)
        self.assertIsNotNone(solution_file.writer)

        # Test with .json extension already included
        solution_file = nextmv.json_solution_file(name="test.json", data=data)
        self.assertEqual(solution_file.name, "test.json")

        # Test with JSON configurations
        solution_file = nextmv.json_solution_file(
            name="test", data=data, json_configurations={"indent": 2, "sort_keys": True}
        )
        self.assertEqual(solution_file.name, "test.json")

    def test_csv_solution_file(self):
        """Test csv_solution_file convenience function."""

        # Test basic CSV solution file
        data = [{"id": 1, "name": "Alice", "score": 95}, {"id": 2, "name": "Bob", "score": 87}]
        solution_file = nextmv.csv_solution_file(name="test", data=data)

        self.assertEqual(solution_file.name, "test.csv")
        self.assertEqual(solution_file.data, data)
        self.assertIsNotNone(solution_file.writer)

        # Test with .csv extension already included
        solution_file = nextmv.csv_solution_file(name="test.csv", data=data)
        self.assertEqual(solution_file.name, "test.csv")

        # Test with CSV configurations
        solution_file = nextmv.csv_solution_file(
            name="test", data=data, csv_configurations={"delimiter": ";", "quoting": csv.QUOTE_ALL}
        )
        self.assertEqual(solution_file.name, "test.csv")

    def test_text_solution_file(self):
        """Test text_solution_file convenience function."""

        # Test basic text solution file
        data = "This is a test solution\nwith multiple lines"
        solution_file = nextmv.text_solution_file(name="test.txt", data=data)

        self.assertEqual(solution_file.name, "test.txt")
        self.assertEqual(solution_file.data, data)
        self.assertIsNotNone(solution_file.writer)

    def test_excel_solution_file(self):
        """Test creating custom SolutionFile for Excel files using pandas."""

        # Test Excel solution file (similar to main.py example)
        data = [{"id": 1, "name": "Alice", "score": 95}, {"id": 2, "name": "Bob", "score": 87}]

        solution_file = nextmv.SolutionFile(
            name="test.xlsx",
            data=data,
            writer=lambda file_path, write_data: pd.DataFrame(write_data).to_excel(file_path, index=False),
        )

        self.assertEqual(solution_file.name, "test.xlsx")
        self.assertEqual(solution_file.data, data)
        self.assertIsNotNone(solution_file.writer)

    def test_output_with_solution_files_validation(self):
        """Test Output validation for solution_files."""

        # Test that solution_files requires MULTI_FILE format
        sol_file = nextmv.json_solution_file("test", {"data": "value"})

        # Should raise error when using solution_files with non-MULTI_FILE format
        with self.assertRaises(ValueError) as context:
            nextmv.Output(output_format=nextmv.OutputFormat.JSON, solution_files=[sol_file])
        self.assertIn(
            "solution_files` are not `None`, but `output_format` is different from `OutputFormat.MULTI_FILE`",
            str(context.exception),
        )

        # Should work with MULTI_FILE format
        output = nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file])
        self.assertEqual(len(output.solution_files), 1)
        self.assertEqual(output.solution_files[0].name, "test.json")

        # Test invalid solution_files type
        with self.assertRaises(TypeError) as context:
            nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files="not a list")
        self.assertIn("unsupported Output.solution_files type", str(context.exception))

    def test_local_writer_multi_file_json(self):
        """Test LocalOutputWriter with MULTI_FILE format and JSON solution files."""

        # Create test directory
        test_dir = "test_output_multi_file_json"

        # Clean up any existing test directory
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            data = {"id": 1, "name": "test", "values": [1, 2, 3]}
            sol_file = nextmv.json_solution_file("solution", data)

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE,
                solution_files=[sol_file],
                statistics={"total_items": 3},
                options={"duration": 5},
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify directory structure
            self.assertTrue(os.path.exists(test_dir))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions")))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions", "solution.json")))

            # Verify solution file content
            with open(os.path.join(test_dir, "solutions", "solution.json")) as f:
                written_data = json.loads(f.read())
                self.assertEqual(written_data, data)

        finally:
            # Clean up
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_csv(self):
        """Test LocalOutputWriter with MULTI_FILE format and CSV solution files."""

        test_dir = "test_output_multi_file_csv"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            data = [{"id": 1, "name": "Alice", "score": 95}, {"id": 2, "name": "Bob", "score": 87}]
            sol_file = nextmv.csv_solution_file("results", data)

            output = nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file])

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify file exists
            csv_path = os.path.join(test_dir, "solutions", "results.csv")
            self.assertTrue(os.path.exists(csv_path))

            # Verify CSV content
            with open(csv_path, newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 2)
                self.assertEqual(rows[0]["id"], "1")
                self.assertEqual(rows[0]["name"], "Alice")
                self.assertEqual(rows[1]["name"], "Bob")

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_text(self):
        """Test LocalOutputWriter with MULTI_FILE format and text solution files."""

        test_dir = "test_output_multi_file_text"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            data = "This is a test solution\nwith multiple lines\nof text data"
            sol_file = nextmv.text_solution_file("log.txt", data)

            output = nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file])

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify file exists
            text_path = os.path.join(test_dir, "solutions", "log.txt")
            self.assertTrue(os.path.exists(text_path))

            # Verify text content
            with open(text_path) as f:
                content = f.read().strip()  # strip to remove the newline added by writer
                self.assertEqual(content, data)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_excel(self):
        """Test LocalOutputWriter with MULTI_FILE format and Excel solution files."""

        test_dir = "test_output_multi_file_excel"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            data = [{"id": 1, "name": "Alice", "score": 95}, {"id": 2, "name": "Bob", "score": 87}]

            sol_file = nextmv.SolutionFile(
                name="data.xlsx",
                data=data,
                writer=lambda file_path, write_data: pd.DataFrame(write_data).to_excel(file_path, index=False),
            )

            output = nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file])

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify file exists
            excel_path = os.path.join(test_dir, "solutions", "data.xlsx")
            self.assertTrue(os.path.exists(excel_path))

            # Verify Excel content
            df = pd.read_excel(excel_path)
            self.assertEqual(len(df), 2)
            self.assertEqual(df.iloc[0]["name"], "Alice")
            self.assertEqual(df.iloc[1]["name"], "Bob")

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_multiple_solution_files(self):
        """Test LocalOutputWriter with multiple solution files of different types."""

        test_dir = "test_output_multi_file_multiple"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create different types of solution files
            json_data = {"summary": "test results", "count": 2}
            csv_data = [{"id": 1, "value": 100}, {"id": 2, "value": 200}]
            text_data = "Log: Process completed successfully"

            sol_files = [
                nextmv.json_solution_file("summary", json_data),
                nextmv.csv_solution_file("data", csv_data),
                nextmv.text_solution_file("log.txt", text_data),
            ]

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=sol_files, statistics={"files_created": 3}
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify all files exist
            solutions_dir = os.path.join(test_dir, "solutions")
            self.assertTrue(os.path.exists(os.path.join(solutions_dir, "summary.json")))
            self.assertTrue(os.path.exists(os.path.join(solutions_dir, "data.csv")))
            self.assertTrue(os.path.exists(os.path.join(solutions_dir, "log.txt")))

            # Verify content of each file
            with open(os.path.join(solutions_dir, "summary.json")) as f:
                json_content = json.loads(f.read())
                self.assertEqual(json_content, json_data)

            with open(os.path.join(solutions_dir, "data.csv"), newline="") as f:
                reader = csv.DictReader(f)
                csv_content = list(reader)
                self.assertEqual(len(csv_content), 2)
                self.assertEqual(csv_content[0]["id"], "1")

            with open(os.path.join(solutions_dir, "log.txt")) as f:
                text_content = f.read().strip()
                self.assertEqual(text_content, text_data)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_solution_file_writer_error_handling(self):
        """Test error handling in solution file writing."""

        test_dir = "test_output_error_handling"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Test with invalid solution file type
            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=["not a SolutionFile object"]
            )

            output_writer = nextmv.LocalOutputWriter()

            with self.assertRaises(TypeError) as context:
                output_writer.write(output, path=test_dir)

            self.assertIn("unsupported solution_file type", str(context.exception))

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_statistics(self):
        """Test LocalOutputWriter with MULTI_FILE format writes statistics to statistics/statistics.json."""

        test_dir = "test_output_multi_file_statistics"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create basic solution file
            sol_file = nextmv.json_solution_file("solution", {"result": "success"})

            # Create statistics
            run_stats = nextmv.RunStatistics(duration=15.5, iterations=100)
            result_stats = nextmv.ResultStatistics(value=42.0)
            statistics = nextmv.Statistics(run=run_stats, result=result_stats)

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file], statistics=statistics
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify statistics file exists
            stats_path = os.path.join(test_dir, "statistics", "statistics.json")
            self.assertTrue(os.path.exists(stats_path))

            # Verify statistics content
            with open(stats_path) as f:
                stats_content = json.loads(f.read())
                self.assertEqual(stats_content["statistics"]["run"]["duration"], 15.5)
                self.assertEqual(stats_content["statistics"]["run"]["iterations"], 100)
                self.assertEqual(stats_content["statistics"]["result"]["value"], 42.0)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_statistics_dict(self):
        """Test LocalOutputWriter with MULTI_FILE format writes dictionary statistics to statistics/statistics.json."""

        test_dir = "test_output_multi_file_statistics_dict"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create basic solution file
            sol_file = nextmv.text_solution_file("log.txt", "Process completed")

            # Create dictionary statistics
            statistics = {"custom_metric": 123.45, "total_processed": 1000, "success_rate": 0.95}

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file], statistics=statistics
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify statistics file exists
            stats_path = os.path.join(test_dir, "statistics", "statistics.json")
            self.assertTrue(os.path.exists(stats_path))

            # Verify statistics content
            with open(stats_path) as f:
                stats_content = json.loads(f.read())
                self.assertEqual(stats_content["statistics"]["custom_metric"], 123.45)
                self.assertEqual(stats_content["statistics"]["total_processed"], 1000)
                self.assertEqual(stats_content["statistics"]["success_rate"], 0.95)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_assets(self):
        """Test LocalOutputWriter with MULTI_FILE format writes assets to assets/assets.json."""

        test_dir = "test_output_multi_file_assets"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create basic solution file
            sol_file = nextmv.csv_solution_file("data", [{"id": 1, "value": "test"}])

            # Create assets
            assets = [
                nextmv.Asset(
                    name="chart_data",
                    content={"type": "bar", "data": [1, 2, 3, 4, 5]},
                    content_type="json",
                    description="Chart visualization data",
                    visual=nextmv.Visual(
                        visual_schema=nextmv.VisualSchema.CHARTJS, label="Performance Chart", visual_type="chart"
                    ),
                ),
                nextmv.Asset(
                    name="summary_table",
                    content={"headers": ["Metric", "Value"], "rows": [["Total", 100], ["Success", 95]]},
                    content_type="json",
                    description="Summary table data",
                ),
            ]

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file], assets=assets
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify assets file exists
            assets_path = os.path.join(test_dir, "assets", "assets.json")
            self.assertTrue(os.path.exists(assets_path))

            # Verify assets content
            with open(assets_path) as f:
                assets_content = json.loads(f.read())
                self.assertEqual(len(assets_content["assets"]), 2)

                # Check first asset
                asset1 = assets_content["assets"][0]
                self.assertEqual(asset1["name"], "chart_data")
                self.assertEqual(asset1["content"]["type"], "bar")
                self.assertEqual(asset1["description"], "Chart visualization data")
                self.assertEqual(asset1["visual"]["schema"], "chartjs")
                self.assertEqual(asset1["visual"]["label"], "Performance Chart")

                # Check second asset
                asset2 = assets_content["assets"][1]
                self.assertEqual(asset2["name"], "summary_table")
                self.assertEqual(asset2["content"]["headers"], ["Metric", "Value"])
                self.assertNotIn("visual", asset2)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_assets_dict(self):
        """Test LocalOutputWriter with MULTI_FILE format writes dictionary assets to assets/assets.json."""

        test_dir = "test_output_multi_file_assets_dict"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create basic solution file
            sol_file = nextmv.json_solution_file("result", {"status": "complete"})

            # Create dictionary assets
            assets = [
                {
                    "name": "performance_metrics",
                    "content": {"cpu_usage": 45.2, "memory_usage": 67.8, "disk_io": 12.3},
                    "content_type": "json",
                    "description": "System performance metrics",
                },
                {
                    "name": "optimization_trace",
                    "content": {"iterations": [1, 2, 3], "objective_values": [100, 85, 70]},
                    "content_type": "json",
                    "description": "Optimization algorithm trace",
                    "visual": {"schema": "chartjs", "label": "Convergence Plot", "type": "line-chart"},
                },
            ]

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[sol_file], assets=assets
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify assets file exists
            assets_path = os.path.join(test_dir, "assets", "assets.json")
            self.assertTrue(os.path.exists(assets_path))

            # Verify assets content
            with open(assets_path) as f:
                assets_content = json.loads(f.read())
                self.assertEqual(len(assets_content["assets"]), 2)

                # Check first asset
                asset1 = assets_content["assets"][0]
                self.assertEqual(asset1["name"], "performance_metrics")
                self.assertEqual(asset1["content"]["cpu_usage"], 45.2)
                self.assertEqual(asset1["description"], "System performance metrics")

                # Check second asset with visual
                asset2 = assets_content["assets"][1]
                self.assertEqual(asset2["name"], "optimization_trace")
                self.assertEqual(asset2["visual"]["schema"], "chartjs")
                self.assertEqual(asset2["visual"]["label"], "Convergence Plot")

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_complete(self):
        """Test LocalOutputWriter with MULTI_FILE format writes solutions, statistics, and assets to
        correct directories."""

        test_dir = "test_output_multi_file_complete"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create multiple solution files
            json_data = {"optimization_result": {"objective": 150.5, "variables": {"x": 10, "y": 15}}}
            csv_data = [{"route_id": 1, "distance": 45.2, "time": 60}, {"route_id": 2, "distance": 38.7, "time": 50}]
            text_data = "Optimization completed successfully\nTotal time: 120 seconds\nFinal objective: 150.5"

            sol_files = [
                nextmv.json_solution_file("optimization_result", json_data),
                nextmv.csv_solution_file("routes", csv_data),
                nextmv.text_solution_file("summary.log", text_data),
            ]

            # Create comprehensive statistics
            run_stats = nextmv.RunStatistics(duration=120.0, iterations=500)
            result_stats = nextmv.ResultStatistics(value=150.5)
            statistics = nextmv.Statistics(run=run_stats, result=result_stats)

            # Create comprehensive assets
            assets = [
                nextmv.Asset(
                    name="route_visualization",
                    content={"routes": [{"points": [[0, 0], [10, 5], [15, 10]], "color": "blue"}]},
                    content_type="json",
                    description="Route visualization data",
                    visual=nextmv.Visual(
                        visual_schema=nextmv.VisualSchema.CHARTJS, label="Route Map", visual_type="map"
                    ),
                ),
                nextmv.Asset(
                    name="convergence_data",
                    content={
                        "iterations": list(range(1, 501)),
                        "objective_values": [200 - i * 0.1 for i in range(500)],
                    },
                    content_type="json",
                    description="Algorithm convergence data",
                ),
            ]

            # Create options
            options = nextmv.Options()
            options.duration = 120
            options.solver = "custom_optimizer"

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE,
                solution_files=sol_files,
                statistics=statistics,
                assets=assets,
                options=options,
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify directory structure
            self.assertTrue(os.path.exists(test_dir))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions")))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "statistics")))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "assets")))

            # Verify solution files
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions", "optimization_result.json")))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions", "routes.csv")))
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions", "summary.log")))

            # Verify statistics file
            stats_path = os.path.join(test_dir, "statistics", "statistics.json")
            self.assertTrue(os.path.exists(stats_path))
            with open(stats_path) as f:
                stats_content = json.loads(f.read())
                self.assertEqual(stats_content["statistics"]["run"]["duration"], 120.0)
                self.assertEqual(stats_content["statistics"]["run"]["iterations"], 500)
                self.assertEqual(stats_content["statistics"]["result"]["value"], 150.5)

            # Verify assets file
            assets_path = os.path.join(test_dir, "assets", "assets.json")
            self.assertTrue(os.path.exists(assets_path))
            with open(assets_path) as f:
                assets_content = json.loads(f.read())
                self.assertEqual(len(assets_content["assets"]), 2)
                self.assertEqual(assets_content["assets"][0]["name"], "route_visualization")
                self.assertEqual(assets_content["assets"][0]["visual"]["schema"], "chartjs")
                self.assertEqual(assets_content["assets"][1]["name"], "convergence_data")

            # Verify solution file contents
            with open(os.path.join(test_dir, "solutions", "optimization_result.json")) as f:
                json_content = json.loads(f.read())
                self.assertEqual(json_content["optimization_result"]["objective"], 150.5)

            with open(os.path.join(test_dir, "solutions", "routes.csv"), newline="") as f:
                reader = csv.DictReader(f)
                csv_content = list(reader)
                self.assertEqual(len(csv_content), 2)
                self.assertEqual(csv_content[0]["route_id"], "1")
                self.assertEqual(csv_content[0]["distance"], "45.2")

            with open(os.path.join(test_dir, "solutions", "summary.log")) as f:
                text_content = f.read().strip()
                self.assertIn("Optimization completed successfully", text_content)
                self.assertIn("Final objective: 150.5", text_content)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_local_writer_multi_file_empty_statistics_assets(self):
        """Test LocalOutputWriter with MULTI_FILE format handles empty statistics and assets correctly."""

        test_dir = "test_output_multi_file_empty"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Create basic solution file
            sol_file = nextmv.json_solution_file("basic", {"result": "test"})

            output = nextmv.Output(
                output_format=nextmv.OutputFormat.MULTI_FILE,
                solution_files=[sol_file],
                statistics={},  # Empty statistics
                assets=[],  # Empty assets
            )

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify only solutions directory exists (empty statistics and assets shouldn't create directories)
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions")))
            self.assertFalse(os.path.exists(os.path.join(test_dir, "statistics")))
            self.assertFalse(os.path.exists(os.path.join(test_dir, "assets")))

            # Verify solution file exists
            self.assertTrue(os.path.exists(os.path.join(test_dir, "solutions", "basic.json")))

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)

    def test_solution_file_configurations(self):
        """Test solution files with various configurations."""

        test_dir = "test_output_configurations"

        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        try:
            # Test JSON with specific configurations
            json_data = {"name": "test", "values": [3, 1, 2]}
            json_sol = nextmv.json_solution_file(
                "config_test", json_data, json_configurations={"indent": 4, "sort_keys": True}
            )

            # Test CSV with specific configurations
            csv_data = [{"name": "Alice", "city": "New York"}, {"name": "Bob", "city": "Los Angeles"}]
            csv_sol = nextmv.csv_solution_file(
                "config_test", csv_data, csv_configurations={"delimiter": "|", "quoting": csv.QUOTE_ALL}
            )

            output = nextmv.Output(output_format=nextmv.OutputFormat.MULTI_FILE, solution_files=[json_sol, csv_sol])

            output_writer = nextmv.LocalOutputWriter()
            output_writer.write(output, path=test_dir)

            # Verify JSON formatting
            with open(os.path.join(test_dir, "solutions", "config_test.json")) as f:
                content = f.read()
                # Should be indented and sorted
                self.assertIn("    ", content)  # Check for indentation
                # Check that keys are sorted (name comes before values)
                name_pos = content.find('"name"')
                values_pos = content.find('"values"')
                self.assertLess(name_pos, values_pos)

            # Verify CSV formatting with custom delimiter
            with open(os.path.join(test_dir, "solutions", "config_test.csv")) as f:
                content = f.read()
                self.assertIn("|", content)  # Check for custom delimiter
                self.assertIn('"Alice"', content)  # Check for quotes (QUOTE_ALL)

        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)
