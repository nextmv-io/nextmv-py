import csv
import json
import os
import shutil
import unittest
from io import StringIO
from typing import Any, Optional
from unittest.mock import patch

import nextmv
from nextmv.base_model import BaseModel


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

        # Test with JSON configurations
        json_config = {"indent": 4, "sort_keys": True}
        output = nextmv.Output(output_format=nextmv.OutputFormat.JSON, json_configurations=json_config)
        result = output.to_dict()
        self.assertEqual(result["json_configurations"]["indent"], 4)
        self.assertEqual(result["json_configurations"]["sort_keys"], True)

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
        self.assertEqual(result["json_configurations"]["indent"], 4)

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
                '{"assets":[],"json_configurations":{"separators":[",",":"],"sort_keys":true},"options":{},"solution":{"empanadas":"are_life"},"statistics":{"foo":"bar"}}\n',
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
