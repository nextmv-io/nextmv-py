import csv
import json
import os
import shutil
import tempfile
import unittest
from io import StringIO
from typing import Any
from unittest.mock import patch

import pandas as pd
from nextmv.base_model import BaseModel
from nextmv.content_format import ContentFormat
from nextmv.manifest import (
    MANIFEST_FILE_NAME,
    Manifest,
    ManifestConfiguration,
    ManifestContent,
    ManifestContentMultiFile,
    ManifestContentMultiFileInput,
    ManifestContentMultiFileOutput,
    ManifestOption,
    ManifestOptions,
    ManifestRuntime,
    ManifestType,
)
from nextmv.options import Option, Options

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
            "metrics": {},
            "assets": [],
        }
        self.assertDictEqual(output.to_dict(), expected)

        # Test with with metrics but no statistics
        output = nextmv.Output(metrics={"message": "hello world"})
        expected = {
            "options": {},
            "solution": {},
            "metrics": {"message": "hello world"},
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

        # Test with metrics object
        metrics = {"custom_metric": 678.90}
        output = nextmv.Output(metrics=metrics)
        result = output.to_dict()
        self.assertEqual(result["metrics"]["custom_metric"], 678.90)

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

        # Test with invalid metrics type
        with self.assertRaises(TypeError) as context:
            output = nextmv.Output(metrics=123)
            output.to_dict()
        self.assertIn("unsupported metrics type", str(context.exception))

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
            metrics={"custom_metric": {"value": 99.9}},
            assets=[asset],
            solution={"value": 42},
            output_format=nextmv.ContentFormat.JSON,
            json_configurations={"indent": 4},
        )

        result = output.to_dict()
        self.assertEqual(result["options"]["duration"], 30)
        self.assertEqual(result["statistics"]["run"]["duration"], 10.5)
        self.assertEqual(result["statistics"]["result"]["value"], 42.0)
        self.assertEqual(result["metrics"]["custom_metric"]["value"], 99.9)
        self.assertEqual(result["assets"][0]["name"], "asset1")
        self.assertEqual(result["assets"][0]["visual"]["schema"], "chartjs")
        self.assertEqual(result["solution"]["value"], 42)

        # Test with complex nested structure - metrics only
        options = nextmv.Options()
        options.duration = 30
        asset = nextmv.Asset(
            name="asset1",
            content={"data": [1, 2, 3]},
            visual=nextmv.Visual(visual_schema=nextmv.VisualSchema.CHARTJS, label="Test Chart"),
        )
        output = nextmv.Output(
            options=options,
            metrics={"custom_metric": {"value": 99.9}},
            assets=[asset],
            solution={"value": 42},
            output_format=nextmv.ContentFormat.JSON,
            json_configurations={"indent": 4},
        )

        result = output.to_dict()
        self.assertEqual(result["options"]["duration"], 30)
        self.assertEqual(result["metrics"]["custom_metric"]["value"], 99.9)
        self.assertEqual(result["assets"][0]["name"], "asset1")
        self.assertEqual(result["assets"][0]["visual"]["schema"], "chartjs")
        self.assertEqual(result["solution"]["value"], 42)

    def test_local_writer_json_stdout_default(self):
        output = nextmv.Output(
            solution={"empanadas": "are_life"},
            statistics={"foo": "bar"},
            metrics={"message": "hello world"},
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
                "metrics": {"message": "hello world"},
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
                "assets": [],
                "metrics": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout(self):
        output = nextmv.Output(
            output_format=nextmv.ContentFormat.JSON,
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
                "metrics": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_with_configurations(self):
        output = nextmv.Output(
            output_format=nextmv.ContentFormat.JSON,
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
                '{"assets":[],"metrics":{},"options":{},"solution":{"empanadas":"are_life"},"statistics":{"foo":"bar"}}\n',
            )

    def test_local_writer_json_stdout_with_options(self):
        options = nextmv.Options()
        options.duration = 5
        options.solver = "highs"

        output = nextmv.Output(
            options=options,
            output_format=nextmv.ContentFormat.JSON,
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
                "metrics": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_writer_json_stdout_with_options_json(self):
        output = nextmv.Output(
            options={"duration": 5, "solver": "highs"},
            output_format=nextmv.ContentFormat.JSON,
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
                "metrics": {},
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
                "metrics": {},
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
            expected = {
                "options": {},
                "solution": {},
                "assets": [],
                "metrics": {},
            }

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

            # The writer extracts known Output fields from the BaseModel's dict;
            # custom fields are not preserved in the envelope.
            expected = {
                "options": {},
                "solution": {},
                "assets": [],
                "metrics": {},
            }

            self.assertDictEqual(got, expected)

    def test_local_write_empty_output(self):
        output = nextmv.Output()

        output_writer = nextmv.LocalOutputWriter()

        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            output_writer.write(output, skip_stdout_reset=True)

            got = json.loads(mock_stdout.getvalue())
            expected = {
                "options": {},
                "solution": {},
                "assets": [],
                "metrics": {},
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
                "metrics": {},
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
                "assets": assets,
                "metrics": {},
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
        function_path: str | None = None,
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
                "metrics": {},
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
            nextmv.Output(output_format=nextmv.ContentFormat.JSON, solution_files=[sol_file])
        self.assertIn(
            "solution_files` are not `None`, but `output_format` is different from `ContentFormat.MULTI_FILE`",
            str(context.exception),
        )

        # Should work with MULTI_FILE format
        output = nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file])
        self.assertEqual(len(output.solution_files), 1)
        self.assertEqual(output.solution_files[0].name, "test.json")

        # Test invalid solution_files type
        with self.assertRaises(TypeError) as context:
            nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files="not a list")
        self.assertIn("unsupported `Output.solution_files` type", str(context.exception))

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
                output_format=nextmv.ContentFormat.MULTI_FILE,
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

            output = nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file])

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

            output = nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file])

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

            output = nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file])

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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=sol_files, statistics={"files_created": 3}
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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=["not a SolutionFile object"]
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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file], statistics=statistics
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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file], statistics=statistics
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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file], assets=assets
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
                output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[sol_file], assets=assets
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
                output_format=nextmv.ContentFormat.MULTI_FILE,
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
                output_format=nextmv.ContentFormat.MULTI_FILE,
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

            output = nextmv.Output(output_format=nextmv.ContentFormat.MULTI_FILE, solution_files=[json_sol, csv_sol])

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


# ---------------------------------------------------------------------------
# Helpers shared by manifest-based write tests
# ---------------------------------------------------------------------------


def _make_json_manifest(
    options_items: list[dict[str, Any]] | None = None,
) -> Manifest:
    """Build a Manifest that uses ContentFormat.JSON, optionally with options."""
    cfg_kwargs: dict[str, Any] = {
        "content": ManifestContent(format=ContentFormat.JSON),
    }
    if options_items:
        cfg_kwargs["options"] = ManifestOptions(
            items=[
                ManifestOption(
                    name=o["name"],
                    option_type=o["option_type"],
                    default=o.get("default"),
                    required=o.get("required", False),
                )
                for o in options_items
            ]
        )
    return Manifest(
        files=["main.py"],
        runtime=ManifestRuntime.PYTHON,
        type=ManifestType.PYTHON,
        configuration=ManifestConfiguration(**cfg_kwargs),
    )


def _make_multi_file_manifest(
    input_path: str = "inputs/",
    solutions_path: str = "outputs/solutions/",
    metrics_path: str = "outputs/metrics/metrics.json",
    assets_path: str = "outputs/assets/assets.json",
    statistics_path: str = "outputs/statistics/statistics.json",
) -> Manifest:
    """Build a Manifest that uses ContentFormat.MULTI_FILE with configurable paths."""
    return Manifest(
        files=["main.py"],
        runtime=ManifestRuntime.PYTHON,
        type=ManifestType.PYTHON,
        configuration=ManifestConfiguration(
            content=ManifestContent(
                format=ContentFormat.MULTI_FILE,
                multi_file=ManifestContentMultiFile(
                    input=ManifestContentMultiFileInput(path=input_path),
                    output=ManifestContentMultiFileOutput(
                        solutions=solutions_path,
                        metrics=metrics_path,
                        assets=assets_path,
                        statistics=statistics_path,
                    ),
                ),
            )
        ),
    )


def _write_app_yaml(dirpath: str, manifest: Manifest) -> None:
    """Serialize a Manifest to app.yaml inside dirpath."""
    manifest.to_yaml(dirpath)


# ---------------------------------------------------------------------------
# Tests: write() – manifest resolution
# ---------------------------------------------------------------------------


class TestWriteNoManifest(unittest.TestCase):
    """write() behaviour when no manifest is available at all."""

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_json_to_stdout_default(self):
        """No manifest, Output with JSON → writes to stdout."""
        output = nextmv.Output(solution={"answer": 42})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"], {"answer": 42})

    def test_json_to_file(self):
        """No manifest, explicit path → writes JSON to file."""
        output = nextmv.Output(solution={"saved": True})
        fpath = os.path.join(self.tmp_dir, "out.json")
        nextmv.write(output, path=fpath)

        with open(fpath) as f:
            got = json.load(f)
        self.assertEqual(got["solution"], {"saved": True})

    def test_json_no_options_empty_dict_in_output(self):
        """No options → output contains empty options dict."""
        output = nextmv.Output(solution={"x": 1})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["options"], {})

    def test_multi_file_no_manifest_default_paths(self):
        """No manifest, MULTI_FILE → uses 'outputs/solutions' default path."""
        sol_file = nextmv.json_solution_file("result", {"val": 7})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )

        output_dir = os.path.join(self.tmp_dir, "outputs", "solutions")
        nextmv.write(output)

        self.assertTrue(os.path.exists(os.path.join(output_dir, "result.json")))
        with open(os.path.join(output_dir, "result.json")) as f:
            self.assertEqual(json.load(f), {"val": 7})

        shutil.rmtree(os.path.join(self.tmp_dir, "outputs"), ignore_errors=True)

    def test_multi_file_no_manifest_metrics_default_paths(self):
        """No manifest, MULTI_FILE → metrics go to 'outputs/metrics/metrics.json'."""
        sol_file = nextmv.json_solution_file("result", {"val": 1})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
            metrics={"elapsed": 1.5},
        )

        nextmv.write(output)

        metrics_path = os.path.join(self.tmp_dir, "outputs", "metrics", "metrics.json")
        self.assertTrue(os.path.exists(metrics_path))
        with open(metrics_path) as f:
            content = json.load(f)
        self.assertEqual(content["metrics"]["elapsed"], 1.5)

        shutil.rmtree(os.path.join(self.tmp_dir, "outputs"), ignore_errors=True)


# ---------------------------------------------------------------------------


class TestWriteManifestProvidedDirectly(unittest.TestCase):
    """write() behaviour when a Manifest is supplied as the `manifest` argument."""

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # JSON format from manifest
    # ------------------------------------------------------------------

    def test_json_format_from_manifest_to_stdout(self):
        """Manifest with JSON format → output is written as JSON to stdout."""
        manifest = _make_json_manifest()
        output = nextmv.Output(solution={"qty": 10})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, manifest=manifest, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["qty"], 10)

    def test_json_format_from_manifest_to_file(self):
        """Manifest with JSON format and explicit path → writes to file."""
        manifest = _make_json_manifest()
        output = nextmv.Output(solution={"file_written": True})
        fpath = os.path.join(self.tmp_dir, "manifest_out.json")

        nextmv.write(output, path=fpath, manifest=manifest)

        with open(fpath) as f:
            got = json.load(f)
        self.assertEqual(got["solution"]["file_written"], True)

    def test_json_manifest_with_metrics(self):
        """Manifest JSON format: metrics are included in output."""
        manifest = _make_json_manifest()
        output = nextmv.Output(solution={"x": 1}, metrics={"speed": 2.5})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, manifest=manifest, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["metrics"]["speed"], 2.5)

    # ------------------------------------------------------------------
    # MULTI_FILE format from manifest
    # ------------------------------------------------------------------

    def test_multi_file_format_from_manifest(self):
        """Manifest with MULTI_FILE: content format is used for writing."""
        sol_dir = os.path.join(self.tmp_dir, "m_solutions")
        metrics_path = os.path.join(self.tmp_dir, "m_metrics", "metrics.json")
        assets_path = os.path.join(self.tmp_dir, "m_assets", "assets.json")
        stats_path = os.path.join(self.tmp_dir, "m_stats", "stats.json")

        manifest = _make_multi_file_manifest(
            input_path=os.path.join(self.tmp_dir, "inputs"),
            solutions_path=sol_dir,
            metrics_path=metrics_path,
            assets_path=assets_path,
            statistics_path=stats_path,
        )

        sol_file = nextmv.json_solution_file("plan", {"route": [1, 2, 3]})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )

        nextmv.write(output, manifest=manifest)

        plan_path = os.path.join(sol_dir, "plan.json")
        self.assertTrue(os.path.exists(plan_path))
        with open(plan_path) as f:
            self.assertEqual(json.load(f), {"route": [1, 2, 3]})

    def test_multi_file_manifest_custom_metrics_path(self):
        """Manifest specifies a custom metrics path; metrics end up there."""
        custom_metrics = os.path.join(self.tmp_dir, "custom_metrics.json")
        manifest = _make_multi_file_manifest(
            solutions_path=os.path.join(self.tmp_dir, "sols"),
            metrics_path=custom_metrics,
            assets_path=os.path.join(self.tmp_dir, "assets.json"),
            statistics_path=os.path.join(self.tmp_dir, "stats.json"),
        )

        sol_file = nextmv.json_solution_file("sol", {"ok": True})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
            metrics={"latency": 0.42},
        )

        nextmv.write(output, manifest=manifest)

        self.assertTrue(os.path.exists(custom_metrics))
        with open(custom_metrics) as f:
            content = json.load(f)
        self.assertEqual(content["metrics"]["latency"], 0.42)

    def test_multi_file_explicit_path_overrides_manifest_paths(self):
        """Explicit path overrides the multi-file paths from the manifest."""
        manifest = _make_multi_file_manifest(
            solutions_path="manifest_solutions/",
            metrics_path="manifest_metrics/metrics.json",
            assets_path="manifest_assets/assets.json",
            statistics_path="manifest_stats/stats.json",
        )

        explicit_out = os.path.join(self.tmp_dir, "explicit_output")
        sol_file = nextmv.json_solution_file("data", {"n": 5})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )

        nextmv.write(output, path=explicit_out, manifest=manifest)

        # Must be under explicit_output/solutions/
        expected = os.path.join(explicit_out, "solutions", "data.json")
        self.assertTrue(os.path.exists(expected))
        # Must NOT be under manifest_solutions/
        self.assertFalse(os.path.exists("manifest_solutions"))


# ---------------------------------------------------------------------------


class TestWriteManifestFromCwd(unittest.TestCase):
    """write() behaviour when app.yaml is found in the current working directory."""

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_json_format_from_cwd_manifest(self):
        """app.yaml with JSON format in cwd is detected and used."""
        manifest = _make_json_manifest()
        _write_app_yaml(self.tmp_dir, manifest)

        output = nextmv.Output(solution={"cwd": True})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["cwd"], True)

    def test_multi_file_format_from_cwd_manifest(self):
        """app.yaml with MULTI_FILE in cwd: output goes to manifest-specified paths."""
        sol_dir = os.path.join(self.tmp_dir, "cwd_solutions")
        metrics_file = os.path.join(self.tmp_dir, "cwd_metrics.json")
        assets_file = os.path.join(self.tmp_dir, "cwd_assets.json")
        stats_file = os.path.join(self.tmp_dir, "cwd_stats.json")

        manifest = _make_multi_file_manifest(
            solutions_path=sol_dir,
            metrics_path=metrics_file,
            assets_path=assets_file,
            statistics_path=stats_file,
        )
        _write_app_yaml(self.tmp_dir, manifest)

        sol_file = nextmv.json_solution_file("output", {"cwd_mf": 1})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )
        nextmv.write(output)

        self.assertTrue(os.path.exists(os.path.join(sol_dir, "output.json")))

    def test_no_app_yaml_in_cwd_defaults_to_json_stdout(self):
        """No app.yaml in cwd → defaults to JSON to stdout."""
        self.assertFalse(os.path.exists(MANIFEST_FILE_NAME))

        output = nextmv.Output(solution={"default": 1})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["default"], 1)


# ---------------------------------------------------------------------------


class TestWriteResolutionPriority(unittest.TestCase):
    """
    Priority order for write():
    explicit kwarg > manifest > Output field > default
    """

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ------------------------------------------------------------------
    # content_format resolution
    # ------------------------------------------------------------------

    def test_explicit_content_format_overrides_manifest(self):
        """Explicit content_format kwarg beats manifest format."""
        # Manifest says MULTI_FILE; explicit says JSON.
        manifest = _make_multi_file_manifest()
        output = nextmv.Output(solution={"override": True})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(
                output,
                content_format=ContentFormat.JSON,
                manifest=manifest,
                skip_stdout_reset=True,
            )
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["override"], True)

    def test_explicit_content_format_overrides_output_format(self):
        """Explicit content_format kwarg beats Output.output_format."""
        # Output says MULTI_FILE; explicit says JSON.
        sol_file = nextmv.json_solution_file("x", {"v": 1})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
            solution=None,
        )

        # Providing a plain solution with the JSON override.
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(
                output,
                content_format=ContentFormat.JSON,
                solution={"forced_json": True},
                skip_stdout_reset=True,
            )
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["forced_json"], True)

    def test_manifest_format_overrides_output_format(self):
        """Manifest format overrides the format set on the Output object."""
        # Manifest says JSON; Output says MULTI_FILE → JSON wins.
        sol_file = nextmv.json_solution_file("x", {"v": 1})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )
        manifest = _make_json_manifest()

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(
                output,
                manifest=manifest,
                solution={"manifest_json": True},
                skip_stdout_reset=True,
            )
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["manifest_json"], True)

    def test_content_format_from_output_object_when_no_manifest(self):
        """No manifest: content_format comes from Output.output_format."""
        sol_file = nextmv.json_solution_file("widget", {"count": 3})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sol_file],
        )
        out_dir = os.path.join(self.tmp_dir, "from_output")
        nextmv.write(output, path=out_dir)

        self.assertTrue(os.path.exists(os.path.join(out_dir, "solutions", "widget.json")))

    def test_dict_output_defaults_to_json_format(self):
        """A plain dict as output defaults to JSON."""
        output = {"solution": {"plain": "dict"}}

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertIn("solution", got)

    # ------------------------------------------------------------------
    # options resolution
    # ------------------------------------------------------------------

    def test_explicit_options_override_output_options(self):
        """Explicit options kwarg overrides Output.options."""
        output = nextmv.Output(
            options={"duration": 10},
            solution={"v": 1},
        )
        override_opts = {"duration": 999, "solver": "custom"}

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, options=override_opts, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["options"]["duration"], 999)
        self.assertEqual(got["options"]["solver"], "custom")

    def test_explicit_options_object_override_output_options(self):
        """Explicit Options instance overrides Output.options dict."""
        output = nextmv.Output(options={"duration": 10}, solution={"v": 1})

        opts = Options(Option("duration", int, default=777, required=False))
        with patch("sys.argv", ["prog"]):
            opts.parse()

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, options=opts, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["options"]["duration"], 777)

    def test_output_options_used_when_no_explicit_options(self):
        """Output.options used when no explicit options are passed."""
        output = nextmv.Output(options={"threads": 4}, solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["options"]["threads"], 4)

    # ------------------------------------------------------------------
    # metrics resolution
    # ------------------------------------------------------------------

    def test_explicit_metrics_override_output_metrics(self):
        """Explicit metrics kwarg overrides Output.metrics."""
        output = nextmv.Output(metrics={"elapsed": 1.0}, solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, metrics={"elapsed": 99.9}, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["metrics"]["elapsed"], 99.9)

    def test_output_metrics_used_when_no_explicit_metrics(self):
        """Output.metrics used when no explicit metrics are passed."""
        output = nextmv.Output(metrics={"score": 42.0}, solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["metrics"]["score"], 42.0)

    # ------------------------------------------------------------------
    # assets resolution
    # ------------------------------------------------------------------

    def test_explicit_assets_override_output_assets(self):
        """Explicit assets kwarg overrides Output.assets."""
        output_asset = nextmv.Asset(name="original", content={"original": True})
        override_asset = nextmv.Asset(name="override", content={"override": True})

        output = nextmv.Output(assets=[output_asset], solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, assets=[override_asset], skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(len(got["assets"]), 1)
        self.assertEqual(got["assets"][0]["name"], "override")

    def test_output_assets_used_when_no_explicit_assets(self):
        """Output.assets used when no explicit assets are passed."""
        asset = nextmv.Asset(name="chart", content={"data": [1, 2, 3]})
        output = nextmv.Output(assets=[asset], solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(len(got["assets"]), 1)
        self.assertEqual(got["assets"][0]["name"], "chart")

    def test_explicit_assets_as_dicts_override_output_assets(self):
        """Explicit assets as dicts override Output.assets."""
        output_asset = nextmv.Asset(name="original", content={"x": 1})
        override_asset_dict = {"name": "dict_asset", "content": {"y": 2}}

        output = nextmv.Output(assets=[output_asset], solution={})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, assets=[override_asset_dict], skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["assets"][0]["name"], "dict_asset")

    # ------------------------------------------------------------------
    # solution resolution
    # ------------------------------------------------------------------

    def test_explicit_solution_overrides_output_solution(self):
        """Explicit solution kwarg overrides Output.solution."""
        output = nextmv.Output(solution={"original": True})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, solution={"overridden": True}, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"], {"overridden": True})

    def test_output_solution_used_when_no_explicit_solution(self):
        """Output.solution used when no explicit solution is passed."""
        output = nextmv.Output(solution={"from_output": 123})

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["from_output"], 123)

    # ------------------------------------------------------------------
    # json_configurations resolution
    # ------------------------------------------------------------------

    def test_explicit_json_configs_override_output_configs(self):
        """Explicit json_configurations kwarg overrides Output.json_configurations."""
        output = nextmv.Output(
            solution={"z": 1},
            json_configurations={"indent": 4},
        )

        with patch("sys.stdout", new=StringIO()) as mock_out:
            # Override to compact format (no indent, custom separators, sorted keys).
            nextmv.write(
                output,
                json_configurations={"indent": None, "separators": (",", ":"), "sort_keys": True},
                skip_stdout_reset=True,
            )
            raw = mock_out.getvalue().strip()

        # Compact: no spaces after separators, keys sorted.
        self.assertNotIn("\n    ", raw)
        self.assertIn('"assets":[]', raw)

    def test_output_json_configs_used_when_no_explicit_configs(self):
        """Output.json_configurations used when no explicit configs are passed."""
        output = nextmv.Output(
            solution={"a": 1, "b": 2},
            json_configurations={"sort_keys": True, "indent": None, "separators": (",", ":")},
        )

        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(output, skip_stdout_reset=True)
            raw = mock_out.getvalue().strip()

        # Keys should be sorted, compact.
        self.assertIn('"assets":[]', raw)

    # ------------------------------------------------------------------
    # solution_files resolution
    # ------------------------------------------------------------------

    def test_explicit_solution_files_override_output_solution_files(self):
        """Explicit solution_files kwarg overrides Output.solution_files."""
        original_sf = nextmv.json_solution_file("original", {"v": 0})
        override_sf = nextmv.json_solution_file("override", {"v": 1})

        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[original_sf],
        )
        out_dir = os.path.join(self.tmp_dir, "sf_override")

        nextmv.write(
            output,
            solution_files=[override_sf],
            path=out_dir,
        )

        self.assertTrue(os.path.exists(os.path.join(out_dir, "solutions", "override.json")))
        self.assertFalse(os.path.exists(os.path.join(out_dir, "solutions", "original.json")))

    def test_output_solution_files_used_when_no_explicit(self):
        """Output.solution_files used when no explicit solution_files are passed."""
        sf = nextmv.json_solution_file("from_output", {"source": "output"})
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sf],
        )
        out_dir = os.path.join(self.tmp_dir, "sf_from_output")

        nextmv.write(output, path=out_dir)

        self.assertTrue(os.path.exists(os.path.join(out_dir, "solutions", "from_output.json")))


# ---------------------------------------------------------------------------


class TestWriteStandaloneArguments(unittest.TestCase):
    """write() with standalone kwargs and no Output object (output=None)."""

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_json_standalone_solution(self):
        """write with only solution kwarg, no Output object → JSON to stdout."""
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(solution={"standalone": True}, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["standalone"], True)

    def test_json_standalone_metrics(self):
        """write with only metrics kwarg → metrics in JSON output."""
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(metrics={"m": 3.14}, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["metrics"]["m"], 3.14)

    def test_json_standalone_assets(self):
        """write with only assets kwarg → assets appear in JSON output."""
        asset = nextmv.Asset(name="standalone_asset", content={"a": 1})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(assets=[asset], skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["assets"][0]["name"], "standalone_asset")

    def test_json_standalone_options(self):
        """write with only options kwarg → options in JSON output."""
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(options={"alpha": 0.01}, skip_stdout_reset=True)
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["options"]["alpha"], 0.01)

    def test_json_standalone_solution_and_metrics_and_assets(self):
        """Combine solution+metrics+assets as standalone kwargs."""
        asset = nextmv.Asset(name="a", content={"x": 9})
        with patch("sys.stdout", new=StringIO()) as mock_out:
            nextmv.write(
                solution={"res": 5},
                metrics={"t": 0.1},
                assets=[asset],
                skip_stdout_reset=True,
            )
            got = json.loads(mock_out.getvalue())

        self.assertEqual(got["solution"]["res"], 5)
        self.assertEqual(got["metrics"]["t"], 0.1)
        self.assertEqual(got["assets"][0]["name"], "a")

    def test_multi_file_standalone_solution_files(self):
        """write with content_format=MULTI_FILE and solution_files kwarg."""
        sf = nextmv.json_solution_file("standalone_sol", {"standalone": True})
        out_dir = os.path.join(self.tmp_dir, "standalone_out")

        nextmv.write(
            content_format=ContentFormat.MULTI_FILE,
            solution_files=[sf],
            path=out_dir,
        )

        sol_path = os.path.join(out_dir, "solutions", "standalone_sol.json")
        self.assertTrue(os.path.exists(sol_path))
        with open(sol_path) as f:
            self.assertEqual(json.load(f), {"standalone": True})

    def test_multi_file_standalone_metrics_and_assets(self):
        """write MULTI_FILE with standalone metrics and assets kwargs."""
        sf = nextmv.json_solution_file("sol", {"ok": True})
        asset = nextmv.Asset(name="vis", content={"type": "chart"})
        out_dir = os.path.join(self.tmp_dir, "standalone_mf")

        nextmv.write(
            content_format=ContentFormat.MULTI_FILE,
            solution_files=[sf],
            metrics={"elapsed": 1.23},
            assets=[asset],
            path=out_dir,
        )

        metrics_path = os.path.join(out_dir, "metrics", "metrics.json")
        assets_path = os.path.join(out_dir, "assets", "assets.json")
        self.assertTrue(os.path.exists(metrics_path))
        self.assertTrue(os.path.exists(assets_path))

        with open(metrics_path) as f:
            self.assertEqual(json.load(f)["metrics"]["elapsed"], 1.23)

        with open(assets_path) as f:
            content = json.load(f)
        self.assertEqual(content["assets"][0]["name"], "vis")

    def test_json_to_file_via_path_kwarg(self):
        """write to file using path kwarg, no Output object."""
        fpath = os.path.join(self.tmp_dir, "result.json")
        nextmv.write(
            solution={"file_result": 99},
            path=fpath,
        )

        with open(fpath) as f:
            got = json.load(f)
        self.assertEqual(got["solution"]["file_result"], 99)


# ---------------------------------------------------------------------------


class TestWriteResolutionErrorCases(unittest.TestCase):
    """Error conditions in the write() resolution logic."""

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_solution_files_with_json_format_raises(self):
        """Providing solution_files with JSON format raises ValueError."""
        sf = nextmv.json_solution_file("x", {"v": 1})
        with self.assertRaises(ValueError):
            with patch("sys.stdout", new=StringIO()):
                nextmv.write(
                    content_format=ContentFormat.JSON,
                    solution_files=[sf],
                    skip_stdout_reset=True,
                )

    def test_solution_with_multi_file_format_raises(self):
        """Providing solution with MULTI_FILE format raises ValueError."""
        sf = nextmv.json_solution_file("x", {"v": 1})
        out_dir = os.path.join(self.tmp_dir, "err_out")
        with self.assertRaises(ValueError):
            nextmv.write(
                content_format=ContentFormat.MULTI_FILE,
                solution_files=[sf],
                solution={"should_fail": True},
                path=out_dir,
            )

    def test_output_solution_with_multi_file_content_format_raises(self):
        """
        Output.solution != None with MULTI_FILE content_format (via kwarg) raises.
        """
        # Output only has solution set (not solution_files).
        output = nextmv.Output(solution={"oops": True})
        out_dir = os.path.join(self.tmp_dir, "err_out2")
        with self.assertRaises(ValueError):
            nextmv.write(
                output,
                content_format=ContentFormat.MULTI_FILE,
                path=out_dir,
            )

    def test_bad_output_type_raises_type_error(self):
        """Non-Output/dict/BaseModel output raises TypeError."""
        with self.assertRaises(TypeError):
            nextmv.write("not a valid output type")


# ---------------------------------------------------------------------------


class TestLoadWriteEndToEnd(unittest.TestCase):
    """
    End-to-end tests: load input → write output in both JSON and MULTI_FILE
    modes, with various manifest configurations.
    """

    def setUp(self):
        self.original_dir = os.getcwd()
        self.tmp_dir = tempfile.mkdtemp()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_json_roundtrip_no_manifest(self):
        """JSON load + JSON write without any manifest."""
        data = {"locations": [1, 2, 3], "vehicles": 2}
        sample = json.dumps(data) + "\n"

        with patch("sys.stdin", new=StringIO(sample)):
            inp = nextmv.load()

        out_path = os.path.join(self.tmp_dir, "output.json")
        nextmv.write(
            solution=inp.data,
            metrics={"vehicles": inp.data["vehicles"]},
            path=out_path,
        )

        with open(out_path) as f:
            got = json.load(f)

        self.assertEqual(got["solution"]["locations"], [1, 2, 3])
        self.assertEqual(got["metrics"]["vehicles"], 2)

    def test_multi_file_roundtrip_no_manifest(self):
        """MULTI_FILE load + MULTI_FILE write without any manifest."""
        inputs_dir = os.path.join(self.tmp_dir, "inputs")
        os.makedirs(inputs_dir)
        stops = [{"id": 1, "lat": 10.0}, {"id": 2, "lat": 20.0}]
        with open(os.path.join(inputs_dir, "stops.json"), "w") as f:
            json.dump(stops, f)

        inp = nextmv.load(
            input_format=ContentFormat.MULTI_FILE,
            data_files=[nextmv.json_data_file("stops")],
        )

        out_dir = os.path.join(self.tmp_dir, "outputs")
        sf = nextmv.json_solution_file("assignments", {"count": len(inp.data["stops.json"])})
        nextmv.write(
            content_format=ContentFormat.MULTI_FILE,
            solution_files=[sf],
            path=out_dir,
        )

        asgn_path = os.path.join(out_dir, "solutions", "assignments.json")
        self.assertTrue(os.path.exists(asgn_path))
        with open(asgn_path) as f:
            self.assertEqual(json.load(f)["count"], 2)

    def test_json_roundtrip_with_manifest_directly(self):
        """JSON load + write both use a directly-provided manifest."""
        manifest = _make_json_manifest(
            options_items=[{"name": "limit", "option_type": "int", "default": 5, "required": False}]
        )

        fpath = os.path.join(self.tmp_dir, "in.json")
        with open(fpath, "w") as f:
            json.dump({"demand": 10}, f)

        inp = nextmv.load(manifest=manifest, path=fpath)
        self.assertEqual(inp.options.limit, 5)

        out_path = os.path.join(self.tmp_dir, "out.json")
        nextmv.write(
            solution={"served": inp.data["demand"] // inp.options.limit},
            manifest=manifest,
            path=out_path,
        )

        with open(out_path) as f:
            got = json.load(f)
        self.assertEqual(got["solution"]["served"], 2)

    def test_multi_file_roundtrip_with_cwd_manifest(self):
        """MULTI_FILE load + write both go through app.yaml in cwd."""
        inputs_dir = os.path.join(self.tmp_dir, "data_inputs")
        outputs_dir = os.path.join(self.tmp_dir, "data_outputs")
        os.makedirs(inputs_dir)

        manifest = _make_multi_file_manifest(
            input_path=inputs_dir,
            solutions_path=os.path.join(outputs_dir, "solutions"),
            metrics_path=os.path.join(outputs_dir, "metrics.json"),
            assets_path=os.path.join(outputs_dir, "assets.json"),
            statistics_path=os.path.join(outputs_dir, "stats.json"),
        )
        _write_app_yaml(self.tmp_dir, manifest)

        orders = [{"order_id": 1, "qty": 100}]
        with open(os.path.join(inputs_dir, "orders.json"), "w") as f:
            json.dump(orders, f)

        inp = nextmv.load(data_files=[nextmv.json_data_file("orders")])
        self.assertEqual(inp.input_format, ContentFormat.MULTI_FILE)

        sf = nextmv.json_solution_file(
            "plan",
            {"assignments": [{"order_id": o["order_id"]} for o in inp.data["orders.json"]]},
        )
        output = nextmv.Output(
            output_format=ContentFormat.MULTI_FILE,
            solution_files=[sf],
            metrics={"total_orders": len(inp.data["orders.json"])},
        )
        nextmv.write(output)

        plan_path = os.path.join(outputs_dir, "solutions", "plan.json")
        self.assertTrue(os.path.exists(plan_path))
        with open(plan_path) as f:
            plan = json.load(f)
        self.assertEqual(plan["assignments"][0]["order_id"], 1)

        metrics_path = os.path.join(outputs_dir, "metrics.json")
        self.assertTrue(os.path.exists(metrics_path))
        with open(metrics_path) as f:
            m = json.load(f)
        self.assertEqual(m["metrics"]["total_orders"], 1)
