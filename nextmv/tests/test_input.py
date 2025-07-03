import csv
import json
import os
import shutil
import unittest
from io import StringIO
from typing import Optional
from unittest.mock import patch

import pandas as pd

import nextmv


class TestInput(unittest.TestCase):
    """
    Tests for the various classes for loading an input.
    """

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create test directory and files
        self.test_dir = "test_inputs"
        os.makedirs(self.test_dir, exist_ok=True)

        # Create test JSON file
        self.json_data = {"message": "Hello from JSON", "numbers": [1, 2, 3]}
        with open(f"{self.test_dir}/test_data.json", "w", encoding="utf-8") as f:
            json.dump(self.json_data, f)

        # Create test CSV file
        self.csv_data = [
            {"name": "Alice", "age": "25", "city": "New York"},
            {"name": "Bob", "age": "30", "city": "London"},
            {"name": "Charlie", "age": "35", "city": "Tokyo"},
        ]
        with open(f"{self.test_dir}/test_data.csv", "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
            writer.writeheader()
            writer.writerows(self.csv_data)

        # Create test text file
        self.text_data = "This is a test text file.\nIt contains multiple lines.\nHello from text!"
        with open(f"{self.test_dir}/test_data.txt", "w", encoding="utf-8") as f:
            f.write(self.text_data)

        # Create test Excel file if pandas is available
        self.excel_data = pd.DataFrame(
            [
                {"product": "Widget A", "price": 10.99, "quantity": 100},
                {"product": "Widget B", "price": 15.50, "quantity": 50},
                {"product": "Widget C", "price": 8.75, "quantity": 200},
            ]
        )
        self.excel_data.to_excel(f"{self.test_dir}/test_data.xlsx", index=False)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

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
        options = nextmv.Options(nextmv.Option("foo", str, default="bar", required=False))
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

    def test_json_data_file_convenience_function(self):
        """Test the json_data_file convenience function."""
        data_file = nextmv.json_data_file("test_data")

        # Test that the name gets .json extension
        self.assertEqual(data_file.name, "test_data.json")

        # Test that the loader is callable
        self.assertTrue(callable(data_file.loader))

        # Test loading data with the convenience function
        result = data_file.loader(f"{self.test_dir}/test_data.json")
        self.assertEqual(result, self.json_data)

    def test_json_data_file_with_extension(self):
        """Test json_data_file when name already has .json extension."""
        data_file = nextmv.json_data_file("test_data.json")
        self.assertEqual(data_file.name, "test_data.json")

    def test_json_data_file_with_configurations(self):
        """Test json_data_file with JSON-specific configurations."""
        # Create a JSON file with custom format for testing
        custom_json = '{"key": 1.5, "another": 2.7}'
        with open(f"{self.test_dir}/custom.json", "w") as f:
            f.write(custom_json)

        data_file = nextmv.json_data_file("custom", json_configurations={"parse_float": str})
        result = data_file.loader(f"{self.test_dir}/custom.json")

        # With parse_float=str, float values should be strings
        self.assertEqual(result["key"], "1.5")
        self.assertEqual(result["another"], "2.7")

    def test_csv_data_file_convenience_function(self):
        """Test the csv_data_file convenience function."""
        data_file = nextmv.csv_data_file("test_data")

        # Test that the name gets .csv extension
        self.assertEqual(data_file.name, "test_data.csv")

        # Test that the loader is callable
        self.assertTrue(callable(data_file.loader))

        # Test loading data with the convenience function
        result = data_file.loader(f"{self.test_dir}/test_data.csv")
        self.assertEqual(result, self.csv_data)

    def test_csv_data_file_with_extension(self):
        """Test csv_data_file when name already has .csv extension."""
        data_file = nextmv.csv_data_file("test_data.csv")
        self.assertEqual(data_file.name, "test_data.csv")

    def test_csv_data_file_with_configurations(self):
        """Test csv_data_file with CSV-specific configurations."""
        # Create a CSV file with quotes for testing
        quoted_csv = '"name","age","city"\n"Alice","25","New York"\n"Bob","30","London"'
        with open(f"{self.test_dir}/quoted.csv", "w") as f:
            f.write(quoted_csv)

        data_file = nextmv.csv_data_file("quoted", csv_configurations={"quoting": csv.QUOTE_ALL})
        result = data_file.loader(f"{self.test_dir}/quoted.csv")

        expected = [{"name": "Alice", "age": "25", "city": "New York"}, {"name": "Bob", "age": "30", "city": "London"}]
        self.assertEqual(result, expected)

    def test_text_data_file_convenience_function(self):
        """Test the text_data_file convenience function."""
        data_file = nextmv.text_data_file("test_data.txt")

        # Test that the name remains as provided (with extension)
        self.assertEqual(data_file.name, "test_data.txt")

        # Test that the loader is callable
        self.assertTrue(callable(data_file.loader))

        # Test loading data with the convenience function
        result = data_file.loader(f"{self.test_dir}/test_data.txt")
        self.assertEqual(result, self.text_data)

    def test_data_file_class_direct_usage(self):
        """Test creating DataFile instances directly."""

        def custom_loader(file_path):
            with open(file_path, encoding="utf-8") as f:
                return f.read().upper()

        data_file = nextmv.DataFile(name="test_data.txt", loader=custom_loader)

        self.assertEqual(data_file.name, "test_data.txt")
        self.assertTrue(callable(data_file.loader))

        # Test that our custom loader works
        result = data_file.loader(f"{self.test_dir}/test_data.txt")
        self.assertEqual(result, self.text_data.upper())

    def test_data_file_with_excel_pandas(self):
        """Test DataFile with custom Excel loader using pandas."""
        data_file = nextmv.DataFile(
            name="test_data.xlsx",
            loader=lambda file_path, **kwargs: pd.read_excel(file_path, **kwargs),
        )

        self.assertEqual(data_file.name, "test_data.xlsx")

        # Test loading Excel data
        result = data_file.loader(f"{self.test_dir}/test_data.xlsx")

        # Convert to dict for comparison
        result_dict = result.to_dict("records")
        expected_dict = self.excel_data.to_dict("records")
        self.assertEqual(result_dict, expected_dict)

    def test_data_file_with_loader_args_and_kwargs(self):
        """Test DataFile with loader_args and loader_kwargs."""

        def custom_loader(file_path, prefix="", suffix="", multiplier=1):
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
                return f"{prefix}{content * multiplier}{suffix}"

        data_file = nextmv.DataFile(
            name="test_data.txt",
            loader=custom_loader,
            loader_args=["[PREFIX]"],
            loader_kwargs={"suffix": "[SUFFIX]", "multiplier": 2},
        )

        # This test would normally be done through the multi-file loader
        # but here we test the structure is correct
        self.assertEqual(data_file.loader_args, ["[PREFIX]"])
        self.assertEqual(data_file.loader_kwargs, {"suffix": "[SUFFIX]", "multiplier": 2})

    def test_load_multi_file_format(self):
        """Test loading multiple files using MULTI_FILE format."""
        data_files = [
            nextmv.json_data_file("test_data"),
            nextmv.csv_data_file("test_data"),
            nextmv.text_data_file("test_data.txt"),
        ]

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.MULTI_FILE)

        # Check that all files were loaded
        self.assertIn("test_data.json", input_data.data)
        self.assertIn("test_data.csv", input_data.data)
        self.assertIn("test_data.txt", input_data.data)

        # Verify data content
        self.assertEqual(input_data.data["test_data.json"], self.json_data)
        self.assertEqual(input_data.data["test_data.csv"], self.csv_data)
        self.assertEqual(input_data.data["test_data.txt"], self.text_data)

    def test_load_multi_file_with_excel(self):
        """Test loading multiple files including Excel using MULTI_FILE format."""
        data_files = [
            nextmv.json_data_file("test_data"),
            nextmv.csv_data_file("test_data"),
            nextmv.text_data_file("test_data.txt"),
            nextmv.DataFile(
                name="test_data.xlsx",
                loader=lambda file_path, **kwargs: pd.read_excel(file_path, **kwargs),
            ),
        ]

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        self.assertIsInstance(input_data, nextmv.Input)
        self.assertEqual(input_data.input_format, nextmv.InputFormat.MULTI_FILE)

        # Check that all files were loaded including Excel
        self.assertIn("test_data.json", input_data.data)
        self.assertIn("test_data.csv", input_data.data)
        self.assertIn("test_data.txt", input_data.data)
        self.assertIn("test_data.xlsx", input_data.data)

        # Verify Excel data was loaded as DataFrame
        excel_result = input_data.data["test_data.xlsx"]
        self.assertIsInstance(excel_result, pd.DataFrame)

    def test_load_multi_file_missing_data_files(self):
        """Test that ValueError is raised when data_files is None for MULTI_FILE format."""
        with self.assertRaises(ValueError) as context:
            nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=None)

        self.assertIn("data_files must be provided", str(context.exception))

    def test_load_multi_file_invalid_data_files_type(self):
        """Test that ValueError is raised when data_files is not a list."""
        with self.assertRaises(ValueError) as context:
            nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files="not_a_list")

        self.assertIn("data_files must be a list", str(context.exception))

    def test_load_multi_file_default_directory(self):
        """Test loading multi-file with default directory 'inputs'."""
        # Create inputs directory and copy test files
        inputs_dir = "inputs"
        os.makedirs(inputs_dir, exist_ok=True)

        try:
            # Copy test files to inputs directory
            shutil.copy(f"{self.test_dir}/test_data.json", f"{inputs_dir}/test_data.json")
            shutil.copy(f"{self.test_dir}/test_data.csv", f"{inputs_dir}/test_data.csv")

            data_files = [nextmv.json_data_file("test_data"), nextmv.csv_data_file("test_data")]

            # Load without specifying path (should use default "inputs" directory)
            input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files)

            self.assertIsInstance(input_data, nextmv.Input)
            self.assertIn("test_data.json", input_data.data)
            self.assertIn("test_data.csv", input_data.data)

        finally:
            if os.path.exists(inputs_dir):
                shutil.rmtree(inputs_dir)

    def test_load_multi_file_nonexistent_directory(self):
        """Test that ValueError is raised when directory doesn't exist."""
        data_files = [nextmv.json_data_file("test_data")]

        with self.assertRaises(ValueError) as context:
            nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path="nonexistent_directory")

        self.assertIn("path nonexistent_directory is not a directory", str(context.exception))

    def test_load_multi_file_path_not_directory(self):
        """Test that ValueError is raised when path points to a file instead of directory."""
        # Create a file instead of directory
        test_file = "not_a_directory.txt"
        with open(test_file, "w") as f:
            f.write("test")

        try:
            data_files = [nextmv.json_data_file("test_data")]

            with self.assertRaises(ValueError) as context:
                nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=test_file)

            self.assertIn(f"path {test_file} is not a directory", str(context.exception))

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_data_file_loader_with_custom_args_kwargs(self):
        """Test DataFile loader with custom args and kwargs in multi-file context."""

        def custom_json_loader(file_path, prefix="", parse_float=None):
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f, parse_float=parse_float)
                if prefix:
                    return {f"{prefix}_{k}": v for k, v in data.items()}
                return data

        # Create a test JSON file with floats
        test_data = {"value": 3.14, "count": 42}
        with open(f"{self.test_dir}/custom.json", "w") as f:
            json.dump(test_data, f)

        data_file = nextmv.DataFile(
            name="custom.json", loader=custom_json_loader, loader_kwargs={"prefix": "custom", "parse_float": str}
        )

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        result = input_data.data["custom.json"]
        expected = {"custom_value": "3.14", "custom_count": 42}
        self.assertEqual(result, expected)

    def test_mixed_data_types_multi_file(self):
        """Test loading different data types in a single multi-file input."""
        # Create additional test files
        with open(f"{self.test_dir}/config.txt", "w") as f:
            f.write("debug=true\nverbose=false")

        # Custom configuration parser
        def parse_config(file_path):
            config = {}
            with open(file_path) as f:
                for line in f:
                    key, value = line.strip().split("=")
                    config[key] = value.lower() == "true" if value.lower() in ["true", "false"] else value
            return config

        data_files = [
            nextmv.json_data_file("test_data"),  # Returns dict
            nextmv.csv_data_file("test_data"),  # Returns list of dicts
            nextmv.text_data_file("test_data.txt"),  # Returns string
            nextmv.DataFile(name="config.txt", loader=parse_config),  # Returns dict
        ]

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        # Verify different data types
        self.assertIsInstance(input_data.data["test_data.json"], dict)
        self.assertIsInstance(input_data.data["test_data.csv"], list)
        self.assertIsInstance(input_data.data["test_data.txt"], str)
        self.assertIsInstance(input_data.data["config.txt"], dict)

        # Verify config parsing worked
        self.assertEqual(input_data.data["config.txt"]["debug"], True)
        self.assertEqual(input_data.data["config.txt"]["verbose"], False)

    # Tests for input_data_key functionality
    def test_json_data_file_with_input_data_key(self):
        """Test json_data_file with custom input_data_key."""
        data_file = nextmv.json_data_file("test_data", input_data_key="custom_json_key")

        # Test that input_data_key is set correctly
        self.assertEqual(data_file.input_data_key, "custom_json_key")

        # Test in multi-file context
        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key instead of filename
        self.assertIn("custom_json_key", input_data.data)
        self.assertNotIn("test_data.json", input_data.data)
        self.assertEqual(input_data.data["custom_json_key"], self.json_data)

    def test_csv_data_file_with_input_data_key(self):
        """Test csv_data_file with custom input_data_key."""
        data_file = nextmv.csv_data_file("test_data", input_data_key="custom_csv_key")

        # Test that input_data_key is set correctly
        self.assertEqual(data_file.input_data_key, "custom_csv_key")

        # Test in multi-file context
        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key instead of filename
        self.assertIn("custom_csv_key", input_data.data)
        self.assertNotIn("test_data.csv", input_data.data)
        self.assertEqual(input_data.data["custom_csv_key"], self.csv_data)

    def test_text_data_file_with_input_data_key(self):
        """Test text_data_file with custom input_data_key."""
        data_file = nextmv.text_data_file("test_data.txt", input_data_key="custom_text_key")

        # Test that input_data_key is set correctly
        self.assertEqual(data_file.input_data_key, "custom_text_key")

        # Test in multi-file context
        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key instead of filename
        self.assertIn("custom_text_key", input_data.data)
        self.assertNotIn("test_data.txt", input_data.data)
        self.assertEqual(input_data.data["custom_text_key"], self.text_data)

    def test_data_file_with_input_data_key_direct(self):
        """Test DataFile with custom input_data_key set directly."""

        def custom_loader(file_path):
            with open(file_path, encoding="utf-8") as f:
                return f.read().upper()

        data_file = nextmv.DataFile(name="test_data.txt", loader=custom_loader, input_data_key="custom_direct_key")

        # Test that input_data_key is set correctly
        self.assertEqual(data_file.input_data_key, "custom_direct_key")

        # Test in multi-file context
        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key instead of filename
        self.assertIn("custom_direct_key", input_data.data)
        self.assertNotIn("test_data.txt", input_data.data)
        self.assertEqual(input_data.data["custom_direct_key"], self.text_data.upper())

    def test_mixed_files_with_and_without_input_data_key(self):
        """Test mix of files with and without custom input_data_key."""
        data_files = [
            nextmv.json_data_file("test_data", input_data_key="json_config"),
            nextmv.csv_data_file("test_data"),  # No custom key, should use filename
            nextmv.text_data_file("test_data.txt", input_data_key="readme_content"),
        ]

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        # Check that custom keys are used where specified
        self.assertIn("json_config", input_data.data)
        self.assertIn("readme_content", input_data.data)
        self.assertNotIn("test_data.json", input_data.data)
        self.assertNotIn("test_data.txt", input_data.data)

        # Check that filename is used when no custom key is specified
        self.assertIn("test_data.csv", input_data.data)

        # Verify data content
        self.assertEqual(input_data.data["json_config"], self.json_data)
        self.assertEqual(input_data.data["test_data.csv"], self.csv_data)
        self.assertEqual(input_data.data["readme_content"], self.text_data)

    def test_input_data_key_with_configurations(self):
        """Test input_data_key works with loader configurations."""
        # Create a CSV file with quotes for testing
        quoted_csv = '"name","age","city"\n"Alice","25","New York"\n"Bob","30","London"'
        with open(f"{self.test_dir}/quoted.csv", "w") as f:
            f.write(quoted_csv)

        data_file = nextmv.csv_data_file(
            "quoted", csv_configurations={"quoting": csv.QUOTE_ALL}, input_data_key="users_data"
        )

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key
        self.assertIn("users_data", input_data.data)
        self.assertNotIn("quoted.csv", input_data.data)

        # Verify data was loaded with configurations
        expected = [{"name": "Alice", "age": "25", "city": "New York"}, {"name": "Bob", "age": "30", "city": "London"}]
        self.assertEqual(input_data.data["users_data"], expected)

    def test_input_data_key_with_json_configurations(self):
        """Test input_data_key works with JSON loader configurations."""
        # Create a JSON file with custom format for testing
        custom_json = '{"key": 1.5, "another": 2.7}'
        with open(f"{self.test_dir}/custom.json", "w") as f:
            f.write(custom_json)

        data_file = nextmv.json_data_file(
            "custom", json_configurations={"parse_float": str}, input_data_key="parsed_floats"
        )

        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use custom key
        self.assertIn("parsed_floats", input_data.data)
        self.assertNotIn("custom.json", input_data.data)

        # With parse_float=str, float values should be strings
        self.assertEqual(input_data.data["parsed_floats"]["key"], "1.5")
        self.assertEqual(input_data.data["parsed_floats"]["another"], "2.7")

    def test_input_data_key_none_uses_filename(self):
        """Test that when input_data_key is None, filename is used as key."""
        data_file = nextmv.json_data_file("test_data", input_data_key=None)

        # Test that input_data_key is None
        self.assertIsNone(data_file.input_data_key)

        # Test in multi-file context
        input_data = nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=[data_file], path=self.test_dir)

        # Should use filename as key
        self.assertIn("test_data.json", input_data.data)
        self.assertEqual(input_data.data["test_data.json"], self.json_data)

    def test_duplicate_input_data_keys_raises_error(self):
        """Test that ValueError is raised when multiple files have the same input_data_key."""
        # Create second JSON file
        second_json_data = {"different": "content", "values": [4, 5, 6]}
        with open(f"{self.test_dir}/second_data.json", "w", encoding="utf-8") as f:
            json.dump(second_json_data, f)

        data_files = [
            nextmv.json_data_file("test_data", input_data_key="shared_key"),
            nextmv.json_data_file("second_data", input_data_key="shared_key"),
        ]

        # Should raise ValueError for duplicate keys
        with self.assertRaises(ValueError) as context:
            nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        self.assertIn("Duplicate input data key found: shared_key", str(context.exception))

    def test_duplicate_key_filename_conflict_raises_error(self):
        """Test that ValueError is raised when custom input_data_key conflicts with a filename."""
        data_files = [
            nextmv.json_data_file("test_data"),  # Uses filename "test_data.json" as key
            nextmv.csv_data_file("test_data", input_data_key="test_data.json"),  # Custom key conflicts with filename
        ]

        # Should raise ValueError for duplicate keys
        with self.assertRaises(ValueError) as context:
            nextmv.load(nextmv.InputFormat.MULTI_FILE, data_files=data_files, path=self.test_dir)

        self.assertIn("Duplicate input data key found: test_data.json", str(context.exception))
